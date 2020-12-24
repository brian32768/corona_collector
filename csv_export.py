#!/usr/bin/env -S conda run -n covid python
"""
    Read covid cases from Portal into a dataframe.
    Export it as a csv file so D3 in JavaScript can read it.
"""
import os
import pytz
from arcgis.gis import GIS
import pandas as pd
import numpy as np
import csv
from datetime import datetime, timezone

from utils import connect
from config import Config

# read data from here
portalUrl = Config.PORTAL_URL
portalUser = Config.PORTAL_USER
portalPasswd = Config.PORTAL_PASSWORD
featurelayerUrl = Config.COVID_CASES_URL
assert portalUrl
assert portalUser
assert portalPasswd
assert featurelayerUrl

tformat = "%Y-%m-%d %H:%M"
pactz = pytz.timezone('America/Los_Angeles')

def utc2local(col):
    """ input: string in utc, "YYYY-MM-DD HH:MM:SS"
        output: string in local time, same format """

    print(col)

    # I'm not sure but maybe I should just set tzinfo here too??
    # tzinfo = timezone.utc
    #return t.astimezone(timezone.utc).replace(microsecond=0, second=0)
    rval = []
    for utc_naive in col:
        utc = utc_naive.tz_localize(timezone.utc)
        #print('utc=', utc, type(utc))
        
        # We're only interested in the date
        p = utc.astimezone(pactz).date()

        rval.append(p.strftime('%m/%d/%y'))

    return rval

def clean_data(sdf):
    """ Return two df's, one for total cases and one for daily cases. """
    
    #print(sdf.columns)

    # We're only interested in data manually entered for Clatsop
    # and there are some whacky entries at the start.
    sdf = sdf[(sdf.editor == 'EMD') & (sdf.total_cases<10000)]

    # Convert to localtime.
    #sdf['date'] = utc2local(sdf['utc_date'])

    # Get rid of extra readings (just one a day is good)
    # With EMD data, these are just test cases when I was developing webforms
    #df = sdf.drop_duplicates(subset='date')
#    print(len(local_df), len(df))

    # Get rid of everything but the time and count.
    #keepers = ['utc_date', 'total_cases']
    #dedupe = df.filter(items=keepers)

    # Get ready to calc new_cases    
    #sorted = dedupe.set_index('utc_date')

    # save the total cases so we can add it back in
    #total_cases = sorted['total_cases']
    #
    ## Calculate proper value for new_cases
    #newdf = sorted.diff()
    #rdf = newdf.rename(columns={'total_cases':'new_cases'})
    #
    # put total_cases back in
    #rdf['total_cases'] = total_cases

    # Convert to localtime
    sdf['date'] = utc2local(sdf['utc_date'])
    df = sdf.set_index('date')

    # Get rid of everything but the time and count.
    keepers = ['date', 'new_cases']
    new_df = df.filter(items=keepers)
    new_df.rename(columns={'new_cases':'cases'},inplace=True)

    # Calculate a 7 day average, some day...
    new_df['avg'] = new_df.iloc[:,0].rolling(window=7).mean()

    # Get rid of everything but the time and count.
    keepers = ['date', 'total_cases']
    total_df = df.filter(items=keepers)
    total_df.rename(columns={'total_cases':'cases'},inplace=True)

    # Calculate a 7 day average, some day...
    total_df['avg'] = total_df.iloc[:,0].rolling(window=7).mean()

    return (new_df, total_df)

#============================================================================
if __name__ == "__main__":

    try:
        portal = GIS(portalUrl, portalUser, portalPasswd)
        print("Logged in as " + str(portal.properties.user.username))
        layer = connect(portal, featurelayerUrl)
    except Exception as e:
        print("Could not connect to portal. \"%s\"" % e)
        print("Make sure the environment variables are set correctly.")
        exit(-1)

    sdf = pd.DataFrame.spatial.from_layer(layer)
    (new_df, total_df) = clean_data(sdf)

    # Easy peasy once the data is in a DF.

    print(new_df)
    print(total_df)

    # deployed
    if os.path.exists('public/cases'):
        new_df.to_csv('public/cases/emd_daily_cases.csv', header=True, index=True)
        total_df.to_csv('public/cases/emd_total_cases.csv', header=True, index=True)
        print("deployed")
        
    # test
    new_df.to_csv('src/emd_daily_cases.csv', header=True, index=True)
    total_df.to_csv('src/emd_total_cases.csv', header=True, index=True)

    print("...and we're done")
    exit(0)
