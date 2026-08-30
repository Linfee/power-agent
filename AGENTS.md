# Power-Agent — Agent 指南

Power-Agent 是面向前沿模型的 Constraint + Verification + Domain Knowledge pack（融合 superpowers 与 Harness Engineering）。完整多阶段编排是 L2 升级能力，不是默认身份。

## 快速参考

- **类型**: AI Agent Skill / 可升级 harness pack
- **Skills**: 13 个可复用 Skill
- **支持平台**: Claude Code, Cursor, Factory, Droid, Gemini, OMP / Codex 类宿主
- **默认姿态**: 单强代理 + 系统外证据；编排与双重审查仅在可靠性边界升级（ADR-0009）

## 架构概览

能力按规划 / 实现 / 审查 / 基础设施分层，**按需加载**，不是每条任务都跑满层。详见 [docs/architecture.md](docs/architecture.md)。

## 知识库导航

| 主题 | 位置 | 说明 |
|------|------|------|
| 系统架构 | [docs/architecture.md](docs/architecture.md) | 模块划分、依赖方向、子代理模式 |
| 开发指南 | [docs/development.md](docs/development.md) | 环境搭建、Skill 开发、文件命名 |
| 工作流机制 | [docs/workflow.md](docs/workflow.md) | Skill 协调、产出物流转、反模式 |
| Harness 体系 | [docs/harness-engineering.md](docs/harness-engineering.md) | 设计哲学、知识库结构、标准工作流 |
| Skill 设计 | [docs/skill-and-harness-design.md](docs/skill-and-harness-design.md) | Skill 结构规范、Harness 设计原则 |
| ADR | [docs/adr/](docs/adr/) | 历史架构决策记录 |
| 执行计划 | [docs/exec-plans/](docs/exec-plans/) | active/ 进行中，completed/ 已归档 |
| 讨论结论 / Spec 文档 | discuss / 用户 | 默认内联讨论结论；按需落盘 `docs/specs/` |

项目记忆消费纪律：产出物命名领域概念时使用 `CONTEXT.md` 原词，不漂移同义词（缺口记录后交 `dev-docs`）；产出与既有 ADR 矛盾时显式声明，不静默覆盖；`CONTEXT.md` / `docs/adr/` 缺失时静默继续，不建议预先创建。

## 核心工作流

**适用范围：** 软件资产变更（代码、测试、配置、自动化、Skill/prompt 或开发工作流）。“计划 / 待办 / 任务拆解”本身不触发 exec-plan。

### 默认分层（先选最早充分层级）

| 层级 | 何时 | 路径 |
|---|---|---|
| **L0（默认）** | 局部、边界清楚、单轮可完成 | `proof-oriented-development` 或主代理直做 → 最小验证 → 短证据 |
| **L1** | 单模块、边界清楚的中等改动 | 讨论结论或短任务卡 → 直做（POD）；仅已有多任务计划时才 `implement` → 短证据；审查按需一次 |
| **L2** | 跨模块 / 多批次 / 跨会话 / 高风险 / 需人审恢复点 | `writing-plans` 薄 exec-plan → `implement` → 风险相称审查 → 完成前验证 → 分支收尾 |

```
L0/L1（多数任务）
  直做 + 短证据
  合主或高风险时升级全量审查；创建 PR 按重要性分层。VBC 要新鲜证据

L2（少数任务）
  discuss（按需）→ writing-plans → implement
    → POD + 按需内审 → code-review（风险相称）→ 工作区检查 → VBC → 分支收尾
```

**调试路径**: `systematic-debugging` →（FIXABLE + 授权匹配）`proof-oriented-development` → 风险相称审查 → 工作区检查 → 完成前验证（L0 可在短证据足够时收束）。

**非开发路由：** 根因未知先 `systematic-debugging`；长期项目知识用 `dev-docs` / `dev-docs-maintain`；研究、运营等用宿主原生清单。按当前主要交付物选单一入口。

**审查与完成证明:** 证据必须来自模型外且新鲜。短 Proof 为默认。全量 `code-review` 与独立终审在合并主分支、高风险、L2 或用户要求时升级；创建 PR 按重要性分层（低/中一次常规审查，高才增强+终审）——不是每条 L0 实现的固定税。完整 VBC 在合并/PR、高风险、L2 或对外宣称完成时升级。用户明确要求跳过审查时记录原因。`dev-docs-maintain` 仅按需，不是固定阶段。

## Skill 速查

