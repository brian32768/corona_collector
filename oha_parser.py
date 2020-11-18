from bs4 import BeautifulSoup
import pandas as pd
import re
from datetime import datetime
from utils import local2utc
from html_gateway import HTMLGateway
from tableau_gateway import TableauGateway
from arcgis.gis import GIS
from arcgis.features import FeatureLayer
import json

featureLayerUrl = "https://services.arcgis.com/uUvqNMGPm7axC2dD/ArcGIS/rest/services/COVID_Cases_Oregon_Public/FeatureServer/0"

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
    def fetch_capacity_df(raw_data):
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
        demographics_tables = demographics_card.findAll("table")

        BEDCAPTABLE = 4

        columns = [OHAParser.format_table_header_column(th) for th
                   in demographics_tables[BEDCAPTABLE].find("thead").findAll("th")]
        print(columns)
        
        parsed_data = []
        regx = r'(\n|\+|,)'
        rows = demographics_tables[BEDCAPTABLE].find("tbody").find_all("tr")

        def sort_alphabetically(element):
            sorted_element = element.findAll("td")[1].get_text().strip()
            return sorted_element
        
        rows.sort(key=sort_alphabetically)
        for row in rows:
            classname = re.sub(regx, "", row.findAll("td")[0].get_text())
            if classname != 'Total': # Ignore the bottom line
                #print("classname '%s' '%s'" % (classname, row))
                parsed_data.append([data.get_text().strip() for data
                                    in row.findAll("td")])
        
        df = pd.DataFrame(parsed_data, columns=columns)
        return df.replace(to_replace=[""], value=0)

    @staticmethod
    def fetch_state_cases_df(raw_data):
        """
        Parses the raw HTML response and returns a DataFrame
        containing state level cases.

        Note this is currently the same table that the "last update" comes from.

        @Params:
        raw_data (string): request.text

        @Returns:
        DataFrame
        """
        soup = BeautifulSoup(raw_data, features="html.parser")
        state_table = soup.find_all('tr')
        columns = ['name']
        parsed_data = ['OR']
        interesting_rows = ['Total cases', 'Total deaths',
                            'Positive tests', 'Negative tests', 'Total tested']
        
        for row in state_table:
            data = row.findAll("td")
            if len(data) == 2:
                column = data[0].get_text().strip()
                if column in interesting_rows:
                    columns.append(column)
                    value = data[1].get_text().strip()

        # The value for total cases has a superscript on it that has to be removed
                    if column == 'Total cases' and value[-1] == '1':
                        value = value[:-1]

                    parsed_data.append(value)
                    
        df = pd.DataFrame([parsed_data], columns=columns)
        return df.replace(to_replace=[""], value=0)

    @staticmethod
    def last_update(raw_data):
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

    @staticmethod
    def fetch_feature_df():
        """
        Download current data from the OHA feature layer.

        @Returns:
        Spatially enabled data frame.
        """

        layer = FeatureLayer(url=featureLayerUrl)

        # The data displayed in the dashboard can come from here or from the web form 

        counties = "altName='Columbia' OR altName='Tillamook' OR altName='Clackamas' OR altName='Multnomah' OR altName='Washington' OR altName='Clatsop'"
        fields = "*"

        # NOTE we're asking for the data in Web Mercator, 3857
        # Default is WGS84, 4269
        # (but we throw it away later!!!)
        return layer.query(where=counties, out_fields=fields, out_sr=3857).sdf

    @staticmethod
    def last_feature_edit():
        """
        Fetch the JSON for the OHA feature layer.

        @Returns:
        Last edit time (datetime object in UTC)
        """
        ohajson = HTMLGateway.fetch(featureLayerUrl + '?f=json')
        oha = json.loads(ohajson)

        # Convert from the Esri format to the real one by /1000
        unixtime = int(oha['editingInfo']['lastEditDate']) / 1000
        utc = datetime.utcfromtimestamp(unixtime)
        return utc

if __name__ == "__main__":
    # Unit test using the file that's created in the html_gateway unit test!

    with open("./oha.html", "r", encoding="utf-8") as fp:
        raw_data = fp.read()

    # This actually reads the data from ArcGIS.com not a file.
    last_edit = OHAParser.last_feature_edit()
    print("Last feature edit", last_edit)

    df = OHAParser.fetch_feature_df()
    print(df)

    last_updated = OHAParser.last_update(raw_data)
    print(last_updated)

    df = OHAParser.fetch_state_cases_df(raw_data)
    print(df)

    df = OHAParser.fetch_capacity_df(raw_data)
    print(df)

    print("Parser succeeded using stored data!")
    exit(0)

# That's all!
