#!/usr/bin/env python
# -*- coding: utf-8 -*-

import jinja2
from pyexcel_ods3 import get_data
from datetime import datetime

TEMPLATE_DIR = 'templates'
DATA_FILE = 'data/oha_county_metrics.ods'
TEMPLATE_FILE = 'county_metrics.html'
OUTPUT_FILE = 'public/county_metrics.html'

timeformat = "%m/%d/%y"

# Set up jinja templates. Look for templates in the TEMPLATE_DIR
env = jinja2.Environment(loader=jinja2.FileSystemLoader(TEMPLATE_DIR))

# Open the csv file and read it
data = get_data(DATA_FILE)
sheet1 = data['Sheet1']

headers = sheet1[0]
del sheet1[0]

table = []
rowcount = 0
for row in sheet1:
    if len(row) >= 5: # Ignore empty rows
        rowcount += 1
        date = row[1]
        row[1] = row[1].strftime(timeformat)
        table.append(row)
        print(row)
rowcount /= 3

date_range = "Jul 5 - Aug 15"
now = datetime.now().strftime(timeformat)
# Get the template and render it to a string. Pass table in as a var called table.
html = env.get_template(TEMPLATE_FILE).render(headers=headers, table=table, now=now, date_range=date_range)

# Write the html string to our OUTPUT_FILE
o = open(OUTPUT_FILE, 'w')
o.write(html)
o.close()
