from selenium import webdriver
from datetime import datetime, timezone

from config import Config

class HOSCAPGateway:

    def login(self):
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        options.add_argument('window-size=1200x600')

        self.driver = webdriver.Chrome(options=options)
        self.driver.get(Config.HOSCAP_LOGIN)
        self.driver.implicitly_wait(5)

        login = self.driver.find_element_by_name('LoginBtn')
        username = self.driver.find_element_by_id('username')
        password = self.driver.find_element_by_id('password')

        username.send_keys(Config.HOSCAP_USER)
        password.send_keys(Config.HOSCAP_PASSWORD)

        login.click()

        return

    def fetch(self, url):
        self.driver.get(url)
        return self.driver.page_source

if __name__ == "__main__":
    # Unit test

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

    exit(0)
# That's all!
