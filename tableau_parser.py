from tableau_gateway import TableauGateway
from bs4 import BeautifulSoup
import pandas as pd
import re
from datetime import datetime
from utils import local2utc
import json

from config import Config

class TableauParser:

    @staticmethod
    def last_update(rawdata):
        """
        Parses the raw data and returns the lastest update time from the webpage

        @Params:
        raw_data (string): from OHA

        @Returns:
        Last updated time (datetime object in UTC)
        """       
        r = re.compile(r'Data current as of (.*)')
        for item in rawdata:
            #print(item)
            mo = r.search(item)
            if mo:
                span = mo.group(1).upper()
                # 9:00am 11/12/2020
                local = datetime.strptime(span, "%I:%M%p %m/%d/%Y")
                return local2utc(local)
        
        return None

    @staticmethod
    def summary(rawdata):
        keys = []
        values = []
        columns=['value']

        # Another hacky web scraping thing
        # the data comes in with column names and data in a single one dimensional list
        # So I read everything and create a column containing values
        # and index containing keys
        # but there are more lines in the indexes
        # so lop those off
        # and of course there are some extra lines that get lopped off at the beginning too

        for item in rawdata:
            if item[0] == '[': continue
            if item.startswith('Contact'): continue
            item = item.replace(',','')
            try:
                number = int(item)
                #print(number)
                values.append([number])
            except ValueError as e:
                #print(item)
                keys.append(item)
        keys = keys[0:len(values)] # lop off extras
        df = pd.DataFrame(values, index=keys, columns=columns)
        return df

if __name__ == "__main__":
    # Unit test

    online = True  # normal mode
    #online = False # debug mode, read HTML file

    gateway = TableauGateway()
    if online:
        gateway.login()
    rawdata = gateway.fetch()
    gateway.close()
    
    parser = TableauParser()

    last_updated = parser.last_update(rawdata)
    print(last_updated)

    df = parser.summary(rawdata)
    print(df)

    s = df.loc['Pediatric non-ICU Beds'].value

    assert df.loc['Pediatric non-ICU Beds'].value != 0
    assert df.loc['NICU/PICU Beds'].value != 0
    assert df.loc['Adult non-ICU Beds'].value != 0
    assert df.loc['Adult ICU Beds'].value != 0
    assert df.loc['Staffed Pediatric non-ICU Beds'].value != 0
    assert df.loc['Staffed NICU/PICU Beds'].value != 0
    assert df.loc['Staffed Adult non-ICU Beds'].value != 0
    assert df.loc['Staffed Adult ICU Beds'].value != 0

    exit(0)

# That's all!
