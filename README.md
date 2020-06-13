# corona_collector
Collects a variety of COVID-19 data and pushes it into ArcGIS Feature Layers

Scrape Worldometer's Coronavirus Information and transform the data into a Dataframe and a JSON easily consumed by third party applications/services such as Bots (Telegram/Discord/Whatever), APIS or Research Studies

Fragments of code from the original project are still here, many
thanks please see:
[chrislopez24/corona-parser](https://github.com/chrislopez24/corona-parser)

## Set up environment

THere is no longer any need to clone ESRI's arcgispro environment,
the requirements.txt file pulls what is needed from conda forge.

   conda create --name covid
   conda activate covid
   conda install -c esri --file requirements.txt

You have to put a portal user and password into .env

   cp sample.env .env

You have to create a suitable feature class as the target for output.
I did this in the catalog in ArcGISPro and then published it to my Portal.

## Run

   python main.py

This will store the data into a feature class.

## Deploy

I plan on installing it on a Debian machine and running it from
cron every 4 hours.


Source of data for OR and WA data

OHA_URL=https://govstatus.egov.com/OR-OHA-COVID-19
WA_URL=https://www.doh.wa.gov/Emergencies/NovelCoronavirusOutbreak2020COVID19/DataDashboard


Code to install the chromedriver on Linux; 

# platform options: linux32, linux64, mac64, win32
PLATFORM=linux64
VERSION=$(curl http://chromedriver.storage.googleapis.com/LATEST_RELEASE)
curl http://chromedriver.storage.googleapis.com/$VERSION/chromedriver_$PLATFORM.zip \
| bsdtar -xvf - -C ~/.conda/envs/covid/bin
chmod +x ~/.conda/envs/covid/bin chromedriver

wget https://dl-ssl.google.com/linux/linux_signing_key.pub
sudo
echo "deb http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/chrome.list
apt-key add linux_signing_key.pub
apt update
apt upgrade
apt install google-chrome-stable