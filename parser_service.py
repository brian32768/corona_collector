from bs4 import BeautifulSoup
import pandas as pd
import re
from datetime import datetime, timezone

class ParserService:

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
    def create_df_worldometer(raw_data):
        """
        Parses the raw HTML response from Worldometer and returns a DataFrame from it

        @Params:
        raw_data (string): request.text from Worldometer

        @Returns:
        DataFrame
        """

        soup = BeautifulSoup(raw_data, features="html.parser")

        _id = "main_table_countries_today"

        countries_table = soup.find("table", attrs={"id": _id})

        columns = [ParserService.format_table_header_column(th) for th
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
        Parses the raw HTML response from Worldometer and returns the lastest update time from the webpage

        @Params:
        raw_data (string): request.text from Worldometer

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

