# 手动创建 Git Worktree

当 Agent 没有 worktree 工具（如 `EnterWorktree`）时的 fallback 方案。

## 前提检查

```bash
git worktree list
```

若已在非主 worktree 中 → 跳过，报告当前位置。

## 创建步骤

### 1. gitignore 验证

```bash
git check-ignore -q .worktrees 2>/dev/null || echo ".worktrees/" >> .gitignore
```

### 2. 创建 worktree

```bash
git worktree add .worktrees/<branch-name> -b <branch-name>
```

创建后，所有文件操作使用 `.worktrees/<branch-name>/` 的绝对路径（Bash 调用间 `cd` 不持久）。

### 3. 项目环境准备

从主目录了解项目类型和依赖管理方式，自主判断如何 setup worktree 环境：

- **依赖锁文件**（如 `package-lock.json`、`pnpm-lock.yaml`、`uv.lock`）会被 git worktree 自动带过来，但 `node_modules/`、`.venv/` 等生成的目录不会
- 根据项目实际情况安装依赖（npm/pnpm/yarn/bun install、pip/uv/poetry install、go mod download 等）
- 若主目录有需要复用的构建产物、缓存、或者临时数据文件（如 `dist/`、`.cache/`, `project.db`），按需拷贝到 worktree
