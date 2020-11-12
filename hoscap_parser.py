from hoscap_gateway import HOSCAPGateway
from bs4 import BeautifulSoup
import pandas as pd
import re
from datetime import datetime

from config import Config

def parse_table(rawdata, attributes):
    soup = BeautifulSoup(rawdata, features="html.parser")
    table = soup.find("table", attrs=attributes)

    columns = [th.get_text().strip().replace(u"\xa0", u" ")
               for th in table.findAll("th")]
    del columns[0]  # empty
    #print(columns)

    indexes = []
    parsed_data = []
    for row in table.find('tbody').find_all('tr'):
        data = row.findAll("td")
        #print(data)
        index = data[1].get_text().strip()
        indexes.append(index)
        values = [data[i].get_text().strip()
                    for i in range(1, len(data))]
        parsed_data.append(values)
    #print(indexes)
    #print(parsed_data)
    df = pd.DataFrame(parsed_data, columns=columns)
    return df.replace(to_replace=[""], value=0)

class HOSCAPParser:

    @staticmethod
    def covid(d):
        _id = 'stGroup6517'
        return parse_table(d, {"id":_id})

    @staticmethod
    def ppe(d):
        _id = 'stGroup6522'
        return parse_table(d, {"id":_id})

    @staticmethod
    def beds(d):
        _id = 'stGroup3086'
        return parse_table(d, {"id":_id})

    @staticmethod
    def vents(d):
        _id = 'stGroup3081'
        return parse_table(d, {"id":_id})
        
    @staticmethod
    def situation(d):
        _id = 'stGroup3083'
        return parse_table(d, {"id":_id})

    @staticmethod
    def last_update(d):
        soup = BeautifulSoup(d, features="html.parser")
        span = soup.find("span", attrs={"id":"statusTime"}).contents[0]

        # 10 Nov 12:01
        local = datetime.strptime(span, "%d %b %H:%M")

# Set the year to 2020
        assert False
        
        return 0

    @staticmethod
    def summary(d):
        df = parse_table(d, {"id":"","summary":""})
        #print(df.columns[0])
        return df.set_index(df.columns[0])
        
if __name__ == "__main__":
    # Unit test

    online = True  # normal mode
    #online = False # debug mode, read HTML file

    gateway = HOSCAPGateway()
    if online:
        gateway.login()

    def fetchSummary():
        if online:
            rawdata = gateway.fetch(Config.HOSCAP_SUMMARY)
        else:
            with open("juvare_summary.html", "r", encoding="UTF-8") as fp:
                rawdata = fp.read()
        return rawdata

    def fetchCMH():
        if online:
            rawdata = gateway.fetch(Config.HOSCAP_CMH)
        else:
            with open("juvare_cmh.html", "r", encoding="UTF-8") as fp:
                rawdata = fp.read()
        return rawdata

    def fetchPSH():
        if online:
            return gateway.fetch(Config.HOSCAP_PSH)
        with open("juvare_psh.html", "r", encoding="UTF-8") as fp:
            d = fp.read()
        return d

    def fetchPPMC():
        if online:
            return gateway.fetch(Config.HOSCAP_PPMC)
        with open("juvare_ppmc.html", "r", encoding="UTF-8") as fp:
            d = fp.read()
        return d

    
    parser = HOSCAPParser()   

# ----
    summary = fetchSummary()
    last_updated = parser.last_update(summary)
    df = parser.summary(summary)
    print(df)

    assert df.loc['Available Beds: Adult ICU', 'Total'] != 0
    assert df.loc['Staffed Beds: Adult ICU', 'Total'] != 0

    assert df.loc['Available Beds: Emergency Department', 'Total'] != 0
    assert df.loc['Staffed Beds: Emergency Dept', 'Total'] != 0

    assert df.loc['Available Beds: Med/Surg', 'Total'] != 0
    assert df.loc['Staffed Beds: Med/Surg', 'Total'] != 0

    assert df.loc['Available Beds: Negative Flow', 'Total'] != 0
    assert df.loc['Staffed Beds: Negative Flow', 'Total'] != 0

    assert df.loc['Available Beds: Other', 'Total'] != 0
    assert df.loc['Staffed Beds: Other', 'Total'] != 0

    assert df.loc['Available Beds: Pediatric', 'Total'] != 0
    assert df.loc['Staffed Beds: Pediatrics', 'Total'] != 0

    assert df.loc['Available Beds: Pediatric ICU', 'Total'] != 0
    assert df.loc['Staffed Beds: Pediatric ICU', 'Total'] != 0

    assert df.loc['Available Beds: Neonatal ICU', 'Total'] != 0
    assert df.loc['Staffed Beds: Neonatal ICU', 'Total'] != 0
# ----

    d = fetchCMH()

    df = parser.covid(d)
    print(df)

    df = parser.vents(d)
    print(df)

    df = parser.beds(d)
    print(df)

    df = parser.ppe(d)
    print(df)

    df = parser.situation(d)
    print(df)

    gateway.close()
    exit(0)

# That's all!
