---
name: dev-docs
description: |-
  当需要把已有代码或权威来源中的稳定系统事实、边界、决策依据或集成参考写入或修订 `docs/` 长期知识时使用。不要用于裸“写文档”、README/公告、会话记录或执行计划；软件资产变更的开发计划交给 writing-plans。
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

- 会修改代码、测试、配置、自动化、Skill/prompt 或开发工作流的实施、重构、迁移计划：委派给 `writing-plans`，不得在本 Skill 中再建计划；纯文档维护、知识重组或普通任务不进入 exec-plan。
- 临时讨论、一次性排障过程、会话级执行细节：默认不进入长期知识库。
- 局部且显然的实现细节：让代码和测试表达；只有它形成稳定边界、不变量、跨文件关系或后续工作约束时才文档化。
- README 营销内容、发布公告、纯代码注释和没有长期消费场景的普通文稿不属于本 Skill。

分类含混时，以“未来 Agent 如何使用这项知识”而非关键词判断；只有选择会改变权威来源或生命周期时才需要澄清。

## 路由判定

先按任务要改变的对象路由，不按“写文档”“更新文档”等关键词路由：

| 请求目标 | 去向 |
|---|---|
| 新建或修订稳定系统事实、领域边界、Playbook、Reference、ADR | `dev-docs` |
| 检查既有 Bundle 健康、验证 freshness、修复扫描发现的漂移、登记验证 | `dev-docs-maintain` |
| 移动、拆分、合并 Concept 或重构目录 | `dev-docs-maintain` 的 `full-maintain`；若同时改变知识语义，再由 `dev-docs` 修订内容 |
| 软件资产变更的实施、重构或迁移计划 | `writing-plans` |
| 共同起草 RFC、Proposal、普通设计文档并做读者验证 | `doc-coauthoring` |
| README、CHANGELOG、发布公告、营销文稿 | 不属于本 Skill |
| 私有实现调整且职责、边界、公开契约和不变量未变 | 无需长期文档变更 |

用户只说“更新文档”且没有指出变化的事实、来源、现有 Concept 或未来消费场景时，不得猜测并写入；先返回 `needs-evidence`，只补齐会改变权威来源或生命周期的最小证据。

## 知识角色与典型位置

沿用仓库已有布局，优先更新现有 Concept，不为满足分类表机械创建目录。

| 知识角色 | 表达内容 | 典型位置 | 推荐 OKF type |
|---|---|---|---|
| 系统模型 | 当前系统边界、组件、依赖、运行与部署关系 | `docs/architecture.md` 或 `docs/architecture/` | `System` / `Architecture` |
| 领域知识 | 项目术语、模型、职责、关系与不变量 | `docs/domain/` 或现有 context 文档 | `Domain` / `Concept` / `Rule` |
| 开发运行方式 | 构建、测试、调试、生成与发布所需的稳定流程 | `docs/development.md` 或 `docs/development/` | `Playbook` / `Process` |
| 精确参考 | API、配置、Schema、命令、第三方集成与来源摘要 | `docs/references/` 或相关模块目录 | `Reference` / `API Endpoint` |
| 决策历史 | 有真实替代方案且会长期约束实现的决定 | `docs/adr/NNNN-slug.md` | `Decision` |
| 执行状态 | 当前工作的目标、任务、证明与恢复点 | `docs/exec-plans/` | 委派给 `writing-plans` |

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

## 可选消费测试

消费测试验证“未来 Agent 能否仅凭文档完成真实任务”，不替代事实核对、freshness 扫描或 verification 登记。仅在以下情况启用：

- 新建或重构 Agent onboarding 入口、跨组件操作路径或面向读者的任务说明，且请求明确要求读者仅凭文档完成真实任务；
- 已知读者虽然看到正确术语，仍无法理解请求流、依赖边界、不变量或操作路径。
- 普通功能完成后的事实回写默认跳过消费测试；仅出现新的重试语义、状态不变量或模块边界，并不等于出现了读者任务变化或理解缺口。不能只因 Concept 类型重要、术语复杂或涉及多个模块就机械启用。

小型精确参考、机械 metadata 修正和不影响跨文件理解的局部事实更新默认跳过。启用时：

1. 基于目标消费场景提出 3–5 个真实问题或任务，例如请求如何流转、哪些依赖被允许、修改前必须检查什么。
2. 启动没有当前会话上下文的 fresh sub-agent，只提供目标 Concept 与必要的一阶链接；不得把作者侧解释补进 prompt。
3. 核对回答是否与权威证据一致，并检查歧义、隐含前提、矛盾和导航缺口。
4. 若读者失败，修订对应 Concept 后用相同问题重测；证据不足时保留 `BLOCKED`，不得靠扩写猜测内容。
5. 当 fresh reader 能稳定回答且不再暴露新缺口时通过；该结果只证明可消费性，需要 freshness 登记时仍交给 `dev-docs-maintain`。

## 执行流程

1. **定位长期知识**：读取 `AGENTS.md`、相关入口和 `docs/index.md`（如存在），判断是更新当前事实、记录 ADR、补来源，还是将软件资产变更的开发计划交给 `writing-plans`。
2. **建立最小证据集**：读取目标 Concept、直接链接、相关 ADR 与直接相关的代码、测试、配置和 Schema；先应用敏感资料边界。
3. **修订权威 Concept**：当前事实直接描述现在是什么；已有稳定 Concept 优先更新；仅在知识确实独立且长期复用时新建。
4. **维护决策、链接与来源**：ADR 只记录真实且耐久的权衡；accepted ADR 不重写历史，改变决定时新建 ADR 并建立 supersede 关系。补充有语义的链接、Citations、必要的 index/log。
5. **核对可消费性**：检查 YAML frontmatter、非空 `type`、内部链接、引用路径与关键声明的权威证据；命中高价值或已知理解缺口时执行可选消费测试并修订到通过。只在语义变化时更新 `timestamp`；需要 freshness 登记时交给 `dev-docs-maintain`。

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
