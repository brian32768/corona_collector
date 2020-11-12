import os

# In PRODUCTION conda sets up the environment,
# so look in ~/.conda/envs/covid/etc/conda/activate.d/env_vars.sh
# to see how it is set up.

class Config(object):
    """ Read environment here to create configuration data. """
    SECRET_KEY=os.environ.get('SECRET_KEY') or "12345678"
 
    PORTAL_URL      = os.environ.get('PORTAL_URL')
    PORTAL_USER     = os.environ.get('PORTAL_USER')
    PORTAL_PASSWORD = os.environ.get('PORTAL_PASSWORD')

# Where to write output
    COVID_CASES_URL = os.environ.get('COVID_CASES_URL')
    PUBLIC_WEEKLY_URL = os.environ.get('PUBLIC_WEEKLY_URL')
    HOSCAP_URL = os.environ.get('HOSCAP_URL')
    PPE_URL = os.environ.get('PPE_URL')

    HOSCAP_USER = os.environ.get('HOSCAP_USER')
    HOSCAP_PASSWORD = os.environ.get('HOSCAP_PASSWORD')

# NONE OF THIS IS SECRET

    WORLDOMETER_WORLD_URL = "https://www.worldometers.info/coronavirus/"
    WORLDOMETER_STATES_URL = "https://www.worldometers.info/coronavirus/country/us"
    OHA_URL = 'https://govstatus.egov.com/OR-OHA-COVID-19'
    OHA_BED_CAPACITY_URL = "https://public.tableau.com/profile/oregon.health.authority.covid.19#!/vizhome/OregonCOVID-19Update/HospitalCapacity"

# This is the one with current data but difficult to parse
#WA_URL=https://www.doh.wa.gov/Emergencies/NovelCoronavirusOutbreak2020COVID19/DataDashboard
    COVIDTRACKING_URL = 'https://covidtracking.com'
    WA_URL = 'https://covidtracking.com/api/v1/states/wa/current.json'

    _hoscap = 'https://emresource.juvare.com/'
    HOSCAP_LOGIN = _hoscap + 'login'
    
    _hoscap_table = 'https://emresource.juvare.com/EMSystem?uc=VIEWSTATUS'
    HOSCAP_PSH =     _hoscap_table + '&nextStep=VIEW_RSD&nextStepDetail=23543'
    HOSCAP_PPMC =    _hoscap_table + '&nextStep=VIEW_RSD&nextStepDetail=23542'
    HOSCAP_CMH =     _hoscap_table + '&nextStep=VIEW_RSD&nextStepDetail=23515'
    HOSCAP_SUMMARY = _hoscap_table + "&nextStep=VIEW_EVENT&currentStep&nextStep=view_event&nextStepDetail=664143&regionID=3103"
    pass


if __name__ == "__main__":

    # To test this in VSCODE
    # source ~/.conda/envs/covid/etc/conda/activate.d/env_vars.sh
    
    assert Config.PORTAL_URL != None
    assert Config.PORTAL_USER != None
    assert Config.PORTAL_PASSWORD != None

    pass

# That's all!
