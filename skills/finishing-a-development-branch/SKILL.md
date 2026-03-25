---
name: finishing-a-development-branch
description: 实现完成、测试通过后，引导完成分支收尾：验证测试 → 呈现 merge/PR/保留/丢弃 4 选项 → 清理 worktree。由 exec-plan-runner 自动调用，也可手动触发。
---

# Finishing a Development Branch

## Overview

通过结构化选项引导完成开发收尾工作。

**核心原则：** 验证测试 → 呈现选项 → 执行选择 → 清理。

**开始时声明：** "I'm using the finishing-a-development-branch skill to complete this work."

## 流程

### Step 1: 验证测试

**呈现选项前必须先确认测试通过：**

```bash
npm test / cargo test / pytest / go test ./...
```

**如果测试失败：**
```
Tests failing (<N> failures). Must fix before completing:
[显示失败详情]
Cannot proceed until tests pass.
```

停止，不进入 Step 2。

### Step 2: 确认 Base Branch

```bash
git merge-base HEAD main 2>/dev/null || git merge-base HEAD master 2>/dev/null
```

### Step 3: 呈现选项（Gate，等待用户决策）

```
Implementation complete. What would you like to do?

1. Merge back to <base-branch> locally
2. Push and create a Pull Request
3. Keep the branch as-is (I'll handle it later)
4. Discard this work

Which option?
```

### Step 4: 执行选择

#### 选项 1：本地 Merge

```bash
git checkout <base-branch>
git pull
git merge <feature-branch>
<test command>   # 验证合并结果
git branch -d <feature-branch>
```

然后执行 Step 5（清理 worktree）。

#### 选项 2：Push + 创建 PR

```bash
git push -u origin <feature-branch>
gh pr create --title "<title>" --body "$(cat <<'EOF'
## Summary
<2-3 bullets of what changed>

## Test Plan
- [ ] <verification steps>
EOF
)"
```

保留 worktree（不执行 Step 5）。

#### 选项 3：保留

报告："Keeping branch <name>. Worktree preserved at <path>."

不执行 Step 5。

#### 选项 4：丢弃

**先确认：**
```
This will permanently delete:
- Branch <name>
- All commits: <commit-list>
- Worktree at <path>

Type 'discard' to confirm.
```

等待精确输入 `discard`。确认后：

```bash
git checkout <base-branch>
git branch -D <feature-branch>
```

然后执行 Step 5（清理 worktree）。

### Step 5: 清理 Worktree

**仅选项 1 和 4 执行：**

```bash
git worktree list | grep $(git branch --show-current)
git worktree remove <worktree-path>
```

## 快速参考

| 选项 | Merge | Push | 保留 Worktree | 删除分支 |
|------|-------|------|---------------|----------|
| 1. 本地 Merge | ✓ | - | - | ✓ |
| 2. 创建 PR | - | ✓ | ✓ | - |
| 3. 保留 | - | - | ✓ | - |
| 4. 丢弃 | - | - | - | ✓（强制） |

## 禁止事项

- 测试未通过就呈现选项
- 合并前不验证合并结果的测试
- 不经确认删除工作成果
- 未收到精确 `discard` 输入就执行丢弃

## Integration

**由以下 Skill 调用：**
- `exec-plan-runner` — Step 4，全量验证通过后的分支收尾

**配对使用：**
- `using-git-worktrees` — 清理由该 skill 创建的 worktree
