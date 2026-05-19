---
name: exec-plan-runner
description: |-
  自主执行或恢复执行 exec-plan：默认先并行委派，不能并行时委派单个子代理推进、冲突检测、审查修复收敛、全量验证、分支收尾与归档。
  Triggers: 执行 exec-plan, 恢复执行, run plan, exec-plan-runner.
version: 1.2.5
---

# Exec-Plan Runner

作为 exec-plan 执行编排器，负责加载与恢复、依赖分析、批次调度、审查收敛、验证与收尾。

---

## Scope

### 要做什么

- 使用状态机执行或恢复执行 exec-plan
- 将实现/修复子代理返回统一为人类可读的结构化结果
- 默认优先并行委派；不能并行时委派单个 sub-agent 继续推进
- 在并行批次后执行冲突检测，再进入审查
- 用收敛判据控制审查-修复循环
- 支持执行中需求变更（Plan Amendment）
- 采用分层上下文策略，控制上下文预算

---

## State Machine

主状态：
`BOOTSTRAP -> READY -> EXECUTING -> VERIFYING -> FINALIZING -> DONE`

异常状态：
`ESCALATED | CANCELLED`

子代理异常结果状态：
`UNKNOWN`（超时、输出不可解析、异常终止）

### 状态持久化（写入 exec-plan）

```markdown
<!-- runner-state: EXECUTING -->
<!-- runner-batch: 2/4 -->
<!-- runner-phase: implement|conflict_check|review|fix -->
<!-- runner-fix-round: 1/3 -->
<!-- runner-next-action: <下一步动作> -->
```

恢复时优先读取上述标记与 Session Log 的“下一步”。

---

## State Transitions

- `BOOTSTRAP -> READY`
  - `using-git-worktrees` 已确认隔离工作区、决定在当前工作区执行，或明确返回可继续
  - 恢复点可判定
  - 基线检查可用（命令成功或已确认可继续）

- `BOOTSTRAP -> ESCALATED`
  - 基线检查持续失败且无法定位可执行路径

- `READY -> EXECUTING`
  - 依赖图与 batch 划分完成
  - 无致命 plan 缺陷

- `READY -> ESCALATED`
  - plan 存在致命缺陷（任务矛盾、关键验收缺失、边界冲突）

- `EXECUTING -> EXECUTING`
  - 当前 batch 完成但仍有后续 batch

- `EXECUTING -> VERIFYING`
  - 所有 batch 完成，且审查阻塞问题已清零

- `EXECUTING -> ESCALATED`
  - 同类阻塞问题连续出现且无收敛
  - plan 前提失效（超出预期关键范围）

- `VERIFYING -> FINALIZING`
  - 全量验证通过

- `VERIFYING -> EXECUTING`
  - 验证失败且可修复（作为追加修复批次回流）

- `VERIFYING -> ESCALATED`
  - 验证反复失败且无法收敛

- `FINALIZING -> FINALIZING`
  - `finishing-a-development-branch` 返回 `READY`
  - 已展示 merge / PR / keep / discard 选项，正在等待用户选择或确认
  - 写入恢复点：`runner-state=FINALIZING`，`runner-next-action=user_select_finish_option`

- `FINALIZING -> VERIFYING`
  - `finishing-a-development-branch` 返回 `BLOCKED`
  - 阻塞原因是 `verification_evidence` 缺失、过期、`commit_sha` 与当前 HEAD 不匹配或 `passed=false`
  - 写入恢复点：`runner-state=VERIFYING`，`runner-next-action=rerun_verification`

- `FINALIZING -> ESCALATED`
  - `finishing-a-development-branch` 返回 `BLOCKED`
  - 阻塞原因是分支上下文、worktree provenance 或 base branch 无法可靠恢复，且补齐状态后仍不可继续
  - 写入恢复点：`runner-state=ESCALATED`，`runner-next-action=escalate_to_user_with_blockers`

- `FINALIZING -> CANCELLED`
  - `finishing-a-development-branch` 返回 `CANCELLED`
  - 用户取消分支处置、拒绝 destructive 确认，或明确要求停止收尾
  - 保留分支与 worktree，不归档为完成；写入恢复点：`runner-state=CANCELLED`，`runner-next-action=user_resume_or_abort`

