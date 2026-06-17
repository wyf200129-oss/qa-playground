"""
BasePage 基类 —— Selenium 操作行为统一封装。

职责：
  - 元素定位、输入、点击、断言
  - 显式等待策略（替代 time.sleep）
  - 验证码自动识别（ddddocr）

设计原则：
  - 所有 Page Object 继承此类，避免重复封装
  - driver 对象由外部（pytest fixture）注入，保证单次测试链路复用同一个浏览器实例
"""

import ddddocr
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class BasePage:
    """Selenium 页面操作基类"""

    def __init__(self, driver: WebDriver):
        self.driver = driver
        self.driver.implicitly_wait(5)

    # ── 基础操作 ──────────────────────────────────

    def open(self, url: str) -> None:
        """访问指定 URL"""
        self.driver.get(url)

    def locator(self, by: str, value: str) -> WebElement:
        """定位单个元素"""
        return self.driver.find_element(by, value)

    def input(self, by: str, value: str, txt: str) -> None:
        """输入文本（自动清空后填入）"""
        el = self.locator(by, value)
        el.clear()
        el.send_keys(txt)

    def click(self, by: str, value: str) -> None:
        """点击元素"""
        self.locator(by, value).click()

    def quit(self) -> None:
        """关闭浏览器"""
        self.driver.quit()

    # ── 等待策略 ──────────────────────────────────

    def wait_for_visible(self, by: str, value: str, timeout: int = 10) -> WebElement:
        """显式等待元素可见"""
        return WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_element_located((by, value))
        )

    def wait_for_invisible(self, by: str, value: str, timeout: int = 10) -> bool:
        """显式等待元素不可见（如弹窗关闭）"""
        return WebDriverWait(self.driver, timeout).until(
            EC.invisibility_of_element_located((by, value))
        )

    def wait_for_url_change(self, old_url: str, timeout: int = 20) -> bool:
        """等待 URL 变更（常用于登录后跳转验证）"""
        return WebDriverWait(self.driver, timeout).until(
            lambda d: d.current_url != old_url
        )

    # ── 断言 ──────────────────────────────────────

    def assert_text(self, expected: str, by: str, value: str) -> None:
        """断言元素文本与预期一致"""
        reality = self.locator(by, value).text
        assert expected == reality, (
            f"文本断言失败：预期「{expected}」，实际「{reality}」"
        )

    def assert_element_present(self, by: str, value: str) -> None:
        """断言元素存在于页面"""
        try:
            self.wait_for_visible(by, value, timeout=5)
        except Exception:
            raise AssertionError(f"元素未找到：{by}={value}")

    # ── 验证码识别 ────────────────────────────────

    def get_code(self, by: str, value: str) -> str:
        """截图验证码图片并用 ddddocr 识别返回文本"""
        img_bytes = self.locator(by, value).screenshot_as_png
        return ddddocr.DdddOcr().classification(img_bytes)
