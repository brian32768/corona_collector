from bs4 import BeautifulSoup
import pandas as pd
import re
from datetime import datetime, timezone

class WorldometerParser:

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
        Parses the raw HTML response and returns as a DataFrame

        @Params:
        raw_data (string): request.text

        @Returns:
        DataFrame
        """

        soup = BeautifulSoup(raw_data, features="html.parser")

        _id = "main_table_countries_today"

        countries_table = soup.find("table", attrs={"id": _id})

        columns = [WorldometerParser.format_table_header_column(th) for th
                   in countries_table.find("thead").findAll("th")]
   
        #vars
        parsed_data = []
        regx = r'(\n|\+|,)'
        country_rows = countries_table.find("tbody").find_all("tr")

        #utility functions
        def sort_alphabetically(element):
            sorted_element = element.findAll("td")[1].get_text().strip()
            return sorted_element
        
        #sort countries
        country_rows.sort(key=sort_alphabetically)

        for country_row in country_rows:
            country_classname = re.sub(regx, "", country_row.findAll("td")[0].get_text())
            #skip continents, we only need countries
#            if country_classname is '' or 0: continue
            #print("country", country_row, country_classname)
            # We're interested only in USA or continents
            if country_classname == '' or country_classname == '1':
                #print("country '%s'" % country_classname)

                parsed_data.append([data.get_text().strip() for data
                                in country_row.findAll("td")])
            
        
        df = pd.DataFrame(parsed_data, columns=columns)
        return df.replace(to_replace=[""], value=0)
    

    @staticmethod
    def parse_last_updated(raw_data):
        """
        Parses the raw HTML and returns the lastest update time from the webpage

        @Params:
        raw_data (string): request.text

        @Returns:
        Last updated time (datetime object in UTC)
        """
        
        soup = BeautifulSoup(raw_data, features="html.parser")
        
        _styles = "font-size:13px; color:#999; margin-top:5px; text-align:center"
        
        last_updated = soup.find("div", {"style": _styles}).text
        #last_updated = 'Last updated: May 28, 2020, 01:46 GMT'

        return datetime.strptime(
            last_updated, 
            "Last updated: %B %d, %Y, %H:%M GMT").replace(tzinfo=timezone.utc)


if __name__ == "__main__":
    # Unit test using the file that's create in the _gateway unit test!

    with open("./worldometer.html", "r", encoding="utf-8") as fp:
        raw_data = fp.read()

    parser = WorldometerParser()

    df = parser.create_df(raw_data)
    print(df)

    last_updated = parser.parse_last_updated(raw_data)
    print(last_updated)

    print("Parser succeeded using worldometer.html data!")
    exit(0)
# That's all!
