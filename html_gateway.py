import urllib
from bs4 import BeautifulSoup

#from cookies import Cookies, Cookie
#import html5lib
#import mechanize
import requests

class HTMLGateway:
    
    def __init__(self):
        pass

    def login(self, route, user, password):
        """
        cookie = Cookies(juvare="hoscap")
        req = mechanize.Browser()
        req.set_cookiejar(cookie)

        req.open(route)

        req.select_form(nr=0)
        req.form['username'] = 'username'
        req.form['password'] = 'password.'
        req.submit()

        print (req.response().read())
        """
        return
    
    @staticmethod
    def fetch(url):
        try:
            res = requests.get(url, timeout=30)
        except requests.Timeout:
            raise HTMLGatewayError("Timeout retrieving data from '%s'" % url)
        
        except requests.RequestException:
            raise HTMLGatewayError("Error fetching data from '%s' : %s" % (url, requests.RequestException))

        if res.status_code != 200:
            raise HTMLGatewayError("Website '%s' returned status code %s" % (url, res.status_code))

        return res.text

class HTMLGatewayError(Exception):
    pass

if __name__ == "__main__":

    # Unit tester
    # For unit testing the parser, make a copy of the data.

    from config import Config

    def test_simple(url, filename):
        data = HTMLGateway.fetch(url)
        with open(filename, "w", encoding="utf-8") as fp:
            fp.write(data)
            print("Wrote", filename)

    def test_worldometer(url):
        html_data = HTMLGateway.fetch(url)
        with open("./worldometer.html", "w", encoding="utf-8") as fp:
            fp.write(html_data)
            print("Wrote worldometer.html")

    def test_hoscap():
        gateway = HTMLGateway()
        gateway.login(Config.HOSCAP_URL + 'login',
                Config.HOSCAP_USER, Config.HOSCAP_PASSWORD)

        url = Config.HOSCAP_URL
        route = url + Config.HOSCAP_PSH
        html_data = gateway.fetch(route)
        with open("./psh.html", "w", encoding="utf-8") as fp:
            fp.write(html_data)
        pass

        route = url + Config.HOSCAP_CMH
        html_data = gateway.fetch(route)
        with open("./cmh.html", "w", encoding="utf-8") as fp:
            fp.write(html_data)
        pass

        route = url + Config.HOSCAP_PPMC
        html_data = gateway.fetch(route)
        with open("./ppmc.html", "w", encoding="utf-8") as fp:
            fp.write(html_data)
        pass


    test_simple(Config.WA_URL, "./wa.json")
#    test_simple(Config.OHA_URL, "./oha.html")
#    test_worldometer("https://www.worldometers.info/coronavirus")
#    test_hoscap()
    
    print("All done!")

# That's all!
