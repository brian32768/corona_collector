"""

    Collect data from Worldometer for World and USA
    Append it to a feature layer on our portal.

"""
from worldometer_gateway import WorldOMeterGateway
from parser_service import ParserService
from datetime import datetime, timezone, timedelta

import os
from arcgis.gis import GIS
import pandas as pd
from utils import connect, s2i

from config import Config
portalUrl    = Config.PORTAL_URL
portalUser   = Config.PORTAL_USER
portalPasswd = Config.PORTAL_PASSWORD
featurelayer = "covid19_cases"

time_format = "%m/%d/%Y %H:%M"

def append_to_database(layer, last_update, df, x=0, y=0):
    """ Write a dataframe to the feature layer. """

    utc = datetime.utcnow()
    name = df.name

    n = {"attributes": {
            "utc_date":     utc,
            "editor":       portalUser,
            "source":       "worldometer",

            "last_update":  last_update,
            "name":         name, # USA | World | Clatsop
            "total_cases":  s2i(df.at['Total Cases']),
            "new_cases":    s2i(df.at['New Cases']),

            "total_tests":  s2i(df.at['Total Tests']),

            "total_recovered": s2i(df.at['Total Recovered']),
            "active_cases": s2i(df.at['Active Cases']),

            "total_deaths": s2i(df.at['Total Deaths']),
            "new_deaths":   s2i(df.at['New Deaths']),
        },
        "geometry": {
            "x": x, "y": y
        }
    }

    results = layer.edit_features(adds=[n])
    return results['addResults'][0]['success']

if __name__ == "__main__":

# Open portal to make sure it's there!
    try:
        portal = GIS(portalUrl, portalUser, portalPasswd)
        layer = connect(portal, featurelayer)
    except Exception as e:
        print("Could not connect to portal. \"%s\"" % e)
        print("Make sure the environment variables are set correctly.")
        exit(-1)
    
# Get data from Worldometer

    try:
        worldometer_gateway = WorldOMeterGateway()
        parser_service = ParserService()
        latest_data = worldometer_gateway.fetch()
    except Exception as e:
        print("Could not fetch data.", e)
        exit(-1)

    df = parser_service.create_df_worldometer(latest_data)
    last_updated = parser_service.parse_last_updated(latest_data)

# Clean the data

    del df['Population']
    del df['#']

    inx = "Country/Other"
    df = df.set_index(inx, drop=True)
    print(df)
    print()

    usa_df = df.loc["USA"]
    print(usa_df)
    print()

    world_df = df.loc['World']
    print(world_df)

    print(last_updated)
    #print(local_tz)

# We used to write to a JSON file
#    df.to_json(r"./cases.json", orient="index", indent=2)
#
# now put it into a feature layer
    try:
        result = append_to_database(layer, last_updated, usa_df, -98,39) # We're not in Kansas anymore
        result = append_to_database(layer, last_updated, world_df, 0, 0) # Null Island
    except Exception as e:
        print("Could not write data to portal. \"%s\"" % e)
        exit(-1)

# That's all!