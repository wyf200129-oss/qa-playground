from selenium import webdriver


def options():
    option = webdriver.ChromeOptions()
    option.add_argument('start-maximized')
    option.add_experimental_option('excludeSwitches', ['enable-logging'])
    option.add_argument('--log_level=3')
    option.add_argument('--disable-gpu')
    option.add_argument('--ignore-certificate-errors')
    return option
