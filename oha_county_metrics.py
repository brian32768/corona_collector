#!/usr/bin/env python
# -*- coding: utf-8 -*-
import csv
import jinja2
from datetime import datetime

TEMPLATE_DIR = 'templates'
DATA_FILE = 'data/oha_county_metrics.csv'
TEMPLATE_FILE = 'county_metrics.html'
OUTPUT_FILE = 'public/county_metrics.html'

timeformat = "%m/%d/%y"

# Set up jinja templates. Look for templates in the TEMPLATE_DIR
env = jinja2.Environment(loader=jinja2.FileSystemLoader(TEMPLATE_DIR))

table = []
rowcount = -1

with open(DATA_FILE, "r") as fp:
    csvreader = csv.reader(fp, delimiter=',', quotechar='"')

    for row in csvreader:
        print(row)

        if len(row) >= 5: # Ignore empty rows
            if rowcount < 0:
                headers = row
            else:
                date = row[1]
                table.append(row)
            rowcount += 1

rowcount /= 3

date_range = "Jul 5 - Sep 26"
now = datetime.now().strftime(timeformat)
# Get the template and render it to a string. Pass table in as a var called table.
html = env.get_template(TEMPLATE_FILE).render(headers=headers, table=table, now=now, date_range=date_range)

# Write the html string to our OUTPUT_FILE
o = open(OUTPUT_FILE, 'w')
o.write(html)
o.close()
