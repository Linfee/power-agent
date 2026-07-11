---
name: plan-impl
description: |-
  Exec-plan 执行 Skill。执行或恢复 compact exec-plan，并完成实现、审查、验证和收尾；用户要求执行计划或恢复执行时触发。
  Triggers: 执行 exec-plan, 恢复执行, run plan, plan-impl.
---

# Plan Implementation

作为 exec-plan 执行编排器，负责加载与恢复、依赖分析、批次调度、审查收敛、验证、收尾与归档。

---

## Scope

### 做什么

- 使用状态机执行或恢复执行 exec-plan。
- `plan.md` 作为执行真源；`review-contract.md` 作为人审边界；按需读取 `context.md / tasks.md`。
- 优先检测并使用 team 模式；不可用时回退并行子代理或单子代理。
- 对中等偏小、边界清楚、验证方式明确的任务，可调用 `plan-impl-lightweight`。
- 在实现批次后执行 `conflict_check -> 单 reviewer 双 verdict -> fix loop`。
- 通过 scratch artifacts 交接 task brief、实现报告和 review package，避免把大段内容复制进 dispatch prompt。
- 先通过 `requesting-code-review` 完成最终全量审查，再通过 `verification-before-completion` 输出 `verification_evidence`。
- 在收尾阶段串联 `finishing-a-development-branch`。

### 不做什么

- 不把 `review-contract.md` 当第二套计划。
- 不允许子代理创建 commit、branch 或 worktree。
- 不把 scratch artifacts 当作 durable source of truth 或纳入 commit。
- 不跳过验证、审查或分支收尾状态管理。

### 输入计划包

- 必须存在 `plan.md`：目标、Scope、关键决策、Agent 边界、Tasks、Proof、阻塞条件和风险。
- 必须存在 `review-contract.md`：执行时必读，用于确认计划边界与审查记录。
- `context.md` 可选：补充证据缓存，不覆盖 `plan.md`。
- `tasks.md` 可选：仅用于复杂任务图、多 Agent 分发或长交接。
- 任一拆分文档与 `plan.md` 冲突时，以 `plan.md` 为准；若冲突影响执行，回到 `writing-plans` 修订。

---

## State Machine

主状态：
`BOOTSTRAP -> READY -> EXECUTING -> REVIEWING -> VERIFYING -> FINALIZING -> DONE`

异常状态：
`ESCALATED | CANCELLED`

子代理异常结果：
`UNKNOWN`（超时、输出不可解析、异常终止）

### 状态持久化

将恢复点写入 `plan.md` 顶部 YAML frontmatter 的 `runner` mapping：

```yaml
runner:
  state: EXECUTING
  batch: 2/4
  phase: implement # implement | conflict_check | review | fix
  fix_round: 1/3
  next_action: <下一步动作>
```

恢复时优先读取该 mapping 与 Session Log 的“下一步”。不再创建、读取或迁移旧式 runner HTML 注释；缺少或不完整的 `runner` mapping 时，从 `READY` 重新判定，而不是猜测旧状态。

### 转移原则

- `BOOTSTRAP -> READY`：工作区/恢复点/基线检查可继续。
- `READY -> EXECUTING`：任务、依赖、Proof、阻塞条件可判定，Plan Review Gate 已通过，且无致命 plan 缺陷。
- `EXECUTING -> REVIEWING`：所有 batch 完成，且内部阻塞问题已清零。
- `REVIEWING -> VERIFYING`：`requesting-code-review` 通过，或用户明确要求跳过并记录原因。
- `VERIFYING -> FINALIZING`：`verification-before-completion` 返回 `DONE` 且 `passed=true`。
- `FINALIZING -> DONE`：`finishing-a-development-branch` 返回 `DONE`，且归档完成。
- 任一阶段遇到 plan 致命缺陷、修复不收敛、验证不可恢复或前提失效导致超范围影响，进入 `ESCALATED`。
- `FINALIZING` 若用户取消收尾或拒绝 destructive 确认，进入 `CANCELLED`。

