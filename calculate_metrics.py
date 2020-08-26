import os
from arcgis.gis import GIS
from arcgis.features import FeatureLayer
import pandas as pd

from config import Config

portalUrl = Config.PORTAL_URL
portalUser = Config.PORTAL_USER
portalPasswd = Config.PORTAL_PASSWORD
covid_cases_url = Config.COVID_CASES_URL

if __name__ == "__main__":

# Read the entire feature class into a dataframe

    try:
        portal = GIS(portalUrl, portalUser, portalPasswd)
        fl = FeatureLayer(covid_cases_url)
        oha_df = fl.query(where = "source='OHA'", order_by_fields = "utc_date DESC").sdf
        clatsop_df = fl.query(where = "source='OHA' AND name='Clatsop'", order_by_fields = "utc_date DESC").sdf

        # seek out and remove duplicates
        l = None
        for row in oha_df.iterrows():
            this = row[1].get('last_update')  
            if l == this:
                print(row)
            l = this
    except Exception as e:
        print("Reading old data failed.", e)
        pass
