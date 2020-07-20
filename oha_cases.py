#!/usr/bin/env -S conda run -n covid python
"""
    Collect data from the Oregon Health Authority.
    Write it to a feature layer on our portal.
"""
from html_gateway import HTMLGateway
from oha_parser import OHAParser
from datetime import datetime
from pytz import timezone

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
covid_cases_url = Config.COVID_CASES_URL

# Let's make up some geometry data here on the spot
# These are centroids more or less
geometry_table = {
    'Clatsop':    {"x": -123.74, "y": 46.09},
    'Columbia':   {"x": -123.21, "y": 46.10},
    'Tillamook':  {"x": -123.72, "y": 45.52},
    'Multnomah':  {"x": -122.42, "y": 44.50},
    'Clackamas':  {"x": -122.17, "y": 45.25},
    'Washington': {"x": -123.09, "y": 45.50},
    'OR':         {"x": -122.07, "y": 44.57},
}

def append_cases(layer, last_updated, df):
    """ Use the data fetched from OHA
        Add timestamp fields
        Append it to an existing database feature class, remapping fieldnames. """

    utc = datetime.utcnow().replace(microsecond=0, second=0, tzinfo=timezone('UTC'))

    df['utc_date']    = utc
    df['last_update'] = last_updated
    df['editor']      = portalUser
    df['source']      = 'OHA'

    #print(df)

    new_features = []
    column_names = list(df.columns)
    for (index, row) in df.iterrows():
        attributes = {}
        geometry = {}
        i = 0
        for item in row:
            #print(column_names[i], item)
            attributes[column_names[i]] = item
            if column_names[i] == 'name':
                name = df['name'].iloc[0]
                geometry = geometry_table[name]
                #print(county, geometry)
            i += 1
        new_features.append({
            "attributes": attributes,
            "geometry": geometry
        })
#        print(attributes)
#        print(geometry)

    results = layer.edit_features(adds=new_features)
    return results['addResults'][0]['success']
    return False

def append_county_cases(layer, last_updated, df):

    # Remap field names to what I use
    df.rename(columns={
        'altName':       'name',
        'Cases':         'total_cases',
        'NegativeTests': 'total_negative',
        'Deaths':        'total_deaths',
    }, inplace=True)

    # Delete all the columns I don't use
    unwanted = ['OBJECTID', 'instName', 'Recovered',
                'Shape__Area', 'Shape__Length', 'GlobalID', 'Population', 'SHAPE']
    for i in unwanted:
        del df[i]

    print(df)
    return append_cases(layer, last_updated, df)


def append_state_cases(layer, last_updated, df):

    # Remap field names to what I use
    df.rename(columns={
        'Total cases':    'total_cases',
        'Negative tests': 'total_negative',
        'Total deaths':   'total_deaths',
        'Total tests':    'total_tests'
    }, inplace=True)

    # Delete all the columns I don't use
    unwanted = ['Positive tests', 'Total tested']
    for i in unwanted:
        del df[i]

    print(df)
    return append_cases(layer, last_updated, df)

def get_data():
    """ Get hospital data from OHA """

#    with open("./oha.html", "r", encoding="utf-8") as fp:
#        return fp.read()
    
    gateway = HTMLGateway()
    return gateway.fetch(url)

#============================================================================
if __name__ == "__main__":

    url = "https://govstatus.egov.com/OR-OHA-COVID-19"
    try:
        raw_data = get_data()
    except Exception as e:
        print("Could not fetch data.", e)
        exit(-1)

# Convert the data into DataFrames
    last_update_state = OHAParser().last_update(raw_data)
    state_cases_df = OHAParser().fetch_state_cases_df(raw_data)

    # Read feature layer directly from ArcGIS.COM, NOT the HTML
    last_edit = OHAParser().last_feature_edit()
    county_cases_df = OHAParser().fetch_feature_df()
    
# Open portal to make sure it's there!
    try:
        portal = GIS(portalUrl, portalUser, portalPasswd)
        #print("Logged in as " + str(portal.properties.user.username))
        layer = connect(portal, covid_cases_url)
    except Exception as e:
        print("Could not connect to portal. \"%s\"" % e)
        print("Make sure the environment variables are set correctly.")
        exit(-1)

# Append new state record
    try:
        success = append_state_cases(layer, last_update_state, state_cases_df)
    except Exception as e:
        print("Could not write state Cases data. \"%s\"" % e)
        exit(-1)

# Append new county records
    try:
        success = append_county_cases(layer, last_edit, county_cases_df)
    except Exception as e:
        print("Could not write county Cases data. \"%s\"" % e)
        exit(-1)

    exit(0)

# That's all!