---

## Path Selection

进入 `EXECUTING` 前先做路径选择：

- `plan-impl-lightweight`：中等偏小、边界清楚、低风险、targeted verification 足以判断局部完成。
- full runner path：多 batch、复杂依赖、需要 team 协作、需要完整审查修复循环或最终证据导向验证。

轻量路径返回映射：

- `状态=DONE/DONE_WITH_CONCERNS` 且 `path_decision=lightweight`：并入当前 batch 结果；若已完成全部任务，进入 `REVIEWING`。
- `状态=BLOCKED/UNKNOWN`、`path_decision=ask_user` 或 `path_decision=escalate_to_full`：停止轻量执行，补齐上下文、回到 full runner path，或升级给用户。
- 轻量路径的 `fix_once` 上限不改变 full runner path 的收敛判据。

---

## BOOTSTRAP / READY

### BOOTSTRAP

- 读取 `plan.md`、`review-contract.md`，按需读取 `context.md / tasks.md`。
- 读取 `plan.md` 的 `Plan Risk` 与 `review-contract.md` 的 `Plan Review Gate`；它们是执行许可，不是仅供展示的 planning 记录。
- 调用 `using-git-worktrees` 检测或建立隔离工作区。
- 判断是否为恢复执行，并读取最近恢复点。
- 做最小基线检查；持续失败且无法定位可执行路径时 `ESCALATED`。

### READY

- 校验 `plan.md` 中任务、依赖、Proof、阻塞条件是否可判定。
- 若存在 `tasks.md`，校验其任务图与 `plan.md` 对齐。
- 强制校验 Plan Review Gate；所有首次执行和恢复执行都走这一步，不能因用户直接调用 `plan-impl` 而绕过。
- 判定当前计划是走轻量路径还是 full runner path。
- 若存在任务矛盾、关键验收缺失、边界冲突等致命缺陷，暂停执行并回到 `writing-plans` 或直接 `ESCALATED`。

### Plan Review Gate

先比较两份计划材料中同名的 `Gate Revision`、`Plan Risk`、`Review Path`、`Plan Review Status`、`Independent Review` 与 `Independent Review Basis` 字段。Independent Review 的 basis 按状态与 revision/history 校验。任一必需字段缺失、枚举非法、两份材料冲突或独立审查 revision/history 不匹配，都是致命 plan 缺陷：保持在 `READY`，写入恢复点并回到 `writing-plans`；不得选择轻量路径、派发任务或恢复旧 batch。

| 风险 | 允许进入 `EXECUTING` 的最小 Gate |
|---|---|
| `low` | `plan_review_status=SELF_REVIEWED`；Independent Review 为 `not_required`。 |
| `medium` | `plan_review_status=APPROVED`；独立审查为 `approved` 且有可定位依据。 |
| `high` | `plan_review_status=APPROVED`；独立审查为 `approved` 且有可定位依据。 |

`PENDING_INDEPENDENT_REVIEW`、`ISSUES_FOUND`、`pending`、`issues_found`、缺失 basis 或任意不一致都不允许执行。legacy plan 缺少 Gate 字段时同样回到 `writing-plans` 做最小补齐；不要以“旧计划”作为例外。

---

## EXECUTING

内部流程：
`implement -> conflict_check -> review -> (fix -> review)*`

### 调度原则

- 优先检测并使用 team 模式。
- 若 team 能力缺失、创建失败或不支持共享上下文，记录降级原因并回退。
- 无 team 时，按 batch 并行启动实现子代理；无法安全并行时，改为单个实现子代理推进。
- 并发上限始终不超过 3。
- 主代理仅在改动极小、明显不值得拆任务时直接处理。

### implement

