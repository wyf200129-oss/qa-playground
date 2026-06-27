import os

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from conf.options import options


def open_browser(type_='Chrome'):
    if type_ != 'Chrome':
        return getattr(webdriver, type_.capitalize())()

    driver_path = os.environ.get('CHROMEDRIVER_PATH') or ChromeDriverManager().install()
    service = Service(driver_path)
    return webdriver.Chrome(service=service, options=options())
