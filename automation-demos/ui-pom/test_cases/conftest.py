import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent.resolve()
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from conf.serve_conf import read
from page_object.depot_page import DepotPage
from page_object.login_page import LoginPage
from page_object.person_page import PersonPage
from page_object.sale_order_page import SaleOrderPage
from page_object.vendor_page import VendorPage
from utils.browser import open_browser


@pytest.fixture(scope='module')
def driver(request):
    driver = open_browser('Chrome')

    def driver_finalizer():
        lp = LoginPage(driver, base_url=read('TEST_ENV')['url'])
        try:
            lp.wait(2)
            lp.click('xpath', '//a[@href="javascript:;"]')
            lp.wait(1)
            lp.click('xpath', '//div[@class="ant-modal-confirm-btns"]/button[2]')
        except Exception:
            pass
        finally:
            lp.quit()

    request.addfinalizer(driver_finalizer)
    return driver


@pytest.fixture()
def serve(request):
    env = request.param
    return read(env)['url']


@pytest.fixture()
def login_page(driver, serve):
    return LoginPage(driver, base_url=serve)


@pytest.fixture()
def vendor_page(driver, serve):
    return VendorPage(driver, base_url=serve)


@pytest.fixture()
def sale_order_page(driver, serve):
    return SaleOrderPage(driver, base_url=serve)


@pytest.fixture()
def depot_page(driver, serve):
    return DepotPage(driver, base_url=serve)


@pytest.fixture()
def person_page(driver, serve):
    return PersonPage(driver, base_url=serve)


@pytest.fixture
def login(request, login_page):
    user = request.param['user']
    pwd = request.param['pwd']
    login_page.login(user, pwd, request.param.get('wait', 2))