- 所有实现子代理必须使用 `references/implementer-prompt.md`，并通过 `proof-oriented-development` 完成实现。
- 主代理必须在派发前分配清晰边界；单任务不得含糊到需要子代理自行拆范围。
- 按 `references/review-artifact-protocol.md` 创建 task brief 和 report path；任务全文只写入 brief，完整 Proof Block 只写入 report。
- 子代理只在当前工作目录处理分配边界，不创建 commit、branch 或 worktree。
- 子代理统一返回：`DONE | DONE_WITH_CONCERNS | BLOCKED | UNKNOWN`。
- `BLOCKED/UNKNOWN` 时，先检查工作树残留，再决定补上下文重试、拆分任务、回退轻量路径或升级。

### conflict_check

在进入审查前强制执行：

- 检测同批次多子代理是否触碰同文件或共享出口文件。
- 文本冲突：进入合并处理。
- 语义冲突（无文本冲突但验证/测试失败）：退化为串行重排。

### review

- 使用 `scripts/review-package` 为当前 task/batch 生成一次性 review package；dirty worktree 含目标外改动时必须传入显式 path scope。
- 启动一个只读内部 reviewer，使用 `references/task-reviewer-prompt.md` 一次读取 task brief、实现 report 和 review package，分别输出 `Spec Compliance` 与 `Code Quality` verdict。
- `Spec=FAIL` 或 `Quality=NEEDS_FIXES` 时返回 `BLOCKED`；两个 verdict 通过但含 `Cannot Verify From Diff` 时返回 `DONE_WITH_CONCERNS`，由主代理逐项核实后才能完成当前 task/batch。
- reviewer 不重复 implementer 已运行的测试，不接受 implementer rationale 或 orchestrator 预判，不修改工作树/HEAD；只有明确 named risk 才扩大到 diff 外 focused check。
- plan-mandated defect 必须报告并交给用户决定，不能因计划已写明而忽略，也不能自行修成与计划相反。
- `receiving-code-review` 只用于处理外部审查反馈，不属于此处内部协议。

### fix loop

- 有阻塞问题时启动新的修复子代理；不复用旧子代理。
- 每轮修复后回到 `review`。
- 若同类 `blocking_issues` 连续出现 >= 2 轮且无新证据，判定不收敛，进入 `ESCALATED`。
- 若问题数量或严重度持续下降，可继续修复回路；但总轮次最多 3 轮。

### 结果契约

- 实现/修复子代理的精确输出契约由 `references/implementer-prompt.md` 定义。
- 内部 reviewer 的精确输出契约由 `references/task-reviewer-prompt.md` 定义。
- 主代理负责把子代理返回归一化为：`DONE / DONE_WITH_CONCERNS / BLOCKED / UNKNOWN`。

---

## Plan Amendment

当用户在执行中追加或修改需求：

1. 暂停新 batch 派发。
2. 判断是否为 material amendment。任何 Scope、Acceptance、Plan Risk、Key Decisions、Agent 自主边界、Proof、Blockers / Escalation 或 Risks / Rollback 的变化都是 material；只修正文案且不改变这些语义时才是 non-material。
3. 记录变更到 Session Log（变更内容、material 判定、影响范围、时间）。
4. non-material 时重新计算依赖图与 batch 划分，保留现有 Gate。
5. material 时冻结所有未启动任务，更新 `plan.md` 与 `review-contract.md`，先将两份材料的 Gate Revision 从 `rN` 同步递增为 `rN+1`，保留不可改写的 `Gate Revision rN` history，追加 `Gate Revision rN+1` history 并清除旧 basis，然后重新计算风险并重新 self-review：
   - 重评为 `low`：更新为 `SELF_REVIEWED`，并确认 Independent Review 为 `not_required`；
   - 重评为 `medium`：更新为 `PENDING_INDEPENDENT_REVIEW`，清除旧 independent-review basis；
   - 重评为 `high`：更新为 `PENDING_INDEPENDENT_REVIEW`，清除旧 independent-review basis；独立审查通过后直接转为 `APPROVED`。
6. material amendment 完成相应 Gate 校验前不得恢复调度；通过后重新计算依赖图与 batch 划分，并生成新的恢复点。

已在跑的子代理允许完成后再判定是否保留产出，但 material amendment 下其产出不得作为恢复调度的许可；未启动任务按新 plan 重排。

