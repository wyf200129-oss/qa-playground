"""
Chrome 浏览器启动选项配置。

覆盖项：
  - 页面最大化启动（非 CI 环境）
  - CI 环境自动启用无头模式（HEADLESS 或 CI 环境变量）
  - 抑制控制台多余日志
  - GPU 加速禁用（避免部分机器黑屏）
  - 容器环境兼容选项（no-sandbox / disable-dev-shm-usage）
  - SSL 证书错误忽略（测试环境常见）
"""

import os
from selenium import webdriver


def browser_options() -> webdriver.ChromeOptions:
    """返回适用于测试环境的 ChromeOptions 实例"""
    options = webdriver.ChromeOptions()

    # ── CI 环境：无头模式 + 固定窗口尺寸 ──
    if os.getenv('CI') or os.getenv('HEADLESS'):
        options.add_argument('--headless=new')
        options.add_argument('--window-size=1920,1080')
    else:
        # 本地开发：页面最大化
        options.add_argument('start-maximized')

    # 日志抑制
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.add_argument('--log-level=3')

    # 兼容性（容器环境必须）
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--ignore-certificate-errors')

    return options
