---
name: finishing-a-development-branch
description: |-
  在实现完成后，作为分支处置决策器输出收尾选项与结构化结果：merge/PR/保留/丢弃。
  依赖调用方提供 verification_evidence；Triggers: 分支收尾, finishing, merge, PR, 保留分支, 丢弃工作.
version: 1.2.5
---

# Finishing a Development Branch

作为分支收尾决策器，只负责基于当前状态给出分支处置路径并返回结构化结果。

## Objective

### 做什么
- 收集分支收尾所需的最小状态：当前分支、候选 base branch、工作区状态、验证证据。
- 检测当前是否为普通 checkout、linked worktree 或 detached HEAD。
- 评估并展示处置路径：`本地合并` / `创建PR` / `保留分支` / `丢弃工作`；detached HEAD 时不展示直接本地合并选项。
- 在高风险路径（`丢弃工作`）执行前要求明确确认。
- 只清理来源明确、由本项目管理的 worktree。
- 返回统一且人类可读的收尾结果，供编排层消费。

### 不做什么
- 不提供或硬编码 git/gh 命令执行菜单。
- 不重复执行完整验证流程。
- 不在确认不充分时继续 destructive 路径。
- 不把 docs 同步提醒作为阻塞 gate。
- 不清理宿主环境、用户或其他工具创建的 worktree。

## Context & Tools

### 必要输入
- `verification_evidence`：绑定当前提交的验证结果（至少包含 `commit_sha`、`passed`、`verified_at`、`evidence[]`）。
- `branch_context`：当前分支、候选 base branch、ahead/behind 状态。
- `working_tree_state`：是否有未提交变更、是否存在未跟踪文件。
- `worktree_context`：当前 worktree 信息（如适用），至少包含 `path`、`is_linked_worktree`、`is_detached_head`、`worktree_source`、`managed_by`、`cleanup_allowed`。

### 处理原则
- 默认最小上下文，只消费当前决策所需信息。
- 缺失关键输入时返回 `BLOCKED`，并在 `blocking_issues` 中给出补齐要求。
- 可给出 docs 同步提醒，但仅进入 `advisories`。
- 当上游为 `verification-before-completion` 时：`commit_sha`、`passed`、`verified_at` 和 `evidence[]` 直接来自其输出字段。

## Constraints & Format

### 规则优先级（高→低）
1. 用户明确选择
2. 安全确认（尤其是 `丢弃工作`）
3. 输出格式完整性
4. 默认建议策略

### 状态机
1. `collect_state`
   - 汇总必要输入；缺失则转 `BLOCKED`。
2. `check_gate`
   - `verification_evidence` 不存在、`commit_sha` 与当前 HEAD 不匹配或 `passed=false` 时，不展示选项，输出 `BLOCKED`。
3. `detect_environment`
   - 判断普通 checkout / linked worktree / detached HEAD / 外部管理工作区。
4. `present_options`
   - 普通 checkout 或 named branch worktree：展示 4 个选项。
   - detached HEAD：展示 3 个选项（创建 PR / 保留 / 丢弃），不展示本地合并。
   - 同时说明不可执行选项的原因。
5. `confirm_destructive_if_needed`
   - 仅 `丢弃工作` 进入确认；确认失败则 `CANCELLED`。
6. `execute`
   - 执行用户选项并记录结果。
7. `cleanup_by_provenance`
   - 仅本地合并或丢弃路径考虑清理。
   - 只有 `worktree_source=power-agent` 且 `cleanup_allowed=true` 时才允许清理。
   - 路径位于 `.worktrees/`、`worktrees/` 或 `~/.config/power-agent/worktrees/` 只能作为辅助证据，不能单独触发删除。
   - `worktree_source=external|unknown` 或缺少 provenance 时必须跳过清理；缺少必需字段时返回 `BLOCKED` 并要求补齐。
   - 创建 PR 与保留分支路径始终保留 worktree，便于继续处理反馈。
8. `report`
   - 输出统一 contract。

### 默认建议策略
- 已准备共享：优先 `创建PR`。
- 本地快速收尾：`本地合并`。
- 需要延后处理：`保留分支`。
- 明确放弃工作：`丢弃工作`（必须确认）。

### 输出格式（必须完整）

完成任务后，用便于阅读的 Markdown 小节输出结果，不使用 YAML：

```markdown
## 分支收尾结果

状态：READY / BLOCKED / DONE / CANCELLED
选择：本地合并 / 创建PR / 保留分支 / 丢弃工作 / 未选择

### 验证证据
- commit_sha：<sha 或 未提供>
- 结果：通过 / 未通过 / 未提供
- 时间：<verified_at 或 未提供>

### 分支状态
- 当前分支：<current_branch 或 未提供>
- 目标基线：<base_branch 或 未提供>
- ahead/behind：<ahead_behind 或 未提供>

### 环境状态
- path：<当前执行工作区绝对路径；无则写 未提供>
- checkout 类型：普通仓库 / linked worktree / detached HEAD / 未确认
- is_linked_worktree：true / false / 未提供
- is_detached_head：true / false / 未提供
- worktree 来源：power-agent / external / unknown / none
- managed_by：using-git-worktrees / host / user / unknown / none
- cleanup_allowed：true / false / 未提供

### 工作区状态
- 工作区：clean / dirty / 未确认
- 未跟踪文件数：<number 或 未确认>

### 高风险操作
- 是否需要确认：是 / 否
- 是否已确认：是 / 否
- 目标：<target_summary 列表；无则写“无”>

### 清理结果
- worktree：已移除 / 已保留 / 不适用 / 跳过-外部管理 / 失败

### 阻塞项
- <code>：<message>
  - 需要动作：<required_action>

### 非阻塞建议
- [信息 / 警告] <message>

### 下一步
- 动作：用户确认 / 重新验证 / 打开PR / 完成
- 负责人：用户 / 代理
```

## References

- `references/options-template.md`：统一 4 选项展示文案，以及不可执行项的原因表达格式。
- `references/destructive-confirmation-template.md`：`丢弃工作`路径的高风险确认文案模板。
- `references/pr-template.md`：选择 `创建PR` 时的 PR 描述模板。
- `references/recovery-playbook.md`：阻塞/取消场景的恢复指引与最小恢复输出要求。

## Integration

- 常与 `verification-before-completion` 串联：先产出验证证据，再执行本 skill。
- 可由 `exec-plan-runner` 在实现完成后调用，消费结构化输出做后续编排。
- 与 `using-git-worktrees` 配套：创建阶段记录路径来源，收尾阶段按 provenance 决定是否清理。
