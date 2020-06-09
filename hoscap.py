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
from copy import deepcopy
from utils import connect, s2i

from config import Config

VERSION = 'oha_beds.py 1.0'

# Output data here
portalUrl = Config.PORTAL_URL
portalUser = Config.PORTAL_USER
portalPasswd = Config.PORTAL_PASSWORD

public_featurelayer = "covid19_public_weekly_data"


def update_beds(layer, last_updated, df):
    """ Use the data fetched from OHA
        Add timestamp fields
        Update the record in an existing database feature class, remapping fieldnames. """

    labels = 'Hospital capacity and usage 5'
    # I have a table with 3 columns
    #print(df)
    hoscap = df.drop([2]) # Ventilators
    print(hoscap)

    # Split the table in two, based on columns.
    avail_df = hoscap.loc[hoscap.index, [labels, 'Available']].set_index(labels)
    #print(avail_df)
    total_df = hoscap.loc[hoscap.index, [labels, 'Total staffed']].set_index(labels)
    #print(total_df)

    # Remap field names to what I use in the output feature class

    def mapper(s) :
        d = {
            'Adult non-ICU\xa0beds':       'OHA_non_ICU_bed_avail',
            'Pediatric non-ICU beds':   'OHA_Ped_non_ICU_bed_avail',
            'Adult ICU beds':           'OHA_ICU_bed_avail',
            'Pediatric NICU/PICU beds': 'OHA_Ped_ICU_bed_avail',
        }
        return d[s]

    avail_df.rename(mapper, axis='index', inplace=True)
    #print(avail_df)

    total_df.rename({
        'Adult non-ICU\xa0beds':       'OHA_non_ICU_bed_total',
        'Pediatric non-ICU beds':   'OHA_Ped_non_ICU_bed_total',
        'Adult ICU beds':           'OHA_ICU_bed_total',
        'Pediatric NICU/PICU beds': 'OHA_Ped_ICU_bed_total',
    }, axis='index', inplace=True)

    total_df.rename(columns={'Total staffed': 'Available'}, inplace=True)
    #print(total_df)

    # Concat them into one dataframe
    df = pd.concat([avail_df, total_df])
    #print(df)
 
    # We used to write to a JSON file
    #df.to_json(r"./oha.json", orient="index", indent=2)

    utc = datetime.utcnow().replace(microsecond=0, second=0)
    #df['utc_date'] = last_updated
    #print(df)

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
    feature.attributes['Editor']  = utc
    feature.attributes['data_enter_date'] = last_updated
    #print(feature.attributes)

    #df[oid] = feature.attributes[oid]
    results = layer.edit_features(updates=[feature])
    return results['updateResults'][0]['success']


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

# Convert the data into a DataFrame
    parser = OHAParser()
    last_updated = parser.parse_last_updated(latest_data)
    # Get the bed data data from OHA
    hospital_df = parser.fetch_capacity_df(latest_data)

# Open portal to make sure it's there!
    try:
        portal = GIS(portalUrl, portalUser, portalPasswd)
        #print("Logged in as " + str(portal.properties.user.username))
        layer = connect(portal, public_featurelayer)
    except Exception as e:
        print("Could not connect to portal. \"%s\"" % e)
        print("Make sure the environment variables are set correctly.")
        exit(-1)

    try:
        success = update_beds(layer, last_updated, hospital_df)
    except Exception as e:
        print("Could not write Beds data. \"%s\"" % e)
        exit(-1)

    print("All done!")
    exit(0)

# That's all!
