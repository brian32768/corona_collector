#!/usr/bin/env -S conda run -n covid python
"""
    Read a table from ArcGIS containing oha county school reopening metrics
    and generate an HTML page from it.
"""
import datetime
import jinja2
from arcgis.features import FeatureLayer
from pandas.core.frame import DataFrame

from config import Config
portalUrl    = Config.PORTAL_URL
portalUser   = Config.PORTAL_USER
portalPasswd = Config.PORTAL_PASSWORD
oha_county_metrics = Config.OHA_COUNTY_METRICS_URL
assert portalUrl
assert portalUser
assert portalPasswd
assert oha_county_metrics

date_range = "Nov 15 - Dec 12, 2020"

TEMPLATE_DIR = 'templates'
TEMPLATE_FILE = 'county_metrics.html'
OUTPUT_FILE = 'public/county_metrics.html'

timeformat = "%m/%d/%y"

# Set up jinja templates. Look for templates in the TEMPLATE_DIR
env = jinja2.Environment(loader=jinja2.FileSystemLoader(TEMPLATE_DIR))

table = []
rowcount = -1

def load_df(url):
    # sort descending on date column to read latest entries
    df = FeatureLayer(url).query(order_by_fields="week_end DESC",
                                return_all_records=False, result_record_count=9,
                                return_geometry=False).sdf

    # filter() gets rid of unwanted columns
    # sort with ignore_index=True causes the new df to be renumbered
    keepers = ["county", "case_count", "case_rate_per_100_000", "test_positivity__", "week_begin", "week_end"]
    reorder = ["county", "week_begin", "week_end", "case_count", "case_rate_per_100_000", "test_positivity__"]
    return df.filter(items=keepers).sort_values(['county','week_begin'], ignore_index=True)[reorder]
    
if __name__ == "__main__":

    df = load_df(oha_county_metrics)
    #print(df)

    # Find the date range
    table_begin = df.loc[0, ['week_begin']]
    table_end = df.loc[2, ['week_end']]

    date_fmt = "%b %d" # NOV 3
    date_range = table_begin[0].strftime(date_fmt) + ' - ' + table_end[0].strftime(date_fmt)

    dfmt = '%m/%d'
    df['week_begin'] = df.apply(lambda row: row['week_begin'].strftime(dfmt) + '-' + row['week_end'].strftime(dfmt), axis=1) 
    sdf = df.drop(['week_end'], axis=1)

    now = datetime.datetime.now().strftime(timeformat)
    table_column_names = [
        'County', 
        'Weeks',
        'Case count', 
        'Case rate / 100,000',
        'Test positivity %'
    ]
    
    # Get the template and render it to a string. Pass table in as a var called table.
    html = env.get_template(TEMPLATE_FILE).render(headers=table_column_names, df=sdf, now=now, date_range=date_range)

    # Write the html string to our OUTPUT_FILE
    o = open(OUTPUT_FILE, 'w')
    o.write(html)
    o.close()
