from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timezone
import json
from utils import local2utc
import re

from arcgis.gis import GIS
import arcgis.features

class WAParser:

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
    def fetch_cases(raw_data):
        """
        Parses the raw data response and returns a DataFrame
        containing cases.

        @Params:
        raw_data (string): json data in a string

        @Returns:
        DataFrame
        """
        parsed_data = json.loads(raw_data) # this will just be a dict
        df = pd.DataFrame(parsed_data.items())
        return df.set_index(keys=[0], drop=True).transpose()

    @staticmethod
    def parse_last_updated(raw_data):
        """
        Parses the raw HTML and returns the lastest update time from the webpage

        @Params:
        raw_data (string): json data in a string

        @Returns:
        Last updated time (datetime object in UTC)
        """
        parsed_data = json.loads(raw_data)  # this will just be a dict
        datestamp = parsed_data['dateModified']
        return datetime.strptime(datestamp, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)

def wa_read():
    with open("./wa.json", "r", encoding="utf-8") as fp:
        raw_data = fp.read()
    return raw_data

if __name__ == "__main__":
    # Unit test using the file that's created in the html_gateway unit test!

    json_data = wa_read()
    df = WAParser.fetch_cases(json_data)
    print(df)

    last_updated = WAParser.parse_last_updated(json_data)
    print(last_updated)

    print("Parser succeeded using stored data!")
    exit(0)

# That's all!
