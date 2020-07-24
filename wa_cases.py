#!/usr/bin/env -S conda run -n covid python
"""
    Collect data from the Oregon Health Authority.
    Write it to a feature layer on our portal.
"""
from html_gateway import HTMLGateway
from wa_parser import WAParser
from datetime import datetime
from pytz import timezone

import os
from arcgis.gis import GIS
import arcgis.features
import pandas as pd
from copy import deepcopy
from utils import connect, s2i

from config import Config

VERSION = 'wa_cases.py 1.0'

# Output data here
portalUrl = Config.PORTAL_URL
portalUser = Config.PORTAL_USER
portalPasswd = Config.PORTAL_PASSWORD
featurelayerUrl = Config.COVID_CASES_URL

wa_centroid = {"x":-120.74, "y": 47.75}

def append_cases(layer, last_updated, df):
    """ Use the data fetched from OHA
        Add timestamp fields
        Append it to an existing database feature class, remapping fieldnames. """

    utc = datetime.utcnow().replace(microsecond=0, second=0, tzinfo=timezone('UTC'))

    i = 1
    try:
        n = {"attributes": {
            "utc_date":       utc,
            "editor":         portalUser,
            "source":         "covidtracking",

            "last_update":    last_updated,
            "name":           df.state[i],

            "total_cases":    s2i(df.positive[i]),
            "new_cases":      s2i(df.positiveIncrease[i]),

            "total_negative": s2i(df.negative[i]),
            "new_negative":   s2i(df.negativeIncrease[i]),

            "total_tests":    s2i(df.totalTestResults[i]),
            "new_tests":      s2i(df.totalTestResultsIncrease[i]),

            "total_recovered": s2i(df.recovered[i]),
            #"active_cases": s2i(dfActive Cases']),

            "total_deaths":   s2i(df.death[i]),
            "new_deaths":     s2i(df.deathIncrease[i]),
        },
            "geometry": wa_centroid
        }
    except Exception as e:
        print("You typed a name wrong", e)
        raise Exception("Typo fix please %s" % e)
    #print(n)

    print(df)
    #return True
    results = layer.edit_features(adds=[n])
    return results['addResults'][0]['success']

#============================================================================
if __name__ == "__main__":

    url = Config.WA_URL

# Get data from the wide world of web
    try:
        gateway = HTMLGateway()
        raw_data = gateway.fetch(url)
    except Exception as e:
        print("Could not fetch data.", e)
        exit(-1)

# Convert the data into a DataFrame
    parser = WAParser()
    last_updated = parser.parse_last_updated(raw_data)
    df = parser.fetch_cases(raw_data)

# Open portal to make sure it's there!
    try:
        portal = GIS(portalUrl, portalUser, portalPasswd)
        #print("Logged in as " + str(portal.properties.user.username))
        layer = connect(portal, featurelayerUrl)
    except Exception as e:
        print("Could not connect to portal. \"%s\"" % e)
        print("Make sure the environment variables are set correctly.")
        exit(-1)

    try:
        success = append_cases(layer, last_updated, df)
    except Exception as e:
        print("Could not write WA cases data. \"%s\"" % e)
        exit(-1)

    exit(0)

# That's all!
