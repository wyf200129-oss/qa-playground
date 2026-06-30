# 🔌 AI 接口自动化框架 — 关键字驱动 + Cursor 契约驱动全流程

> 基于 Requests + pytest + Allure 的接口自动化框架，搭配 Cursor .cursorrules 实现契约驱动的四阶段门禁工作流。实际应用于 ERP 进销存系统，覆盖销售、采购、仓库三模块 116 个接口、400+ 条用例。

---

## 🎯 AI 工作流：契约驱动四阶段门禁

> 这是本框架区别于普通接口自动化框架的核心——通过 **4 条规则 + 3 个 Skill**，从 OpenAPI 契约到可执行 pytest 用例全流程 AI 辅助，每个阶段须人工评审通过才能进入下一阶段。

### 四阶段流程

```
OpenAPI 契约读取
       ↓
  【A 试点骨架】    产出：1 条业务流程 class + TODO 占位（无完整 assert）
       ↓  人工评审：「结构合理？覆盖方向对？」
  【B 试点实现】    产出：试点流程完整断言，body → status 联合校验
       ↓  人工评审：「断言准确？契约字段覆盖全？」
  【C 全盘骨架】    产出：全部 flows + scenarios + META 标记（无完整 assert）
       ↓  人工评审：「全量范围正确？fiture 依赖合理？」
  【D 全盘实现】    产出：全量完整用例 + Allure 报告 + 二次 check 审计简报
       ↓
  失败修复闭环（①红→绿 ②维持红 ③xfail ④skip，须含 pytest 执行证据）
```

### 断言三原则

| 优先级 | 规则 | 说明 |
|:---|:---|:---|
| **1** | body 优先 | 先检查 body 字段/类型/语义，再与 status_code 联合校验 |
| **2** | 仅来自契约 | path/method/status/schema 全部来自 OpenAPI，禁止编造 |
| **3** | 二次 check 审计 | 逐 step 核对断言，status-only 须标注假绿风险 |

### 契约驱动的核心约束

```
✓ 先读 OpenAPI 再写用例        ✓ body → status 联合断言，禁止仅 assert status_code
✓ 四阶段不越级，评审门禁        ✓ fixture 链 ≤ 2 层，业务化命名
✓ parametrize 强制中文 ids      ✓ autouse 默认禁止，显式注入
✓ 数据脱敏 [ENV_*] 占位         ✓ 底层 api_keys 只读，修改须用户确认
✓ TODO 必须有 说明/来源/解析     ✓ 反向用例以绿色稳定通过为目标
```

---

## 🛠️ 规则与 Skill 明细

### 4 条 Cursor Rules

| 规则 | 职责 | 核心要点 |
|:---|:---|:---|
| `接口自动化-pytest骨架与实现` | 四阶段执行纪律 | A试点→B实现→C全盘→D全盘，禁止跳过评审写满断言 |
| `接口用例生成-契约优先` | 输入约束 | 先读 OpenAPI，path/method/status 全来自契约，禁止编造 |
| `接口用例生成-落盘路径` | 产物管理 | 用例表→`接口用例集/`，数据→`接口数据集/`，简报→`接口用例简报集/` |
| `pytest-fixture与用例实现` | 代码规范 | fixture≤2层、function scope、中文ids、禁止autouse |

### 3 个 Skills

| Skill | 触发 | 输出 |
|:---|:---|:---|
| `测试用例生成/接口` | 从契约生成 Markdown 用例表 | 正反向用例表 + 字段对契约验证 |
| `pytest-fixture与用例实现` | 生成/重构 fixture + 用例代码 | 合规的 conftest + test_*.py |
| `pytest失败修复闭环` | pytest 执行后有失败用例 | 按四方式修复（红→绿 / xfail / skip），每条含 pytest 证据 |

---

## 📂 目录结构

```
api-keyword/
├── api_client.py                ← 核心：ApiClient 关键字驱动类
├── conftest.py                  ← pytest session 级 fixtures
├── conf/
│   ├── server.ini               ← 多环境配置（Test/Dev/Staging）
│   └── config_loader.py         ← ini + YAML 读写工具
├── test_cases/
│   ├── conftest.py              ← pytest Fixture（api / set_env / clear_token）
│   └── test_erp_user.py         ← 测试用例：登录 → token 提取 → 用户信息断言
├── test_data/
│   ├── erp_login.yaml           ← 登录 + 用户信息 测试数据
│   └── erp_user_balance.yaml    ← 用户信息 + 充值 测试数据
└── requirements.txt             ← Python 依赖
```

---

## 🧠 设计亮点

| 特性 | 说明 |
|:---|:---|
| **关键字驱动** | YAML 定义用例数据 → `api.request(**data)` 执行，数据与代码分离 |
| **四阶段门禁** | A→B→C→D 逐级评审，禁止越过人工确认批量产出 |
| **契约优先** | body+status 联合断言，杜绝仅 `assert status_code` 的假绿 |
| **环境切换** | `@pytest.mark.parametrize('set_env', ['Test_Env'], indirect=True)` 一行切换 |
| **Token 自动注入** | 登录后 token 写入 ini，后续请求自动带 `Authorization` 头 |
| **JSONPath 提取** | `api.get_text(res.json(), 'token')` 支持 `$..key` 递归搜索 |
| **fixture 治理** | ≤2层、function scope、业务化命名、中文 ids |
| **失败修复闭环** | 红→绿 / xfail / skip 四方式，每条含 pytest 证据 |
| **Allure 报告** | `@allure.epic/feature/story/step` 全链路标注 |

---

## 🔗 与 UI 自动化框架的关系

| 框架 | 目录 | 核心 | AI 工作流 |
|:---|:---|:---|:---|
| UI 端 | `ui-pom/` | Selenium POM + pytest + YAML | 截图驱动 12 步流水线 |
| 接口端 | `api-keyword/` | Requests 关键字驱动 + pytest | 契约驱动四阶段门禁 |

双端共享同一套设计理念：**数据驱动 + pytest + YAML + Cursor AI 流水线**。

---

## 🚀 快速开始

```bash
pip install -r requirements.txt

# 修改环境配置后运行
cd test_cases
pytest test_erp_user.py -sv

# 生成 Allure 报告
pytest test_erp_user.py -sv --alluredir=allure_data
allure serve allure_data
```
