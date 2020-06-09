from datetime import datetime
from pytz import timezone

def connect(portal, featurelayer):

    # Amusingly the GIS search function is sloppy and returns several...
    # there does not appear to be an exact match option.

    layercollectionlist = portal.content.search(query=featurelayer,
                                          item_type="Feature Layer Collection")
    if len(layercollectionlist) < 1:
        error = "No feature services found. \"%s\"" % featurelayer
        raise Exception(error)

    # Search for the correct Feature Service
    try:
        layercollection = [item for item in layercollectionlist if item.title == featurelayer][0]
    except Exception as e:
        raise Exception("Layer not found. \"%s\", %s" % (featurelayer, e))

    return layercollection.layers[0]


def s2i(s):
    """ Convert a string to an integer even if it has + and , in it. """
    if type(s)==type(0):
        return s
    if s:
        return int(float(s.replace(',', '')))
    return None


def local2utc(t):
    """ Change a datetime object from local to UTC """
    return t.astimezone(timezone('UTC'))


# That's all!