- `FINALIZING -> DONE`
  - `finishing-a-development-branch` 返回 `DONE`
  - 分支处置完成且归档完成

---

## 统一结果格式

所有实现/修复子代理统一返回：

```markdown
## 子代理结果

状态：DONE / DONE_WITH_CONCERNS / BLOCKED / UNKNOWN

### 证据
- [command / diff / test / review] <path、sha 或 command>

### 阻塞项
- BI-xxx：<阻塞原因>
  - 影响范围：<impact>

### 非阻塞建议
- <建议内容>

### 下一步
- 动作：retry / split / proceed / escalate
- 负责人：orchestrator / implementer / reviewer / verifier
```

规则：
- `DONE` / `DONE_WITH_CONCERNS`：默认 concise
- `BLOCKED` / `UNKNOWN`：必须 detailed，并附最小复现证据
- 子代理原始状态归一化：
  - `DONE` -> `DONE`
  - `DONE_WITH_CONCERNS` -> `DONE_WITH_CONCERNS`
  - `BLOCKED` -> `BLOCKED`
  - 旧提示词或模型输出的 `NEEDS_CONTEXT` -> `BLOCKED`，并生成 `BI-needs-context`
  - 超时、异常终止或无法解析 -> `UNKNOWN`

审查 prompt 使用 runner 内部审查协议，必须返回 `DONE / DONE_WITH_CONCERNS / BLOCKED`。
若内部审查输出 `通过 / 通过_含建议 / 阻塞 / 需澄清` 等外部全量审查状态，视为协议错误：标记为 `UNKNOWN`，生成 `BI-invalid-review-protocol`，并启动重新审查；若输出中已有明确阻塞证据，主代理可保守转为 `BLOCKED` 处理，但仍必须修正 prompt 后复审。

---

## EXECUTING 内部流程

`implement -> conflict_check -> review -> (fix -> review)*`

### 1) implement

- 优先按 batch 并行启动实现子代理；无法并行时，改为单个实现子代理逐任务推进
- 主代理仅在改动极小、明显不值得拆分为任务时直接处理
- 所有实现子代理在同一工作目录工作，不拥有独立 worktree 或 branch。
- 主代理必须在派发前分配清晰边界：单任务不得含糊到需要子代理自行拆解范围
- 子代理不得自行创建 commit；完成后只报告修改内容、验证证据和文件列表，由主代理统一检查、整合与提交。
- 子代理使用 `test-driven-development`
- 返回 `DONE | DONE_WITH_CONCERNS | BLOCKED | UNKNOWN`

`BLOCKED/UNKNOWN` 处理：
- 先检查工作树残留（`git status` / `git diff`）
- 判定重试路径：补充上下文重试 / 任务拆分 / 升级

### 2) conflict_check（新增强制节点）

在进入审查前执行：
- 检测同批次多子代理是否触碰同文件/共享出口文件
- 文本冲突：进入合并处理
- 语义冲突（无文本冲突但测试失败）：退化为串行重排

### 3) review

- 并行启动审查子代理（规格符合性 + 代码质量）
- 子代理使用 `references/spec-reviewer-prompt.md` 和 `references/code-quality-reviewer-prompt.md`；`receiving-code-review` 仅用于收到审查反馈后的采纳/驳回评估。

### 4) fix + 收敛判据

有阻塞问题时进入修复回路：
- 启动新的修复子代理，不重用旧子代理
- 每轮修复后回到 review

收敛判据（替代纯固定轮次）：
- 若同类 `blocking_issues` 连续出现 >= 2 轮且无新证据，判定不收敛 -> `ESCALATED`
- 若问题数量/严重度持续下降，可继续修复回路
- 仍保留上限保护：修复回路最多 3 轮

---

## Plan Amendment（执行中变更协议）

当用户在执行中追加/修改需求：

1. 暂停新 batch 派发
2. 记录变更到 Session Log（变更内容、影响范围、时间）
3. 重新计算依赖图与 batch 划分
4. 生成新的恢复点并继续

