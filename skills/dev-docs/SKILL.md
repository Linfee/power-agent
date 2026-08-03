---
name: dev-docs
description: |-
  当需要把已有代码或权威来源中的稳定系统事实、边界、决策依据或集成参考写入或修订 `docs/` 长期知识时使用。不要用于裸“写文档”、README/公告、会话记录或执行计划。
  Triggers: 文档知识沉淀, 系统事实回写, ADR 记录, 集成参考, dev-docs.
---

# 维护长期开发知识

把 `docs/` 维护为 Agent 可检索、可验证、可持续修正的外部记忆。只处理会在未来工作中复用的长期知识，不以产出泛化文稿为目标。

## 边界

本 Skill 负责：

- 描述系统当前状态：架构、领域模型、模块边界、关键流程、开发方式与精确参考。
- 记录无法从当前代码恢复的长期决策原因（ADR）。
- 代码或设计变化后，把新的长期事实回写到已有 Concept。
- 维护 Concept 链接、来源、目录索引与必要的变更日志。
- 接收消费侧信号：探索或产出中发现的术语缺口与同义词漂移（补入 `CONTEXT.md` 或领域 Concept）；经用户确认重开的 ADR 冲突（新建 ADR 并建立 supersede 关系）。

不属于本 Skill：

- 纯文档维护、知识重组不进入 exec-plan。
- Bundle 健康检查、漂移修复、验证登记 → `dev-docs-maintain`。
- README、CHANGELOG、发布公告不属于本 Skill。
- 临时讨论、一次性排障过程、会话级执行细节——不进长期知识库。
- 局部且显然的实现细节——让代码和测试表达；只有形成稳定边界、不变量、跨文件关系或后续工作约束时才文档化。

分类含混时，以“未来 Agent 如何使用这项知识”判断，不按关键词；只有选择会改变权威来源或生命周期时才需要澄清。用户只说“更新文档”且没有指出变化事实、来源或消费场景时，不得猜测写入，返回 `needs-evidence`，只补齐会改变权威来源或生命周期的最小证据。

## 知识角色与位置

沿用仓库已有布局，优先更新现有 Concept，不为满足分类表机械创建目录：

| 知识角色 | 表达内容 | 典型位置 | 推荐 OKF type |
|---|---|---|---|
| 系统模型 | 系统边界、组件、依赖、运行与部署关系 | `docs/architecture.md` 或 `docs/architecture/` | `System` / `Architecture` |
| 领域知识 | 术语、模型、职责、关系与不变量 | `docs/domain/` 或现有 context 文档 | `Domain` / `Concept` / `Rule` |
| 开发运行方式 | 构建、测试、调试、生成与发布的稳定流程 | `docs/development.md` 或 `docs/development/` | `Playbook` / `Process` |
| 精确参考 | API、配置、Schema、命令、第三方集成与来源摘要 | `docs/references/` 或相关模块目录 | `Reference` / `API Endpoint` |
| 决策历史 | 有真实替代方案且长期约束实现的决定 | `docs/adr/NNNN-slug.md` | `Decision` |

## 证据与敏感资料边界

- 只读取支撑目标 Concept 所需的最小代码、测试、配置、Schema、ADR 和一阶链接；证据缺口明确时才扩大范围。
- 不把密钥、令牌、认证头、会话 Cookie、个人数据、客户标识符、私有 URL query、原始日志或受限资料复制进 `docs/`、示例或 Citations。
- 用已脱敏的事实、合成示例和不含凭据的 canonical resource 表达；需要可追溯性时指向受控来源的稳定名称或路径，而不是泄露内容。
- 无法在不泄露敏感资料的前提下建立可审查来源时，保留该事实未确认，并在输出风险中说明访问前提；不得以模型记忆补足。

## OKF 写入约定

