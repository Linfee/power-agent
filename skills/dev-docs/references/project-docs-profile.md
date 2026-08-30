# OKF Project Docs Profile

本文档把 OKF v0.1-compatible 规范应用到以 Agent 自动化为主的 Git 开发仓库。规范原文见 [okf-v0.1.md](./okf-v0.1.md)；冲突时以原文为准，本文件只定义项目级选择与 custom fields。

## Bundle 边界

- `docs/` 是主 Knowledge Bundle。
- `AGENTS.md`、`README.md`、Skill 定义和仓库根目录的工具控制文件不自动属于该 Bundle。
- `docs/index.md` 是 Agent 与工程师共同使用的知识入口；它应说明“什么任务读取什么 Concept”，而不仅是文件列表。
- `docs/log.md` 可选，用于记录 Bundle 级重要知识变化。
- `docs/` 下除 `index.md`、`log.md` 外的 Markdown 都是 Concept Document，包括 ADR 和 exec-plan 包中的 Markdown。

若仓库当前不满足这一边界，按渐进迁移处理：新建和实质修改的文档先合规，需要结构级迁移时交给 `dev-docs-maintain` 做结构性维护。

## 推荐 type

OKF 不限制 type 枚举。项目文档可采用：

| 内容 | type |
|---|---|
| 系统或总体架构 | `System` / `Architecture` |
| 服务或组件 | `Service` / `Component` |
| 领域或 bounded context | `Domain` |
| 术语或稳定概念 | `Term` / `Concept` |
| 规则、不变量、策略 | `Rule` |
| 开发、运维或排障步骤 | `Playbook` / `Process` |
| ADR | `Decision` |
| 外部资料与集成说明 | `Reference` |
| API | `API Endpoint` |
| 执行计划及其配套文件 | `Execution Plan` / `Review Contract` / `Evidence Cache` / `Task Graph` |

未知 type 合法。选择最能说明 Agent 应如何消费文档的值，不要为了固定枚举牺牲语义。

## 推荐 frontmatter

```yaml
---
type: Domain
title: Payment Domain
description: Payment 领域的职责、边界与核心不变量。
tags: [domain, payment]
timestamp: 2026-07-10T00:00:00Z
verification:
  strategy: source-change-and-periodic
  target: P90D
status: active
scope:
  - src/payment/**
sources:
  - src/payment/service.ts
  - src/payment/model.ts
owners:
  - team-payments
---
```

字段语义：

YAML frontmatter 是 Concept Document 元数据的唯一权威。旧 HTML header metadata（包括 `verified`、`scope` 与 `status`）已弃用，既不生产也不消费；它不能作为 YAML 字段或 verification ledger 的输入。

- `timestamp`：文档语义最后变化时间。格式化、扫描、链接检查不应刷新它。
- `verification`：可选的稳定 freshness 策略：
  - `strategy` 决定由来源变化、周期、生成器或历史完整性触发验证；当前事实推荐 `source-change-and-periodic`。
  - `target` 是允许的最长验证间隔，使用 ISO 8601 duration；它是 freshness SLO，不是错误等级阈值。
- 验证时间、Git HEAD、文档 hash、来源指纹和验证方法不写入 Concept；统一由 `dev-docs-maintain` 维护在 `docs/.okf/verification.json`。该登记是机器维护的派生状态，不是 Concept Document。
- `scope`：该 Concept 覆盖的代码区域、系统范围或知识边界；可以是 glob，也可以是概念描述。
- `sources`：支撑当前声明的代码、测试、配置、Schema 或内部文档路径。
- `status`：概念生命周期，例如 `active`、`proposed`、`accepted`、`deprecated`、`superseded`。
- `owners`：可选维护责任人或团队，不作为内容正确性的替代证据。

`type` 是唯一 OKF MUST 字段；其余字段按价值添加。不要为了字段完整度填入虚构信息。

### 项目级 freshness 默认值

项目可以在根 `docs/index.md` frontmatter 中声明默认 freshness policy，Concept 局部配置覆盖默认值：

```yaml
---
okf_version: "0.1"
freshness:
  default_strategy: source-change-and-periodic
  default_target: P90D
  rules:
    - type: Playbook
      target: P30D
    - type: Decision
      strategy: historical
---
```

示例周期不是本 Profile 的固定要求。项目应按知识变化速度、执行风险和定时维护容量选择；未声明 target 时可以进行年龄排序和来源变化检测，但不能声称提供有上界的 freshness 保证。

为支持快速全 Bundle 扫描，`scope` 和 `sources` 中用于 Git 变更检测的路径应以仓库根目录为基准，优先使用稳定的精确路径或 glob。scanner 只把现存的 scope 路径和显式 glob 作为来源；路径形的概念范围（例如 `docs/workflow`）不是 source。需要声明“该来源必须存在”或追踪未来/已删除路径时，必须写入 `sources`；纯概念范围可保留在 `scope`，但不能被 scanner 当作机器可解析的变更映射。

## 链接与证据

- 内部关系使用 Markdown 链接和上下文文字表达。
- 本 Profile 默认使用相对链接，因为它在 GitHub、编辑器与 Bundle 搬迁中更稳健。
- 外部事实进入 `# Citations`；需要长期保留摘要时，在 `docs/references/` 创建 `type: Reference` 的 Concept。
- 代码事实不必全部复制进 Citations。用 `sources`、路径链接和少量必要说明建立可追溯性。
- Broken link 不使 Bundle 整体失效，但维护任务应记录并修复影响 Agent 路由的链接。

## Concept 粒度

一个文档应表达一个稳定、可复用的知识概念。以下情况通常应拆分：

- 不同部分由不同代码范围或权威来源支撑；
- 不同部分有独立生命周期；
- Agent 常只需要其中一个部分，但每次都必须加载整篇长文档。

以下情况通常应合并：

- 多个文件重复描述同一职责、术语或不变量；
- 任一文件脱离其他文件就无法形成独立 Concept；
- 文件只是历史追加形成的碎片，而非独立知识。

目录只用于组织和缩小检索范围，不承担严格语义。分类关系主要通过 `type`、`tags` 和链接表达。

## 当前事实、决策与计划

- 当前事实文档描述“系统现在是什么”，实现变化后直接修订。
- ADR 描述“为什么作出这个耐久决定”，接受后保留历史，通过新 ADR supersede。
- exec-plan 描述“接下来做什么以及做到哪里”，完成后不能成为当前系统事实的唯一来源。
- 计划完成时，应把新事实回写到当前事实 Concept，把耐久决定写入 ADR，再归档计划。

## 渐进迁移

对已有仓库不要一次性大规模改写：

1. 新建 Concept 必须合规。
2. 实质更新旧文档时，补齐 frontmatter 和直接相关链接。
3. 无争议格式迁移可直接做；移动、拆分、合并与删除是结构级操作，需要证据与授权。
4. 遇到已弃用的 HTML header metadata 时，删除而不读取、不复制、不迁移其值。需要 `scope`、`status` 或 `verification` 时，仅依据当前正文和权威来源写入 YAML；旧 `verified` 日期绝不回填验证登记。
5. 修改 Concept ID 时更新全部内部链接，并在相关 `log.md` 记录 Move/Rename。

## 与现有 Skill 套件的兼容提醒

`setup-power-agent` 初始化产出、`dev-docs` 语义写入与 `dev-docs-maintain` 机械维护同属知识维护子系统：它们生产的 Concept 具有合法 YAML frontmatter 和非空 `type`，验证运行状态由 verification ledger 维护。对未走该子系统的其他文档生产者仍采用渐进迁移，不擅自重写其已有文档。
