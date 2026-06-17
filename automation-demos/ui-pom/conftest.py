"""
pytest 全局配置 —— fixtures 定义。

核心 fixture：
  - driver      : session 级别浏览器实例（所有测试复用同一窗口）
  - test_data   : 从 YAML 加载测试数据
  - logged_in   : 预登录 fixture（依赖此 fixture 的测试在登录态下执行）
"""

import pytest
import yaml
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from utils.browser_options import browser_options
from page_object.erp_login_page import ErpLoginPage
from page_object.erp_vendor_page import ErpVendorPage


# ── 路径常量 ──────────────────────────────────────
TEST_DATA_DIR = Path(__file__).parent / 'test_data'


def _load_yaml(filename: str) -> dict:
    """加载 test_data 目录下的 YAML 文件"""
    filepath = TEST_DATA_DIR / filename
    with open(filepath, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


# ── Fixtures ──────────────────────────────────────

@pytest.fixture(scope='session')
def driver():
    """
    初始化 Chrome 浏览器实例（session 级别）。

    使用 webdriver-manager 自动管理 chromedriver，
    无需手动下载或配置路径。
    """
    service = Service(ChromeDriverManager().install())
    drv = webdriver.Chrome(service=service, options=browser_options())
    yield drv
    drv.quit()


@pytest.fixture
def test_data():
    """加载 ERP 供应商测试数据（YAML）"""
    return _load_yaml('erp_vendor.yaml')


@pytest.fixture
def login_page(driver):
    """返回 ErpLoginPage 实例"""
    return ErpLoginPage(driver)


@pytest.fixture
def vendor_page(driver):
    """返回 ErpVendorPage 实例"""
    return ErpVendorPage(driver)


@pytest.fixture
def logged_in(login_page, test_data):
    """
    预登录 fixture：执行登录后返回 login_page。

    所有需要登录态的测试只需依赖此 fixture。
    """
    user = test_data['login']['user']
    pwd  = test_data['login']['pwd']
    login_page.login(user, pwd)
    return login_page
