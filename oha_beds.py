#!/usr/bin/env -S conda run -n covid python
"""
    Collect data from HOSCAP.
    Write it to a feature layer on our portal.
"""
from hoscap_gateway import HOSCAPGateway
from hoscap_parser import HOSCAPParser
from datetime import datetime, timezone

import sys
import os
from arcgis.gis import GIS
import arcgis.features
import pandas as pd
from copy import deepcopy
from utils import connect, s2i, local2utc

from config import Config

VERSION = 'oha_beds.py 2.0'

# Output data here
portalUrl = Config.PORTAL_URL
portalUser = Config.PORTAL_USER
portalPasswd = Config.PORTAL_PASSWORD

public_weekly_url = Config.PUBLIC_WEEKLY_URL

def format_bed_info(df):
    # Create a new df containing only the data we want.

    l_staffed = [
        #'Staffed Beds: Burn Unit',
        'Staffed Beds: Emergency Dept',
        #'Staffed Beds: Med/Surg',
        'Staffed Beds: Negative Flow',
        #'Staffed Beds: OR',
        'Staffed Beds: Obstetric',
        'Staffed Beds: Other',
        'Staffed Beds: Psych',
    ]
    l_available = [
        #'Available Beds: Burn Unit',
        'Available Beds: Emergency Department',
        #'Available Beds: Med/Surg',
        'Available Beds: Negative Flow',
        #'Available Beds: OR',
        'Available Beds: Obstetric',
        'Available Beds: Other',
        'Available Beds: Psych',
    ]

    staffed = 0
    available = 0
    for category in l_available:
        available += int(df.loc[category, 'Total'].replace(',', ''))
    for category in l_staffed:
        staffed += int(df.loc[category, 'Total'].replace(',', ''))
    print(available, staffed)

    bed_df = pd.DataFrame([
        [available],
        [staffed],

        [int(df.loc['Available Beds: Pediatric', 'Total'].replace(',', ''))],
        [int(df.loc['Staffed Beds: Pediatrics', 'Total'].replace(',', ''))],

        [int(df.loc['Available Beds: Adult ICU', 'Total'].replace(',', ''))],
        [int(df.loc['Staffed Beds: Adult ICU', 'Total'].replace(',', ''))],

        [int(df.loc['Available Beds: Pediatric ICU', 'Total'].replace(',', ''))
        + int(df.loc['Available Beds: Neonatal ICU', 'Total'].replace(',', ''))],

        [int(df.loc['Staffed Beds: Pediatric ICU', 'Total'].replace(',', ''))
        + int(df.loc['Staffed Beds: Neonatal ICU', 'Total'].replace(',', ''))],

    ], index=['OHA_non_ICU_bed_avail',
        'OHA_non_ICU_bed_total',

        'OHA_Ped_non_ICU_bed_avail',
        'OHA_Ped_non_ICU_bed_total',

        'OHA_ICU_bed_avail',
        'OHA_ICU_bed_total',

        'OHA_Ped_ICU_bed_avail',
        'OHA_Ped_ICU_bed_total'],
        columns=['Total']
    )
    print(bed_df)
    return bed_df

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
    #return True
    results = layer.edit_features(updates=[feature])
    return results['updateResults'][0]['success']

def load_df(online):
    if online:
        # Get hospital data from HOSCAP
        gateway = HOSCAPGateway()
        gateway.login()
        summary_data = gateway.fetch(Config.HOSCAP_SUMMARY)
    else:
        with open("juvare_summary.html", "r", encoding="UTF-8") as fp:
            summary_data = fp.read()

    parser = HOSCAPParser()   
    return parser.summary(summary_data)

#============================================================================
if __name__ == "__main__":

    hoscap_df = load_df(True)
    print(hoscap_df)
    df = format_bed_info(hoscap_df)

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
