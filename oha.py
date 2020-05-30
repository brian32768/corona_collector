#!/usr/bin/env -S conda run -n covid python
"""
Collect data from the Oregon Health Agency feature service.
Write it to a feature layer on our portal.
"""
import os
from arcgis.gis import GIS
import arcgis.features
import pandas as pd
from datetime import datetime
from config import Config
from utils import connect, s2i

sourceUrl = "https://services.arcgis.com/uUvqNMGPm7axC2dD/ArcGIS/rest/services/COVID_Cases_Oregon_Public/FeatureServer/0"

portalUrl = Config.PORTAL_URL
portalUser   = Config.PORTAL_USER
portalPasswd = Config.PORTAL_PASSWORD
featurelayer = "covid19_test_results"

def fetch_data():
    """ Download today's data from the OHA site.
    Return it in a spatially enabled data frame. """
  
    layer = arcgis.features.FeatureLayer(url=sourceUrl)
    counties = "altName='Clatsop' OR altName='Columbia' OR altName='Tillamook' OR altName='Lincoln' OR altName='Clackamas' OR altName='Multnomah' OR altName='Washington'"
    fields = "*"
    sdf = layer.query(where=counties, out_fields=fields).sdf

    return sdf

def append_to_database(layer, last_updated, df):
    """ Use the data fetched from OHA
        Add timestamp fields
        Append it to an existing database feature class, remapping fieldnames. """

    n=[]
    for index, row in df.iterrows():
        print(index, row)
        n.append({ "attributes": {
                "CreateDate": last_updated,
                "county":     row.at["altName"],
                "positive":   s2i(row.at["Cases"]),
                "negative":   s2i(row.at["NegativeTests"]),
                "deaths":     s2i(row.at["Deaths"]),
#                "recovered":  s2i(row.at["Recovered"]),
            },
            "geometry": row.at["SHAPE"]
        })

    results = layer.edit_features(adds=n)
    return results['addResults'][0]['success']

#============================================================================
if __name__ == "__main__":

# Open portal to make sure it's there!
    try:
        portal = GIS(portalUrl, portalUser, portalPasswd)
        print("Logged in as " + str(portal.properties.user.username))
        layer = connect(portal, featurelayer)
    except Exception as e:
        print("Could not connect to portal. \"%s\"" % e)
        print("Make sure the environment variables are set correctly.")
        exit(-1)

    try:
        sdf = fetch_data()
    except Exception as e:
        print("Could not read data from source. \"%s\"" % e)
        exit(-1)

    # Fields I don't need
    del sdf['OBJECTID']
    del sdf['instName']
    del sdf['Recovered']
    del sdf['Population']
    del sdf['GlobalID']

    # Remap
    sdf.rename(columns={
        'altName':       'county',
        'Cases':         'positive',
        'NegativeTests': 'negative',
        'Deaths':        'deaths',
    }, inplace=True)

    print(sdf)

    # We used to write to a JSON file
    sdf.to_json(r"./oha.json", orient="index", indent=2)

    try:
        append_to_database(layer, datetime.utcnow(), sdf)
    except Exception as e:
        print("Could not write data. \"%s\"" % e)
        exit(-1)

    print("All done!")
    exit(0)

# That's all!
