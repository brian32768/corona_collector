#!/usr/bin/env -S conda run -n covid python
"""
    Collect data from Worldometer for World and USA
    Append it to a feature layer on our portal.
"""
from html_gateway import HTMLGateway
from worldometer_parser import WorldometerParser
from datetime import datetime
from pytz import timezone

import os
from arcgis.gis import GIS
import pandas as pd
from utils import connect, s2i

from config import Config
portalUrl    = Config.PORTAL_URL
portalUser   = Config.PORTAL_USER
portalPasswd = Config.PORTAL_PASSWORD
covid_cases_url = Config.COVID_CASES_URL

worldometer_world_url = Config.WORLDOMETER_WORLD_URL
worldometer_states_url = Config.WORLDOMETER_STATES_URL

usa_geometry = {"x": -98, "y": 39}
or_geometry = {"x": -121, "y": 44}
null_island = {"x":   0, "y":  0}

time_format = "%m/%d/%Y %H:%M"

def append_to_database(layer, last_update, df, geometry):
    """ Write a dataframe to the feature layer. """

    utc = datetime.utcnow().replace(microsecond=0, second=0, tzinfo=timezone('UTC'))
    name = df.name

    attributes = {
        "utc_date":     utc,
        "editor":       portalUser,
        "source":       "worldometer",

        "last_update":  last_update,
        "name":         name, # USA | World | Clatsop
        "total_cases":  s2i(df.at['Total Cases']),
        "new_cases":    s2i(df.at['New Cases']),

        "total_tests":  s2i(df.at['Total Tests']),

        "active_cases": s2i(df.at['Active Cases']),

        "total_deaths": s2i(df.at['Total Deaths']),
        "new_deaths":   s2i(df.at['New Deaths']),
    }
    try: 
        attributes["total_recovered"] = s2i(df.at['Total Recovered'])
    except KeyError:
        pass
    n = { "attributes": attributes, "geometry": geometry }
    print(n)
    #return True
    results = layer.edit_features(adds=[n])
    rval = results['addResults'][0]['success']
    return rval

#============================================================================
if __name__ == "__main__":

    STATE_KEY = "Oregon" # Used to be "Oregon" and then they added a column with # in it.

    world_data = None
    try:
        world_data = HTMLGateway.fetch(worldometer_world_url)
    except Exception as e:
        print("Could not fetch world data.", e)
        exit(-1)

    parser = WorldometerParser()

    # Convert the data into a DataFrame
    world_df = parser.create_df(world_data, "main_table_countries_today", '1')
    world_last_updated = parser.parse_last_updated(world_data)

    state_data = None
    try:
        state_data = HTMLGateway.fetch(worldometer_states_url)
    except Exception as e:
        print("Could not fetch state data.", e)
        exit(-1)

    # Convert the data into a DataFrame
    try:
        states_df = parser.create_df(
            state_data, "usa_table_countries_today", STATE_KEY, rowindex=1)
    except KeyError:
        print("KeyError Oregon on", state_data)
        sys.exit("KeyError = Oregon")
    states_last_updated = parser.parse_last_updated(state_data)

# Open portal to make sure it's there!
# this won't work unless the environment is properly set up
    try:
        portal = GIS(portalUrl, portalUser, portalPasswd)
        layer = connect(portal, covid_cases_url)
    except Exception as e:
        print("Could not connect to portal. \"%s\"" % e)
        print("Make sure the environment variables are set correctly.")
        exit(-1)
  
# Clean the data

    del world_df['Population']
    del world_df['#']

    world_df = world_df.set_index("Country/Other", drop=True)
    or_df = states_df.set_index("USA State", drop=True)
    print(or_df)
    or_df = or_df.loc["Oregon"].transpose()
    or_df.name = 'Oregon'

    usa_df = world_df.loc["USA"]

    world_df = world_df.loc['World']
    print(world_df)

# now put it into a feature layer
    try:
        result = append_to_database(layer, states_last_updated, or_df, or_geometry)
        result = append_to_database(layer, world_last_updated, usa_df, usa_geometry)
        result = append_to_database(layer, world_last_updated, world_df, null_island)
    except Exception as e:
        print("Could not write data to portal. \"%s\"" % e)
        exit(-1)

# That's all!
