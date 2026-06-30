---
name: pytest-fixture-and-test-impl
description: >-
  Govern pytest fixture and test case implementation: max 2 fixture layers,
  function scope by default, autouse off unless user confirms, business-meanful names,
  preserve existing behavior. Use when creating or refactoring pytest tests,
  conftest.py, fixtures, scope, parametrize, ids, fixture 治理, or 测试用例实现.
---

# pytest fixture 与用例实现

> **前置**：遵守 Rule [`.cursor/rules/代码修改-先方案后执行.mdc`](../../rules/代码修改-先方案后执行.mdc)（先方案 → 用户确认 → 再改文件）。  
> **硬约束摘要**：Rule [`.cursor/rules/pytest-fixture与用例实现.mdc`](../../rules/pytest-fixture与用例实现.mdc)。

## 何时启用

- 新建或重构 **pytest 测试代码**、`conftest.py`、fixture 依赖链
- 调整 fixture **scope**、合并/拆分 fixture、优化 parametrize
- 用户提到 fixture 治理、conftest 精简、测试结构优化

**不覆盖**：契约/PRD **用例文档**生成（见 [测试用例生成](../测试用例生成/SKILL.md)）；**阶段 A 骨架**（见 [接口自动化实现](../接口自动化实现/SKILL.md)）；纯 traceback 排错（见 [代码调试与修改](../代码调试与修改/SKILL.md)）。

## 与接口自动化实现的分工

| 阶段 | Skill | 典型产出 |
|------|-------|----------|
| 用例文档 | [测试用例生成/接口](../测试用例生成/接口/SKILL.md) | cases.md + 接口数据集 yaml |
| 代码骨架（A） | [接口自动化实现](../接口自动化实现/SKILL.md) | test_*.py 请求 + TODO |
| 代码实现（B） | 接口自动化实现 + **本 Skill** | 补全 assert/fixture；遵守本文 fixture 约束 |

阶段 B 补全 fixture/断言时，**须** 读本 Skill 全文；阶段 A 仅读 fixture 链 ≤2 层与中文 ids 摘要即可。

## 方案阶段输出模板

生成或重构代码前，须先输出：

```text
1. 目标：{新建 / 重构什么}
2. 现状 fixture 链：{test ← A ← B，层数 N}
3. Scope 决策：{各 fixture 的 scope 及理由；默认 function}
4. 命名对照：{旧名 → 新名（若有），业务含义}
5. Parametrize ids：{每组参数的中文 id 及对应数据特征}
6. autouse 决策：{默认否；若拟用 autouse=True，须说明理由并等待用户确认}
7. 行为保留：{哪些断言/参数/场景必须不变}
8. 关联文件：{预计改动的路径}
9. 验证：{pytest 命令}
```

等待用户确认后再改文件。

---

## 1. Fixture 层数 ≤ 2

### 如何计数

从 **测试函数**（或 `@pytest.mark.parametrize` 包裹的测试）出发，沿 fixture **参数依赖**向下数 `@pytest.fixture` 层数：

```text
test_create_order(logged_in_user)           → 1 层 ✅
test_pay(order_ctx, mall_api_client)      → 2 层 ✅（两个并列依赖各算 1 层）
test_x(a) 且 a 依赖 b                       → 2 层 ✅（test ← a ← b）
test_x(a) 且 a→b→c                          → 3 层 ❌
```

并列依赖（测试函数同时注入多个 fixture）**不叠加**层数；**链式依赖**才叠加。

### 超过 2 层时

| 手段 | 适用 |
|------|------|
| 合并相邻 fixture | 中间层仅被单一下游使用 |
| 内联一次性 setup | 仅一个用例使用的薄封装 |
| 提取普通函数 | 无 pytest 生命周期需求时，不用 fixture |
| 拆测试文件 | 不同业务域共用链过深 |

**禁止**：为「看起来专业」增加 `base → mixin → context → helper` 式抽象。

---

## 2. Scope 默认 function

### 默认值

- 不写 `scope` 即 **function**（每用例隔离）。
- 新建 fixture **不得** 默认写 `session` 或 `autouse=True`。

### Scope 选型

