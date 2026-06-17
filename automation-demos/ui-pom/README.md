# POM + YAML UI 自动化框架 Demo

> 基于 Page Object Model 设计模式 + YAML 数据驱动的 Web UI 自动化框架
> 实际应用于 ERP 进销存系统，提升回归测试效率

---

## 🏗️ 架构设计

```
project/
├── base/
│   └── base_page.py          # 封装 Selenium 基础操作
├── pages/
│   ├── login_page.py          # 登录页对象
│   ├── purchase_page.py       # 采购单页对象
│   └── sales_page.py          # 销售单页对象
├── data/
│   └── test_data.yaml         # YAML 数据驱动
├── tests/
│   ├── test_purchase.py       # 采购模块用例
│   └── test_sales.py          # 销售模块用例
├── conftest.py                # pytest 公共 fixture
└── pytest.ini                 # pytest 配置
```

## 🎯 设计思路

### 1. POM 分层 —— 页面对象与用例分离

每个页面封装为一个类，页面元素定位与操作方法集中管理。页面变化时只需改一处。

```python
# pages/purchase_page.py
class PurchasePage(BasePage):
    """采购单页面对象"""

    # 元素定位（集中管理）
    BTN_CREATE = (By.XPATH, "//button[contains(text(), '新建采购单')]")
    INPUT_SKU = (By.ID, "sku-search")
    BTN_ADD_TO_CART = (By.CSS_SELECTOR, ".add-to-cart")

    def create_purchase_order(self, sku, quantity):
        """创建采购单 —— 业务方法"""
        self.click(self.BTN_CREATE)
        self.input(self.INPUT_SKU, sku)
        self.input(self.INPUT_QTY, quantity)
        self.click(self.BTN_SUBMIT)
        return self.get_order_id()
```

### 2. BasePage 封装 —— 统一异常处理与等待

```python
# base/base_page.py
class BasePage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    def find(self, locator):
        """带显式等待的元素查找"""
        return self.wait.until(EC.presence_of_element_located(locator))

    def click(self, locator):
        self.find(locator).click()

    def input(self, locator, text):
        el = self.find(locator)
        el.clear()
        el.send_keys(text)
```

### 3. YAML 数据驱动 —— 测试数据与代码分离

```yaml
# data/test_data.yaml
purchase_order:
  normal:
    sku: "SKU-001"
    quantity: 100
    supplier: "供应商A"
  multi_sku:
    items:
      - { sku: "SKU-001", quantity: 50 }
      - { sku: "SKU-002", quantity: 30 }
  boundary:
    min_qty: 1
    max_qty: 99999
```

用例通过 `@pytest.mark.parametrize` 读取 YAML 数据，一份代码跑多组数据。

### 4. pytest + Jenkins CI —— 接入流水线

```ini
# pytest.ini
[pytest]
testpaths = tests
python_files = test_*.py
addopts = -v -s --html=report.html --self-contained-html
```

配置 Jenkins 定时任务，每日/每次发布前自动执行回归用例，生成 HTML 报告。

---

## 📊 实际效果

- 采购/销售模块高频流程全部实现自动化
- 与接口自动化联动形成「接口冒烟 → UI 核心链路」回归策略
- 纳入 Jenkins 定时执行，减少人工回归时间

---

## 🚀 快速启动

```bash
# 1. 安装依赖
pip install selenium pytest pyyaml pytest-html

# 2. 下载对应版本的 ChromeDriver

# 3. 运行用例
pytest tests/test_purchase.py -v

# 4. 查看报告
open report.html
```

---

## 📝 代码说明

本 demo 中的代码为脱敏后的框架骨架，展示了：
- POM 设计模式和页面对象分层
- BasePage 通用封装思路
- YAML 数据驱动方案
- pytest 与 Jenkins CI 集成方式

完整实际代码因涉及公司业务逻辑已脱敏，如需交流框架设计细节欢迎联系。
