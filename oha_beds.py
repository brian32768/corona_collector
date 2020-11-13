#!/usr/bin/env -S conda run -n covid python
"""
    Collect bed data from HOSCAP or maybe it's OHA here today.
    Write it to a feature layer on our portal.
"""
#from hoscap_gateway import HOSCAPGateway
#from hoscap_parser import HOSCAPParser
from tableau_gateway import TableauGateway
from tableau_parser import TableauParser
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

def format_bed_info(df, column):
    # Create a new df containing only the data we want.

    bed_df = pd.DataFrame([
        [df.loc['Adult non-ICU Beds','value']],
        [df.loc['Staffed Adult non-ICU Beds','value']],

        [df.loc['Pediatric non-ICU Beds','value']],
        [df.loc['Staffed Pediatric non-ICU Beds','value']],

        [df.loc['Adult ICU Beds','value']],
        [df.loc['Staffed Adult ICU Beds','value']],

        [df.loc['NICU/PICU Beds','value']],
        [df.loc['Staffed NICU/PICU Beds','value']],
    ], index=[
        'OHA_non_ICU_bed_avail',
        'OHA_non_ICU_bed_total',

        'OHA_Ped_non_ICU_bed_avail',
        'OHA_Ped_non_ICU_bed_total',

        'OHA_ICU_bed_avail',
        'OHA_ICU_bed_total',

        'OHA_Ped_ICU_bed_avail',
        'OHA_Ped_ICU_bed_total'],
        columns=[column]
    )
    return bed_df

def update_beds(layer, last_updated, df, column):
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
        v = df.loc[k, column]
        feature.attributes[k] = v

    feature.attributes['Creator'] = VERSION
    feature.attributes['Editor']  = utc_date
    feature.attributes['data_enter_date'] = last_updated
    #print(feature.attributes)

    #df[oid] = feature.attributes[oid]
    #return True
    results = layer.edit_features(updates=[feature])
    return results['updateResults'][0]['success']

#============================================================================
if __name__ == "__main__":

    # Get hospital data from HOSCAP
    gateway = TableauGateway()
    gateway.login()
    rawdata = gateway.fetch()
    gateway.close()
    
    parser = TableauParser()   
    last_updated = parser.last_update(rawdata)
    print("Last updated:",last_updated)

    summary_df = parser.summary(rawdata)

    value_column = 'Total'
    bed_df = format_bed_info(summary_df, value_column)
    print(bed_df)

    # These have to be set or we die here.
    assert portalUrl
    assert portalUser
    assert portalPasswd
    assert public_weekly_url

# Open portal to make sure it's there!
    try:
        portal = GIS(portalUrl, portalUser, portalPasswd)
        #print("Logged in as " + str(portal.properties.user.username))
        layer = connect(portal, public_weekly_url)
    except Exception as e:
        print("Make sure the environment variables are set correctly.")
        sys.exit("Could not connect to portal. \"%s\"" % e)

    try:
        success = update_beds(layer, last_updated, bed_df, value_column)
    except Exception as e:
        sys.exit("Could not write Beds data. \"%s\"" % e)

    exit(0)
# That's all!
