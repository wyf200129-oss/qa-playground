# 🔌 接口自动化测试框架 — 关键字驱动 + pytest + Allure

> 基于 Requests 封装的 ERP 接口自动化框架，支持环境一键切换、token 自动注入、JSONPath 数据提取、Allure 可视化报告。

---

## 📂 目录结构

```
api-keyword/
├── README.md                    ← 本文件
├── requirements.txt             ← Python 依赖
├── api_client.py                ← 核心：ApiClient 关键字驱动类
├── conf/
│   ├── server.ini               ← 多环境配置（Test/Dev/Staging）
│   └── config_loader.py         ← ini + YAML 读写工具
├── test_cases/
│   ├── conftest.py              ← pytest Fixture（api / set_env / clear_token）
│   └── test_erp_user.py         ← 测试用例：登录 → token 提取 → 用户信息断言
└── test_data/
    ├── erp_login.yaml           ← 登录 + 用户信息 测试数据
    └── erp_user_balance.yaml    ← 用户信息 + 充值 测试数据
```

---

## 🚀 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 修改环境配置
vi conf/server.ini   # 替换 [ERP_TEST_HOST] 等占位符

# 3. 修改测试数据
vi test_data/erp_login.yaml  # 替换账号密码占位符

# 4. 运行测试
cd test_cases
pytest test_erp_user.py -sv

# 5. 生成 Allure 报告
pytest test_erp_user.py -sv --alluredir=allure_data
allure serve allure_data
```

---

## 🧠 设计亮点

| 特性 | 说明 |
|------|------|
| **关键字驱动** | YAML 定义用例数据 → `api.request(**data)` 执行，数据与代码分离 |
| **环境切换** | `@pytest.mark.parametrize('set_env', ['Test_Env'], indirect=True)` 一行切换 |
| **Token 自动注入** | 登录后 token 写入 ini，后续请求自动带 `Authorization` 头 |
| **JSONPath 提取** | `api.get_text(res.json(), 'token')` 支持 `$..key` 递归搜索 |
| **Allure 报告** | `@allure.epic/feature/story/step` 全链路标注 |
| **自动清理** | `clear_token` fixture 在用例结束后自动清空缓存 |

---

## 🔗 与 UI 自动化框架的关系

| 框架 | 目录 | 说明 |
|------|------|------|
| UI 端 | `ui-pom/` | Selenium POM + pytest + YAML 数据驱动 |
| 接口端 | `api-keyword/` | Requests 关键字驱动 + pytest + ini 环境管理 |

两者共享同一套设计理念：**数据驱动 + pytest + YAML**，面试官可看到完整的双端自动化能力。

---

## 📝 用例执行流程示意

```
erp_login.yaml
    │
    ▼ test_login()
登录 → 提取 token → write_conf('data', 'token', token)
    │
    ▼ token 自动注入请求头
test_user_info() → assert username / role
    │
    ▼ clear_token fixture
token 清空 → 用例隔离
```
