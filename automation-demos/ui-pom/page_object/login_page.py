from base_page.basepage import BasePage


class LoginPage(BasePage):
    PATH = '/user/login'

    login_name = ('id', 'loginName')
    login_pwd = ('id', 'password')
    login_button = ('css selector', '.login-button')
    notice_close = ('xpath', '//*[@class="ant-notification-notice-close"]')

    def login(self, user, pwd, wait=2):
        self.open_path(self.PATH)
        self.click_close(*self.notice_close)
        self.input(*self.login_name, txt=user)
        self.input(*self.login_pwd, txt=pwd)
        self.click(*self.login_button)
        self.wait(wait)
