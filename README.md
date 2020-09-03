# corona_collector
Collects a variety of COVID-19 data and pushes it into ArcGIS Feature Layers

Scrape Worldometer's Coronavirus Information and transform the data into a Dataframe and a JSON easily consumed by third party applications/services such as Bots (Telegram/Discord/Whatever), APIS or Research Studies

Fragments of code from the original project are still here, many
thanks please see:
[chrislopez24/corona-parser](https://github.com/chrislopez24/corona-parser)

## Set up environment

The requirements.txt file pulls what is needed from conda forge, so you don't need ArcGIS Pro installed for this project to work.

However, if you ARE working in an ArcGIS Pro world you should use "clone" to avoid getting DLL runtime errors about pandas.

   conda create --name=covid --clone=arcgispro-py3
   conda activate covid
   conda install -c esri --file=requirements.txt

You have to put a portal user and password into .env

   cp sample.env .env

You have to create a suitable feature class as the target for output.
I did this in the catalog in ArcGISPro and then published it to my Portal.

## Run

There are multiple executables here.

These all store the data into local feature classes via Portal.
hoscap.py     scrapes the HOSCAP site
oha_beds.py   scrapes the OHA site for bed capacity data
oha_cases.py  scrapes the OHA site AND reads feature data, for cases
wa_cases.py   scrapes the WA site for cases

This generates static HTML pages. Included in dashboards.
generator.py  generates from OHA cases feature data
	      using static/ and templates/


## Deploy

These are all run from cron on Debian machines.





Source of data for OR and WA data

OHA_URL=https://govstatus.egov.com/OR-OHA-COVID-19
WA_URL=https://www.doh.wa.gov/Emergencies/NovelCoronavirusOutbreak2020COVID19/DataDashboard


Code to install the chromedriver on Linux; 
DON'T use Conda version

# platform options: linux32, linux64, mac64, win32
PLATFORM=linux64
VERSION=$(curl http://chromedriver.storage.googleapis.com/LATEST_RELEASE)
curl http://chromedriver.storage.googleapis.com/$VERSION/chromedriver_$PLATFORM.zip \
| bsdtar -xvf - -C ~/.conda/envs/covid/bin
chmod +x ~/.conda/envs/covid/bin/chromedriver

wget https://dl-ssl.google.com/linux/linux_signing_key.pub
sudo
echo "deb http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/chrome.list
apt-key add linux_signing_key.pub
apt update
apt upgrade
apt install google-chrome-stable
