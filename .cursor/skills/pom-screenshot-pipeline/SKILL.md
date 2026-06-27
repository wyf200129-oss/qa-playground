---
name: pom-screenshot-pipeline
description: >-
  POM 截图一键工作流：单张截图 → 页面对象 → 关联已有代码(conftest/login/BasePage) → 自检 → 用例/数据 → pytest → Allure → 幂等。
  执行前先 TodoWrite 拆解任务并实时更新进度。任一步失败即停。校验/正式数据分离。
  Use when generating page objects from screenshots, ERP UI automation, POM tests, 页面对象/测试用例/测试数据生成, or 截图驱动自动化.
---

# POM 截图驱动全流程

## 触发场景

用户提供 **一张页面截图**（可附业务流程说明），要求实现完整自动化测试时，**必须**按本 Skill 执行。  
目标：**一张截图 → 一个页面对象 → 与已有工程代码关联 → 可运行的业务流程自动化**。

## 执行模式：Todo 驱动（最高优先级）

> **用户通过 Cursor 任务面板查看进度，Agent 不得静默连跑后一次性汇报。**

### 强制节奏

1. **第一个工具调用**：`TodoWrite(merge=false)` 创建下方 12 项清单
2. **每一阶段**：
   - `TodoWrite(merge=true)` → 该项 `in_progress`
   - **仅执行该项工作**（写文件 / 跑命令 / 分析）
   - `TodoWrite(merge=true)` → 该项 `completed`
   - 再进入下一项
3. **禁止**：连续完成多阶段后批量更新 Todo；禁止跳过 `in_progress`

### 标准 Todo 列表（按截图新建页面时使用）

| id | 内容 |
|----|------|
| `analyze` | 分析截图：页面名称、PATH、元素、业务流程 |
| `code-scan` | 扫描已有代码：login_page / conftest / 同类 page_object 模板 |
| `page-object` | 生成 `page_object/{module}_page.py` |
| `validate-data` | 生成 `test_data/validate/{module}.yaml` |
| `registry` | 在 `scripts/validate_page_object.py` 的 `PAGE_REGISTRY` 注册映射 |
| `self-check` | 执行 `validate_page_object.py` 页面对象自检 |
| `test-data` | 生成 `test_data/{module}.yaml`（与 validate 数据不同） |
| `fixture` | 在 `conftest.py` 注册 `{module}_page` fixture |
| `test-case` | 生成 `test_cases/test_{module}.py` |
| `pytest-run` | 执行 pytest 并确认 PASSED |
| `allure-report` | 生成 Allure HTML 报告 |
| `bump-data` | 执行 `bump_test_data.py` 递增唯一字段 |

**规则：**
- 同时只有一个任务为 `in_progress`
- 某步失败 → 该项 blocked / 保持 `in_progress`，**停止后续 Todo**，向用户展示报错
- **进度以 Todo 面板为准**；每步完成必须立即 `TodoWrite(merge=true)`，不得最后统一更新
- 修复定位失败时追加 `repair-diagnose` / `repair-attempt-1~3` 子 Todo（见 `pom-locator-repair.mdc`）

---

## 一张截图 → 完整自动化（工作流总览）

> **执行粒度**：下方为逻辑分组示意；实际须按上方 **12 个独立 Todo** 逐步推进，不得合并。

```
[用户截图]
    ↓
Todo: analyze → code-scan              ← 识别 PATH/元素；对齐已有代码
    ↓
Todo: page-object                      ← 生成页面对象
    ↓
Todo: validate-data → registry → self-check   ← 校验数据 + 注册 + 自检（失败即停）
    ↓
Todo: test-data → fixture → test-case         ← 正式数据 + conftest + 用例
    ↓
Todo: pytest-run                       ← 登录 → 业务方法 → 断言（失败即停）
    ↓
Todo: allure-report → bump-data        ← 报告 + 幂等递增
```

### 与已有代码的关联清单

