# QA Playground — 王贺龙的测试开发技术仓库

> 2.5 年测试开发经验 · Python 自动化 · Jenkins CI/CD · Allure 可视化报告 · AI 辅助测试

[![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python)](https://github.com/wyf200129-oss/qa-playground)
[![Selenium](https://img.shields.io/badge/Selenium-4.x-43B02A?logo=selenium)](https://github.com/wyf200129-oss/qa-playground)
[![pytest](https://img.shields.io/badge/pytest-9.x-0A9EDC?logo=pytest)](https://github.com/wyf200129-oss/qa-playground)
[![Allure](https://img.shields.io/badge/Allure-Report-orange)](https://github.com/wyf200129-oss/qa-playground)
[![Jenkins](https://img.shields.io/badge/Jenkins-Pipeline-success?logo=jenkins&logoColor=white)](https://github.com/wyf200129-oss/qa-playground)

---

## 关于我

财务管理专业出身，在校期间主动转型软件测试，毕业即拿到测试开发 Offer。

目前具备 **2.5 年 Web/App 双端测试开发经验**，擅长接口自动化与 UI 自动化框架搭建，在国内较早探索并落地 AI 辅助测试方案，取得了 **用例设计工时缩短 50%、需求场景覆盖率由 80% 提升至 95%** 的实际效果。

**期望城市：大连** | 📧 346296043@qq.com | 📱 18840823821

---

## 技术栈

| 类别 | 技能 |
|------|------|
| **语言** | Python |
| **UI 自动化** | Selenium · POM 设计模式 · YAML 数据驱动 · ddddocr 验证码识别 |
| **接口自动化** | Requests · 关键字驱动 · JSONPath · pytest-allure |
| **CI/CD** | Jenkins Pipeline · Allure Report 插件 · Git SCM |
| **性能测试** | JMeter · TPS / 95线 / 错误率分析 |
| **App 测试** | adb 调试 · Monkey 稳定性测试 · Fiddler 抓包 |
| **数据库** | MySQL 多表联查 |
| **工具链** | Git · Docker · Linux Shell · 禅道 · Cursor AI |

---

## 仓库结构

```
qa-playground/
├── automation-demos/
│   ├── ui-pom/          # 🖥️  POM + YAML UI 自动化框架（Selenium + pytest）
│   └── api-keyword/     # 🔌  关键字驱动接口自动化框架（Requests + pytest）
├── ai-testing/          # 🤖  AI 辅助测试工作流与实践
├── ci/                  # 🐳  Docker 相关配置
└── Jenkinsfile          # 🚀  Jenkins Pipeline（4 个 Stage，含 Allure Report）
```

---

## Jenkins CI/CD Pipeline

**4 个 Stage 全程自动化，推代码即触发构建：**

```
Env Check  →  Install Dependencies  →  Run POM Tests  →  Allure Report
   ✅                ✅                      ✅                ✅
```

**最新一次构建结果：7 passed in 0.06s ✅**

```
test_cases/test_mock_ci.py::TestMockLogin::test_login_success_url_changes    PASSED
test_cases/test_mock_ci.py::TestMockLogin::test_verify_logged_in_visible     PASSED
test_cases/test_mock_ci.py::TestMockLogin::test_verify_logged_in_not_visible PASSED
test_cases/test_mock_ci.py::TestMockVendor::test_add_supplier_flow           PASSED
test_cases/test_mock_ci.py::TestMockVendor::test_search_supplier_flow        PASSED
test_cases/test_mock_ci.py::TestConfig::test_yaml_config_exists_and_valid    PASSED
test_cases/test_mock_ci.py::TestConfig::test_page_object_imports             PASSED
```

> 演示用例采用全流程 Mock，不依赖任何真实后端，任何人 clone 后可直接 `Build Now` 复现全绿结果。

### 快速复现

1. Fork 本仓库
2. Jenkins 新建 Pipeline，选 **Pipeline script from SCM**，填入仓库地址
3. 点击 **Build Now**，约 2 分钟全绿（第二次因 `.venv` 复用更快）

**环境要求：** Python 3.x · Jenkins 2.x · Allure Jenkins Plugin · Git

---

## UI 自动化框架 — POM + YAML 数据驱动

**路径：`automation-demos/ui-pom/`**

基于 Page Object Model 的三层分离架构，实际应用于 ERP 供应商管理模块。

### 架构分层

| 层 | 职责 |
|----|------|
| `base_page/` | Selenium 原子操作封装：定位、输入、点击、显式等待 |
| `page_object/` | 页面业务流程：登录、新增供应商、查询 |
| `test_cases/` | 用例编排与断言 |

### 核心亮点

**✅ 显式等待替代 sleep — 快 3 倍，消除假阳性**
```python
self.wait_for_url_change(self.url, timeout=20)         # 登录后 URL 跳转
self.wait_for_invisible(*self.vendor_modal, timeout=10)  # 弹窗关闭
```

**✅ ddddocr 验证码自动识别**
```python
def get_code(self, by, value):
    img_bytes = self.locator(by, value).screenshot_as_png
    return ddddocr.DdddOcr().classification(img_bytes)
```

**✅ YAML 数据驱动，测试数据与代码完全分离**
```yaml
login:
  user: "[ERP测试账号]"
  pwd:  "[ERP测试密码]"
vendor:
  name: "[供应商测试名称]"
```

[→ 查看详细文档](./automation-demos/ui-pom/README.md)

---

## 接口自动化框架 — 关键字驱动

**路径：`automation-demos/api-keyword/`**

基于 Requests 封装的关键字驱动接口框架，支持多环境一键切换、Token 自动注入、Allure 报告。

### 设计亮点

| 特性 | 说明 |
|------|------|
| 关键字驱动 | YAML 定义用例数据，`api.request(**data)` 执行，数据与代码分离 |
| 多环境切换 | `@pytest.mark.parametrize('set_env', ['Test_Env'], indirect=True)` 一行切换 |
| Token 自动注入 | 登录后 token 写入 ini，后续请求自动带 `Authorization` 头 |
| JSONPath 提取 | `api.get_text(res.json(), 'token')` 支持 `$..key` 递归搜索 |
| Allure 报告 | `@allure.epic/feature/story/step` 全链路标注 |
| 自动清理 | `clear_token` fixture 在用例结束后自动清空缓存 |

[→ 查看详细文档](./automation-demos/api-keyword/README.md)

---

## AI 辅助测试实践

**路径：`ai-testing/`**

在实际项目中探索并落地 AI 辅助测试设计，量化效果如下：

| 指标 | 优化前 | 优化后 | 变化 |
|------|--------|--------|------|
| 用例设计工时 | 基准值 | — | **减少约 50%** |
| 需求场景覆盖率 | 80% | 95% | **↑ 15 个百分点** |

**工作流：**
```
业务需求文档
    → AI 解析需求要点（Prompt Engineering）
    → AI 生成测试场景草稿
    → 人工评审 + 补充边界 & 异常路径
    → 代码化 → 纳入 Jenkins 自动回归
```

[→ 查看完整工作流](./ai-testing/workflow.md)

---

## 项目经历

### ERP 企业资源计划系统（2025.05 – 2026.03）
面向服装企业的 Web + App 双端进销存系统，覆盖 13 个业务模块。

- 主导采购/销售/库存三模块全流程测试，双端共 **360+ 条功能用例**
- 独立搭建 POM UI 自动化 + 关键字驱动接口自动化双框架
- **90 条用例接入 Jenkins 定时回归**
- 探索并落地 AI 大模型（ChatGPT/Kimi）+ RAG 辅助测试设计，用例设计工时缩短 50%

### CCAS 后台管理系统（2024.10 – 2025.04）
电子档案编制管理系统，支持多层级归档、CA 数字证书电子签章。

- 独立完成功能测试与接口/压力测试
- 保障电子档案与纸质档案数据一致性，实现跨档案类型数据稽核

---

## 联系方式

- 📧 邮箱：346296043@qq.com
- 📱 电话：18840823821
- 🐙 GitHub：[github.com/wyf200129-oss](https://github.com/wyf200129-oss)

---

> 💡 **"不只会用工具，更会从 0 到 1 搭建工具。"**
>
> 欢迎技术交流，大连地区的 HR 和猎头也欢迎直接联系。
