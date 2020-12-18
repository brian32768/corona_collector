"""

This is supposed to transform CSV data into a feature service in Portal

*** FAIL ***

The code to write the feature service silently fails for no known reason.

The service was originally created by importing a CSV into Portal via the built in import feature.
Now I can't update it.

"""
import sys
from arcgis.gis import GIS
import arcgis.features
import pandas as pd
from datetime import datetime
from utils import connect, s2i

from config import Config
DATA_FILE = 'data/oha_county_metrics.csv'

# Append data here
portalUrl = Config.PORTAL_URL
portalUser = Config.PORTAL_USER
portalPasswd = Config.PORTAL_PASSWORD
tableUrl = "https://delta.co.clatsop.or.us/server/rest/services/Hosted/oha_county_metrics/FeatureServer/0"

timeformat = "%m/%d/%y"

def append_metrics(layer, df):

    df.rename(columns = {
        "County": "county",
        "Case count": "case_count",
        "Case rate per 100,000": "case_rate_per_100_000",
        "Test positivity %": "test_positivity__",
        "Week": "week_begin",
    }, inplace=True)

    new_features = []
    column_names = list(df.columns)
    recent_county = ''
    for (index, row) in df.iterrows():
        attributes = {}
        i = 0
        for item in row:
#            print(column_names[i], item)
            if column_names[i] == 'county':
                ##print(item, type(item))
                if type(item) == type(""):
                    recent_county = item
                else:
                    item = recent_county

            elif column_names[i] == 'week_begin':
                item = item[0:5] + '/2020 00:00'
                #item = datetime.strptime(item, "%m/%d/%y")
                #print(item, type(item))

            attributes[column_names[i]] = item
            i += 1
        new_features.append({
            "attributes":attributes
        })
        print(attributes)

    print(new_features)
    #return True
    results = layer.edit_features(adds=new_features)
    print(results)
    try:
        rval = results['addResults'][0]['success']
    except IndexError:
        rval = False
    return rval

#============================================================================
if __name__ == "__main__":

    df = pd.read_csv(DATA_FILE)
    print(df)

# Open portal to make sure it's there!
    try:
        portal = GIS(portalUrl, portalUser, portalPasswd)
        #print("Logged in as " + str(portal.properties.user.username))
        layer = connect(portal, tableUrl)
    except Exception as e:
        print("Make sure the environment variables are set correctly.")
        sys.exit("Could not connect to portal. \"%s\"" % e)

# Examine the layer
#    for f in layer.properties:
#        print(f)

# Make sure I can edit.
    capabilities = layer.properties.capabilities
    if not 'Editing' in capabilities:
        sys.exit("Ack, we cannot edit.")

    append_metrics(layer, df)

# That's all!

