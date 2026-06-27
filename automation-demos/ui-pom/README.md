# POM + YAML + Cursor 截图驱动 UI 自动化框架

> 基于 Page Object Model + pytest + YAML 数据驱动的 Web UI 自动化框架，搭配 Cursor .cursorrules 实现截图一键生成全流程自动化。实际应用于 ERP 销售、采购、仓库三大模块（12 类核心单据），累计 200+ 条 UI 自动化用例。

---

## 🏗️ 目录结构

```
ui-pom/
├── conftest.py                    # pytest fixtures（driver + test_data + page 注入）
├── pytest.ini                     # pytest 配置文件
├── requirements.txt               # Python 依赖
├── base_page/
│   ├── basepage.py               # Selenium 操作封装 + 显式等待 + ddddocr 验证码识别
│   └── __init__.py
├── page_object/
│   ├── login_page.py             # 登录页（验证码自动识别）
│   ├── depot_page.py             # 仓库管理页（出入库、调拨）
│   ├── sale_order_page.py        # 销售订单页
│   ├── person_page.py            # 人员管理页
│   └── vendor_page.py            # 供应商管理页
├── test_cases/
│   ├── conftest.py               # 用例级 fixtures
│   ├── test_depot.py             # 仓库模块测试
│   ├── test_sale_order.py        # 销售订单测试
│   ├── test_person.py            # 人员管理测试
│   ├── test_erp.py               # 综合业务流程测试
│   └── test_mock_ci.py           # 全流程 Mock CI 演示（不依赖后台）
├── test_data/
│   ├── login.yaml                # 登录数据
│   ├── depot.yaml                # 仓库数据
│   ├── sale_order.yaml           # 销售订单数据
│   ├── person.yaml               # 人员数据
│   ├── add.yaml                  # 新增操作通用数据
│   └── validate/                 # 自检验证数据（与正式数据隔离）
│       ├── depot.yaml
│       └── person.yaml
├── conf/
│   ├── options.py                # 命令行参数解析
│   ├── serve_conf.py             # 服务端配置
│   ├── server_conf.ini           # 环境连接信息
│   └── yaml_conf.py              # YAML 文件加载与解析
├── scripts/
│   ├── validate_page_object.py   # 页面对象自检脚本
│   └── bump_test_data.py         # 幂等递增测试数据唯一字段
└── utils/
    ├── browser.py                # Chrome 驱动管理
    ├── element_repair.py         # 元素定位自动修复
    ├── locator_strategy.py       # 定位策略（id>name>css>xpath）
    └── locator_failure_cache.py  # 定位失败缓存记录
```

---

## 🎯 Cursor .cursorrules 截图驱动流水线

搭配仓库根目录 `.cursor/rules/` 的 5 条规则 + `.cursor/skills/pom-screenshot-pipeline/` Skill，实现**截图 → 页面对象 → 自检 → 用例 → pytest → Allure → 幂等**一键式自动化：

| 规则 | 核心机制 |
|:---|:---|
| `pom-page-object` | 页面对象编写规范：继承 BasePage、定位器优先级 id>name>css>xpath |
| `pom-locator-repair` | 定位器自愈：失败→分析DOM→替换定位器→重试（≤3次），超限等待人工 |
| `pom-pipeline-gate` | 12 步流水线门禁：一步失败即停，禁止静默跳过 |
| `pom-test-data` | 数据双分离：`validate/` 自检数据与正式数据独立，pytest 后幂等递增 |
| `pom-todo-progress` | Todo 驱动：全流程任务面板可见，每步 `in_progress → completed` |

---

## 🎯 框架亮点

### 1. POM 多层分离

| 层 | 职责 | 示例 |
|----|------|------|
| `base_page/` | Selenium 原子操作封装 | 定位、输入、点击、断言、显式等待 |
| `page_object/` | 页面业务流程 | 登录 → 新增供应商 → 销售出库 → 库存查询 |
| `test_cases/` | 用例编排与 Pytest 断言 | 正向流程 + 异常校验 + 数据一致性 |
| `test_data/` | YAML 数据驱动 | 测试数据与代码完全分离 |
| `conf/` | 配置管理 | Server 连接、YAML 加载、命令行参数 |
| `utils/` | 工具类 | 元素修复、定位策略、浏览器封装 |

### 2. 显式等待替代 sleep

```python
# ❌ 之前：硬编码 sleep(15)，慢且不稳定
self.wait(15)

# ✅ 现在：WebDriverWait 条件触发，又快又稳
self.wait_for_url_change(self.url, timeout=20)           # 登录后 URL 跳转
self.wait_for_invisible(*self.vendor_modal, timeout=10)    # 弹窗关闭
```

### 3. 验证码自动识别（ddddocr）

```python
def get_code(self, by, value):
    img_bytes = self.locator(by, value).screenshot_as_png
    return ddddocr.DdddOcr().classification(img_bytes)
```

### 4. YAML 数据驱动 + 双文件分离

```yaml
# test_data/login.yaml（正式数据）
login:
  user: "[ERP测试账号]"
  pwd:  "[ERP测试密码]"

# test_data/validate/person.yaml（自检验证数据，独立于正式数据）
person:
  name: "验证人员_001"
  phone: "13800138001"
```

### 5. 定位器自愈修复

```python
# 元素定位失败时自动尝试 id → name → css → xpath 优先级替换
from utils.locator_strategy import LocatorStrategy
from utils.element_repair import repair_locator
from utils.locator_failure_cache import LocatorFailureCache

# ≤3 次重试，超限写入缓存并等待人工确认
```

### 6. 幂等数据递增

```python
# pytest 跑完后自动递增 YAML 中唯一字段（编号、名称等），确保下次运行不冲突
python scripts/bump_test_data.py
```

### 7. webdriver-manager 自动管理驱动

```python
from webdriver_manager.chrome import ChromeDriverManager
service = Service(ChromeDriverManager().install())
```

---

## 🚀 快速启动

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 修改 test_data/ 中 YAML 文件的占位符为真实测试数据

# 3. 运行全部用例
pytest test_cases/ -v --alluredir=allure_data

# 4. 生成 Allure 报告
allure generate allure_data -o allure_report

# 5. 仅运行仓库模块测试
pytest test_cases/test_depot.py -v

# 6. 运行全流程 Mock CI 演示（不依赖后台）
pytest test_cases/test_mock_ci.py -v
```

---

## 📊 实际应用效果

- 覆盖 ERP 采购/销售/仓库三模块 12 类核心单据，累计编写 **200+ 条 UI 自动化用例**
- 与接口自动化联动形成「接口冒烟 → UI 核心链路」回归策略，接入 Jenkins 定时回归
- 验证码自动识别 + 显式等待大幅降低用例执行时间和假阳性
- Cursor 截图驱动流水线实现"一张截图→完整可运行用例"，大幅缩短 UI 自动化开发周期
- 定位器自愈机制减少页面改版后的维护成本

---

## 🔐 脱敏说明

本仓库所有敏感信息已替换为占位符（`[ERP_BASE_URL]`、`[ERP测试账号]` 等），运行前请替换为真实的测试环境数据。
