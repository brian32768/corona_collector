#!/usr/bin/env -S conda run -n covid python
"""
    Collect data from HOSCAP.
    Write it to a feature layer on our portal.
"""
from hoscap_gateway import HOSCAPGateway
from hoscap_parser import HOSCAPParser
from datetime import datetime, timezone
from utils import local2utc

import os
from arcgis.gis import GIS
import arcgis.features
import pandas as pd
from utils import connect, s2i

from config import Config

VERSION = 'hoscap.py 1.1'

# Output data here
portalUrl    = Config.PORTAL_URL
portalUser   = Config.PORTAL_USER
portalPasswd = Config.PORTAL_PASSWORD
hoscap_url   = Config.HOSCAP_URL
ppe_url      = Config.PPE_URL

# 11 Jun 2020 09:54
timeformat = "%d %b %Y %H:%M"

# Let's make up some geometry data here on the spot
# These are centroids more or less
geometry_table = {
    'CMH':   {"x": -123.819, "y": 46.189},
    'PSH':   {"x": -123.912, "y": 45.989},
}

def get_hoscap(gateway, facility, url):
    parser = HOSCAPParser()
    
    utc_date = datetime.utcnow().replace(microsecond=0, second=0, tzinfo=timezone.utc)
    
    STATUS = 1 # column containing the values
    DATE = 3

    d = gateway.fetch(url)
    covid_df = parser.covid(d)
    print('Facility=',facility)
    print(covid_df)

    beds_df = parser.beds(d)
    print(beds_df)
    vents_df = parser.vents(d)

    situ_df = parser.situation(d)

    vents_total     = s2i(vents_df.iloc[0][STATUS])
    vents_available = s2i(vents_df.iloc[1][STATUS])
    # weirdly PSH always reports more available than total
    # so avoid reporting this as a negative number
    vents_in_use    = max([vents_total - vents_available, 0])

    return {
        'facility': facility, 
        'utc_date'    : utc_date,

        'covid_date': local2utc(datetime.strptime(
            covid_df.iloc[0][DATE], timeformat)),
        'covid_admits'  : s2i(covid_df.iloc[0][STATUS]),
        'covid_icu_beds': s2i(covid_df.iloc[2][STATUS]),
        'covid_vents'   : s2i(covid_df.iloc[4][STATUS]),

        'beds_date'     : local2utc(datetime.strptime(
            beds_df.iloc[0][DATE], timeformat)),
        'beds_total': s2i(beds_df.iloc[0][STATUS]),
        'beds_icu'      : s2i(beds_df.iloc[1][STATUS]),
        #'beds_available':
        #'beds_icu_available:

        'vents_date'     : local2utc(datetime.strptime(
            beds_df.iloc[0][DATE], timeformat)),
        'vents_total'   : vents_total,
        'vents_surge'   : s2i(vents_df.iloc[2][STATUS]),
        'vents_in_use'  : vents_available,
        'vents_in_use'  : vents_in_use,

        'situation_date': local2utc(datetime.strptime(
            situ_df.iloc[0][DATE], timeformat)),
        'staff_ok': 1 if situ_df.iloc[7][STATUS] == 'No' else 0
    }
 
def build_hoscap_df(gateway):
    rows = []
    rows.append(get_hoscap(gateway, 'CMH', Config.HOSCAP_CMH))
    rows.append(get_hoscap(gateway, 'PSH', Config.HOSCAP_PSH))
    return pd.DataFrame.from_dict(rows, orient='columns')

def get_ppe(gateway, facility, url):
    parser = HOSCAPParser()

    CreateDate = datetime.utcnow().replace(tzinfo=timezone.utc)
    STATUS = 1  # column containing the values
    DATE   = 3
    N95    = 0  # row indexes
    MASK   = 2 
    SHIELD = 4
    GLOVE  = 6
    GOWN   = 8

    # PPMC provides only PPE data, which we put under PSH
    d = gateway.fetch(url)
    ppe_df = parser.ppe(d)
    print(ppe_df)

    return {
        'facility': facility,
        'utc_date': CreateDate,
        'editor': VERSION,

        'n95_date': local2utc(datetime.strptime(ppe_df.iloc[N95][DATE], timeformat)),
        'n95':      s2i(ppe_df.iloc[N95][STATUS]),
        'n95_burn': s2i(ppe_df.iloc[N95+1][STATUS]),

        'mask_date': local2utc(datetime.strptime(ppe_df.iloc[MASK][DATE], timeformat)),
        'mask':      s2i(ppe_df.iloc[MASK][STATUS]),
        'mask_burn': s2i(ppe_df.iloc[MASK+1][STATUS]),

        'shield_date': local2utc(datetime.strptime(ppe_df.iloc[SHIELD][DATE], timeformat)),
        'shield':      s2i(ppe_df.iloc[SHIELD][STATUS]),
        'shield_burn': s2i(ppe_df.iloc[SHIELD+1][STATUS]),

        'glove_date': local2utc(datetime.strptime(ppe_df.iloc[GLOVE][DATE], timeformat)),
        'glove':      s2i(ppe_df.iloc[GLOVE][STATUS]),
        'glove_burn': s2i(ppe_df.iloc[GLOVE+1][STATUS]),

        'gown_date': local2utc(datetime.strptime(ppe_df.iloc[GOWN][DATE], timeformat)),
        'gown':      s2i(ppe_df.iloc[GOWN][STATUS]),
        'gown_burn': s2i(ppe_df.iloc[GOWN+1][STATUS]),
    }
    
def build_ppe_df(gateway):
    rows = []
    rows.append(get_ppe(gateway, 'CMH', Config.HOSCAP_CMH))
    rows.append(get_ppe(gateway, 'PSH', Config.HOSCAP_PPMC))
    return pd.DataFrame.from_dict(rows, orient='columns')

def append_df(layer, facility_key, df):
    n = []
    for i in range(0, len(df)):
        d = df.iloc[i].transpose().to_dict()
        facility = d[facility_key]
        n.append({
            'attributes': d,
            'geometry': geometry_table[facility]
        })
    #print(n)
    results = layer.edit_features(adds=n)
    return results['addResults'][0]['success']

#============================================================================
if __name__ == "__main__":

# Get PPE data from HOSCAP
    try:
        gateway = HOSCAPGateway()
        gateway.login()
    except Exception as e:
        print("Could not connect to data source.", e)
        exit(-1)

    # HOSCAP

    # Build a single dataframe for CMH and PSH
    df = build_hoscap_df(gateway)
    print(df)

    # Open portal to make sure it's there!
    try:
        portal = GIS(portalUrl, portalUser, portalPasswd)
        #print("Logged in as " + str(portal.properties.user.username))
        layer = connect(portal, hoscap_url)
    except Exception as e:
        print("Could not connect to HOSCAP feature class. \"%s\"" % e)
        print("Make sure the environment variables are set correctly.")
        exit(-1)

    # Write the dataframe out to the feature class
    try:
        success = append_df(layer, 'facility', df)
    except Exception as e:
        print("Could not write HOSCAP data. \"%s\"" % e)

    # PPE

    # Build a single dataframe for CMH and PSH
    df = build_ppe_df(gateway)

    # Open portal to make sure it's there!
    try:
        layer = connect(portal, ppe_url)
    except Exception as e:
        print("Could not connect to PPE feature class. \"%s\"" % e)
        print("Make sure the environment variables are set correctly.")
        exit(-1)

    # Write the dataframe out to the feature class
    try:
        success = append_df(layer, 'facility', df)
    except Exception as e:
        print("Could not write PPE data. \"%s\"" % e)

# That's all!
