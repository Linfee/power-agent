---
name: using-git-worktrees
description: 在执行 exec-plan 前建立隔离 worktree，包含自检跳过逻辑、.gitignore 安全验证和基线测试验证。由 exec-plan-runner 自动调用，也可手动触发。
---

# Using Git Worktrees

## 概述

Git worktrees 共享同一仓库但提供独立工作目录，让实现工作在隔离环境中进行，不影响主分支状态。

**核心原则：** 自检决策 + 安全验证 = 可靠隔离。

**开始时声明：** "I'm using the using-git-worktrees skill to set up an isolated workspace."

## 自检：是否需要创建 worktree

按顺序检查，命中任一条即跳过创建：

### 1. 已在 worktree 中

```bash
git worktree list
```

若当前目录已是非主 worktree（输出包含当前路径且不是主仓库路径） → 报告当前 worktree 位置，跳过创建。

### 2. AGENTS.md 全局禁用

```bash
grep -i "worktree.*disabled\|worktree.*skip\|no.*worktree" AGENTS.md 2>/dev/null
```

若有匹配 → 跳过创建，报告原因。

### 3. 其余情况 → 继续创建流程

## 目录选择（优先级顺序）

### 1. 检查已有目录

```bash
ls -d .worktrees 2>/dev/null     # 优先（隐藏目录）
ls -d worktrees 2>/dev/null      # 备选
```

两者都存在时使用 `.worktrees`。

### 2. 检查 AGENTS.md 偏好

```bash
grep -i "worktree.*director" AGENTS.md 2>/dev/null
```

有配置则直接使用，无需询问。

### 3. 询问用户

```
未找到 worktree 目录，请选择创建位置：

1. .worktrees/（项目本地，隐藏目录）
2. ~/.worktrees/<project-name>/（全局位置）
```

## 安全验证（项目本地目录）

**创建前必须确认目录已被 git 忽略：**

```bash
git check-ignore -q .worktrees 2>/dev/null || git check-ignore -q worktrees 2>/dev/null
```

**未被忽略时：**
1. 向 `.gitignore` 添加对应行
2. 提交变更
3. 继续创建

全局目录（`~/.worktrees`）无需此验证。

## 创建步骤

### 1. 获取项目名

```bash
project=$(basename "$(git rev-parse --show-toplevel)")
```

### 2. 创建 Worktree

```bash
git worktree add "$path" -b "$BRANCH_NAME"
cd "$path"
```

### 3. 运行项目初始化（自动检测）

```bash
if [ -f package.json ]; then npm install; fi
if [ -f Cargo.toml ]; then cargo build; fi
if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
if [ -f pyproject.toml ]; then poetry install; fi
if [ -f go.mod ]; then go mod download; fi
```

### 4. 验证基线测试

```bash
# 使用项目适用的测试命令
npm test / cargo test / pytest / go test ./...
```

- 测试通过 → 报告就绪
- 测试失败 → 报告失败详情，询问是否继续或先调查

### 5. 报告结果

```
Worktree ready at <full-path>
Tests passing (<N> tests, 0 failures)
Ready to implement <feature-name>
```

## 快速参考

| 情况 | 处理 |
|------|------|
| 已在 worktree 中 | 跳过创建，报告当前位置 |
| AGENTS.md 全局禁用 | 跳过创建，报告原因 |
| `.worktrees/` 已存在 | 使用（验证已忽略） |
| `worktrees/` 已存在 | 使用（验证已忽略） |
| 两者都存在 | 使用 `.worktrees/` |
| 都不存在 | 检查 AGENTS.md → 询问用户 |
| 目录未被忽略 | 添加到 .gitignore + 提交 |
| 基线测试失败 | 报告失败 + 询问 |
| 无 package.json 等 | 跳过依赖安装 |

## 禁止事项

- 跳过 .gitignore 验证（项目本地目录）
- 跳过基线测试验证
- 测试失败时不询问直接继续
- 不查 AGENTS.md 就假设目录位置

## Integration

**由以下 Skill 调用：**
- `exec-plan-runner` — Step 0，无条件调用，由本 skill 自行决策是否创建

**配对使用：**
- `finishing-a-development-branch` — 工作完成后清理 worktree
