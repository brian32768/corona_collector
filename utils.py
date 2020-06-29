from arcgis.features import FeatureLayer
from datetime import datetime, timezone

def connect(portal, url):
    layer = FeatureLayer(url, portal)
    # You can look at properties with
    # layer.properties
    # or get the list of fields with layer.properties.fields
    return layer


def s2i(s):
    """ Convert a string to an integer even if it has + and , in it. """

    # Turns out sometimes there can be text in the string, for example "pending",
    # and that made this function crash.
    if type(s)==type(0):
        # Input is already a number
        return s
    try:
        # Sometimes input has a number with commas in it, remove those.
        if s:
            return int(float(s.replace(',', '')))
    except ValueError:
        pass
    return None


def local2utc(t):
    """ Change a datetime object from local to UTC """

    # I'm not sure but maybe I should just set tzinfo here too??
    # tzinfo = timezone.utc
    return t.astimezone(timezone.utc).replace(microsecond=0, second=0)


# UNIT TESTS
if __name__ == "__main__": 
    from arcgis.gis import GIS
    from config import Config

    assert s2i(None) == None
    assert s2i("") == None
    assert s2i("pending") == None
    assert s2i(123) == 123
    assert s2i("1,100") == 1100
    assert s2i("123456.123456") == 123456

    print(local2utc(datetime.now()))

    portalUrl = Config.PORTAL_URL
    portalUser = Config.PORTAL_USER
    portalPasswd = Config.PORTAL_PASSWORD

    layers = [
        Config.COVID_CASES_URL,
        Config.PUBLIC_WEEKLY_URL,
        Config.HOSCAP_URL,
        Config.PPE_URL,
    ]

    try:
        portal = GIS(portalUrl, portalUser, portalPasswd)
        #print("Logged in as " + str(portal.properties.user.username))
    except Exception as e:
        print("Could not connect to portal. \"%s\"" % e)
        print("Make sure the environment variables are set correctly.")
        exit(-1)

    for url in layers:
        try:
            layer = connect(portal, url)
            print("name = '%s'" % layer.properties.name)#, layer.properties.fields)
        except Exception as e:
            print("Open failed for '%s' : %s" % (url, e))
            exit(-1)

# That's all!
