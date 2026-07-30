# 破坏性操作确认模板（discard_work）

This action will permanently delete:
- Branch: `<branch>`
- Commits: `<commit-range-or-summary>`
- Worktree: `<worktree-path>`

Worktree cleanup policy:
- `created_by_agent=true`: may be removed after user confirmation.
- External or unknown-origin worktrees: never remove; report manual cleanup requirement.

If you want to continue, reply exactly:
`discard`

若输入不是精确 `discard`，则取消该操作并返回 `status=CANCELLED`。
