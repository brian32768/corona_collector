"""
This will be a microservice to build a page
for inclusion in the dash.
"""
from flask import render_template, redirect
from app import app
from config import Config

from oha_parser import OHAParser, featureLayerUrl

import os
from arcgis.gis import GIS
from arcgis.features import FeatureLayer
import pandas as pd

import datetime
from pytz import timezone

portal_url = Config.PORTAL_URL
portal_user = Config.PORTAL_USER
portal_password = Config.PORTAL_PASSWORD

cases_url = Config.COVID_CASES_URL
#ppe_url = Config.PPE_URL

def get_cases(whereclause, records):
#    portal = GIS(portal_url, portal_user, portal_password)
#    results_df = FeatureLayer(cases_url).query(where=whereclause, order_by_fields="utc_date DESC, name ASC",
#                     return_all_records=False, result_record_count=records, return_geometry=False).sdf
    results_df = FeatureLayer(url=featureLayerUrl).query(where=whereclause, order_by_fields="OBJECTID DESC, altName ASC",
                    return_all_records=False, result_record_count=records, return_geometry=False).sdf
    #print(results_df)
    return results_df

def cases(region, df):
#    utc_date = pd.to_datetime(df.loc[0, "utc_date"]).replace(
#        tzinfo=datetime.timezone.utc)
#    runtime = utc_date.astimezone(timezone('America/Los_Angeles'))
#    print(runtime)

#    last_update = pd.to_datetime(df.loc[0, "last_update"]).replace(
#        tzinfo=datetime.timezone.utc)
    last_update = OHAParser.last_feature_edit().replace(
                tzinfo=datetime.timezone.utc)
    edittime = last_update.astimezone(timezone('America/Los_Angeles')).strftime("%m/%d/%y %H:%M %Z")
    #print(edittime)

    ohaUrl = '<a href="https://govstatus.egov.com/OR-OHA-COVID-19">OHA</a>'
    return render_template('cases.html',
            region=region, source=ohaUrl, last_update=edittime, df=df)

@app.route('/rural')
def ruralcases() :
    w ="altName='Clatsop' or altName='Tillamook' or altName='Columbia'"
    df = get_cases(w, 3)
    return cases('Rural', df)

@app.route('/metro')
def metrocases() :
#   "source='OHA' AND (name='Multnomah' OR name='Clackamas' OR name='Washington')", 3)
    w = "altName='Multnomah' or altName='Clackamas' or altName='Washington'"
    df=get_cases(w, 3)
    return cases('Metro', df)

@app.route('/ppe')
def ppe():
    return render_template('ppe.html', data=ppe)


@app.route('/')
def root():
    return render_template('index.html')

# That's all!
