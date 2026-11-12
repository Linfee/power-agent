---
type: Decision
status: superseded
verification:
  strategy: historical
supersedes:
  - 0010-judgment-oriented-skills.md
  - 0011-knowledge-navigation-lifecycle.md
superseded_by:
  - 0013-skill-invocation-and-hook-boundaries.md
  - ../0014-current-baseline.md
sources:
  - docs/archive/2026-11-11-matt-power-agent-fusion.md
  - AGENTS.md
  - skills/proof-oriented-development/SKILL.md
  - skills/implement-spec/SKILL.md
---

# ADR-0012: Matt 主干、整包组合与授权内连续推进

> 历史记录：已由 [ADR-0014](../0014-current-baseline.md) 归并取代，原有取代关系保留。下文的决定、状态说明与旧 Skill 名称保留当时含义，不作为当前指令。

**日期：** 2026-11-11

**后续决定（2026-11-12）：** [ADR-0013](0013-skill-invocation-and-hook-boundaries.md) 取代本记录的默认调用策略，收敛为 17 个模型可调用入口与 8 个手动入口，并明确 hook 先验证缺口再增强；其余融合原则由新决定继续采用。下文保留当时的决定与修订。

**同日后续修订：** 用户要求 `grilling` 与 `grill-with-docs` 恢复 Matt 固定版本原文及调用元数据。下文保留初次融合决定；其中“25 个均可模型调用”更新为 `grill-with-docs` 手动、其余可模型调用，讨论的完成与行动边界以原版问题树和用户共同理解确认为准。具体当时契约见[融合设计 S05/S06](../../archive/2026-11-11-matt-power-agent-fusion.md#s05-grilling)，其余融合决定不变。

**内容深度修订：** 用户进一步要求按 Matt 原版的篇幅设计，避免过度压缩。迁入内容改以固定原版正文与 references 为底稿，保留完整方法、理由、反例、示例和模板，仅在已确认的融合差异处局部改写。轻量衡量加载、重复、人工接力和状态成本，不以文件更短为目标；不设置等长配额，也不借恢复内容重引已否决的流程和授权政策。具体规则见[融合设计 §3.4](../../archive/2026-11-11-matt-power-agent-fusion.md#34-原版内容深度与删改判据)。

## 背景

用户选择以 Matt 的轻量工程能力和稳定内核为主干，保留 Power 的 POD、独有判断、项目知识与更高自动化。此前“普通 Skill 必须独立安装、仅知识子系统可具名协作”的政策会复制规则，也会让能力切换变成人工接力。用户已批准正式设计和本地迁移；旧 ADR 不是新目标的硬约束。

## 决定

- 平铺分发设计中的 25 个 Skill，均可由模型调用，允许同包具名依赖，不承诺单 Skill 安装，不引入品牌 router。
- 能力按需组合而非固定流水线。用户确认目标和必要取舍后，Agent 连续完成授权内的实现、证明、适用审查与修复；讨论、建议、计划与草稿仍不授权实施或发布。
- POD 保留名称，融合 Matt TDD；可自动验证的行为默认红绿重构，保留已知失败复用、绿色重构以及 UI/文档/机械变更的匹配证据。审查同时覆盖需求与工程；诊断保留因果证据资格；模块边界由真实复杂度和责任证明。
- 小任务及现成完整 issue 直接实现。需要持久调度时，选定 tracker 是唯一执行状态源，spec/tickets/地图表达目标与真实依赖；仓库文档保存知识，handoff 和计划只指向状态。
- 普通 sub-agent 使用新上下文，按依赖与写所有权并行，协调者负责整体验收。工作树协作是完整路径；Git 隔离、提交、发布、关闭和清理不由任务编排暗中授权。
- 普通知识按项目已有协议保存，不强制启用 Bundle。已有 Bundle 的来源、freshness、ledger 安全语义保持；OKF 只有一个 reference。知识导航的目标、历史覆盖和实际消费证据要求保留。
- 旧 `discuss`、`writing-plans`、`systematic-debugging`、`finish-development`、`writing-skills`、`harness-engineering-review` 退出并迁移当前消费者，不留别名。逐项归属见正式设计。

## 与历史决定的关系

本决定取代 [ADR-0010](0010-judgment-oriented-skills.md) 的独立安装/具名协作限制及旧能力划分，保留判断导向、真实证据、风险相称与不强制固定流程。

本决定取代 [ADR-0011](0011-knowledge-navigation-lifecycle.md) 的显式调用政策、协作例外和旧环境评估归属；知识导航初始化/演进的目标和证据要求保留，环境评估并入 `retro`。

ADR-0008 的固定 ordered ladder、旧 Gate 与固定审查轮数不恢复；复杂度需要当前依据、授权不能扩张、机器协议必须准确等仍成立。历史正文保留，不全仓替换当时的 Skill 名称。

## 后果与验收

同步入口、25 项索引、调用元数据、分发 catalog、脚本指针、现行文档和第三方署名。源版本固定，授权的本地退出完成后再发布；不迁移用户已安装目录或业务 tracker。

验收分开报告结构、脚本安全、实际行为、自然发现和外部服务。真实工具执行和产物才能证明推进与边界；少量场景不支持跨模型普遍收益，未验证宿主或远端操作必须明示。完整验证口径见正式设计与迁移计划。
