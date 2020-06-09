#!/usr/bin/env -S conda run -n covid python
"""
    Collect data from the Oregon Health Authority.
    Write it to a feature layer on our portal.
"""
from html_gateway import HTMLGateway
from oha_parser import OHAParser
from datetime import datetime, timezone, timedelta

import os
from arcgis.gis import GIS
import arcgis.features
import pandas as pd
from utils import connect, s2i

from config import Config

# Output data here
portalUrl = Config.PORTAL_URL
portalUser = Config.PORTAL_USER
portalPasswd = Config.PORTAL_PASSWORD
covid_cases_featurelayer = "covid19_cases"

# Let's make up some geometry data here on the spot
# These are centroids more or less
geometry_table = {
    'Clatsop':    {"x": -123.74, "y": 46.09},
    'Columbia':   {"x": -123.21, "y": 46.10},
    'Tillamook':  {"x": -123.72, "y": 45.52},
    'Multnomah':  {"x": -122.42, "y": 44.50},
    'Clackamas':  {"x": -122.17, "y": 45.25},
    'Washington': {"x": -123.09, "y": 45.50},
}

def append_cases(layer, last_updated, df):
    """ Use the data fetched from OHA
        Add timestamp fields
        Append it to an existing database feature class, remapping fieldnames. """

    try:
        # Remove fields I don't need
        del df['OBJECTID']
        del df['instName']
        del df['Recovered']
        del df['Population']
        del df['GlobalID']
        del df['SHAPE']    # We ignore the MULTIPOLYON and write a point.
        del df['Shape__Area']
        del df['Shape__Length']
    except Exception as e:
        print("Data cleaning failed, ", e)
        raise Exception("data cleaning failed; %s" % e)

    # Remap field names to what I use
    df.rename(columns={
        'altName':       'name',
        'Cases':         'total_cases',
        'NegativeTests': 'total_negative',
        'Deaths':        'total_deaths',
    }, inplace=True)

    utc = datetime.utcnow().replace(microsecond=0, second=0)

    df['utc_date'] = utc
    df['last_update'] = last_updated
    df['editor'] = portalUser
    df['source'] = 'OHA'

    print(df)

    new_features = []
    column_names = list(df.columns)
    #print(column_names)

    for (index, row) in df.iterrows():
        attributes = {}
        geometry = {}
        i = 0
        for item in row:
            #print(column_names[i], item)
            attributes[column_names[i]] = item
            if column_names[i] == 'name':
                county = df['name'].iloc[0]
                geometry = geometry_table[county]
                print(county, geometry)
            i += 1
        new_features.append({
            "attributes": attributes,
            "geometry": geometry
        })
    #print(new_features[0])

    results = layer.edit_features(adds=new_features)
    return results['addResults'][0]['success']

#============================================================================
if __name__ == "__main__":

    url = "https://govstatus.egov.com/OR-OHA-COVID-19"

# Get hospital data from OHA
    try:
        gateway = HTMLGateway()
        latest_data = gateway.fetch(url)
    except Exception as e:
        print("Could not fetch data.", e)
        exit(-1)

# Convert the data into a DataFrames
    parser = OHAParser()
    last_updated = parser.parse_last_updated(latest_data)

# Get the case data from OHA
    cases_df = parser.fetch_feature_df()

# Open portal to make sure it's there!
    try:
        portal = GIS(portalUrl, portalUser, portalPasswd)
        #print("Logged in as " + str(portal.properties.user.username))
        layer = connect(portal, covid_cases_featurelayer)
    except Exception as e:
        print("Could not connect to portal. \"%s\"" % e)
        print("Make sure the environment variables are set correctly.")
        exit(-1)

# Append a new record
    try:
        success = append_cases(layer, last_updated, cases_df)
    except Exception as e:
        print("Could not write Cases data. \"%s\"" % e)
        exit(-1)

    print("All done!")
    exit(0)

# That's all!
