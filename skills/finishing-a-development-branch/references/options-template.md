<!-- verified: 2026-05-05 -->
<!-- scope: finishing-a-development-branch -->

# 选项展示模板

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
- `merge_local` / `discard_work`：仅当 `worktree_source=power-agent` 且 `cleanup_allowed=true` 时才清理。
- `.worktrees/`、`worktrees/`、`~/.config/power-agent/worktrees/` 路径只能作为辅助证据，不能单独触发删除。
- 外部管理 worktree：跳过清理，并在结果中标记 `跳过-外部管理`。

## 不可执行项说明

当某个选项不可执行时，按以下格式补充：

- `<option>` unavailable: `<reason>`
