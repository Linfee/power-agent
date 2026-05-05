<!-- verified: 2026-05-05 -->
<!-- scope: finishing-a-development-branch -->

# 高风险确认模板（discard_work）

This action will permanently delete:
- Branch: `<branch>`
- Commits: `<commit-range-or-summary>`
- Worktree: `<worktree-path>`

Worktree cleanup policy:
- `worktree_source=power-agent` and `cleanup_allowed=true`: may be removed after confirmation.
- `worktree_source=external|unknown` or missing provenance: do not remove automatically; report manual cleanup requirement.

If you want to continue, reply exactly:
`discard`

若输入不是精确 `discard`，则取消该操作并返回 `status=CANCELLED`。
