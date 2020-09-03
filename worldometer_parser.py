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
    def create_df(raw_data, table_id, myClassname, rowindex=0):
        """
        Parses the raw HTML response and returns as a DataFrame

        @Params:
        raw_data (string): request.text in HTML
        table_id (string): name of the table in the HTML
        myClassname (string): what to look for, eg 'Oregon'
        rowindex (int): which row to search in the table
        @Returns:
        DataFrame
        """

        soup = BeautifulSoup(raw_data, features="html.parser")
        table = soup.find("table", attrs={"id": table_id})
        columns = [WorldometerParser.format_table_header_column(th) for th
                   in table.find("thead").findAll("th")]

        parsed_data = []
        regx = r'(\n|\+|,)'
        rows = table.find("tbody").find_all("tr")

        #utility functions
        def sort_alphabetically(element):
            sorted_element = element.findAll("td")[1].get_text().strip()
            return sorted_element
        
        rows.sort(key=sort_alphabetically)

        for row in rows:
            classname = re.sub(regx, "", row.findAll("td")[rowindex].get_text().strip())
            #print("classname '%s'" % classname)
            if  classname == '' or classname == myClassname:
                parsed_data.append([data.get_text().strip() for data
                                in row.find_all("td")])
                pass
        
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

        #last_updated = 'Last updated: May 28, 2020, 01:46 GMT'

        style1 = "font-size:13px; color:#999; margin-top:5px; text-align:center"
        style2 = "font-size:13px; color:#999; text-align:center"
        try:
            div1 = soup.find('div', {"style": style1}).text
            dt = datetime.strptime(div1, "Last updated: %B %d, %Y, %H:%M GMT")
        except Exception as e:
            #print(e)
            pass
        try:
            div2 = soup.find('div', {"style": style2}).text
            dt = datetime.strptime(div2, "Last updated: %B %d, %Y, %H:%M GMT")
        except Exception as e:
            #print(e)
            pass
            
        return dt.replace(tzinfo=timezone.utc)


if __name__ == "__main__":
    # Unit test using the file that's create in the _gateway unit test!

    # curl -o worldometer_states.html https://www.worldometers.info/coronavirus/country/us
    with open("./worldometer_states.html", "r", encoding="utf-8") as fp:
        raw_data = fp.read()
    parser = WorldometerParser()
    last_updated = parser.parse_last_updated(raw_data)
    print(last_updated)
    df = parser.create_df(raw_data, "usa_table_countries_today", 'Oregon', rowindex=1)
    print(df)
    assert df.at[0, 'USA State'] == 'Oregon'

    with open("./worldometer.html", "r", encoding="utf-8") as fp:
        raw_data = fp.read()
    parser = WorldometerParser()
    last_updated = parser.parse_last_updated(raw_data)
    print(last_updated)
    df = parser.create_df(raw_data, "main_table_countries_today", '1')
    print(df)

    print("Parser succeeded using worldometer html data!")
    exit(0)
# That's all!
