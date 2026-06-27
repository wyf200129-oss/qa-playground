# POM 流水线参考模板

## validate YAML 模板

`test_data/validate/depot.yaml`:

```yaml
-
  depot:
    name: 仓库Validate01
    address: 深圳市福田区
    warehousing: '0.1'
    truckage: '5'
    principal: test123
    sort: '99'
    remark: 页面对象自检数据
  wait: 3
```

## 正式 test YAML 模板

`test_data/depot.yaml`:

```yaml
-
  depot:
    name: 仓库Pom测试05
    address: 深圳市南山区
    warehousing: '0.5'
    truckage: '10'
    principal: test123
    sort: '1'
    remark: POM自动化测试仓库
  wait: 3
```

## validate_page_object.py 调用示例

```bash
python scripts/validate_page_object.py --page depot --data test_data/validate/depot.yaml
```

## bump 调用示例

```bash
# 将 depot.name 末尾数字 +1
python scripts/bump_test_data.py --file test_data/depot.yaml --fields depot.name --strategy suffix

# 追加时间戳
python scripts/bump_test_data.py --file test_data/depot.yaml --fields depot.name --strategy timestamp
```

## 报错展示模板（Agent 回复用户）

```markdown
## 流水线在 Step {N} 失败，已停止

**步骤：** {步骤名称}
**命令：** `{命令}`
**错误：**
{traceback 或 pytest 输出}

**截图：** `{path}`（若存在）

**建议排查：**
1. ...
```

## 页面对象自检脚本配置项（validate yaml 扩展字段，可选）

```yaml
validate:
  method: add_depot          # 调用的页面对象方法名
  biz_key: depot             # YAML 业务数据键
  assert_field: name         # 断言字段
  assert_xpath: '//td[contains(text(), "{value}")]'
```

若未配置 `validate` 节，脚本对 `depot` 模块使用内置默认映射。

---

## 一张截图完整工作流（文件产出清单）

以「仓库信息-新增」为例，`module=depot`：

| 阶段 | 产出文件 | 关联已有代码 |
|------|----------|--------------|
| 页面对象 | `page_object/depot_page.py` | 继承 `BasePage` |
| 校验数据 | `test_data/validate/depot.yaml` | 独立于正式数据 |
| 注册 | `scripts/validate_page_object.py` → `PAGE_REGISTRY['depot']` | 自检脚本 |
| 正式数据 | `test_data/depot.yaml` | `yaml_conf.read()` |
| Fixture | `test_cases/conftest.py` → `depot_page` | 复用 `driver`/`serve` |
| 用例 | `test_cases/test_depot.py` | `login` fixture + `login.yaml` |
| 报告 | `allure_report/index.html` | `pytest.ini` 已配 `--alluredir` |

**业务流程调用链（pytest 运行时）：**

```
driver(fixture) → login(login.yaml) → depot_page(conftest) → add_depot(depot.yaml) → search → assert
```

---

## TodoWrite 调用示例

**任务开始时：**

```json
{
  "merge": false,
  "todos": [
    {"id": "analyze", "content": "分析截图：仓库信息页 PATH/元素/新增流程", "status": "in_progress"},
    {"id": "code-scan", "content": "扫描 depot_page/vendor_page/conftest 模板", "status": "pending"},
    {"id": "page-object", "content": "生成 page_object/depot_page.py", "status": "pending"},
    ...
  ]
}
```

**页面对象完成后：**

```json
{
  "merge": true,
  "todos": [
    {"id": "analyze", "status": "completed"},
    {"id": "code-scan", "status": "completed"},
    {"id": "page-object", "status": "completed"},
    {"id": "validate-data", "status": "in_progress"}
  ]
}
```

**失败时（自检未通过）：**

- `self-check` 保持 `in_progress` 或说明 blocked
- 后续 Todo 保持 `pending`，不标记 completed
- 回复用户：失败 Todo id、命令、traceback、截图路径

---

## 完成汇总模板（Agent 最终回复）

```markdown
## 截图自动化交付完成

**模块：** depot（仓库信息-新增）

### Todo 进度
全部 12 项已完成 ✓

### 新增/修改文件
- page_object/depot_page.py（新增）
- test_data/validate/depot.yaml（新增）
- test_data/depot.yaml（新增）
- test_cases/test_depot.py（新增）
- test_cases/conftest.py（修改：depot_page fixture）
- scripts/validate_page_object.py（修改：PAGE_REGISTRY）

### 执行结果
- 自检：PASSED
- pytest：PASSED（55s）
- 报告：pytest_pom/allure_report/index.html
- 幂等：depot.name 已递增为 仓库Pom测试06
```

---

## 元素定位失败修复流程

### 触发条件

**仅** `NoSuchElementException` / `Unable to locate element` 等元素定位错误触发；断言失败、业务异常 **不修复**，直接抛出。

### 定位优先级（生成 + 自愈统一）

```
id  →  name  →  css selector  →  相对 xpath
```

### 禁止使用的动态特征

- `data-v-*`（Vue scoped）
- `data-__meta` / `data-__field`
- UUID 形式 id、`rcDialogTitle0` 等运行时 id
- 含上述特征的 xpath/css 备选方案

### 相对 xpath 示例

```python
('id', 'name')  # 最优
('name', 'supplier')
('css selector', '#type .ant-select-selection')
('xpath', '//form[@id="personModal"]//input[@id="name"]')
('xpath', '//label[contains(.,"姓名")]/following-sibling::div//input')
('xpath', '//div[contains(@class,"ant-popover-buttons")]//button[contains(@class,"ant-btn-primary")]')
```

### 修复步骤（Agent / 运行时）

```
定位失败
  → 保存 DOM 至 log/dom_snapshots/
  → 查失败缓存，跳过已失败方案
  → locator_strategy.suggest_locators() 按 id→name→css→相对xpath 生成备选
  → 跳过含动态特征的方案，逐次尝试（合计 ≤ 3 次）
  → 仍失败：抛出完整报错，停止修复
```

### 相关模块

| 模块 | 作用 |
|------|------|
| `utils/locator_strategy.py` | 优先级策略、动态过滤、相对 xpath 生成 |
| `utils/element_repair.py` | DOM 快照、调用策略、3 次上限 |
| `utils/locator_failure_cache.py` | 失败方案持久化缓存 |
| `base_page/basepage.py` | locator/click/input 集成修复 |

### 手动清理缓存

删除或编辑 `log/locator_failure_cache.json` 后可重新尝试曾被标记失败的定位方案。

---

## Todo 驱动执行规范（全工作流通用）

### 原则

- **进度展示载体**：Cursor Todo 任务面板（不是 Agent 最终总结）
- **首个动作**：`TodoWrite(merge=false)`
- **单步节奏**：`in_progress` → 执行该项 → `completed` → 下一项

### 禁止行为

| 禁止 | 说明 |
|------|------|
| 静默连跑 | 连续写代码、跑 pytest、生成报告而不更新 Todo |
| 批量更新 | 全部做完后一次性把 Todo 标 completed |
| 跳过 in_progress | 直接从 pending 到 completed |
| 多项并行 | 同时两个及以上 in_progress |

### 用例变更 Todo 示例

```
analyze-change → update-page-object → update-test-case → pytest-run
```

### 修复子 Todo 示例

```
repair-diagnose → repair-attempt-1 → repair-attempt-2 → repair-attempt-3
```