| scope | 何时考虑 |
|-------|----------|
| **function**（默认） | 被测状态、登录态、DB 记录、mock 需用例间隔离 |
| **class** | 同一 TestClass 内多方法共享昂贵只读 setup |
| **module** | 单文件内只读、创建成本高（如加载大配置、启动本地 stub） |
| **session** | 全局只读、进程级一次初始化（DB 连接池、全量 env）；**慎用** |

### 非 function scope 须书面说明

方案中须包含：

1. **共享资源**是什么  
2. **创建成本**（时间/IO/外部依赖）  
3. **为何 function（或更低 scope）不够**  
4. **隔离风险**与 teardown/yield 清理策略  

理由不充分时，**建议降级**：优先 `class` → `module`，最后才 `session`。

---

## autouse 默认关闭（强制）

`autouse=True` 会在 **未显式声明** 的情况下自动注入 fixture，易造成：
- 无关用例被隐式修改环境（flaky、难复现）
- traceback 中 fixture 链不直观，排错成本上升

### 默认策略

| 策略 | 要求 |
|------|------|
| **默认** | **禁止** `autouse=True`；用测试函数参数 **显式注入** fixture |
| **确需 autouse** | **先方案说明 → 用户确认 → 再写代码**（遵守 Rule §7） |

### 方案中须说明（拟用 autouse 时）

1. **影响范围**：哪些目录/模块/用例会被自动影响  
2. **为何不能显式注入**：例如插件级 hook 约束（仍须论证）  
3. **隔离与排查**：如何定位 autouse 带来的副作用  
4. **替代方案**：是否可用显式 fixture / 普通函数 / `pytestmark` 替代  

**未经用户明确确认，不得生成或合入 `autouse=True` 代码。**

### 反例

```python
# ❌ 禁止：未获确认默认 autouse，全局改环境
@pytest.fixture(autouse=True)
def reset_env():
    os.environ["ENV"] = "test"

# ✅ 推荐：显式注入，作用域清晰
def test_login(blackcore_api_client, clear_jwt_token_after_test):
    ...
```

---

## 3. 命名体现业务

fixture 名 = **业务域 + 对象/角色 + 必要状态**。

| ✅ 推荐 | ❌ 避免 |
|---------|---------|
| `logged_in_mall_user` | `user`、`setup_user` |
| `mall_admin_token` | `token`、`auth` |
| `order_pending_payload` | `data`、`payload` |
| `expired_jwt_headers` | `headers`、`context` |
| `blackcore_api_client` | `client`、`helper` |

---

## 4. Parametrize 必须提供业务化 ids

使用 `@pytest.mark.parametrize` 读取/驱动数据时，**必须** 显式提供 `ids` 参数（或通过 `pytest.param(..., id=...)` 逐条指定）。

### 目标

失败输出中应能 **一眼看出**：哪条业务场景、哪类数据出了问题，无需回查参数表或数下标。

### 命名要求

1. **关联业务**：说明测的是什么场景（登录、下单、权限、边界等）。
2. **关联数据**：点出关键差异（空值、过期、超限、非法枚举等）。
3. **优先中文**：团队可读性优先，例如 `缺少Authorization头`、`订单金额为负`。
4. **长度适中**：一条 id 说清场景即可，不必写整段用例描述。

### 正反例

| ✅ 推荐（中文） | ❌ 禁止 |
|----------------|---------|
| `有效JWT登录` | `0`、`1`、`2` |
| `Token已过期` | `case1`、`case2` |
| `缺少Authorization头` | `test_1`、`data3` |
| `订单金额为负` | `invalid`、`error` |
| `商品ID不存在` | `token_test_01` |

### 代码示例

```python
@pytest.mark.parametrize(
    "headers,expected_status",
    [
        pytest.param({"Authorization": "Bearer valid"}, 200, id="有效JWT登录"),
        pytest.param({"Authorization": "Bearer expired"}, 401, id="Token已过期"),
        pytest.param({}, 401, id="缺少Authorization头"),
    ],
)
def test_get_profile(headers, expected_status):
    ...
```

多参数组合时，id 应概括 **该组数据的业务含义**，而非罗列字段名：

```python
# ✅
ids=["正常下单_库存充足", "下单失败_库存不足", "下单失败_金额为负"]

# ❌
ids=["case1", "case2", "case3"]
```

### 与 YAML/外部数据对齐

从 YAML/CSV 驱动时，约定 **一行数据 ↔ 一个业务 id**：

