---
name: plan-impl-lightweight
description: |-
  轻量执行 Skill。处理边界清楚、可局部验证的中小任务；用户要求轻量执行、局部验证或中小任务执行时触发。
  Triggers: 轻量执行, 中小任务执行, 局部验证, proof-oriented 实现, 轻量审查, 升级 plan-impl.
---

# Lightweight Exec Path

面向中等偏小任务的轻量执行路径。目标是在不启动 team、多任务编排或恢复机制的情况下，仍保留边界检查、`proof-oriented-development`、局部验证和有限 review/fix 闭环。

---

## Objective

### 做什么

- 先执行 `scope_check`，判断任务是否适合轻量路径。
- 在边界清楚时，由主代理直接执行，或委派一个实现子代理执行。
- 实现阶段必须使用 `proof-oriented-development`。
- 完成后执行 targeted verification。
- 验证通过后进入轻量 review/fix 循环。
- 范围扩大、验证不可收敛或 review 阻塞时，升级到完整 `plan-impl`。

### 不做什么

- 不处理 team 编排、通用并行分发或多实现子代理协作。
- 不处理恢复点、batch、复杂依赖图或多阶段迁移。
- 不承担分支收尾、归档或合并前全量审查职责。
- 不在证据不足时输出完成声明。
- 不允许无限 review/fix 循环。

---

## Eligibility

### 进入条件

必须同时满足：

- 目标行为、允许修改范围、禁止范围和完成判据明确。
- 有至少一个可执行或可观察的验证方式。
- 通常只影响 1-3 个核心文件或一个局部模块。
- 无复杂跨模块依赖，无多阶段迁移。
- 无明显 team/并行收益，或收益低于协调成本。
- 不涉及安全、权限、密钥、支付、数据一致性或外部发布风险。
- 当前工作树变更可以安全区分本次任务边界。

### 禁止条件

出现任一情况，使用完整 `plan-impl`、`writing-plans` 或其它更合适路径：

- 需要拆分多个相互依赖的任务。
- 需要多个实现子代理并行协作。
- 需要架构决策、公共 API 大改、数据迁移或存储格式变更。
- 验证失败原因可能跨模块或根因不明。
- 预期需要多轮审查修复。
- 用户明确要求完整 exec-plan，或当前任务已属于复杂 active exec-plan。

---

## Protocol

### 1) scope_check

使用 `references/scope-check-template.md`。输出结论只能是：

- `LIGHTWEIGHT_OK`：可进入轻量路径。
- `USE_FULL_RUNNER`：升级完整 `plan-impl` 或先创建 exec-plan。
- `ASK_USER`：目标、范围、验收或验证方式缺失，需要用户澄清。

`scope_check` 失败时不要启动实现。

### 2) execute

执行模式：

- `MAIN_AGENT`：主代理直接执行，适合明确、局部、无需额外探索的改动。
- `SINGLE_IMPLEMENTER`：启动一个实现子代理，适合中等偏小但需要局部探索的任务。

`SINGLE_IMPLEMENTER` 使用 `references/task-card-template.md`，且必须遵守：

- 使用 `proof-oriented-development`。
- 不创建 commit、branch 或 worktree。
- 不扩大允许修改范围。
- 发现任务超出轻量条件时立即 `BLOCKED`，并建议 `escalate_to_full`。

### 3) targeted_verify

验证不固定命令菜单，按任务选择最小充分证据：

1. 用户或任务卡指定验证命令。
2. 受影响模块的局部测试。
3. 局部 lint、类型检查或格式检查。
4. 可观察手动验证，如 CLI 输出、生成文件、文档渲染或截图。

无法验证时不得返回 `DONE`。验证失败且根因局部清楚时，可进入一次 `fix_once`；验证失败且原因跨模块或不明时，升级完整流程或调试流程。


### 4) review

验证通过后执行轻量 review：

