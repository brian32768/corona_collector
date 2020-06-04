import requests

class HTMLGateway:
    @staticmethod
    def fetch(url):
        try:
            res = requests.get(url, timeout=15)
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

    try:
        html_data = HTMLGateway.fetch("https://govstatus.egov.com/OR-OHA-COVID-19")
        with open("./oha.html", "w", encoding="utf-8") as fp:
            fp.write(html_data)
        print("Wrote oha.html")
    except Exception as e:
        print("Fetch failed", e)

    try:
        html_data = HTMLGateway.fetch("https://www.worldometers.info/coronavirus")
        with open("./worldometer.html", "w", encoding="utf-8") as fp:
            fp.write(html_data)
        print("Wrote worldometer.html")
    except Exception as e:
        print("Fetch failed", e)

    print("All done!")
# That's all!
