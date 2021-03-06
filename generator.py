#!/usr/bin/env -S conda run -n covid python
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

from html_gateway import HTMLGateway
from worldometer_parser import WorldometerParser
from wa_parser import WAParser

from config import Config
from oha_parser import OHAParser, featureLayerUrl

# Set to True to read files instead of web.
dryrun = False

cases_url = Config.COVID_CASES_URL
#ppe_url = Config.PPE_URL
worldometer_world_url = Config.WORLDOMETER_WORLD_URL
worldometer_states_url = Config.WORLDOMETER_STATES_URL
covidtracking_url = Config.COVIDTRACKING_URL

jinja = Environment(loader=FileSystemLoader('templates'))
timeformat = "%m/%d/%y %H:%M"
now = datetime.datetime.now().strftime(timeformat)

def get_cases(url, whereclause, records):
    #    portal = GIS(portal_url, portal_user, portal_password)
    #    results_df = FeatureLayer(cases_url).query(where=whereclause, order_by_fields="utc_date DESC, name ASC",
    #                     return_all_records=False, result_record_count=records, return_geometry=False).sdf
    results_df = FeatureLayer(url=url).query(where=whereclause, order_by_fields="OBJECTID DESC, altName ASC",
                                                         return_all_records=False, result_record_count=records, return_geometry=False).sdf
    #print(results_df)
    return results_df


def oha_cases_html():
    """ Create the HTML for the Oregon Health Authority cases data.

    Returns
    -------
        HTML data in a string.
    """
    try:
        w = "altName='Clatsop' or altName='Tillamook' or altName='Columbia'"
        rural = get_cases(featureLayerUrl, w, 3)
        w = "altName='Multnomah' or altName='Clackamas' or altName='Washington'"
        metro = get_cases(featureLayerUrl, w, 3)
    except Exception as e:
        print("Can't read cases from '%s' : %s" % (featureLayerUrl, e))
        return None

    last_update = OHAParser.last_feature_edit().replace(
        tzinfo=datetime.timezone.utc)
    edittime = last_update.astimezone(
        timezone('America/Los_Angeles')).strftime(timeformat)
    #print(edittime)
    ohaUrl = '<a href="https://govstatus.egov.com/OR-OHA-COVID-19">OHA</a>'

    template = jinja.get_template('cases.html')
    html = template.render(
        source=ohaUrl,
        last_update=edittime, localnow=now,
        ruraldf=rural, metrodf=metro
    )
    return html

def worldometer_world_read():
    world_data = None
    if dryrun:
        with open("./worldometer.html", "r", encoding="utf-8") as fp:
            world_data = fp.read()
    else:
        try:
            world_data = HTMLGateway.fetch(worldometer_world_url)
        except Exception as e:
            sys.exit("Could not fetch world data. %s" % e)
    return world_data


def worldometer_states_read():
    state_data = None
    if dryrun:
        with open("./worldometer_states.html", "r", encoding="utf-8") as fp:
            state_data = fp.read()
    else:
        try:
            state_data = HTMLGateway.fetch(worldometer_states_url)
        except Exception as e:
            sys.exit("Could not fetch state data. %s" % e)
    return state_data


def wa_read():
    raw_data = None
    if dryrun:
        with open("./wa.json", "r", encoding="utf-8") as fp:
            raw_data = fp.read()
    else:
    # Get data from the wide world of web
        url = Config.WA_URL
        try:
            gateway = HTMLGateway()
            raw_data = gateway.fetch(url)
        except Exception as e:
            sys.exit("Could not fetch WA data. %s" % e)

    return raw_data


def world_cases_html():
    """ Create the HTML for the worldometer and covidtracking and WA data.

        Output will have 
        * world cases
        * US cases, tests, deaths
        * OR cases, tests, deaths
        * WA cases, tests, deaths

    Returns
    -------
        HTML data in a string.
    """
    worldometer_href = '<a href="%s">worldometer</a>' % worldometer_world_url
    covidtracking_href = '<a href="%s">covidtracking</a>' % covidtracking_url

    parser = WorldometerParser()

    raw_data = worldometer_world_read()
    last_updated = parser.parse_last_updated(raw_data).astimezone(
        timezone('America/Los_Angeles')).strftime(timeformat)
    #print(last_updated)
    world_df = parser.create_df(raw_data, "main_table_countries_today", '1')
    #print(world_df)

    raw_data = worldometer_states_read()
    or_update = parser.parse_last_updated(raw_data).astimezone(
        timezone('America/Los_Angeles')).strftime(timeformat)
    #print(or_update)
    or_df = parser.create_df(raw_data, "usa_table_countries_today", 'Oregon', rowindex=1)
    print(or_df)
    assert or_df.at[0, 'USA State'] == 'Oregon'

    d = wa_read()
    wa_update = WAParser.parse_last_updated(d).astimezone(
        timezone('America/Los_Angeles')).strftime(timeformat)
    #print(wa_update)
    wa_df = WAParser.fetch_cases(d)
    #print(wa_df)

    template = jinja.get_template('world_cases.html')
    html = template.render(localnow=now, 
        worldometer=worldometer_href,
        covidtracking=covidtracking_href,
        or_last_update=or_update, ordf=or_df,
        wa_last_update=wa_update, wadf=wa_df,
        world_last_update=or_update, worlddf=world_df,
    )
    return html


if __name__ == "__main__":

    outputdir = '../docker/capacity/html'
    staticdir = os.path.join(outputdir, 'static')

    # Set up output folder for supporting files
    if not os.path.exists(staticdir):
        os.makedirs(staticdir)
    
    # Copy supporting files
    file = 'ms.css'
    outputfile = os.path.join(staticdir, file)
    if os.path.exists(outputfile):
        os.unlink(outputfile)
    shutil.copyfile(os.path.join('templates/static', file), outputfile)

    # Copy index page... should render this I suppose
    shutil.copyfile('templates/index.html', os.path.join(outputdir, 'index.html'))

    # Generate static pages
    # Gather data first; don't destroy page if can't read new data!

    ohahtml = oha_cases_html()
    if ohahtml:
        with open(os.path.join(outputdir, 'cases.html'), 'w') as fp:
            fp.write(ohahtml)
        print("Wrote cases.html")

    worldhtml = world_cases_html()
    if worldhtml:
        with open(os.path.join(outputdir, 'world_cases.html'), 'w') as fp:
            fp.write(worldhtml)
        print("Wrote world_cases.html")

    # Send something meaningful as an error message

    if not ohahtml or not worldhtml:
        msg = ""
        if not ohahtml:
            msg += "oha "
        if not worldhtml:
            msg += "world"
        sys.exit("Data read failed on", msg)

# That's all
