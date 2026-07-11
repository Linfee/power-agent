---
name: dev-docs
description: |-
  当需要把已有代码或权威来源中的稳定系统事实、边界、决策依据或集成参考写入或修订 `docs/` 长期知识时使用。不要用于裸“写文档”、README/公告、会话记录或执行计划；计划交给 writing-plans。
  Triggers: 文档知识沉淀, 系统事实回写, 架构事实更新, 领域知识维护, ADR 依据记录, 集成参考沉淀, dev-docs.
---

# 维护长期开发知识

将项目文档维护为 Agent 可检索、可验证、可持续修正的外部记忆。此 Skill 只处理将在未来工作中复用的 `docs/` 知识，不以产出泛化文稿为目标。

## 何时读取参考资料

| 资料 | 读取时机 |
|---|---|
| [OKF 规范](./references/okf-v0.1.md) | 判断 Concept、frontmatter、链接或 Bundle 最小合规时。 |
| [项目 Docs Profile](./references/project-docs-profile.md) | 写入本仓库 `docs/`、选择 custom fields、处理 YAML 迁移或 freshness 策略时。 |
| [压力场景](./references/stress-scenarios.md) | 触发边界、敏感来源、YAML 迁移或链接处理可能被误判时。 |

## 工作边界

### 本 Skill 负责

- 描述系统当前状态：架构、领域模型、模块边界、关键流程、开发方式与精确参考信息。
- 记录无法从当前代码恢复的长期决策原因（ADR）。
- 在代码或设计变化后，把新的长期事实回写到已有 Concept Document。
- 维护直接有用的 Concept 链接、来源、目录索引与必要的变更日志。

### 委派或跳过

- 实施计划、重构计划、迁移计划、任务拆解：委派给 `writing-plans`，不得在本 Skill 中再建计划。
- 临时讨论、一次性排障过程、会话级执行细节：默认不进入长期知识库。
- 局部且显然的实现细节：让代码和测试表达；只有它形成稳定边界、不变量、跨文件关系或后续工作约束时才文档化。
- README 营销内容、发布公告、纯代码注释和没有长期消费场景的普通文稿不属于本 Skill。

分类含混时，以“未来 Agent 如何使用这项知识”而非关键词判断；只有选择会改变权威来源或生命周期时才需要澄清。

## 知识角色与典型位置

沿用仓库已有布局，优先更新现有 Concept，不为满足分类表机械创建目录。

| 知识角色 | 表达内容 | 典型位置 | 推荐 OKF type |
|---|---|---|---|
| 系统模型 | 当前系统边界、组件、依赖、运行与部署关系 | `docs/architecture.md` 或 `docs/architecture/` | `System` / `Architecture` |
| 领域知识 | 项目术语、模型、职责、关系与不变量 | `docs/domain/` 或现有 context 文档 | `Domain` / `Concept` / `Rule` |
| 开发运行方式 | 构建、测试、调试、生成与发布所需的稳定流程 | `docs/development.md` 或 `docs/development/` | `Playbook` / `Process` |
| 精确参考 | API、配置、Schema、命令、第三方集成与来源摘要 | `docs/references/` 或相关模块目录 | `Reference` / `API Endpoint` |
| 决策历史 | 有真实替代方案且会长期约束实现的决定 | `docs/adr/NNNN-slug.md` | `Decision` |
| 执行状态 | 已批准工作的目标、任务、证明与恢复点 | `docs/exec-plans/` | 委派给 `writing-plans` |

## 证据与敏感资料边界

- 只读取支撑目标 Concept 所需的最小代码、测试、配置、Schema、ADR 和一阶链接；证据缺口明确时才扩大范围。
- 不把密钥、令牌、认证头、会话 Cookie、个人数据、客户标识符、私有 URL query、原始日志或完整受限资料复制进 `docs/`、示例或 Citations。
- 用已脱敏的事实、合成示例和不含凭据的 canonical resource 表达；需要可追溯性时指向受控来源的稳定名称或路径，而不是泄露内容。
- 若无法在不泄露敏感资料的前提下建立可审查来源，保留该事实未确认，并在输出风险中说明访问前提；不得以模型记忆补足。

## OKF 写入约定

- `docs/` 是主 Bundle；`index.md` 和 `log.md` 是导航与目录变更日志，不是普通 Concept Document。
- 除 `index.md`、`log.md` 外，文档元数据唯一权威是文件顶部 YAML frontmatter，其中 `type` 必须非空。`title`、`description`、`tags`、`timestamp`、`scope`、`sources`、`verification`、`status` 和 `owners` 按需要写入 YAML。
- 旧 HTML header metadata（包括 `verified`、`scope` 与 `status` 注释）已弃用：不生产、不读取、不复制、不作为迁移输入。旧 `verified` 日期绝不写入验证登记。
- `timestamp` 表示内容语义变化时间，不是扫描或验证时间。验证运行状态只由 `dev-docs-maintain` 写入 `docs/.okf/verification.json`；新建或修改 Concept 不等于已验证。
- 文件路径就是 Concept ID。除非概念边界确实改变，不随意移动或重命名。
- 内部关系用标准 Markdown 链接表达；本仓库默认优先相对链接。外部资料、业务规则、第三方行为或原始资料整理出的声明应在 `# Citations` 保留来源。
- 仅在新增、移除、移动 Concept 或导航语义改变时更新相关 `index.md`；仅将长期有意义的知识变化写入 `log.md`。

```markdown
---
type: Domain
title: Payment Domain
description: Payment 领域的职责、边界与核心不变量。
tags: [domain, payment]
timestamp: 2026-07-10T00:00:00Z
verification:
  strategy: source-change-and-periodic
  target: P90D
scope:
  - src/payment/**
sources:
  - src/payment/service.ts
  - src/payment/model.ts
---

# Overview

Payment Domain 定义支付状态流转和重试约束。
```

## 执行流程

1. **定位长期知识**：读取 `AGENTS.md`、相关入口和 `docs/index.md`（如存在），判断是更新当前事实、记录 ADR、补来源还是交给 `writing-plans`。
2. **建立最小证据集**：读取目标 Concept、直接链接、相关 ADR 与直接相关的代码、测试、配置和 Schema；先应用敏感资料边界。
3. **修订权威 Concept**：当前事实直接描述现在是什么；已有稳定 Concept 优先更新；仅在知识确实独立且长期复用时新建。
4. **维护决策、链接与来源**：ADR 只记录真实且耐久的权衡；accepted ADR 不重写历史，改变决定时新建 ADR 并建立 supersede 关系。补充有语义的链接、Citations、必要的 index/log。
5. **核对可消费性**：检查 YAML frontmatter、非空 `type`、内部链接、引用路径与关键声明的权威证据；只在语义变化时更新 `timestamp`。需要登记时交给 `dev-docs-maintain`。

## 稳定输出 contract

最终输出必须是 Markdown，始终按以下顺序包含这些二级标题；没有对应内容时写“无”或“无需”，不得省略：

## 状态

写明 `DONE`、`DONE_WITH_CONCERNS` 或 `BLOCKED`，以及一句结论。

## 范围

列出实际检查或修改的 Concept、来源和明确排除项。

## 变更/修复

列出创建、更新、删除或确认无需变更的长期知识及其语义。

## 证据

列出核对过的权威来源、链接/frontmatter 检查和已执行的验证；未执行的操作不得声称完成。

## 剩余问题/风险

列出未确认事实、敏感资料访问限制、broken link 或知识漂移；无则写“无”。

## 下一步

给出明确的后续动作；无需动作时写“无需”。
