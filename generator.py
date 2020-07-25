"""
Generates static html file(s)

We're going to read data directly from a feature class at OHA,
grab data from it, and stick it into HTML pages.
We can do this on a schedule to refresh the HTML pages.
The pages can be incorporated into ESRI Dashboards.

templates/   jinja2 templates
static/      static assets like CSS files
public/      we write output here

"""
import sys
import os
import shutil
from jinja2 import Template, Environment, FileSystemLoader
import datetime
from pytz import timezone

from arcgis.gis import GIS
from arcgis.features import FeatureLayer
import pandas as pd

from config import Config
from oha_parser import OHAParser, featureLayerUrl


cases_url = Config.COVID_CASES_URL
#ppe_url = Config.PPE_URL

jinja = Environment(loader=FileSystemLoader('templates'))

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
    edittime = last_update.astimezone(
        timezone('America/Los_Angeles')).strftime("%m/%d/%y %H:%M %Z")
    #print(edittime)

    ohaUrl = '<a href="https://govstatus.egov.com/OR-OHA-COVID-19">OHA</a>'

    template = jinja.get_template('cases.html')
    html = template.render(
            region=region,
            source=ohaUrl, 
            last_update=edittime, 
            df=df
    )
    return html


def ruralcases():
    w = "altName='Clatsop' or altName='Tillamook' or altName='Columbia'"
    df = get_cases(w, 3)
    return cases('Rural', df)

def metrocases():
    #   "source='OHA' AND (name='Multnomah' OR name='Clackamas' OR name='Washington')", 3)
    w = "altName='Multnomah' or altName='Clackamas' or altName='Washington'"
    df = get_cases(w, 3)
    return cases('Metro', df)


def recursive_overwrite(src, dest, ignore=None):
    if os.path.isdir(src):
        if not os.path.isdir(dest):
            os.makedirs(dest)
        files = os.listdir(src)
        if ignore is not None:
            ignored = ignore(src, files)
        else:
            ignored = set()
        for f in files:
            if f not in ignored:
                recursive_overwrite(os.path.join(src, f),
                                    os.path.join(dest, f),
                                    ignore)
    else:
        shutil.copyfile(src, dest)

if __name__ == "__main__":

    # Wipe output and
    # Copy static content to output. 
    try:
        recursive_overwrite('static', 'public/static')
    except Exception as e:
        print("Error copying static files. %s" % e)

    # Generate static pages

    with open('public/rural.html', 'w') as fp:
        html = ruralcases()
        fp.write(html)

    with open('public/metro.html', 'w') as fp:
        html = metrocases()
        fp.write(html)

# That's all
