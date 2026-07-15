---
name: finishing-a-development-branch
description: |-
  分支收尾 Skill。工作区 dirty 或仓库尚无 HEAD 时先给出友好的待提交提示；clean 且验证通过后给出 merge/PR/保留/丢弃选项。实现完成并需要处置分支时触发。
  Triggers: 分支收尾, finishing, 完成后合并, 提交并 push 后合并, 合并到 test/master/目标分支, 完成后创建 PR/MR, 发起 PR/MR, 保留分支, 丢弃已完成工作.
---

# Finishing a Development Branch

作为分支收尾决策器，只负责基于当前状态给出分支处置路径并返回结构化结果。

## Objective

### 做什么
- 先检查工作区；dirty 或无 HEAD 时提示提交，否则收集标准分支处置所需状态。
- 检测当前是否为普通 checkout、linked worktree 或 detached HEAD。
- 评估并展示处置路径：`本地合并` / `创建PR` / `保留分支` / `丢弃工作`；detached HEAD 时不展示直接本地合并选项。
- 在破坏性路径（`丢弃工作`）执行前要求明确确认。
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
- `working_tree_state`：是否有未提交变更、是否存在未跟踪文件、`has_head`（仓库是否已有 HEAD 提交）。
- `verification_evidence`：绑定当前提交的验证结果（至少包含 `commit_sha`、`passed`、`verified_at`、`evidence[]`）；仅 clean 工作区进入标准分支处置时需要。
- `branch_context`：当前分支、候选 base branch、ahead/behind 状态；仅标准分支处置时需要。
- `worktree_context`：当前 worktree 信息（如适用），至少包含 `path`、`is_linked_worktree`、`is_detached_head`、`worktree_source`、`managed_by`、`cleanup_allowed`；仅标准分支处置时需要。

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
   - 先读取 `working_tree_state`，不预取标准路径的其他输入。
2. `route_worktree`
   - dirty（含 staged、unstaged、untracked）或 `has_head=false`：按 `references/options-template.md#未提交改动展示` 输出提示，返回内部 handoff `READY / mode=uncommitted / selection=unselected / options=[commit_then_continue]`；不运行或展示完成前验证。
   - clean 且 `has_head=true`：补齐标准路径输入并进入 `check_gate`；缺失则 `BLOCKED`。
   - `commit_then_continue` 仍需提交授权；提交后回到 `collect_state`，不得直接进入验证。
3. `check_gate`
   - `verification_evidence` 不存在、`commit_sha` 与当前 HEAD 不匹配或 `passed=false` 时，不展示标准处置选项，输出 `BLOCKED`。
4. `detect_environment`
   - 判断普通 checkout / linked worktree / detached HEAD / 外部管理工作区。
5. `present_options`
   - 普通 checkout 或 named branch worktree：展示 4 个选项。
   - detached HEAD：展示 3 个选项（创建 PR / 保留 / 丢弃），不展示本地合并。
   - 同时说明不可执行选项的原因。
6. `confirm_destructive_if_needed`
   - 仅 `丢弃工作` 进入确认；确认失败则 `CANCELLED`。
7. `execute`
   - 执行用户选项并记录结果。
8. `cleanup_by_provenance`
   - 仅本地合并或丢弃路径考虑清理。
   - 只有 `worktree_source=power-agent` 且 `cleanup_allowed=true` 时才允许清理。
   - 路径位于 `.worktrees/`、`worktrees/` 或 `~/.config/power-agent/worktrees/` 只能作为辅助证据，不能单独触发删除。
   - `worktree_source=external|unknown` 或缺少 provenance 时必须跳过清理；缺少必需字段时返回 `BLOCKED` 并要求补齐。
   - 创建 PR 与保留分支路径始终保留 worktree，便于继续处理反馈。
9. `report`
   - 输出统一 contract。

### 默认建议策略
- 已准备共享：优先 `创建PR`。
- 本地快速收尾：`本地合并`。
- 需要延后处理：`保留分支`。
- 明确放弃工作：`丢弃工作`（必须确认）。

### 标准处置输出

`mode=uncommitted` 初始路径只展示引用的友好提示，内部 handoff 不重复渲染。其他路径用下方完整格式，不使用 YAML：

```markdown
## 分支收尾结果

状态：READY / BLOCKED / DONE / CANCELLED
模式：branch_disposition / 未确认
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
- 工作区：clean / 未确认
- HEAD：存在 / 未确认
- 未跟踪文件数：<number 或 未确认>

### 破坏性操作确认
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

- `references/options-template.md`：未提交提示、标准选项和压力场景。
- `references/destructive-confirmation-template.md`：`丢弃工作`路径的破坏性操作确认文案模板。
- `references/pr-template.md`：选择 `创建PR` 时的 PR 描述模板。
- `references/recovery-playbook.md`：阻塞/取消场景的恢复指引与最小恢复输出要求。

## Integration

- 与 `verification-before-completion` 串联：只有 `route_worktree` 判定 clean 且有 HEAD 后才运行验证。
- 可由 `plan-impl` 在实现完成后调用，消费结构化输出做后续编排。
- 与 `using-git-worktrees` 配套：创建阶段记录路径来源，收尾阶段按 provenance 决定是否清理。