- YAML 每组须含 **`场景`** 字段（ids 说明，优先中文）；可选 `case_id` 追溯用例编号。
- 生成 pytest 用数据时，见 [测试数据生成](../测试数据生成/SKILL.md)「pytest 参数化 YAML」与 Rule [测试数据生成-pytest-yaml](../../rules/测试数据生成-pytest-yaml.mdc)。
- 避免 pytest 自动生成的 `[0]`、`[1]`、`[data0]`。

### conftest 必须配置中文 ids 支持

pytest 默认会将非 ASCII 的 parametrize ids 转义为 `\uXXXX`，导致失败日志难以阅读。**生成或新建测试目录时，须在 `conftest.py` 中加入以下 hook**（三者为一套，一并保留）：

```python
def pytest_addoption(parser):
    parser.addini(
        "disable_test_id_escaping_and_forfeit_all_rights_to_community_support",
        type="bool",
        default="true",
        help="为 true 时保留 parametrize ids 中的中文等非 ASCII 字符原样显示",
    )


def pytest_collection_modifyitems(items):
    """兜底：将仍被转义的 unicode 还原为可读中文。"""
    for item in items:
        if "\\u" not in item.name and "\\u" not in item.nodeid:
            continue
        item.name = item.name.encode("utf-8").decode("unicode_escape")
        item._nodeid = item.nodeid.encode("utf-8").decode("unicode_escape")


def pytest_make_parametrize_id(config, val, argname):
    """YAML 数据行未显式传 ids 时，从 dict 提取中文 id。"""
    if isinstance(val, dict):
        for key in ("case_id", "场景", "id", "用例名称"):
            candidate = val.get(key)
            if candidate:
                return str(candidate)
    return None
```

参考实现：[`第八节课/interface_pytest/test_cases/conftest.py`](../../../第八节课/interface_pytest/test_cases/conftest.py)。

---

## 5. 保留原有用例行为

重构 **只允许** 改结构，**禁止** 改语义：

| ✅ 允许 | ❌ 禁止 |
|---------|---------|
| 合并/拆分 fixture | 修改断言预期值或比较方式 |
| 调整 scope（有理由） | 修改请求 path、method、body 语义 |
| 重命名（同步所有引用） | 删除原覆盖的异常/边界场景 |
| 提取重复 setup 为函数/fixture | 「顺手」改业务逻辑或跳过失败用例 |

diff 说明须包含 **行为等价**：「原：登录后下单断言 201 → 现：仍登录同一账号、同一 payload、仍断言 201」。

---

## 工作流

```
- [ ] 阅读现有测试与 conftest，画出 fixture 链
- [ ] 按模板输出方案（层数、scope、命名、parametrize ids、行为保留）
- [ ] 等待用户确认
- [ ] 最小范围修改，匹配项目现有风格
- [ ] 给出 pytest 验证命令
- [ ] 执行文末自检清单
```

---

## 生成后自检

- [ ] fixture 依赖链 ≤ 2 层（链式）
- [ ] 非 function scope 已在方案中说明理由
- [ ] 无泛化命名（setup/context/helper 等）
- [ ] parametrize 已显式提供 ids，且为业务化中文（非数字/编号）
- [ ] conftest 已配置中文 ids 显示 hook（新建测试目录时）
- [ ] 原用例断言、参数、覆盖场景未变
- [ ] **未使用 autouse=True**（若使用，方案已说明且用户已确认）
- [ ] 未滥用 session scope
- [ ] 已先方案、用户确认后再改文件

---

## 关联资源

| 资源 | 路径 |
|------|------|
| 硬约束 Rule | `.cursor/rules/pytest-fixture与用例实现.mdc` |
| 修改流程 Rule | `.cursor/rules/代码修改-先方案后执行.mdc` |
| Traceback / fixture 链 | `第七节课/第07节-Traceback与fixture链与基于事实排错.md` |
| Scope / parametrize 讲义 | `第八节课/第08节-Parametrize与fixture治理.md` |
| 代码调试与修改 | `.cursor/skills/代码调试与修改/SKILL.md` |
| pytest fixture 与用例实现 | `.cursor/skills/pytest-fixture与用例实现/SKILL.md` |
| **接口自动化实现（两阶段工作流）** | `.cursor/skills/接口自动化实现/SKILL.md` |
| 测试数据生成 | `.cursor/skills/测试数据生成/SKILL.md` |
