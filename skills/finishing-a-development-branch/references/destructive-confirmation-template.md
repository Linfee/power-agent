<!-- verified: 2026-04-21 -->
<!-- scope: finishing-a-development-branch -->

# 高风险确认模板（discard_work）

This action will permanently delete:
- Branch: `<branch>`
- Commits: `<commit-range-or-summary>`
- Worktree: `<worktree-path>`

If you want to continue, reply exactly:
`discard`

若输入不是精确 `discard`，则取消该操作并返回 `status=cancelled`。