已在跑的子代理：
- 允许完成后再判定是否保留产出
- 未启动任务按新 plan 重排

---

## Layered Context Strategy

- **L1 (default/minimal)**：任务目标、验收、约束、相关文件路径
- **L2 (targeted)**：补单一缺口（关键接口/失败日志/必要片段）
- **L3 (detailed)**：仅用于 `BLOCKED/UNKNOWN` 或关键冲突诊断

原则：
- 默认不下发“任务全文 + 大段代码 + 全量命令输出”组合包
- 成功路径尽量 concise，阻塞路径再扩展上下文

---

## VERIFYING / FINALIZING / ARCHIVE

### VERIFYING

- 启动验证子代理（`verification-before-completion`）
- 输出验证矩阵（命令、摘要、结论）
- 失败可回流到 `EXECUTING` 形成追加修复批次

### FINALIZING

- 合并/PR 前默认调用 `requesting-code-review`；仅当用户明确要求跳过时可跳过，并在 Session Log 记录原因。
- 使用 `finishing-a-development-branch`
- 走用户决策 Gate（merge / PR / keep / discard）
- 消费 `finishing-a-development-branch` 的四态输出：
  - `READY`：展示选项后暂停，保留 `runner-state=FINALIZING` 与 `runner-next-action=user_select_finish_option`，等待用户选择后恢复。
  - `BLOCKED`：先按阻塞项补齐状态；验证证据问题回到 `VERIFYING`，分支/worktree 上下文问题补齐后重试一次，仍失败则 `ESCALATED`。
  - `CANCELLED`：停止收尾并保留现状，记录 `runner-state=CANCELLED` 与 `runner-next-action=user_resume_or_abort`。
  - `DONE`：继续 `ARCHIVE`。

### ARCHIVE

- 将 exec-plan 从 `docs/exec-plans/active/` 移动到 `completed/`
- 在 exec-plan 的 `## Session Log` 中记录执行摘要与后续文档同步建议
- `dev-docs-maintain` 仅作为按需手动文档维护建议，不是每次开发执行的固定阶段

---

## Escalation Triggers

以下触发 `ESCALATED`：
- plan 致命缺陷
- 修复回路不收敛
- 验证不可恢复
- plan 前提失效导致超范围影响

升级输出必须包含：
- 事实摘要
- 已尝试恢复动作
- 可选决策（replan / retry / abort）

---

## Reference Prompts Usage

以下 references 按状态与触发条件使用，不是固定顺序脚本。

- `using-git-worktrees`
  - 状态：`BOOTSTRAP`
  - 触发：执行或恢复 exec-plan 前
  - 用途：检测现有隔离、优先使用内置 worktree 工具、建立或跳过隔离工作区；git worktree fallback 细节由 `skills/using-git-worktrees/references/manual-worktree-setup.md` 维护

- `implementer-prompt.md`（`references/implementer-prompt.md`）
  - 状态：`EXECUTING / implement`
  - 触发：启动实现子代理
  - 用途：约束实现范围、测试策略与结构化回报

- `spec-reviewer-prompt.md`（`references/spec-reviewer-prompt.md`）
  - 状态：`EXECUTING / review`
  - 触发：需要判定是否满足计划验收标准
  - 用途：规格符合性审查（是否做对）

- `code-quality-reviewer-prompt.md`（`references/code-quality-reviewer-prompt.md`）
  - 状态：`EXECUTING / review`
  - 触发：规格审查通过后，或与规格审查并行执行
  - 用途：代码质量审查（可读性、可维护性、实现质量）

- `progress-log-template.md`（`references/progress-log-template.md`）
  - 状态：跨状态
  - 触发：batch 完成、进入 `ESCALATED` 前、Plan Amendment 后
  - 用途：统一写入 Session Log，保证可恢复性

使用规则：
- 正常路径默认 `concise`
- `BLOCKED/UNKNOWN` 或关键冲突时升级 `detailed`
- 多个审查 prompt 可组合，但输出必须回填“统一结果格式”
