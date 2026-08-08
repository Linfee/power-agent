---
name: finishing-a-development-branch
description: |-
  实现完成后处置分支：工作区 dirty 或无 HEAD 时给出待提交提示；clean 且验证通过后给出 merge/PR/保留/丢弃选项。
  Triggers: 分支收尾, finishing, 合并到目标分支, 创建 PR, 保留分支, 丢弃已完成工作.
---

# Finishing a Development Branch

分支收尾决策器：基于当前状态给出分支处置路径，返回结构化结果。不硬编码 git/gh 命令菜单，不重复执行验证流程。

## 输入

- `working_tree_state`（必填）：是否有未提交变更、是否存在未跟踪文件、`has_head`。
- `verification_evidence`（标准路径必填）：绑定当前提交的验证结果，至少含 `commit_sha`、`passed`、`verified_at`、`evidence[]`；上游是 `verification-before-completion` 时直接取这四个字段。
- `branch_context`（标准路径必填）：当前分支、候选 base branch、ahead/behind。
- `worktree_context`（标准路径必填）：`created_by_agent`（本次 agent 运行是否创建该 worktree）；`path`、`is_linked_worktree`、`is_detached_head` 由 collect_state 自行检测，不作为调用输入。

缺关键输入返回 `BLOCKED` 并写明补齐要求。docs 同步提醒只能进非阻塞建议，不作为阻塞 gate。

## 流程

1. **collect_state**：先只看 `working_tree_state`，不预取标准路径的其他输入。
2. **route_worktree**：dirty（含 staged、unstaged、untracked）或 `has_head=false` → 按 `references/options-template.md#未提交改动展示` 输出友好提示，返回 `READY / mode=uncommitted / options=[commit_then_continue]`；不运行、不展示完成前验证，也不渲染验证失败措辞。clean 且有 HEAD → 补齐标准路径输入，继续往下。
   - `commit_then_continue` 仍需提交授权；提交后回到 collect_state 重新检查，不得直接进入验证。
3. **check_gate**：`verification_evidence` 不存在、`commit_sha` 与当前 HEAD 不匹配或 `passed=false` → `BLOCKED`，不展示处置选项。
4. **present_options**：普通 checkout 或 named branch worktree 展示 4 个选项（本地合并 / 创建PR / 保留分支 / 丢弃工作）；detached HEAD 或外部管理工作区不展示本地合并。不可执行的选项要说明原因。默认建议：准备共享 → 创建PR；本地快速收尾 → 本地合并；延后处理 → 保留分支。
5. **confirm_destructive**：仅“丢弃工作”需要明确确认（文案见 `references/destructive-confirmation-template.md`）；确认失败 → `CANCELLED`，保留现状。
6. **execute + cleanup**：执行用户选项。仅本地合并或丢弃路径考虑清理 worktree，且只有 `created_by_agent=true` 并经用户确认后才允许；外部或来源不明的 worktree 一律跳过清理并标记 `跳过-外部管理`。创建 PR 与保留分支路径始终保留 worktree，便于继续处理反馈。
7. **report**：输出结果。

规则优先级：用户明确选择 > 安全确认 > 输出格式完整性 > 默认建议策略。

## 输出契约

编排层消费的必填字段如下（其余展示信息按需补充，不用 YAML）：

```markdown
## 分支收尾结果

状态：READY / BLOCKED / DONE / CANCELLED
模式：branch_disposition / uncommitted / 未确认
选择：本地合并 / 创建PR / 保留分支 / 丢弃工作 / 未选择

### 阻塞项
- <code>：<message> → 需要动作：<required_action>；无则写“无”

### 非阻塞建议
- <建议；无则写“无”>

### 下一步
- 动作：用户确认 / 重新验证 / 打开PR / 完成
- 负责人：用户 / 代理
```

- `READY` 时附 `options`（如 `commit_then_continue`）供编排层透传。
- 面向用户展示时按需补充：验证证据摘要（commit_sha / 结果 / 时间）、分支状态（当前分支、base、ahead/behind）、环境状态（checkout 类型、worktree 是否 agent 创建）、清理结果。
- `mode=uncommitted` 只展示未提交提示，内部 handoff 不重复渲染。

## References

- `references/options-template.md`：未提交提示与标准选项展示。
- `references/destructive-confirmation-template.md`：丢弃路径的破坏性操作确认文案。
- `references/pr-template.md`：选择“创建PR”时的 PR 描述模板。
- `references/recovery-playbook.md`：阻塞/取消场景的恢复指引与最小恢复输出要求。

## Integration

- 与 `verification-before-completion` 串联：只有 clean 且有 HEAD 后才运行验证；dirty 或无 HEAD 时先走未提交提示。
- 可由 `implement` 在实现完成后调用，消费结构化输出做后续编排。
- worktree 规则：agent 创建的 worktree 在创建时记录来源，收尾只清理自己创建的；外部或来源不明的不动。具体 worktree 使用规则由项目或 harness 定义。
