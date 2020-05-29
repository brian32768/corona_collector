# corona_collector
Collects a variety of COVID-19 data and pushes it into ArcGIS Feature Layers

Scrape Worldometer's Coronavirus Information and transform the data into a Dataframe and a JSON easily consumed by third party applications/services such as Bots (Telegram/Discord/Whatever), APIS or Research Studies

Fragments of code from the original project are still here, many
thanks please see:
[chrislopez24/corona-parser](https://github.com/chrislopez24/corona-parser)

## Set up environment

   conda create --name covid --clone arcgispro-py3-vscode
   conda install --file requirements.txt

## Run

   python main.py

This will generate a new cases.json file
and store the data into a feature class.

## Deploy

I plan on installing it on a Debian machine and running it from
cron every 4 hours.

