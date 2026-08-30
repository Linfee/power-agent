---
name: implement
description: |-
  开发实施编排 Skill。执行或恢复会修改软件资产的开发计划——exec-plan、手写计划、任务清单或 spec；无计划的局部改动不走本 Skill。
  Triggers: 执行开发计划, 恢复开发实施, 推进计划执行, implement.
---

# Implement

开发计划的执行编排器：加载与恢复、批次调度、按需审查、验证、收尾与归档。服务已有计划的工作（L2 exec-plan，或用户给出的多任务清单）；没有计划的局部改动走 `proof-oriented-development`。

执行应该是无聊的：思考在上游（讨论与计划），纪律在 `proof-oriented-development`，本 Skill 只做编排者独有的判断。`code-review` 与 `verification-before-completion` 按风险升级，不是每条执行链的固定阶段。

## 输入

- **exec-plan**（`docs/exec-plans/` 下的 `plan.md + review-contract.md`）：`plan.md` 是执行真源，必须通过 Plan Review Gate（见下）。
- **其他计划**（讨论结论、手写计划、任务清单、spec）：目标、边界、验收、Proof 可判定即可执行。
- 没有计划的直接小改动：不经过本 Skill，走 `proof-oriented-development`。

根因未知的异常先交给 `systematic-debugging`；非开发工作不进入本 Skill。

## 准备

读计划材料（exec-plan 读 `plan.md`、`review-contract.md`，`context.md` / `tasks.md` 按需，冲突以 `plan.md` 为准）→ 需要隔离时用 git worktree 准备独立工作区（使用规则由项目或 harness 定义；不创建嵌套 worktree，agent 创建的记录来源）→ 最小基线检查（持续失败且无法定位可执行路径时升级）。

- 其他计划：动手前向用户复述理解（目标、边界、验收、Proof），确认后执行；要素欠缺时补齐或问用户；计划单薄但范围大、风险高时，建议先经 `writing-plans` 成型或请用户确认。
- 改动极小、明显不值得拆任务时，主代理直接处理。
- 致命计划缺陷（任务矛盾、关键验收缺失、边界冲突）：exec-plan 回 `writing-plans`，其他计划向用户补齐或升级。

### Plan Review Gate（仅 exec-plan）

只读 `review-contract.md` 的 Gate，不与 `plan.md` 对账。缺 contract、状态非法、或 medium/high 未 approved，不得执行：停在准备阶段，回 `writing-plans`。首次执行与恢复都校验。旧计划若两份都有 Gate 字段，以 contract 为准，不对 plan.md 做字段对齐。

| 风险 | 允许执行的最小 Gate |
|---|---|
| low | `Plan Review Status=SELF_REVIEWED`；`Independent Review` 为 `not_required` |
| medium / high | `Independent Review=approved` |

## 执行

内部循环：`实现 →（按需）冲突检查 / 审查 → (修复 → 审查)*`

- **调度**：独立任务并行派发；存在写冲突时串行或分批。
- **实现**：子代理使用 `references/implementer-prompt.md` 并经 `proof-oriented-development` 完成；派发前分配清晰边界，task brief 必须包含 Agent 自主边界（可自由决策 / 不可自行决策 / 不变量），缺则补齐后再派发。单任务不得含糊到需要子代理自行拆范围。单代理串行以工作区 diff + Proof 交接，不默认创建 `.power-agent/review-runs`。多 agent、并行或启用批次审查时，task brief 与 report 按 `references/review-artifact-protocol.md`。子代理返回 `DONE | DONE_WITH_CONCERNS | BLOCKED | UNKNOWN`——UNKNOWN 是编排器对超时、输出不可解析、异常终止的归类，implementer 主动返回为前三枚举；`BLOCKED / UNKNOWN` 先检查工作树残留，再决定补上下文重试、拆分任务或升级。
- **冲突检查**：启用批次审查，或同批次可能写同一文件 / 共享出口文件时执行；单代理串行且无共享写冲突可跳过。文本冲突合并处理，语义冲突退化为串行重排。
- **批次审查**：仅多 agent 并行、存在写冲突、或计划要求内审时启用。用 `scripts/review-package` 生成一次性 package（dirty worktree 含目标外改动时必须传显式 path scope）；一个只读 reviewer 按 `references/task-reviewer-prompt.md` 输出 Spec / Quality 双 verdict。Review Assets 只按 manifest 传入，校验与安全边界见 protocol；未提供 manifest 时不得扫描 `.power-agent`。单代理串行默认不做双 verdict。
- **修复**：修复子代理一次性；修复验证优先原 reviewer，替代 reviewer 带完整修复上下文；修复验证必须产生新双 verdict，修复实质改变范围或风险边界时重新发起完整内部审查。收敛判据：同类 blocking 连续 ≥2 轮且无新证据，或单任务总轮次 >3 → 不收敛，升级。
- plan-mandated defect 报告给用户决定，不因计划已写明而忽略，也不自行修成与计划相反。

用户在执行中变更需求时按 `references/plan-amendment.md` 处理；material 变化在相应 Gate 校验通过前不恢复调度。

## 审查 / 验证 / 收尾

- **审查 / 验证**：是否全量 `code-review`、是否跑 `verification-before-completion`，见 `AGENTS.md`。用户明确跳过审查时记录原因。阻塞反馈按 `code-review`「反馈评估」处理。
- **收尾**：exec-plan 完成需归档、用户要分支处置、或 dirty 需要待提交提示时调用 `finishing-a-development-branch`。`DONE` 时 exec-plan 从 `docs/exec-plans/active/` 归档到 `completed/`。Session Log 仅跨会话恢复或 `BLOCKED / UNKNOWN` 时记录。`dev-docs-maintain` 按需，不是固定阶段。

## 恢复与升级

恢复点写入 `plan.md` frontmatter 的 `runner` mapping（`state` / `batch` / `phase` / `fix_round` / `next_action`）；其他格式的计划写进计划文件本身，或在回复中明确记录下一步。恢复时读 mapping 与 Session Log 的“下一步”；缺失或不完整时从准备阶段重新判定，不猜旧状态。不再创建、读取或迁移旧式 runner HTML 注释。

子代理不创建 commit、branch 或 worktree；scratch artifacts 不进 commit、不当持久真源。

升级输出必须包含：事实摘要、已尝试恢复动作、可选决策（`replan / retry / abort`）。

## References

- `references/implementer-prompt.md`：实现子代理任务卡与返回契约。
- `references/review-artifact-protocol.md`：scratch workspace、task/report 交接、review package 与 Review Assets 协议。
- `references/task-reviewer-prompt.md`：单 reviewer 双 verdict 的输出契约。
- `references/plan-amendment.md`：执行中需求变更的 material 判定与 Gate 处理。
- `references/progress-log-template.md`：Session Log 格式；正常路径 concise，`BLOCKED / UNKNOWN` 或关键冲突时 detailed。
- `scripts/review-workspace` / `scripts/review-package`：scratch 目录与 review package 生成。
