import os
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

    WORLDOMETER_WORLD_URL = "https://www.worldometers.info/coronavirus"
    WORLDOMETER_STATES_URL = "https://www.worldometers.info/coronavirus/country/us"
    OHA_URL = 'https://govstatus.egov.com/OR-OHA-COVID-19'

# This is the one with current data but difficult to parse
#WA_URL=https://www.doh.wa.gov/Emergencies/NovelCoronavirusOutbreak2020COVID19/DataDashboard
    COVIDTRACKING_URL = 'https://covidtracking.com'
    WA_URL = 'https://covidtracking.com/api/v1/states/wa/current.json'

    _hoscap = 'https://emresource.juvare.com/'
    HOSCAP_LOGIN = _hoscap + 'login'
    
    _hoscap_table = 'https://emresource.juvare.com/EMSystem?uc=VIEWSTATUS&nextStep=VIEW_RSD'
    HOSCAP_PSH = _hoscap_table + '&nextStepDetail=23543'
    HOSCAP_PPMC = _hoscap_table + '&nextStepDetail=23542'
    HOSCAP_CMH = _hoscap_table + '&nextStepDetail=23515'

    pass

if __name__ == "__main__":
    pass

# That's all!
