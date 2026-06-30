---
name: test-case-generation
description: >-
  Orchestrates test case generation: routes to functional or API sub-skills,
  enforces shared principles (no fabrication, pending labels, desensitization).
  Use when generating test cases, 测试用例, 功能用例, 接口用例, system test cases,
  or API test cases from PRD or OpenAPI contracts.
---

# 测试用例生成（统筹）

本 Skill 为 **用例生成总入口**：识别任务类型 → 加载共通原则 → **委派子 Skill** 执行。

## 路由规则（必须先判断）

| 用户意图 / 关键词 | 读取并执行 |
|-------------------|------------|
| 功能测试、系统测试、UI、业务场景、验收用例、四段式 | [功能/SKILL.md](功能/SKILL.md) |
| 接口测试、API 用例、HTTP、契约、OpenAPI、Requests | [接口/SKILL.md](接口/SKILL.md) |
| **接口自动化 pytest 代码**、骨架、conftest、Day_17、Requests 实现、工作流 | [接口自动化实现](../接口自动化实现/SKILL.md) → **先读** `工作流体系.md` |
| **运行 pytest、测试执行、失败修复闭环**（含 traceback） | [pytest 失败修复闭环](../pytest失败修复闭环/SKILL.md) |
| **知识库语料入库、切分、Chroma ingest、检索验收** | [知识库语料管理](../知识库语料管理/SKILL.md) → Rule `知识库语料-入库与切分.mdc` |
| 用例/脚本 **仅咨询 trace、分析排错**（未要求跑测） | [代码调试与修改](../代码调试与修改/SKILL.md) |
| 同时涉及两者 | 先读共通原则，再 **分别** 执行两个子 Skill，产出分目录存放 |

**执行任何子 Skill 前，必须先读** [通用原则.md](通用原则.md)。

## 标准工作流

```
Task Progress:
- [ ] Step 1: 判断类型 → 功能 / 接口文档 / 接口自动化代码 / pytest执行
- [ ] Step 2: 读取 通用原则.md
- [ ] Step 3: 读取对应子 Skill 全文
- [ ] Step 4: 读取材料（PRD / 契约 / 业务节选）；读不到则仅待确认，禁止编造
- [ ] Step 5: 按子 Skill 生成（接口自动化代码 → 先阶段 A 骨架+TODO，评审后再 B）
- [ ] Step 6: 子 Skill 自检清单 + **二次 Check**（功能 F1～F12 / 接口 C1～C14）
- [ ] Step 7: Check 通过后 **质量评分**（功能 F1～F8 / 接口 S1～S8）；落盘并回复路径与简报
```

### 接口自动化代码专用流程（两阶段）

```
契约 +（可选）业务节选
  → 读 接口自动化实现/工作流体系.md
  → 阶段 A：2～3 接口、骨架、TODO、脱敏
  → 人工评审（用户确认）
  → 阶段 B：补全断言、pytest 执行
```

## 子 Skill 一览

| 子 Skill | 路径 | 材料依据 | 产出目录 |
|----------|------|----------|----------|
| 功能测试用例 | [功能/SKILL.md](功能/SKILL.md) | PRD / 需求 | `功能用例集/`（工作区根目录） |
| 接口测试用例（文档） | [接口/SKILL.md](接口/SKILL.md) | OpenAPI 契约 | `接口用例集/` + `接口数据集/`（工作区根目录） |
| **接口自动化代码（pytest）** | [接口自动化实现](../接口自动化实现/SKILL.md) | 契约 + 业务节选 | 用户框架目录（如 `Day_17_interface_frame/`） |

## 关联资源

| 资源 | 路径 |
|------|------|
| API 契约 | `6.测试用例生成/docs/contracts/` |
| 契约优先 Rule | `.cursor/rules/接口用例生成-契约优先.mdc` |
| 功能用例落盘 Rule | `.cursor/rules/功能用例生成-落盘路径.mdc` |
| 接口用例落盘 Rule | `.cursor/rules/接口用例生成-落盘路径.mdc` |
| 测试数据生成 | `.cursor/skills/测试数据生成/SKILL.md` |
| pytest 参数化 YAML Rule | `.cursor/rules/测试数据生成-pytest-yaml.mdc` |
| pytest fixture 与用例实现 | `.cursor/skills/pytest-fixture与用例实现/SKILL.md` |
| 脱敏规范 | `.cursor/skills/测试数据生成/脱敏规范.md` |
| pytest 失败修复闭环 | `.cursor/skills/pytest失败修复闭环/SKILL.md` |
| **接口自动化实现（骨架→评审→代码）** | `.cursor/skills/接口自动化实现/SKILL.md` |
| 代码调试与修改 | `.cursor/skills/代码调试与修改/SKILL.md` |

## Agent 行为

- 用户未说明类型时，**先询问** 要生成「功能用例」「接口用例文档」还是「接口自动化 pytest 代码」，勿默认混写。
- 用户提交 **业务方向节选** 时，接口自动化任务须读 `接口自动化实现/业务节选接入.md` 并写入 TODO 来源。
- 子 Skill 与统筹 Skill **同时生效**；冲突时以更具体的子 Skill 为准。
- **pytest 可执行代码** 须走 [接口自动化实现](../接口自动化实现/SKILL.md) 两阶段流程（骨架 → 评审 → 完整实现），禁止跳过评审直接写满断言。
- 禁止跳过子 Skill 直接输出完整用例表或完整测试代码。