---

## Layered Context Strategy

- `L1`：任务目标、验收、约束、相关文件路径。
- `L2`：单一缺口补充（关键接口、失败日志、必要片段）。
- `L3`：仅用于 `BLOCKED/UNKNOWN` 或关键冲突诊断。

原则：成功路径保持 concise；阻塞路径再扩展上下文。

---

## REVIEWING

- 默认调用 `requesting-code-review`；仅当用户明确要求跳过时可跳过，并在 Session Log 记录原因。
- 审查返回 `阻塞` 或 `需澄清` 时，按 `receiving-code-review` 评估反馈，采纳修复项后重新审查。
- 修复审查反馈后不得沿用旧验证证据；审查通过后进入 `VERIFYING` 重新生成最终 `verification_evidence`。

---

## VERIFYING

- 调用 `verification-before-completion`。
- 消费实现子代理返回的 Proof Block 或等价证据块。
- 审计 Proof Block，必要时补跑最小额外验证。
- 输出 `verification_evidence`：`commit_sha`、`passed`、`verified_at`、`evidence[]`。
- 只有 `DONE && passed=true` 才能进入 `FINALIZING`。
- `PARTIAL/BLOCKED` 时，根据 next_action 回流到追加修复、调试、回到 `writing-plans` 或重跑最小验证。

---

## FINALIZING / ARCHIVE

### FINALIZING

- 调用 `finishing-a-development-branch`。
- 消费其四态输出：
  - `READY`：展示 `merge / PR / keep / discard` 选项，写入恢复点，等待用户选择。
  - `BLOCKED`：先补齐状态；验证证据问题回到 `VERIFYING`，分支/worktree/base 问题补齐后重试一次，仍失败则 `ESCALATED`。
  - `CANCELLED`：停止收尾，保留现状，并写入恢复点。
  - `DONE`：继续归档。

### ARCHIVE

- 将 exec-plan 从 `docs/exec-plans/active/` 移动到 `completed/`。
- 在 `## Session Log` 中记录执行摘要与后续文档同步建议。
- `dev-docs-maintain` 是在 docs 健康检查、漂移修复或 verification ledger 登记需要时按需触发的普通 Skill，不是固定阶段。

---

## Escalation

以下情况进入 `ESCALATED`：

- plan 致命缺陷。
- 修复回路不收敛。
- 验证不可恢复。
- plan 前提失效导致超范围影响。

升级输出必须包含：

- 事实摘要。
- 已尝试恢复动作。
- 可选决策（`replan / retry / abort`）。

---

## References

- `using-git-worktrees`
  - `BOOTSTRAP` 阶段：检测/建立隔离工作区。
- `plan-impl-lightweight`
  - `READY / EXECUTING` 阶段：处理中等偏小、低风险任务。
- `references/implementer-prompt.md`
  - `EXECUTING / implement`：实现子代理任务卡与 Proof Block 契约。
- `references/review-artifact-protocol.md`
  - `EXECUTING`：scratch workspace、task/report handoff、review package 与恢复边界。
- `scripts/review-workspace` / `scripts/review-package`
  - `EXECUTING`：创建自忽略 scratch 目录，并按 base + path scope 生成工作树 review package。
- `references/task-reviewer-prompt.md`
  - `EXECUTING / review`：单 reviewer 一次读取 diff，分别输出规格符合性与代码质量 verdict。
- `references/review-stress-scenarios.md`
  - 后续真实模型 eval：controller 预判、Cannot Verify From Diff、失败 verdict 无 finding。
- `references/progress-log-template.md`
  - 跨状态：batch 完成、进入 `ESCALATED` 前、Plan Amendment 后写入 Session Log。

使用规则：

- 正常路径默认 `concise`。
- `BLOCKED/UNKNOWN` 或关键冲突时升级 `detailed`。
- 内部 task/batch 审查固定使用单 reviewer 双 verdict；最终全分支审查仍由 `requesting-code-review` 独立执行。
