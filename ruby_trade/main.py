from selenium import webdriver
from time import sleep
from bs4 import BeautifulSoup as bs
import re

ma = ''
pw = ''

def Login():
    driver = webdriver.PhantomJS()
    driver.get('https://lightning.bitflyer.jp/?lang=ja')

    login_id = driver.find_element_by_id("LoginId")
    login_id.send_keys(ma)

    login_pw = driver.find_element_by_id("Password")
    login_pw.send_keys(pw)

    driver.find_element_by_id("login_btn").click()
    while True:
        html = driver.page_source.encode("utf-8")
        soup = str(bs(html,"html.parser"))
        p = '<option value="ASK">(.+)</option>'
        m = re.findall(p,soup)
        print(m[0])

if __name__ == '__main__':
    Login()
