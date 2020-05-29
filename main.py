from worldometer_gateway import WorldOMeterGateway
from parser_service import ParserService
from datetime import datetime, timezone, timedelta

import os
from arcgis.gis import GIS
import pandas as pd

from config import Config
portalUrl    = Config.PORTAL
portalUser   = Config.PORTAL_USER
portalPasswd = Config.PORTAL_PASSWORD
featurelayer = Config.FEATURELAYER

time_format = "%m/%d/%Y %H:%M"

def connect(portal):

    # Amusingly the GIS search function is sloppy and returns several...
    # there does not appear to be an exact match option.

    search_result = portal.content.search(featurelayer,
                                          item_type="Feature Service")
    if len(search_result) < 1:
        error = "Feature service '%s' not found." % featurelayer
        raise Exception(error)

    # Search for the correct Feature Service
    layer = None
    for item in search_result:
        #print(featurelayer, item)
        if featurelayer == item.title:
            layer = item.layers[0]

    return layer

def s2i(s):
    """ Convert a string to an integer even if it has + and , in it. """
    if s:
        return int(float(s.replace(',', '')))
    return None

def update(layer, last_update, df, x=0, y=0):
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
        layer = connect(portal)
    except Exception as e:
        print("Could not connect to portal.", e)
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
        result = update(layer, last_updated, usa_df, -98,39) # We're not in Kansas anymore
        result = update(layer, last_updated, world_df, 0, 0) # Null Island
    except Exception as e:
        print("Could not write data to portal.", e)
        exit(-1)

# That's all!
