"""
pytest 全局配置 —— fixtures 定义。

模块级 fixture（按需使用）：
  - driver        : module 级别浏览器实例
  - login_page    : 登录页对象
  - vendor_page   : 供应商管理页对象
  - depot_page    : 仓库管理页对象
  - sale_order_page : 销售订单页对象
  - person_page   : 人员管理页对象
  - login         : 预登录 fixture

详细 fixture 定义见 test_cases/conftest.py。
运行测试请从项目根目录或 test_cases/ 目录执行。
"""
