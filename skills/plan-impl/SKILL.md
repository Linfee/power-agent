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
- 在实现批次后执行 `conflict_check -> review -> fix loop`。
- 先通过 `requesting-code-review` 完成最终全量审查，再通过 `verification-before-completion` 输出 `verification_evidence`。
- 在收尾阶段串联 `finishing-a-development-branch`。

### 不做什么

- 不把 `review-contract.md` 当第二套计划。
- 不允许子代理创建 commit、branch 或 worktree。
- 不跳过验证、审查或分支收尾状态管理。

### 输入计划包

- 必须存在 `plan.md`：目标、Scope、关键决策、Agent 边界、Tasks、Proof、阻塞条件和风险。
- 必须存在 `review-contract.md`：执行时必读，但仅用于确认批准边界。
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

将恢复点写入 exec-plan：

```markdown
<!-- runner-state: EXECUTING -->
<!-- runner-batch: 2/4 -->
<!-- runner-phase: implement|conflict_check|review|fix -->
<!-- runner-fix-round: 1/3 -->
<!-- runner-next-action: <下一步动作> -->
```

恢复时优先读取这些标记与 Session Log 的“下一步”。

### 转移原则

- `BOOTSTRAP -> READY`：工作区/恢复点/基线检查可继续。
- `READY -> EXECUTING`：任务、依赖、Proof、阻塞条件可判定，且无致命 plan 缺陷。
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

- `状态=DONE/DONE_WITH_CONCERNS` 且 `path_decision=lightweight`：并入当前 batch 结果；若已完成全部任务，进入 `VERIFYING`。
- `状态=BLOCKED/UNKNOWN`、`path_decision=ask_user` 或 `path_decision=escalate_to_full`：停止轻量执行，补齐上下文、回到 full runner path，或升级给用户。
- 轻量路径的 `fix_once` 上限不改变 full runner path 的收敛判据。

---

## BOOTSTRAP / READY

### BOOTSTRAP

- 读取 `plan.md`、`review-contract.md`，按需读取 `context.md / tasks.md`。
- 调用 `using-git-worktrees` 检测或建立隔离工作区。
- 判断是否为恢复执行，并读取最近恢复点。
- 做最小基线检查；持续失败且无法定位可执行路径时 `ESCALATED`。

### READY

- 校验 `plan.md` 中任务、依赖、Proof、阻塞条件是否可判定。
- 若存在 `tasks.md`，校验其任务图与 `plan.md` 对齐。
- 判定当前计划是走轻量路径还是 full runner path。
- 若存在任务矛盾、关键验收缺失、边界冲突等致命缺陷，暂停执行并回到 `writing-plans` 或直接 `ESCALATED`。

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
- 子代理只在当前工作目录处理分配边界，不创建 commit、branch 或 worktree。
- 子代理统一返回：`DONE | DONE_WITH_CONCERNS | BLOCKED | UNKNOWN`。
- `BLOCKED/UNKNOWN` 时，先检查工作树残留，再决定补上下文重试、拆分任务、回退轻量路径或升级。

### conflict_check

在进入审查前强制执行：

- 检测同批次多子代理是否触碰同文件或共享出口文件。
- 文本冲突：进入合并处理。
- 语义冲突（无文本冲突但验证/测试失败）：退化为串行重排。

### review

- 启动规格符合性审查与代码质量审查。
- 使用 `references/spec-reviewer-prompt.md` 和 `references/code-quality-reviewer-prompt.md`。
- 内部 reviewer 只允许返回 `DONE / DONE_WITH_CONCERNS / BLOCKED`。
- `receiving-code-review` 只用于处理外部审查反馈，不属于此处内部协议。

### fix loop

- 有阻塞问题时启动新的修复子代理；不复用旧子代理。
- 每轮修复后回到 `review`。
- 若同类 `blocking_issues` 连续出现 >= 2 轮且无新证据，判定不收敛，进入 `ESCALATED`。
- 若问题数量或严重度持续下降，可继续修复回路；但总轮次最多 3 轮。

### 结果契约

- 实现/修复子代理的精确输出契约由 `references/implementer-prompt.md` 定义。
- 内部 reviewer 的精确输出契约由各自 reference prompt 定义。
- 主代理负责把子代理返回归一化为：`DONE / DONE_WITH_CONCERNS / BLOCKED / UNKNOWN`。

---

## Plan Amendment

当用户在执行中追加或修改需求：

1. 暂停新 batch 派发。
2. 记录变更到 Session Log（变更内容、影响范围、时间）。
3. 重新计算依赖图与 batch 划分。
4. 生成新的恢复点并继续。

已在跑的子代理允许完成后再判定是否保留产出；未启动任务按新 plan 重排。

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
- `dev-docs-maintain` 仅作为按需手动建议，不是固定阶段。

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
- `references/spec-reviewer-prompt.md`
  - `EXECUTING / review`：规格符合性审查。
- `references/code-quality-reviewer-prompt.md`
  - `EXECUTING / review`：代码质量审查。
- `references/progress-log-template.md`
  - 跨状态：batch 完成、进入 `ESCALATED` 前、Plan Amendment 后写入 Session Log。

使用规则：

- 正常路径默认 `concise`。
- `BLOCKED/UNKNOWN` 或关键冲突时升级 `detailed`。
- 多个审查 prompt 可组合，但输出必须仍可归一化到 runner 协议。
