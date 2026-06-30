---
name: api-test-case
description: >-
  Generates API test cases from OpenAPI contracts: full operation coverage,
  1 positive + 3 negative per endpoint, contract-only assertions, desensitized
  data in separate files. Sub-skill of test-case-generation. Use for 接口测试用例,
  API cases, HTTP testing, OpenAPI, blackcore-mall, or 契约用例.
---

# 接口测试用例生成（子 Skill）

> **前置**：已由 [测试用例生成/SKILL.md](../SKILL.md) 路由；已读 [通用原则.md](../通用原则.md)。  
> **产出形态**：本 Skill 生成 **用例表 + YAML 数据**（落盘工作区根目录 `接口用例集/`、`接口数据集/`）。  
> **落盘 Rule**：[`.cursor/rules/接口用例生成-落盘路径.mdc`](../../rules/接口用例生成-落盘路径.mdc)  
> **可执行 pytest 代码**（Requests + conftest）→ [接口自动化实现](../../接口自动化实现/SKILL.md)（两阶段：骨架 TODO → 人工评审 → 完整实现）。

## 硬性要求（a～h）

| 代号 | 要求 | 执行要点 |
|------|------|----------|
| **a** | 包含 **所有** 接口请求 | 遍历契约 `paths` 每个 operation；数量 = operation 数 × 4 |
| **b** | 用例中 **不出现** IP/端口 | path 仅写 `/xxx`；基址统一 `[ENV_API_BASE_URL]` |
| **c** | 敏感数据 **提前脱敏** | 用例表用占位符或 `@数据文件`；见 [数据布局.md](数据布局.md) |
| **d** | 断言 **body 优先 + 联合 status** | 获取响应后先 body 再 status；**状态码 → body 信息 → body 字段** 均对齐契约；禁止契约外必过断言 |
| **e** | 每接口 **1 正 3 反** | `_001` 正向，`_002～_004` 反向且触发条件互不相同 |
| **f** | 测试数据 **单独管理** | 用例 → `接口用例集/`；数据 → `接口数据集/`（工作区根目录） |
| **g** | 固定 **8 列表头** | 用例编号、path、method、headers、body、预期结果（预期response）、实际结果 |
| **h** | 不明确 → **待确认-角色** | 如 `待确认-产品：…`、`待确认-开发：…`；不得写死 |

读不到契约文件时：**禁止编造**（见 Rule `接口用例生成-契约优先.mdc`）。

## 材料路径（必须先读）

| 资源 | 路径 |
|------|------|
| 契约清单 | `6.测试用例生成/docs/contracts/README.md` |
| 黑核商城契约 | `6.测试用例生成/docs/contracts/blackcore-mall/openapi-swagger2.json` |
| 可选 PRD 节选 | 用户 @ 的文件（双源对齐，不替代契约结构断言） |

确认 `info.version` 并写入用例文件文首。

## 工作流

1. 读取契约 JSON + README（失败则停止，仅输出待确认-开发）
2. 列出全部 operation（method + path）
3. 每个 operation 设计 4 条（1+3），反向条件互不重复
4. 为每条用例编写 `接口数据集/{domain}/{用例编号}.yaml`
5. 填写用例表 → `接口用例集/{domain}/cases.md`
6. **自动执行二次 Check**（见下文，最多 2 轮，可自动修复）
7. **Check 通过后自动质量评分**（S1～S8，满分 100）
8. 回复用例路径、简报路径、Check 结论、**质量总分/档位**；若 <85 按 §10 做 1 轮质量提升后复评

## 二次 Check（生成后必做）

用例落盘后 **必须** 运行二次 Check，不得跳过。

```bash
cd 6.测试用例生成
python scripts/api_case_second_check.py --domain blackcore-mall --max-rounds 2
```

| 轮次 | 行为 |
|------|------|
| 第 1 轮 | 按 [检查清单.md](检查清单.md) 校验；发现问题 **自动修复** 后写回用例/数据 |
| 第 2 轮 | 再次校验；仍不通过 → **FAIL**，生成失败简报，**禁止**定稿交付 |
| 通过 | 生成成功简报 → 可进入 HITL / Requests |

- 清单定义：[检查清单.md](检查清单.md)（C1～C14）
- 简报模板：[简报模板.md](简报模板.md)
- 简报目录：`接口用例简报集/{domain}_check_brief_{YYYYMMDD_HHMM}.md`（文件名与 §1 评审时间均精确到分钟）

`generate_api_cases.py` 生成结束后会自动调用本 Check。

**Agent 必须**：执行 Check 脚本 → 将简报路径、Check 结论、**质量评分** 回复用户；Check 不通过时说明 §6 遗留问题且 **不评分**。

## 质量评分（Check 通过后必做）

