import sys
from selenium import webdriver
from datetime import datetime, timezone

from config import Config

class TableauGateway:

    def fetch(self, url):
        self.driver.get(url)
        return self.driver.page_source

    def close(self):
        self.driver.close()
        self.driver.quit()
        return

if __name__ == "__main__":
    # Unit test

    gateway = TableauGateway()
    
    d = gateway.fetch(Config.OHA_BED_CAPACITY_URL)
    with open("oha_bed_capacity.html", "w", encoding="UTF-8") as fp:
        fp.write(d)

    gateway.close()

    exit(0)
# That's all!
