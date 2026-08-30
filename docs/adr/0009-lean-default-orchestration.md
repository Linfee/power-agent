---
type: Decision
status: accepted
---

# ADR-0009: Lean Default 与可靠性边界编排

**状态：** accepted（不 supersede 既有 ADR；与 0003 默认义务冲突时以本 ADR 为准）  
**日期：** 2026-08-28  
**影响文件：** `AGENTS.md`, `docs/architecture.md`, `docs/workflow.md`, `docs/harness-engineering.md`

## 背景

Power-Agent 早期默认叙事接近完整 Workflow OS：`discuss → writing-plans → implement → 批次审查 → 全量 code-review → VBC → 收尾`。在前沿模型与宿主 runtime（compaction、checkpoint、resume、native multi-agent）条件下，generic planning、session handoff 仪式、双重审查和默认 scratch 交接的边际收益下降，固定阶段税上升。

ADR-0006 已把「实现前人工批准」收成规划 Gate + 实现自主，但默认路径仍偏重。需要在不放弃证据外置与高风险约束的前提下，把**默认强度**与**升级能力**分开。

## 约束

- 完成声明仍须有模型外、可复现的新鲜证据
- 根因未知不得直接修复；高风险（安全、数据、权限、破坏性 API、不可逆操作）不得因“模型变强”取消独立约束
- 工程不变量、ADR、验收入口仍以仓库为 canonical store
- 不在本 ADR 中重写各 Skill 的逐步实现细节；运行时行为以后续 skill 契约变更为准
- 历史 ADR 保留；本 ADR 修正其**默认解读**，不静默删除既有能力

## 决定

### 1. 产品身份

Power-Agent 是面向前沿模型的 **Constraint + Verification + Domain Knowledge** pack，附带按需升级的编排能力；不是默认编排一切的 Workflow OS。

### 2. 默认路径分层（L0 / L1 / L2）

| 层级 | 何时 | 默认路径 |
|---|---|---|
| **L0** | 局部、边界清楚、单轮可完成 | 主代理（或 `proof-oriented-development`）直做 → 最小相关验证 → 短证据 |
| **L1** | 单模块/边界清楚的中等改动 | 短任务卡或讨论结论 → 直做（POD）；仅已有多任务计划时才 `implement` → 短证据；审查按需一次 |
| **L2** | 跨模块、多批次、跨会话、高风险、需人审恢复点 | 薄 exec-plan + Gate → `implement` 编排 → 风险相称审查 → 完成前证据审计 → 分支收尾 |

路由口令：先选最早充分层级；只有可靠性边界不够时才升级，不因“更完整”默认抬到 L2。

### 3. 原则重述（默认解读）

| 主题 | 新默认解读 |
|---|---|
| 仓库真相 | **工程 canonical store 仍是 repo**；运行时还可消费 CI/issue/观测/宿主 session 等权威源。权威源须 machine-legible；不是“宇宙唯一只认 git 里的 md” |
| 产出物协调（ADR-0003） | **Durable artifact** 用于跨会话、跨 vendor、高风险、人审与恢复；同会话 L0/L1 以 git diff + 短证据即可，不作每个 hop 的 session 仪式 |
| 上下文交接 | pull-based；scratch review artifacts / manifest **仅多 agent 或 L2 审查**启用，非默认 |
| 审查 | 合并为**风险相称的一次审查**为默认目标；全量 `code-review` 与独立终审是合并主分支、高风险或用户要求时的升级，不是每条实现链的固定税。创建 PR 按重要性分层：低/中一次常规审查，高才增强+终审 |
| 完成证明 | 短 Proof 默认；长 Proof / 完整 VBC 在 bugfix、性能、安全、数据、公共 API、对外宣称完成或 L2 时加码 |
| 人类决策 | 人类保留意图、不可逆、授权边界与高风险取舍；不默认审批 decomposition、generic loop 与每次 handoff |
| Ablation | 模型或宿主升级后，先问**可以删除哪些默认组件**，再考虑加编排 |

### 4. 与既有 ADR 的关系

- **不 supersede** ADR-0001 / 0004 / 0008：执行单元、精简 AGENTS、契约优先层级最小仍然成立
- **限定解读** ADR-0003：产出物协调保留为能力，不再解读为“每个阶段默认落盘”。**与 0003 的默认义务冲突时，以本 ADR 为准；0003 文本保留，不标 superseded。**
- **延续** ADR-0006：规划可执行性 Gate 与实现自主；本 ADR 把审查/计划/交接的默认义务同样降为升级触发
- **ADR-0007** 仍约束“一旦启用 reviewer 时”的连续性；不强制 L0/L1 启用 reviewer

## 后果

- `AGENTS.md` / `workflow.md` / `architecture.md` / `harness-engineering.md` 以 L0 为默认叙事，全链路标为 L2 升级
- `code-review` / `verification-before-completion` / `implement` / `proof-oriented-development` / `writing-plans` / `discuss` 的触发与交接已按分层收紧。其余 Skill 若仍偏旧默认，以本 ADR + AGENTS 路由为准
- 高风险与证据外置不因 lean default 放宽
- 创建 PR 不再自动等于全量审查；VBC 在合并/PR 路径上的证据审计不变
- 不引入新的运行时状态机或强制 feature_list primitive