> **Check 管进门，评分管好坏**；Check 不过不评分。

| | 二次 Check | 质量评分 |
|--|------------|----------|
| 结论 | 通过 / 不通过 | **0～100 分** + 档位 |
| 时机 | 用例落盘后 | **仅 Check 通过** 后 |

### 八维基础分（S1～S8 = 100）

| 代号 | 维度 | 上限 | 你的考量对应 |
|------|------|------|--------------|
| S1 | 格式规范 | 10 | 格式 |
| S2 | 数量与覆盖 | 15 | 数量 |
| S3 | 正反向结构 | 15 | 正向反向 |
| S4 | 数据精准性 | 15 | 数据精准性 |
| S5 | 响应断言质量 | 15 | 响应断言 |
| S6 | 数据脱敏 | 10 | 数据脱敏 |
| S7 | 业务流程关联 | 10 | 业务流程 |
| S8 | 可执行性与可追溯 | 10 | （补充）转 Requests / 可追溯 |

细则与 **高分导向**：[评分细则.md](评分细则.md)

### 档位与 Agent 行为

| 总分 | 档位 | Agent 行为 |
|------|------|------------|
| ≥85 | 良好+ | 可交付；生成时以此时为默认目标 |
| 75～84 | 合格 | 可交付，简报 §10 列改进项 |
| <75 | 偏低/不合格 | **须 1 轮质量提升** 后复评 |

**生成时主动靠拢高分**：反向条件互异、断言含契约 description、少待确认、yaml 含 required、链路 login→Token→下单 可串。避免反向预期复制粘贴、neg 复用 pos 数据。

```bash
# Check 已内嵌评分；也可单独跑：
python scripts/api_case_quality_score.py --domain blackcore-mall
```

## 输出模板

表头与编号见 [用例模板.md](用例模板.md)。  
数据目录见 [数据布局.md](数据布局.md)。

## 断言基本要求

获取响应结果后（用例表「预期结果」列 / pytest 实现均适用）：

1. **body 优先，再联合 status**：先写 body 信息要点与关键字段，再写 HTTP 状态码；二者须 **联合** 可判定。
2. **契约对齐**：**状态码 → body 信息 → body 字段** 均须可追溯至该 operation 的 `responses`、description、schema / examples。
3. **反向用例同等适用**：预期结果同样 **先 body 错误要点、再 status**；设计时 **以稳定通过（绿色）为目标**——固定触发、独立数据、可复现；禁止「非 2xx 即可」或复制粘贴同一预期。

## 反向用例设计参考

在 **契约声明的 responses 范围内** 选择触发条件；每条反向预期须含 **契约内 status + body 错误要点**：

| 类型 | 示例 | 前提 | 断言设计（可绿） |
|------|------|------|------------------|
| 鉴权 | 缺 Authorization、错误 Token | 契约有 401/403/400 | 固定无效 token / 清 ini；body 无 token 或 error 语义 + status |
| 参数 | 缺 required 字段、错误类型 | 契约有 400/422 | 独立 yaml；body 含 validation/error 要点 + status |
| 资源/业务 | 不存在 ID、余额不足 | 契约有 404/400/503 | 可复现的无效 id；body + status 均在契约内 |

若契约未声明对应错误码，预期写 `待确认-开发：{缺什么说明}`，**不得** 虚构必过码。

**PRD/契约不清晰、无法写可判定预期时**：用例表标 **待确认**；**xfail/skip 仅在 pytest 执行后的二次 check / 修复闭环 / 一页简报中决策**（见 [xfail与skip治理.md](../../接口自动化实现/xfail与skip治理.md)）。

## 断言来源（内部标注，可写在 yaml notes 或扩展列）

- **契约**：HTTP 码、response schema 字段
- **PRD**：业务语义（不可替代结构断言）
- **开发**：文档未写清的错误触发条件

## 落盘示例

> 路径相对于**工作区根目录**。

```text
接口用例集/blackcore-mall/cases.md
接口数据集/blackcore-mall/POST_user_services_login_001.yaml
…（共 19×4=76 条用例时，76 个数据文件）
```

## 关联

- 统筹 Skill：[../SKILL.md](../SKILL.md)
- 功能用例子 Skill：[../功能/SKILL.md](../功能/SKILL.md)
- Cursor Rule：`.cursor/rules/接口用例生成-契约优先.mdc`、`.cursor/rules/接口用例生成-落盘路径.mdc`
- 脱敏：[../../测试数据生成/脱敏规范.md](../../测试数据生成/脱敏规范.md)

## 与 测试数据生成 协作

需要 Pydantic 结构化数据（如 order_flow）时，先走 **测试数据生成** Skill，再将必要字段 **映射** 到 `接口数据集/` 的 HTTP body；勿混放目录。