- `docs/` 是主 Bundle；`index.md` 和 `log.md` 是导航与目录变更日志，不是普通 Concept。
- 除 `index.md`、`log.md` 外，元数据唯一权威是文件顶部 YAML frontmatter，`type` 必须非空；`title`、`description`、`tags`、`timestamp`、`scope`、`sources`、`verification`、`status`、`owners` 按需要写入。
- 已弃用的 HTML header metadata（`verified`、`scope`、`status` 注释）不生产、不读取、不作为迁移输入；旧 `verified` 日期绝不写入验证登记。
- `timestamp` 表示内容语义变化时间，不是扫描或验证时间；验证运行状态只由 `dev-docs-maintain` 写入 `docs/.okf/verification.json`，新建或修改 Concept 不等于已验证。
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

## 何时读取参考资料

| 资料 | 读取时机 |
|---|---|
| [OKF 规范](./references/okf-v0.1.md) | 判断 Concept、frontmatter、链接或 Bundle 最小合规时 |
| [项目 Docs Profile](./references/project-docs-profile.md) | 写入本仓库 `docs/`、选择 custom fields、处理 YAML 迁移或 freshness 策略时 |

## 可选消费测试

消费测试验证“未来 Agent 能否仅凭文档完成真实任务”，不替代事实核对、freshness 扫描或验证登记。仅在以下情况启用：

- 新建或重构 Agent onboarding 入口、跨组件操作路径或面向读者的任务说明，且请求明确要求读者仅凭文档完成真实任务；
- 已知读者虽然看到正确术语，仍无法理解请求流、依赖边界、不变量或操作路径。

普通功能完成后的事实回写默认跳过——出现新的重试语义、状态不变量或模块边界，不自动等于读者任务变化或理解缺口。小型精确参考、机械 metadata 修正和不影响跨文件理解的局部更新也默认跳过。

启用时：

1. 基于目标消费场景提出 3–5 个真实问题（请求如何流转、哪些依赖被允许、修改前必须检查什么）。
2. 启动没有当前会话上下文的 fresh sub-agent，只提供目标 Concept 与必要一阶链接，不把作者侧解释补进 prompt。
3. 核对回答与权威证据一致，检查歧义、隐含前提、矛盾和导航缺口。
4. 读者失败就修订后重测；证据不足时保留 `BLOCKED`，不靠扩写猜测内容。
5. fresh reader 能稳定回答且不再暴露新缺口时通过；需要 freshness 登记仍交给 `dev-docs-maintain`。

## 执行流程

1. **定位长期知识**：读 `AGENTS.md`、相关入口和 `docs/index.md`，判断是更新事实、记录 ADR 还是补来源。
2. **建立最小证据集**：读目标 Concept、直接链接、相关 ADR 与直接相关的代码、测试、配置、Schema；先应用敏感资料边界。
3. **修订权威 Concept**：当前事实直接描述现在是什么；已有稳定 Concept 优先更新；仅在知识独立且长期复用时新建。
4. **维护决策、链接与来源**：ADR 只记录真实且耐久的权衡；accepted ADR 不重写历史，改变决定时新建 ADR 并建立 supersede 关系。补充有语义的链接、Citations 和必要的 index/log。
5. **核对可消费性**：检查 frontmatter、非空 `type`、内部链接、引用路径与关键声明的权威证据；命中消费测试条件时执行并修订到通过。只在语义变化时更新 `timestamp`；需要 freshness 登记交给 `dev-docs-maintain`。

## 输出 contract

最终输出为 Markdown，按顺序包含六个二级标题；没有内容时写“无”或“无需”，不省略：

1. `## 状态`：`DONE` / `DONE_WITH_CONCERNS` / `BLOCKED` + 一句结论。
2. `## 范围`：实际检查或修改的 Concept、来源和明确排除项。
3. `## 变更/修复`：创建、更新、删除或确认无需变更的长期知识及其语义。
4. `## 证据`：核对过的权威来源、链接/frontmatter 检查和已执行的验证；未执行的不得声称完成。
5. `## 剩余问题/风险`：未确认事实、敏感资料访问限制、broken link 或知识漂移。
6. `## 下一步`：明确动作；无需动作写“无需”。
