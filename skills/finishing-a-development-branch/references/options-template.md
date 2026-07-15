# 选项展示模板

## 未提交改动展示

```markdown
## 当前改动尚未提交

当前工作区尚未形成可验证的提交（存在未提交改动，或仓库尚无 HEAD 提交）。请先提交；提交后再运行完成前验证并继续分支收尾。

如需代理提交，请回复：`提交后继续`。
```

工作区 dirty（含 staged、unstaged 或 untracked）或仓库尚无 HEAD 提交时使用。它是收尾前置提示，不是验证结果；不要先调用或展示 `verification-before-completion`，也不要显示 `PARTIAL`、`passed=false` 或 `commit_sha=unknown`。

## 压力场景

### 场景：新仓库尚无 HEAD
- 用户输入：完成当前实现并收尾。
- 无本规则易错行为：把 `commit_sha` 不存在渲染为 `PARTIAL / passed=false / unknown`。
- 期望行为：直接展示“当前改动尚未提交”，提示提交后继续。
- 验收点：不出现验证失败措辞；不要求 HEAD、base 或验证证据。

### 场景：已有 HEAD，但本轮改动未提交
- 用户输入：处理完改动后走分支收尾。
- 无本规则易错行为：先运行完成前验证，再因 HEAD 未包含当前改动而报错。
- 期望行为：在验证前展示未提交提示。
- 验收点：不声称已有提交级验证；不展示 merge / PR 选项；提交后重新检查工作区，再决定是否进入 VBC。

### 场景：工作区 clean，但验证失败
- 用户输入：提交后验证失败，尝试继续分支收尾。
- 无本规则易错行为：把任何收尾问题都包装成未提交提示。
- 期望行为：按原 gate 返回 `BLOCKED / passed=false`。
- 验收点：不展示未提交提示；明确报告真实失败证据。

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
