---
name: dev-docs
description: |-
  把稳定系统事实、边界、决策依据或集成参考写入或修订 `docs/` 长期知识时使用；不用于裸“写文档”、README/公告、会话记录或执行计划。
  Triggers: 文档知识沉淀, ADR 记录, dev-docs.
---

# 维护长期开发知识

把 `docs/` 维护为 Agent 可检索、可验证、可持续修正的外部记忆。只处理会在未来工作中复用的长期知识，不以产出泛化文稿为目标。

## 判断什么值得写入

- 描述系统当前状态：架构、领域模型、模块边界、关键流程、开发方式与精确参考。
- 记录无法从当前代码恢复的长期决策原因（ADR）。
- 代码或设计变化后，把新的长期事实回写到已有 Concept。
- 消费侧信号：探索或产出中发现的术语缺口与同义词漂移；经用户确认重开的 ADR 冲突（新建 ADR 并建立 supersede 关系）。

哪些不属于本 Skill：

- README、CHANGELOG、发布公告。
- 临时讨论、一次性排障过程、会话级执行细节。
- 局部且显然的实现细节——让代码和测试表达；只有形成稳定边界、不变量、跨文件关系或后续工作约束时才文档化。
- 执行计划内容（由计划类 Skill 或流程承担，本 Skill 不裁定其生命周期）。

分类含混时，以“未来 Agent 如何使用这项知识”判断，不按关键词；只有选择会改变权威来源或生命周期时才需要澄清。用户只说“更新文档”且没有指出变化事实、来源或消费场景时，不得猜测写入——补齐会改变权威来源或生命周期的最小证据，或明确缺口。

## 知识角色与位置

沿用仓库已有布局，优先更新现有 Concept，不为满足分类表机械创建目录：

| 知识角色 | 表达内容 | 典型位置 | 推荐 OKF type |
|---|---|---|---|
| 系统模型 | 系统边界、组件、依赖、运行与部署关系 | `docs/architecture.md` 或 `docs/architecture/` | `System` / `Architecture` |
| 领域知识 | 术语、模型、职责、关系与不变量 | `docs/domain/` 或现有 context 文档 | `Domain` / `Concept` / `Rule` |
| 开发运行方式 | 构建、测试、调试、生成与发布的稳定流程 | `docs/development.md` 或 `docs/development/` | `Playbook` / `Process` |
| 精确参考 | API、配置、Schema、命令、第三方集成与来源摘要 | `docs/references/` 或相关模块目录 | `Reference` / `API Endpoint` |
| 决策历史 | 有真实替代方案且长期约束实现的决定 | `docs/adr/NNNN-slug.md` | `Decision` |

## 要保护什么

### 敏感资料边界

- 不把密钥、令牌、认证头、会话 Cookie、个人数据、客户标识符、私有 URL query、原始日志或受限资料复制进 `docs/`、示例或 Citations。
- 用已脱敏的事实、合成示例和不含凭据的 canonical resource 表达；需要可追溯性时指向受控来源的稳定名称或路径。
- 无法在不泄露敏感资料的前提下建立可审查来源时，保留该事实未确认，并在输出风险中说明访问前提；不得以模型记忆补足。

### OKF 元数据权威

`docs/` 是主 Bundle；`index.md` 和 `log.md` 是导航与目录变更日志，不是普通 Concept。除 `index.md`、`log.md` 外，元数据唯一权威是文件顶部 YAML frontmatter，`type` 必须非空；`title`、`description`、`tags`、`timestamp`、`scope`、`sources`、`verification`、`status`、`owners` 按需要写入。

已弃用的 HTML header metadata（`verified`、`scope`、`status` 注释）不生产、不读取、不作为迁移输入；旧 `verified` 日期绝不写入验证登记。`timestamp` 表示内容语义变化时间，不是扫描或验证时间；新建或修改 Concept 不等于已验证，验证运行状态只由 `dev-docs-maintain` 写入 `docs/.okf/verification.json`。

- 文件路径就是 Concept ID；除非概念边界确实改变，不随意移动或重命名。
- 内部关系用标准 Markdown 链接表达，本仓库优先相对链接；外部资料、业务规则或第三方行为整理出的声明在 `# Citations` 保留来源。
- 仅在新增、移除、移动 Concept 或导航语义变化时更新 `index.md`；仅把长期有意义的变化写入 `log.md`。

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

## 什么时候需要更多证据

只读取支撑目标 Concept 所需的最小代码、测试、配置、Schema、ADR 和一阶链接；证据缺口明确时才扩大范围。写入后核对：frontmatter 与 `type`、内部链接、引用路径与关键声明的权威证据；只在语义变化时更新 `timestamp`。

消费测试（用无当前会话上下文的 fresh sub-agent，只给目标 Concept 与一阶链接，验证其能否仅凭文档完成真实任务）只在以下情况启用，不是每次写入的固定步骤：

- 新建或重构 Agent onboarding 入口、跨组件操作路径或面向读者的任务说明，且请求明确要求读者仅凭文档完成真实任务；
- 已知读者虽然看到正确术语，仍无法理解请求流、依赖边界、不变量或操作路径。

启用时提出 3–5 个真实问题（请求如何流转、哪些依赖被允许、修改前必须检查什么），核对回答与权威证据一致；读者失败就修订后重测，证据不足时保留未确认状态，不靠扩写猜测内容。

## 与其他知识维护 Skill 的绑定

本 Skill 负责知识语义。出现以下实际缺口时按需使用其他两者，不形成每次必跑的链：

- 需要验证登记、freshness 扫描、或结构性维护（frontmatter 迁移、Concept 移动/删除、registry 修复）→ `dev-docs-maintain`
- 仓库还没有 `docs/` Bundle 或项目记忆骨架 → 先由 `setup-power-agent` 初始化最小结构

普通语义写入（修订已有 Concept、补 ADR、补精确参考）可独立完成，不需要调用其他 Skill。

## 参考资料

| 资料 | 读取时机 |
|---|---|
| [OKF 规范](./references/okf-v0.1.md) | 判断 Concept、frontmatter、链接或 Bundle 最小合规时 |
| [项目 Docs Profile](./references/project-docs-profile.md) | 写入本仓库 `docs/`、选择 custom fields、处理 YAML 迁移或 freshness 策略时 |