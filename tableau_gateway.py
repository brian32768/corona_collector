import sys
import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime, timezone

from config import Config

class TableauGateway:

    def login(self):
        return True

    def fetch(self):
        r = requests.get(Config.OHA_BED_CAPACITY_URL)
        soup = BeautifulSoup(r.text, "html.parser")
        find = soup.find("textarea", {"id": "tsConfigContainer"})
        tableauData = json.loads(find.text)
        dataUrl = f'https://public.tableau.com{tableauData["vizql_root"]}/bootstrapSession/sessions/{tableauData["sessionid"]}'

        r = requests.post(dataUrl, data= {
            "sheet_id": tableauData["sheetId"],
        })

        dataReg = re.search('\d+;({.*})\d+;({.*})', r.text, re.MULTILINE)
        info = json.loads(dataReg.group(1))
        data = json.loads(dataReg.group(2))
        table = data["secondaryInfo"]["presModelMap"]["dataDictionary"]["presModelHolder"]["genDataDictionaryPresModel"]["dataSegments"]["0"]["dataColumns"]
        d = table[1]["dataValues"]

        return d
    
    def close(self):
        return

if __name__ == "__main__":
    # Unit test

    gateway = TableauGateway()
    gateway.login()
    
    d = gateway.fetch()
    for item in d:
        print(item)

    gateway.close()

    exit(0)
# That's all!
