import os
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd

from config import Config

DATA_DIR = './data'
FILE_NAME = 'oha_county_metrics.csv'
data_path = os.path.join(DATA_DIR, FILE_NAME)
cases = pd.read_csv(data_path)

## Create the app
app = dash.Dash(__name__)
#app.config.from_object(Config)

# Creating a Plotly figure
trace = go.Histogram(
        x = cases['Week']
        )

layout = go.Layout(
        title = 'Cases',
        xaxis = dict(title='Week'),
        yaxis = dict(title='Test positivity %')
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

