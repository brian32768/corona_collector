# read covid cases into a dataframe
# export it as a csv file

import os
import pytz
from arcgis.gis import GIS
import pandas as pd
import csv
from datetime import datetime, timezone

from utils import connect
from config import Config

# Output data here
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
        
        p = utc.astimezone(pactz)
        # We're only interested in the date

        rval.append(p.date())

    return rval

def clean_sdf(sdf):
    #print(sdf.columns)

    # We're only interested in data manually entered for Clatsop
    # and there are some whacky entries at the start.
    sdf = sdf[(sdf.editor == 'EMD') & (sdf.total_cases<10000)]

    # Convert to localtime.
    sdf['local'] = utc2local(sdf['utc_date'])

    # Get rid of everything but the time and count.
    keepers = ['local', 'total_cases']
    local_df = sdf.filter(items=keepers)
    #print(local_df)

    # Get rid of extra readings (just one a day is good)
    # With EMD data, these are just test cases when I was developing webforms
    df = local_df.drop_duplicates(subset='local')
#    print(len(local_df), len(df))

    return df.set_index('local')

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
    local_df = clean_sdf(sdf)
    print(local_df)
    local_df.to_csv('data/emd_cases.csv', header=True, index=True)

    print("...and we're done")
    exit(0)
