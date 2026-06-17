# POM + YAML 数据驱动 UI 自动化框架 — ERP 供应商管理实战 Demo

> 基于 Page Object Model + pytest + YAML 数据驱动的 Web UI 自动化框架
> 实际应用于 ERP 系统供应商管理模块，演示从登录到业务操作的完整自动化链路

---

## 🏗️ 目录结构

```
ui-pom/
├── conftest.py                    # pytest fixtures（driver + test_data + logged_in）
├── requirements.txt               # Python 依赖
├── base_page/
│   └── basepage.py               # Selenium 操作封装 + 显式等待 + ddddocr 验证码识别
├── page_object/
│   ├── erp_login_page.py         # ERP 登录页（验证码自动识别）
│   └── erp_vendor_page.py        # ERP 供应商管理页（新增 + 查询）
├── test_cases/
│   └── test_erp_vendor.py        # 测试用例（pytest）
├── test_data/
│   └── erp_vendor.yaml           # 测试数据（敏感信息已脱敏）
└── utils/
    └── browser_options.py        # Chrome 启动配置
```

---

## 🎯 框架亮点

### 1. POM 三层分离

| 层 | 职责 | 示例 |
|----|------|------|
| `base_page/` | Selenium 原子操作封装 | 定位、输入、点击、断言、显式等待 |
| `page_object/` | 页面业务流程 | 登录流程、新增供应商、查询 |
| `test_cases/` | 用例编排与断言 | 正向登录、新增供应商验证 |

### 2. 显式等待替代 sleep

```python
# ❌ 之前：硬编码 sleep(15)，慢且不稳定
self.wait(15)

# ✅ 现在：WebDriverWait 条件触发，又快又稳
self.wait_for_url_change(self.url, timeout=20)       # 登录后 URL 跳转
self.wait_for_invisible(*self.vendor_modal, timeout=10)  # 弹窗关闭
```

### 3. 验证码自动识别（ddddocr）

```python
def get_code(self, by, value):
    img_bytes = self.locator(by, value).screenshot_as_png
    return ddddocr.DdddOcr().classification(img_bytes)
```

### 4. YAML 数据驱动 + pytest

```yaml
# test_data/erp_vendor.yaml
login:
  user: "[ERP测试账号]"
  pwd:  "[ERP测试密码]"
vendor:
  name: "[供应商测试名称]"
  tele: "[供应商测试电话]"
```

Python 侧通过 `conftest.py` 统一加载，测试只关心业务逻辑：

```python
def test_login_success(self, login_page, test_data):
    url = login_page.login(test_data['login']['user'], test_data['login']['pwd'])
    assert '/user/login' not in url
    assert login_page.verify_logged_in()
```

### 5. webdriver-manager 自动管理驱动

无需手动下载 chromedriver，`webdriver-manager` 自动匹配 Chrome 版本下载：

```python
from webdriver_manager.chrome import ChromeDriverManager
service = Service(ChromeDriverManager().install())
```

---

## 🚀 快速启动

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 修改 test_data/erp_vendor.yaml 中的占位符为真实测试数据

# 3. 运行全部用例
pytest test_cases/ -v

# 4. 仅运行登录测试
pytest test_cases/test_erp_vendor.py::TestErpLogin -v
```

---

## 📊 实际应用效果

- ERP 供应商模块新增/查询高频流程实现 UI 自动化
- 与接口自动化联动形成「接口冒烟 → UI 核心链路」回归策略
- 验证码自动识别 + 显式等待大幅降低用例执行时间和假阳性

---

## 🔐 脱敏说明

本 demo 中所有敏感信息已替换为占位符（`[ERP_BASE_URL]`、`[ERP测试账号]` 等），运行前请替换为真实的测试环境数据。

---
