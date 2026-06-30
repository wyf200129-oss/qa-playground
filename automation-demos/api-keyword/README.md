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

## 🎯 Cursor .cursorrules 接口自动化工作流

搭配仓库根目录 `.cursor/rules/` 的 4 条接口自动化规则 + `.cursor/skills/` 的 3 个 Skill，实现**契约驱动的接口自动化全流程**：

### 4 条规则

| 规则 | 核心机制 |
|:---|:---|
| `接口自动化-pytest骨架与实现` | 四阶段门禁：A试点骨架→B试点实现→C全盘骨架→D全盘实现，禁止越级 |
| `接口用例生成-契约优先` | 先读OpenAPI契约再写用例，body+status联合断言，禁止编造 |
| `接口用例生成-落盘路径` | 用例文档/数据集/简报三类产物分目录落盘，与pytest代码分轨 |
| `pytest-fixture与用例实现` | fixture ≤2层、默认function scope、业务化命名、中文ids、禁止autouse |

### 3 个 Skill

| Skill | 功能 | 核心流程 |
|:---|:---|:---|
| `测试用例生成/接口` | Markdown用例表+契约验证 | 读契约→正反向用例→对字段→分类断言 |
| `pytest-fixture与用例实现` | fixture治理+用例生成 | 分析依赖→合并≤2层→命名业务化→配置中文ids |
| `pytest失败修复闭环` | 用例修复四方式 | ①红→绿 ②维持红 ③xfail ④skip；须含pytest证据 |

### 四阶段工作流总览

```
OpenAPI契约读取
       ↓
  A 试点骨架（1条流程class + TODO，无完整assert）
       ↓ 人工评审
  B 试点实现（试点流程完整断言，body+status联合）
       ↓ 人工评审
  C 全盘骨架（全部flows/scenarios + META，无完整assert）
       ↓ 人工评审
  D 全盘实现（全量完整用例 + Allure报告 + 二次check简报）
       ↓
  失败修复闭环（红→绿 / 维持红 / xfail / skip）
```

### 断言三原则

| 优先级 | 规则 | 说明 |
|:---|:---|:---|
| **1** | body → status | 先body字段/类型/语义，再联合status_code校验 |
| **2** | 仅来自契约 | path/method/status/responses/schema全来自OpenAPI，禁止编造 |
| **3** | 二次check审计 | 逐step核对断言模式，status-only须标注假绿风险 |

### 核心约束速记

```
✓ 契约优先，禁止编造    ✓ body+status联合断言
✓ 四阶段不越级          ✓ fixture ≤2层 + 业务命名
✓ parametrize中文ids    ✓ autouse默认禁止
✓ 数据脱敏[ENV_*]       ✓ 底层只读，修改须确认
```

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
