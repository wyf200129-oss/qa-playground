from time import sleep

from selenium.common.exceptions import WebDriverException

from utils.element_repair import find_element_with_repair, is_element_error


class BasePage:
    IMPLICIT_WAIT = 10

    def __init__(self, driver, base_url=''):
        self.driver = driver
        self.base_url = base_url.rstrip('/')
        self.driver.implicitly_wait(self.IMPLICIT_WAIT)

    def open(self, url):
        self.driver.get(url)

    def open_path(self, path):
        self.open(f'{self.base_url}{path}')

    def locator(self, by, value, key=''):
        """
        定位单个元素；key 为定位器名称（如 delete_confirm），用于失败修复与缓存。
        """
        try:
            return find_element_with_repair(
                self.driver, self.__class__.__name__, key, by, value,
            )
        except WebDriverException:
            raise

    def input(self, by, value, txt, key=''):
        """定位元素并输入文本。"""
        self.locator(by, value, key=key).send_keys(txt)

    def click(self, by, value, key=''):
        """定位元素并点击。"""
        self.locator(by, value, key=key).click()

    def quit(self):
        self.driver.quit()

    def wait(self, time_):
        sleep(int(time_))

    def assert_text(self, expected, by, value, key=''):
        """断言元素文本是否匹配。"""
        reality = self.locator(by, value, key=key).text
        assert expected == reality, (
            f'预期结果为{expected}，实际结果为{reality}。\n{expected} != {reality}'
        )

    def click_close(self, by, value):
        """关闭可选弹窗/通知；不存在时立即跳过，避免隐式等待空等。"""
        self.driver.implicitly_wait(0)
        try:
            for el in self.driver.find_elements(by, value):
                el.click()
        finally:
            self.driver.implicitly_wait(self.IMPLICIT_WAIT)

    def get_png(self):
        return self.driver.get_screenshot_as_png()

    @staticmethod
    def should_repair(exc):
        """判断异常是否属于元素定位失败（可触发修复流程）。"""
        return is_element_error(exc)
