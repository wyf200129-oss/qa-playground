"""
ERP 系统 — 登录页 Page Object

演示要点：
  1. 验证码自动识别（ddddocr）—— 体现实战问题解决能力
  2. 显式等待替代 time.sleep —— URL 变更检测确认登录成功
  3. 元素定位以元组封装，结构化维护
"""

from base_page.basepage import BasePage


class ErpLoginPage(BasePage):
    """ERP 登录页"""

    url = '[ERP_BASE_URL]/user/login'

    # ── 元素定位 ──────────────────────────────────
    login_name    = ('xpath', '//*[@id="loginName"]')
    login_pwd     = ('xpath', '//*[@id="password"]')
    login_code    = ('id', 'inputCode')
    login_img     = ('xpath', '//img[@data-v-4f5798c5]')
    login_button  = ('xpath', '//button[@data-v-4f5798c5]')

    # 登录成功后页面出现的标志元素（仪表盘/导航）
    dashboard_indicator = ('xpath', '//div[@class="table-operator"]')

    # ── 业务流程 ──────────────────────────────────

    def login(self, user: str, pwd: str) -> str:
        """
        执行登录操作，返回登录后当前 URL。

        步骤：
          1. 打开登录页
          2. 填入用户名/密码/验证码
          3. 点击登录按钮
          4. 显式等待 URL 变更，确认登录成功
        """
        self.open(self.url)
        self.input(*self.login_name, txt=user)
        self.input(*self.login_pwd, txt=pwd)
        self.input(*self.login_code, txt=self.get_code(*self.login_img))
        self.click(*self.login_button)

        # 显式等待：URL 从 login → 首页/仪表盘（替代 sleep(15)）
        self.wait_for_url_change(self.url, timeout=20)

        # 二次确认：Dashboard 区域可见
        self.wait_for_visible(*self.dashboard_indicator, timeout=10)

        return self.driver.current_url

    def verify_logged_in(self) -> bool:
        """验证当前是否处于登录状态（Dashboard 元素可见）"""
        try:
            self.wait_for_visible(*self.dashboard_indicator, timeout=3)
            return True
        except Exception:
            return False
