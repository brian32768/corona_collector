#!/usr/bin/env -S conda run -n covid python
"""
    Collect data from the Oregon Health Authority.
    Write it to a feature layer on our portal.
"""
from html_gateway import HTMLGateway
from oha_parser import OHAParser
from datetime import datetime, timezone

import os
from arcgis.gis import GIS
import arcgis.features
import pandas as pd
from copy import deepcopy
from utils import connect, s2i, local2utc

from config import Config

VERSION = 'oha_beds.py 1.1'

# Output data here
portalUrl = Config.PORTAL_URL
portalUser = Config.PORTAL_USER
portalPasswd = Config.PORTAL_PASSWORD

public_weekly_url = Config.PUBLIC_WEEKLY_URL

def format_bed_info(df):
    labels = 'Hospital capacity and usage 5'
    # I have a table with 3 columns
    #print(df)

    # Split the table in two, based on columns.
    avail_df = df.loc[df.index, [labels, 'Available']].set_index(labels)
    #print(avail_df)
    total_df = df.loc[df.index, [labels, 'Total staffed']].set_index(labels)
    #print(total_df)

    # Remap field names to what I use in the output feature class

    avail_df.rename({
        'Adult non-ICU\xa0beds':    'OHA_non_ICU_bed_avail',
        'Pediatric non-ICU beds':   'OHA_Ped_non_ICU_bed_avail',
        'Adult ICU beds':           'OHA_ICU_bed_avail',
        'Pediatric NICU/PICU beds': 'OHA_Ped_ICU_bed_avail',
    }, axis='index', inplace=True)
    #print(avail_df)

    total_df.rename({
        'Adult non-ICU\xa0beds':    'OHA_non_ICU_bed_total',
        'Pediatric non-ICU beds':   'OHA_Ped_non_ICU_bed_total',
        'Adult ICU beds':           'OHA_ICU_bed_total',
        'Pediatric NICU/PICU beds': 'OHA_Ped_ICU_bed_total',
    }, axis='index', inplace=True)

    total_df.rename(columns={'Total staffed': 'Available'}, inplace=True)
    #print(total_df)

    # Concat them into one dataframe
    df = pd.concat([avail_df, total_df])
    df.drop(['Ventilators'], inplace=True)

    return df

def update_beds(layer, last_updated, df):
    """ Use the data fetched from OHA
        Add timestamp fields
        Update the record in an existing database feature class, remapping fieldnames.         """

    utc_date = datetime.utcnow().replace(microsecond=0, second=0, tzinfo=timezone.utc)

    # There is always only one feature in this layer.
    featureset = layer.query()
    #print(layer.properties.capabilities)
    original_feature = featureset.features[0]
    feature = deepcopy(original_feature)
    
    for k in df.index:
        v = df.loc[k, 'Available']
        try:
            feature.attributes[k] = v
        except Exception as e:
            print("You did something wrong with names.", e)

    feature.attributes['Creator'] = VERSION
    feature.attributes['Editor']  = utc_date
    feature.attributes['data_enter_date'] = last_updated
    #print(feature.attributes)

    #df[oid] = feature.attributes[oid]
    print(df)
    results = layer.edit_features(updates=[feature])
    return results['updateResults'][0]['success']

def load_data():
    """ Get hospital data from OHA """

#    with open("./oha.html", "r", encoding="utf-8") as fp:
#        return fp.read()

    gateway = HTMLGateway()
    return gateway.fetch(url)

#============================================================================
if __name__ == "__main__":

    url = "https://govstatus.egov.com/OR-OHA-COVID-19"

# Get hospital data from OHA
    try:
        raw_data = load_data()
    except Exception as e:
        sys.exit("Could not fetch data.", e)

# Convert the data into a DataFrame
    last_updated = OHAParser.last_update(raw_data)
    hospital_df = OHAParser.fetch_capacity_df(raw_data)
    df = format_bed_info(hospital_df)

# Open portal to make sure it's there!
    try:
        portal = GIS(portalUrl, portalUser, portalPasswd)
        #print("Logged in as " + str(portal.properties.user.username))
        layer = connect(portal, public_weekly_url)
    except Exception as e:
        print("Make sure the environment variables are set correctly.")
        sys.exit("Could not connect to portal. \"%s\"" % e)

    try:
        success = update_beds(layer, last_updated, df)
    except Exception as e:
        sys.exit("Could not write Beds data. \"%s\"" % e)

    exit(0)
# That's all!
