# 选项展示模板

## 未提交改动展示

```markdown
## 当前改动尚未提交

当前工作区尚未形成可验证的提交（存在未提交改动，或仓库尚无 HEAD 提交）。请先提交；提交后再运行完成前验证并继续分支收尾。

如需代理提交，请回复：`提交后继续`。
```

工作区 dirty（含 staged、unstaged 或 untracked）或仓库尚无 HEAD 提交时使用。它是收尾前置提示，不是验证结果；不要先调用或展示 `verification-before-completion`，也不要显示 `PARTIAL`、`passed=false` 或 `commit_sha=unknown`。

## 标准展示

Implementation complete. What would you like to do?

1. merge_local — Merge back to base branch locally
2. create_pr — Push and create a Pull Request
3. keep_branch — Keep the branch as-is and handle later
4. discard_work — Permanently discard this branch and worktree

请选择一个选项，并在需要时补充偏好（例如 PR 标题风格）。

## Detached HEAD 展示

Implementation complete. Current checkout is detached HEAD or externally managed, so direct local merge is unavailable.

1. create_pr — Push as a new branch and create a Pull Request
2. keep_branch — Keep the workspace as-is and handle later
3. discard_work — Permanently discard this workspace

请选择一个选项。

## Worktree 清理说明

- `create_pr`：保留 worktree，方便处理 PR 反馈。
- `keep_branch`：保留 worktree。
- `merge_local` / `discard_work`：仅当 `created_by_agent=true` 且用户确认后才清理。
- 外部或来源不明的 worktree：跳过清理，并在结果中标记 `跳过-外部管理`。

## 不可执行项说明

当某个选项不可执行时，按以下格式补充：

- `<option>` unavailable: `<reason>`
