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

# Run

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

One machine runs scripts that write into ArcGIS, since that machine does not need to be publicly visible.
The other has to publish a web page so it's on a machine that _is_ visible.

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

### Notifications

Originally my Debian virtual machines were not set up to send out email so when crontab runs these scripts the email piled up. 
I changed that recently, now they use Sendgrid and the mail
comes to me directly every time a cronjob runs. 

But if I break anything or just as likely the data source sites change and the
scripts break, then I want to know about it.

So I put together a bash script "send_sms.sh" that will send text messages to 
my phone via Twilio. The script sources a .env file that has Twilio secrets in it.

## Visualizations

I successfully ported the OregonLive app (see link) but now
I am working on a Dash app.

https://projects.oregonlive.com/coronavirus/caseavg.html?initialWidth=540&childId=promo&parentTitle=Coronavirus%20in%20Oregon%3A%201%2C180%20new%20cases%2C%20six%20deaths%2C%20as%20state%20welcomes%20historic%20vaccine%20arrival%20-%20oregonlive.com&parentUrl=https%3A%2F%2Fwww.oregonlive.com%2Fcoronavirus%2F2020%2F12%2Fcoronavirus-in-oregon-1180-new-cases-six-deaths-as-state-welcomes-historic-vaccine-arrival.html

The Javascript/D3 app inspired from OregonLive is currently mostly in src/

The Dash/Plotly app is mostly in app/ and start_app.py.

There are configurations to launch each of these for debugging.

Since I plan to delete the D3 app I am not writing more about it here.

More documentation on the Dash app will be in app/README.md.
