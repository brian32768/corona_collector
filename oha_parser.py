from bs4 import BeautifulSoup
import pandas as pd
import re
from datetime import datetime, timezone
from utils import local2utc

from arcgis.gis import GIS
import arcgis.features

class OHAParser:

    @staticmethod
    def format_table_header_column(th):
        """
        Parses a raw HTML table header column and returns formatted string

        @Params:
        th (string): TableHeader column from countries table

        @Returns:
        Table header as string
        """

        header = " ".join(th.strings)  # join strings broken by <br> tags
        # replace non-breaking space with space and remove \n
        header = header.replace(u"\xa0", u" ").replace("\n", "") 
        return header.replace(", ", "/")

    @staticmethod
    def create_df(raw_data):
        """
        Parses the raw HTML response and returns a DataFrame
        containing hospital capacity and usage data.

        I tried collecting case data but they don't put negative tests on the web page
        only cases so I still get that from the feature class

        @Params:
        raw_data (string): request.text

        @Returns:
        DataFrame
        """

        soup = BeautifulSoup(raw_data, features="html.parser")

        _id = "collapseDemographics"

        demographics_card = soup.find("div", attrs={"id": _id})

        columns = [OHAParser.format_table_header_column(th) for th
                   in demographics_card.find("thead").findAll("th")]
   
        #vars
        parsed_data = []
        regx = r'(\n|\+|,)'
        rows = demographics_card.find("tbody").find_all("tr")

        def sort_alphabetically(element):
            sorted_element = element.findAll("td")[1].get_text().strip()
            return sorted_element
        
        rows.sort(key=sort_alphabetically)
        for row in rows:
            classname = re.sub(regx, "", row.findAll("td")[0].get_text())
            if classname != 'Total':
                #print("classname '%s' '%s'" % (classname, row))
                parsed_data.append([data.get_text().strip() for data
                                    in row.findAll("td")])
        
        df = pd.DataFrame(parsed_data, columns=columns)
        return df.replace(to_replace=[""], value=0)


    @staticmethod
    def fetch_feature_df():
        """ Download today's data from the OHA site.
        Return it in a spatially enabled data frame. """

        sourceUrl = "https://services.arcgis.com/uUvqNMGPm7axC2dD/ArcGIS/rest/services/COVID_Cases_Oregon_Public/FeatureServer/0"

        layer = arcgis.features.FeatureLayer(url=sourceUrl)
        counties = "altName='Clatsop' OR altName='Columbia' OR altName='Tillamook' OR altName='Clackamas' OR altName='Multnomah' OR altName='Washington'"
        fields = "*"

        # NOTE we're asking for the data in Web Mercator, 3857
        # Default is WGS84, 4269
        # (but we throw it away later!!!)
        return layer.query(where=counties, out_fields=fields, out_sr=3857).sdf

    @staticmethod
    def parse_last_updated(raw_data):
        """
        Parses the raw HTML and returns the lastest update time from the webpage

        @Params:
        raw_data (string): request.text from OHA

        @Returns:
        Last updated time (datetime object in UTC)
        """
        soup = BeautifulSoup(raw_data, features="html.parser")
        re_datestamp = re.compile(r'Data current as of (\S+,\s+\S+\s+[a|p]?)')
        try:
            th = soup.find_all('th')[0].text
            mo = re_datestamp.search(th)
            if mo:
                last_updated = mo.group(1) + 'm'
                local = datetime.strptime(last_updated, "%m/%d/%Y, %I:%M %p")
                return local2utc(local)
        except Exception as e:
            print("Date parse failed.", e) 
        return datetime.utcnow()

if __name__ == "__main__":
    # Unit test using the file that's create in the _gateway unit test!

    with open("./oha.html", "r", encoding="utf-8") as fp:
        raw_data = fp.read()

    parser = OHAParser()

    df = parser.create_df(raw_data)
    print(df)

    # This actually reads the data from ArcGIS.com not a file.
    df = parser.fetch_feature_df()
    print(df)

    last_updated = parser.parse_last_updated(raw_data)
    print(last_updated)

    print("Parser succeeded using oha.html data!")
    exit(0)
