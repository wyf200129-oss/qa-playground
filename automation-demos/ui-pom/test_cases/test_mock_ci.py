"""
CI Mock 演示测试 — Jenkins Pipeline 全流程演示

设计意图：
  替代依赖外部 ERP 系统的真实 UI 测试，用 Mock 对象模拟所有 Selenium 交互，
  让 Jenkins Pipeline 可以稳定跑通全绿，用于面试展示 CI/CD 能力。

Mock 范围：
  - driver          : MagicMock 模拟浏览器
  - BasePage 方法   : Mock 覆盖 open/input/click/wait 等
  - 验证码识别       : Mock 返回固定值

不依赖：Chrome、WebDriver、ERP 后端、ddddocr 识别准确率
"""

import pytest
from unittest.mock import Mock, MagicMock, patch


# ──────────────────────────────────────────────
# Mock 辅助
# ──────────────────────────────────────────────

def _make_login_page_mocked():
    """构造一个所有 Selenium 方法都被 Mock 的 ErpLoginPage"""
    from page_object.erp_login_page import ErpLoginPage

    mock_driver = MagicMock()
    mock_driver.current_url = 'http://erp.example.com/dashboard'

    page = ErpLoginPage(mock_driver)
    # 用 Mock 覆盖所有会触发真实 Selenium 调用的方法
    page.open = Mock()
    page.input = Mock()
    page.get_code = Mock(return_value='A1B2')      # 固定验证码
    page.click = Mock()
    page.wait_for_url_change = Mock()
    page.wait_for_visible = Mock()
    page.url = 'http://mock-erp/user/login'         # 替换占位符
    return page


def _make_vendor_page_mocked():
    """构造一个所有 Selenium 方法都被 Mock 的 ErpVendorPage"""
    from page_object.erp_vendor_page import ErpVendorPage

    mock_driver = MagicMock()
    page = ErpVendorPage(mock_driver)
    page.open = Mock()
    page.click = Mock()
    page.input = Mock()
    page.wait_for_invisible = Mock()
    page.url = 'http://mock-erp/system/vendor'
    return page


# ──────────────────────────────────────────────
# 登录模块 Mock 测试
# ──────────────────────────────────────────────

class TestMockLogin:
    """登录流程 Mock 测试 — 演示 POM 模式下登录交互逻辑"""

    def test_login_success_url_changes(self):
        """
        Mock 正向用例：合法账号密码登录后 URL 跳转至 Dashboard。
        验证 point：login() 方法按预期调用了 open → input×3 → click → wait 链路。
        """
        page = _make_login_page_mocked()
        url = page.login('admin', 'p@ssw0rd')

        # 断言调用链完整
        page.open.assert_called_once_with(page.url)
        assert page.input.call_count == 3                 # user / pwd / code
        page.click.assert_called_once()
        page.wait_for_url_change.assert_called_once()
        page.wait_for_visible.assert_called_once()

        # 断言返回值来自 mocked driver
        assert url == 'http://erp.example.com/dashboard'

    def test_verify_logged_in_visible(self):
        """
        Mock 验证登录态：Dashboard 指示器可见时返回 True。
        """
        page = _make_login_page_mocked()
        assert page.verify_logged_in() is True
        page.wait_for_visible.assert_called()

    def test_verify_logged_in_not_visible(self):
        """
        Mock 反例：wait_for_visible 抛异常时返回 False。
        """
        page = _make_login_page_mocked()
        page.wait_for_visible = Mock(side_effect=TimeoutError('element not found'))
        assert page.verify_logged_in() is False


# ──────────────────────────────────────────────
# 供应商管理 Mock 测试
# ──────────────────────────────────────────────

class TestMockVendor:
    """供应商管理 Mock 测试 — 演示 POM 模式下 CRUD 交互"""

    def test_add_supplier_flow(self):
        """
        Mock 新增供应商：点击新增 → 填入名称/电话 → 点击保存 → 等弹窗关闭。
        """
        page = _make_vendor_page_mocked()
        page.add_supplier('杭州测试供应商', '0571-88888888')

        page.open.assert_called_once_with(page.url)
        assert page.input.call_count == 2               # name + tele
        assert page.click.call_count == 2               # 新增按钮 + 保存按钮
        page.wait_for_invisible.assert_called_once()

    def test_search_supplier_flow(self):
        """
        Mock 查询供应商：输入关键词 → 点击查询。
        """
        page = _make_vendor_page_mocked()
        page.search('test vendor')

        page.open.assert_called_once_with(page.url)
        page.input.assert_called_once()
        page.click.assert_called_once()


# ──────────────────────────────────────────────
# 配置/数据加载测试
# ──────────────────────────────────────────────

class TestConfig:
    """配置与测试数据完整性验证"""

    def test_yaml_config_exists_and_valid(self):
        """
        确认 erp_vendor.yaml 存在且能正常解析，包含必需的 login/vendor 节点。
        这是真实 YAML 文件读取，不属于 Mock。
        """
        import yaml
        from pathlib import Path

        config = Path(__file__).parent.parent / 'test_data' / 'erp_vendor.yaml'
        data = yaml.safe_load(config.read_text(encoding='utf-8'))

        assert 'login' in data,  '缺少 login 配置节点'
        assert 'vendor' in data, '缺少 vendor 配置节点'
        assert 'user' in data['login'], '缺少 login.user'
        assert 'pwd' in data['login'],  '缺少 login.pwd'

    def test_page_object_imports(self):
        """
        Regression：确认所有 Page Object 模块可以正常导入。
        防止重构后 import 路径断裂。
        """
        from page_object.erp_login_page import ErpLoginPage   # noqa: F811
        from page_object.erp_vendor_page import ErpVendorPage  # noqa: F811
        from utils.browser_options import browser_options      # noqa: F811

        assert ErpLoginPage is not None
        assert ErpVendorPage is not None
        assert callable(browser_options)