| 已有代码 | 关联方式 |
|----------|----------|
| `base_page/basepage.py` | 页面对象继承 `BasePage` |
| `page_object/login_page.py` | 自检/pytest 通过 `login` fixture 或脚本内 `LoginPage.login()` |
| `test_cases/conftest.py` | 新增 `{module}_page` fixture；复用 `driver` / `serve` / `login` |
| `test_data/login.yaml` | 所有流程共用登录数据，`@pytest.mark.parametrize('login', ...)` |
| `conf/yaml_conf.py` | 用例与脚本通过 `read('test_data/...')` 读 YAML |
| `conf/serve_conf.py` + `server_conf.ini` | 环境 URL，`serve` fixture / `--env TEST_ENV` |
| `page_object/{同类}_page.py` | 参照定位器风格、方法命名、PATH 命名规则 |
| `scripts/validate_page_object.py` | 新页面注册 `PAGE_REGISTRY` |
| `AGENTS.md` | Allure 装饰器、异常截图、YAML 列表格式 |

---

## 流水线 5 步（任一步失败即停止）

```
Step 0 截图分析 → Step 1 页面对象 → Step 2 自检 → Step 3 用例/数据 → Step 4 pytest → Step 5 报告+幂等
```

**硬性约束：**
1. 页面对象生成后 **必须先跑 Step 2**，通过后才能进入 Step 3。
2. 任何环节报错 → **立即停止**，更新 Todo，展示失败步骤、traceback、截图路径。
3. **校验数据**（`test_data/validate/`）与 **正式测试数据**（`test_data/`）必须分文件、分内容。

---

## Step 0：截图分析 + 代码扫描（Todo: analyze / code-scan）

**从截图提取：** 页面名、菜单路径、列表/弹窗/工具栏元素、主业务流程。  
**从已有代码确认：** PATH、表单 id/placeholder、参照 `vendor_page.py` / `depot_page.py`。  
**输出：** 向用户说明 `{module}` 命名、PATH、主方法名，再进入 Step 1。

---

## Step 1：页面对象生成（Todo: page-object）

**输出：** `pytest_pom/page_object/{module}_page.py`

- 继承 `BasePage`，定义 `PATH`
- 定位器：id > name > css > xpath；禁止 `data-v-*`
- 每个 public 方法写函数级 docstring
- 封装截图涉及的 **完整业务流程方法**（如 `add_depot()`）

---

## Step 2：页面对象自检（Todo: validate-data / registry / self-check）

```bash
cd pytest_pom
python scripts/validate_page_object.py --page {module} --data test_data/validate/{module}.yaml
```

**前置：** `test_data/validate/{module}.yaml` + `PAGE_REGISTRY` 注册。  
**exit 0** → 进入 Step 3；**exit 1** → 停止，展示 `log/validate_{module}_error.png`。

---

## Step 3：测试数据 + 用例 + Fixture（Todo: test-data / fixture / test-case）

- `test_data/{module}.yaml` — 正式数据，唯一字段与 validate 不同
- `conftest.py` — `{module}_page` fixture
- `test_cases/test_{module}.py` — 登录 → 业务 → 断言；Allure 装饰器齐全

---

## Step 4：执行用例（Todo: pytest-run）

```bash
pytest test_cases/test_{module}.py -s -v
```

PASSED → Step 5；FAILED → 停止。

**pytest 元素定位失败：** 见 `.cursor/rules/pom-locator-repair.mdc`（DOM 快照 → 失败缓存 → 最多 3 次修复）。

---

## Step 5：报告 + 幂等（Todo: allure-report / bump-data）

```bash
allure generate allure_data/ -o allure_report/ --clean
python scripts/bump_test_data.py --file test_data/{module}.yaml --fields {biz_key}.{unique_field} --strategy suffix
```

全部完成后汇总：文件清单、pytest 结果、报告路径、递增后的数据值。

---

## 进度同步要求（Todo 模式）

1. **任务开始前**：`TodoWrite(merge=false)` — 必须是首个工具调用
2. **每项开始**：`in_progress` → 只做该项 → `completed`
3. **失败时**：blocked，后续保持 `pending`，停止执行
4. **禁止静默执行**：不得在未更新 Todo 的情况下连续跑自检、pytest、报告
5. **全部完成**：附文件清单与报告路径（Todo 已全部 completed 后）

---

## 参考

- 项目架构：`AGENTS.md`
- 流水线门禁：`.cursor/rules/pom-pipeline-gate.mdc`
- Todo 进度：`.cursor/rules/pom-todo-progress.mdc`
- 测试数据：`.cursor/rules/pom-test-data.mdc`
- 元素修复：`.cursor/rules/pom-locator-repair.mdc`
- 详细模板：[reference.md](reference.md)
