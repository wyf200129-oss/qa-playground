"""
Chrome 浏览器启动选项配置。

覆盖项：
  - 页面最大化启动
  - 抑制控制台多余日志
  - GPU 加速禁用（避免部分机器黑屏）
  - SSL 证书错误忽略（测试环境常见）
"""

from selenium import webdriver


def browser_options() -> webdriver.ChromeOptions:
    """返回适用于测试环境的 ChromeOptions 实例"""
    options = webdriver.ChromeOptions()

    # 页面最大化
    options.add_argument('start-maximized')

    # 日志抑制
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.add_argument('--log-level=3')

    # 兼容性
    options.add_argument('--disable-gpu')
    options.add_argument('--ignore-certificate-errors')

    # 可选：无头模式（CI/CD 环境启用）
    # options.add_argument('--headless')

    return options
