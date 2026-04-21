---
name: finishing-a-development-branch
description: |-
  在实现完成后，作为分支处置决策器输出收尾选项与结构化结果：merge/PR/保留/丢弃。
  依赖调用方提供验证证据；本 skill 不内嵌命令脚本。
version: 1.2.0
---

# Finishing a Development Branch

作为分支收尾决策器，只负责基于当前状态给出分支处置路径并返回结构化结果。

## Objective

### 做什么
- 收集分支收尾所需的最小状态：当前分支、候选 base branch、工作区状态、验证证据。
- 评估并展示 4 类处置路径：`本地合并` / `创建PR` / `保留分支` / `丢弃工作`。
- 在高风险路径（`丢弃工作`）执行前要求明确确认。
- 返回统一输出 contract，供编排层消费。

### 不做什么
- 不提供或硬编码 git/gh 命令执行菜单。
- 不重复执行完整验证流程。
- 不在确认不充分时继续 destructive 路径。
- 不把 docs 同步提醒作为阻塞 gate。

## Context & Tools

### 必要输入
- `verification_evidence`：绑定当前提交的验证结果（至少包含 `sha`、`passed`、`timestamp`）。
- `branch_context`：当前分支、候选 base branch、ahead/behind 状态。
- `working_tree_state`：是否有未提交变更、是否存在未跟踪文件。
- `worktree_context`：当前 worktree 信息（如适用）。

### 处理原则
- 默认最小上下文，只消费当前决策所需信息。
- 缺失关键输入时返回 `BLOCKED`，并在 `blocking_issues` 中给出补齐要求。
- 可给出 docs 同步提醒，但仅进入 `advisories`。
- 当上游为 `verification-before-completion` 时：`passed = (status == DONE)`，`sha` 来自 `commit_sha` 字段，`timestamp` 来自 `evidence[0].timestamp`。

## Constraints & Format

### 规则优先级（高→低）
1. 用户明确选择
2. 安全确认（尤其是 `丢弃工作`）
3. 输出 contract 完整性
4. 默认建议策略

### 状态机
1. `collect_state`
   - 汇总必要输入；缺失则转 `BLOCKED`。
2. `check_gate`
   - `verification_evidence` 不存在、`sha` 不匹配或 `passed=false` 时，不展示选项，输出 `BLOCKED`。
3. `present_options`
   - 展示可执行选项与不可执行原因。
4. `confirm_destructive_if_needed`
   - 仅 `丢弃工作` 进入确认；确认失败则 `CANCELLED`。
5. `execute`
   - 执行用户选项并记录结果。
6. `report`
   - 输出统一 contract。

### 默认建议策略
- 已准备共享：优先 `创建PR`。
- 本地快速收尾：`本地合并`。
- 需要延后处理：`保留分支`。
- 明确放弃工作：`丢弃工作`（必须确认）。

### 输出 contract（必须完整）
```yaml
status: READY | BLOCKED | DONE | CANCELLED
selected_option: 本地合并 | 创建PR | 保留分支 | 丢弃工作 | null
evidence:
  verification:
    sha: string | null
    passed: boolean | null
    timestamp: string | null
  branch_state:
    current_branch: string | null
    base_branch: string | null
    ahead_behind: string | null
  working_tree:
    clean: boolean | null
    untracked_count: number | null
destructive_action:
  required: boolean
  confirmed: boolean
  target_summary: string[]
cleanup_result:
  worktree: 已移除 | 已保留 | 不适用 | 失败
blocking_issues:
  - code: string
    message: string
    required_action: string
advisories:
  - level: 信息 | 警告
    message: string
next_action:
  type: 用户确认 | 重新验证 | 打开PR | 完成
  owner: 用户 | 代理
```

## References

- `references/options-template.md`：统一 4 选项展示文案，以及不可执行项的原因表达格式。
- `references/destructive-confirmation-template.md`：`丢弃工作`路径的高风险确认文案模板。
- `references/pr-template.md`：选择 `创建PR` 时的 PR 描述模板。
- `references/recovery-playbook.md`：阻塞/取消场景的恢复指引与最小恢复输出要求。

## Integration

- 常与 `verification-before-completion` 串联：先产出验证证据，再执行本 skill。
- 可由 `exec-plan-runner` 在实现完成后调用，消费结构化输出做后续编排。
