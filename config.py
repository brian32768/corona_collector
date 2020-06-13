import os
class Config(object):
    """ Read environment here to create configuration data. """
    SECRET_KEY=os.environ.get('NO_TIME_LIKE_THE_present') or "12345678"
 
    PORTAL_URL      = os.environ.get('PORTAL_URL')
    PORTAL_USER     = os.environ.get('PORTAL_USER')
    PORTAL_PASSWORD = os.environ.get('PORTAL_PASSWORD')

    OHA_URL = os.environ.get('OHA_URL')
    WA_URL  = os.environ.get('WA_URL')
    
    HOSCAP_LOGIN    = os.environ.get('HOSCAP_LOGIN')
    HOSCAP_PSH      = os.environ.get('HOSCAP_PSH')
    HOSCAP_PPMC     = os.environ.get('HOSCAP_PPMC')
    HOSCAP_CMH      = os.environ.get('HOSCAP_CMH')
    HOSCAP_USER     = os.environ.get('HOSCAP_USER')
    HOSCAP_PASSWORD =  os.environ.get('HOSCAP_PASSWORD')

    # Where to write output
    COVID_CASES_URL   = os.environ.get('COVID_CASES_URL')
    PUBLIC_WEEKLY_URL = os.environ.get('PUBLIC_WEEKLY_URL')
    HOSCAP_URL        = os.environ.get('HOSCAP_URL')
    PPE_URL           = os.environ.get('PPE_URL')

    pass

# That's all!