- 默认先由主代理自审。
- 满足任一条件时，可额外启动一个 reviewer：
  - 改动超过一个核心文件。
  - 修改公共接口、prompt 协议、测试基础设施或配置入口。
  - 实现结果为 `DONE_WITH_CONCERNS`。
  - targeted verification 覆盖不完整但可能接受。
  - 用户明确要求审查。

review 输出使用 `DONE / DONE_WITH_CONCERNS / BLOCKED`。

### 5) fix_once

轻量路径保留一个有上限的 review/fix 闭环：

```text
execute -> targeted_verify -> review -> fix_once -> targeted_verify -> review
```

- targeted verification 或 review 首次失败时，可进入一次 `fix_once`。
- 第二次仍失败、review 仍阻塞、需要扩大范围，或根因不再局部时，返回 `path_decision=escalate_to_full`。

### 6) final_verification_handoff

- 通过 targeted verification 和轻量 review 只证明局部增量，不等同于可对用户声明整个请求已完成。
- 仅当最终轻量 review 为 `DONE` 或 `DONE_WITH_CONCERNS` 且无 blocking issue 时，独立轻量路径才可继续：默认调用 `requesting-code-review`；只有用户明确要求跳过时才能跳过，并记录原因。审查通过后必须调用 `verification-before-completion`。
- 若本 Skill 由 `plan-impl` 调用，则返回局部证据，由完整编排器依次执行 `REVIEWING -> VERIFYING`。

---

## Output Contract

使用 `references/result-contract.md`。主输出必须包含：

```markdown
## Lightweight Exec Result

状态：DONE / DONE_WITH_CONCERNS / BLOCKED / UNKNOWN
path_decision：lightweight / escalate_to_full / ask_user
execution_mode：MAIN_AGENT / SINGLE_IMPLEMENTER / NONE

### Scope Check
- 结论：LIGHTWEIGHT_OK / USE_FULL_RUNNER / ASK_USER
- 原因：<一句话>
- allowed_scope：<文件/模块>
- forbidden_scope：<禁止范围>

### 证据
- [command / diff / test / review] <path、file:line 或 command>

### Verification
- 结论：PASSED / FAILED / INCONCLUSIVE
- 覆盖：<已覆盖行为>
- 未覆盖：<明确写出>

### Review
- 状态：self_reviewed / reviewer_done / blocked
- 摘要：<审查摘要>

### 阻塞项
- BI-xxx：<阻塞原因>
  - 影响范围：<impact>

### 非阻塞建议
- <建议；无则写“无”>

### 下一步
- 动作：proceed / fix_once / ask_user / escalate_to_full
- 交棒给：orchestrator / plan-impl / systematic-debugging / user
```

消费规则：

- `DONE`：必须有验证证据，review 已通过，且无 blocking issue。
- `DONE_WITH_CONCERNS`：必须有验证证据和 review 结果，可有非阻塞建议。
- `BLOCKED`：必须有 blocking issue，并说明是澄清、升级还是调试。
- `UNKNOWN`：用于超时、输出不可解析或异常终止；必须检查工作树残留后再决定 salvage、retry、revert 或升级。

---

## Handoff Rules

- 用户直接请求中等偏小任务时，可先用本 Skill 做轻量执行决策。
- `plan-impl` 可在 READY/EXECUTING 前调用本 Skill 处理低风险小批次。
- 本 Skill 只允许主代理执行或单实现子代理执行，不承担 team/batch 编排。
- targeted verification 可借用 `verification-before-completion` 的证据优先原则，但不承担最终分支收尾前全量验证。
- `path_decision=escalate_to_full` 时，返回给 `plan-impl` 或建议先用 `writing-plans` 创建完整 exec-plan。

---

## References

- `references/scope-check-template.md`：轻量路径准入检查。
- `references/task-card-template.md`：单实现子代理任务卡。
- `references/result-contract.md`：输出契约与消费规则。
- `references/stress-scenarios.md`：压力场景。
