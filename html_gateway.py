import requests

class HTMLGateway:
    
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

    test_simple(Config.WA_URL, "./wa.json")
    test_simple(Config.OHA_URL, "./oha.html")
    test_worldometer("https://www.worldometers.info/coronavirus")

# That's all!
