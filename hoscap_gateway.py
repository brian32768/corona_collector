import sys
from selenium import webdriver
from datetime import datetime, timezone

from config import Config

class HOSCAPGateway:

    def login(self):
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        options.add_argument('window-size=1200x600')

        try:
            self.driver = webdriver.Chrome(options=options)
            self.driver.get(Config.HOSCAP_LOGIN)
            self.driver.implicitly_wait(5)
        except Exception as e:
            print("Failed to open Chrome, this can happen if Chrome and chromedriver versions don't match.")
            print(e)
            exit(-1)
        
        # Login page has two stages, first enter name and click button
        # Then enter password and click button
        # Looks like it's just hiding and unhiding some fields
        # so maybe I can do it all in one go?

        try:
            username = self.driver.find_element_by_id('username')
        except Exception as e:
            sys.exit("Could not find username field. %s" % e)

        username.send_keys(Config.HOSCAP_USER)

        try:
            checkname_button = self.driver.find_element_by_id('checkUsername')
            checkname_button.click()
        except Exception as e:
            sys.exit("Could not find the check name button. %s" % e)

        try:
            password = self.driver.find_element_by_id('password')
        except Exception as e:
            sys.exit("Could not find password field. %s" % e)
        password.send_keys(Config.HOSCAP_PASSWORD)

        try:
            login_button = self.driver.find_element_by_id('loginBtn')
        except Exception as e:
            sys.exit("Could not find login button. %s" % e)
        rval = login_button.click()

        return rval

    def fetch(self, url):
        self.driver.get(url)
        return self.driver.page_source

    def close(self):
        self.driver.close()
        self.driver.quit()

if __name__ == "__main__":
    # Unit test

    assert(Config.HOSCAP_USER)
    assert(Config.HOSCAP_PASSWORD)

    gateway = HOSCAPGateway()
    gateway.login()
    
    d = gateway.fetch(Config.HOSCAP_CMH)
    with open("juvare_cmh.html", "w", encoding="UTF-8") as fp:
        fp.write(d)

    d = gateway.fetch(Config.HOSCAP_PSH)
    with open("juvare_psh.html", "w", encoding="UTF-8") as fp:
        fp.write(d)

    d = gateway.fetch(Config.HOSCAP_PPMC)
    with open("juvare_ppmc.html", "w", encoding="UTF-8") as fp:
        fp.write(d)

    gateway.close()

    exit(0)
# That's all!
