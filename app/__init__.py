import os
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd
from arcgis.gis import GIS
from arcgis.features import FeatureLayer
import arcgis.features
import pytz
from datetime import datetime, timezone

stylesheets = ['static/main.css']

from config import Config

DATA_DIR = './data'
FILE_NAME = 'oha_county_metrics.csv'
data_path = os.path.join(DATA_DIR, FILE_NAME)
cases = pd.read_csv(data_path)

def connect(layername):
    layer = None
    portal = GIS(Config.PORTAL_URL, Config.PORTAL_USER, Config.PORTAL_PASSWORD)
    #print("Logged in as " + str(portal.properties.user.username))
    layer = FeatureLayer(layername, portal)
    return layer

def read_df():
    layer = connect(Config.COVID_CASES_URL)
    sdf = pd.DataFrame.spatial.from_layer(layer)
    del layer
    df = sdf[sdf.editor == 'EMD'] # Just Clatsop County
    print(df)
    return df


tformat = "%Y-%m-%d %H:%M"
pactz = pytz.timezone('America/Los_Angeles')

def utc2localdate(utc_naive):
    """ input: timestamp from dataframe in utc, "YYYY-MM-DD HH:MM:SS"
        output: string in local time, same format """

    # I'm not sure but maybe I should just set tzinfo here too??
    # tzinfo = timezone.utc
    #return t.astimezone(timezone.utc).replace(microsecond=0, second=0)
    utc = utc_naive.tz_localize(timezone.utc)
    #print('utc=', utc, type(utc))
    # We're only interested in the date
    p = utc.astimezone(pactz).date()
    rval = p.strftime('%m/%d/%y')
    return rval

def clean_data(sdf):
    """ Return two df's, one for total cases and one for daily cases. """

    # Convert to localtime
    # see https://pandas.pydata.org/pandas-docs/stable/user_guide/indexing.html#returning-a-view-versus-a-copy
    date = []
    for utc_naive in sdf.loc[:, 'utc_date']:
        date.append(utc2localdate(utc_naive))
    sdf['date'] = date
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

sdf = read_df()
(new_df, total_df) = clean_data(sdf)
print(new_df)
print(total_df)

app = dash.Dash(__name__, external_stylesheets=stylesheets)
#app.config.from_object(Config)

# Creating a Plotly figure
trace = go.Histogram(
        y = new_df['cases']
        )

layout = go.Layout(
        title = 'Cases',
        xaxis = dict(title='Week'),
        yaxis = dict(title='New cases')
        )

figure = go.Figure(
        data = [trace],
        layout = layout
        )

app.layout = html.Div([
        html.H1('%s, this is my first Dash App!' % Config.PORTAL_USER),
        html.H2('Debug mode = %s' % os.environ.get('DASH_DEBUG')),
        html.P('This is some normal text, we can use it to describe something about the application.'),
        dcc.Graph(id='my-histogram', figure=figure)
        ])