| Skill | 用途 | 触发词 |
|-------|------|--------|
| `discuss` | 通用讨论：任何需要想清楚再行动的问题（产品、架构、方案、营销等），行动前讨论、澄清与对齐 | '讨论', '需求讨论', 'brainstorming' |
| `writing-plans` | 创建包含验收与验证路径的开发 compact exec-plan | '创建开发 exec-plan', '开发任务拆解' |
| `codebase-design` | 具体模块的接口、深度、seam / adapter 与可观察测试表面判断 | '模块设计', '接口收敛', 'seam', 'port', '端口设计' |
| `implement` | 执行或恢复任何开发计划（exec-plan、手写计划、任务清单或 spec） | '执行开发计划', '恢复开发实施' |
| `systematic-debugging` | 探索式根因调查：以因果证据、安全边界和风险相称的性能/稳定性证据约束修复交接 | 'bug', '测试失败', '性能退化', 'flaky', 'debug' |
| `proof-oriented-development` | 证明导向开发闭环：小步实现、最小相关验证、交付 Proof Block | '实现功能', 'Proof Block', '最小有效验证' |
| `code-review` | 全量代码审查编排与审查反馈评估 | '代码审查', 'code review', '审查反馈' |
| `verification-before-completion` | 完成前审计 Proof Block 并输出 verification_evidence | '完成前验证', 'verification', 'Proof Block 审计' |
| `dev-docs` | 长期开发知识回写 | '文档知识沉淀', 'ADR 记录', 'dev-docs' |
| `dev-docs-maintain` | Docs Bundle 健康检查、漂移修复与验证登记 | 'docs 健康检查', '验证登记', '文档漂移修复', 'dev-docs-maintain' |
| `setup-power-agent` | 项目初始化 | 手动调用 |
| `harness-engineering-review` | 实践审查 | 手动调用 |
| `writing-skills` | 创建/修改/验证 Skill | '写skill', '修改skill' |
| `finishing-a-development-branch` | dirty / 无 HEAD 待提交提示；clean 验证后 merge/PR/保留/丢弃 | '分支收尾', 'finishing', '合并到目标分支', '创建 PR' |

## 约束（硬规则）

| 规则 | 说明 |
|------|------|
| 依赖方向 | 只能从上层指向下层，禁止反向 |
| 默认分层 | 先 L0/L1；仅可靠性不足时升 L2（ADR-0009） |
| 子代理生命周期 | 实现/修复子代理一次性；启用 reviewer 时同 session 优先原 reviewer 验证 findings（ADR-0007） |
| 规划 Gate | 仅 L2 exec-plan：low self-review；medium/high 独立审查通过后方可执行（ADR-0006） |
| 证据优先 | 没有运行验证不得声称完成；完成证明外置于模型 |
| 根因优先 | 没有根本原因分析没有修复 |
| Skill description 长度 | 硬上限约 110 token、目标 ~100；改动后运行 `scripts/check-description-length.py`（cl100k 近似估算，误差 ±10） |

## 文档规范

**YAML frontmatter（仅 `docs/` Knowledge Bundle 内的 Concept Document）**:
```yaml
---
type: Concept # 替换为能表达文档用途的非空类型
scope:
  - architecture
status: active # 按生命周期需要添加
---
```

`docs/` 中除 `index.md` / `log.md` 外的 Concept 必须有非空 `type`；`scope` 和 `status` 仅在有实际语义时填写。验证运行状态由 `docs/.okf/verification.json` ledger 维护，不写入 Concept。Bundle 外的 `AGENTS.md`、`CONTEXT.md` / `CONTEXT-MAP.md` 不应机械添加 frontmatter。ADR 使用 `type: Decision`，并以 YAML `status` 表示 `accepted`、`proposed` 或 `superseded` 等历史状态。

**命名约定**:
- Skill 主文件: `SKILL.md` (大写)
- ADR: `0001-slug.md`
- Spec: `YYYY-MM-DD-topic.md`
- Exec-plan: `YYYY-MM-DD-title/`

## 工作流约定

- **L0/L1 不强制** `docs/exec-plans/`；仅 L2（跨模块、多批次、跨会话或高风险）才创建开发执行计划。
- 开发任务完成后，将 exec-plan 从 `active/` 移动到 `completed/`。
- 跨会话 L2 执行接近极限时，更新 exec-plan 进度并提醒用户；L0/L1 不写 session 仪式日志。
- 重大变更后，检查 docs/ 相关文档是否需要同步更新。
- 需要文档维护时，由 `dev-docs-maintain` 按需触发；它不是每次开发的固定阶段。
- ADR 保留历史决策与 YAML lifecycle status；决策过期时用新 ADR supersede。与 ADR-0003 的**默认义务**冲突时以 [ADR-0009](docs/adr/0009-lean-default-orchestration.md) 为准（0003 文本保留、不标 superseded）；其余默认解读冲突时以更新的 accepted ADR 为准。
- Concept 的验证运行状态以 `docs/.okf/verification.json` ledger 为准；来源变化或策略到期时运行验证，不把旧日期迁入文档。
- Harness 随模型/宿主升级做 ablation：先问可删的默认组件，再加编排。

## 上游追踪

| 项目 | 来源 |
|------|------|
| superpowers | github.com/obra/superpowers |
| Harness Engineering | openai.com/index/harness-engineering |
