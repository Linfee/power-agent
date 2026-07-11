# 手动创建 Git Worktree

当 `using-git-worktrees` 进入 Step 3 git worktree fallback，且宿主环境没有原生 worktree 工具时使用。

## 前提检查

```bash
git rev-parse --show-toplevel
GIT_DIR=$(cd "$(git rev-parse --git-dir)" 2>/dev/null && pwd -P)
GIT_COMMON=$(cd "$(git rev-parse --git-common-dir)" 2>/dev/null && pwd -P)
git rev-parse --show-superproject-working-tree 2>/dev/null
git worktree list
```

若 `GIT_DIR != GIT_COMMON` 且不是 submodule → 已在 linked worktree，跳过创建并报告当前位置：

```yaml
path: <current-path>
is_linked_worktree: true
is_detached_head: false
worktree_source: external | unknown
managed_by: host | user | unknown
cleanup_allowed: false
```

若处于 detached HEAD → 记录为外部管理工作区，收尾时不要假设可直接 merge 当前分支：

```yaml
path: <current-path>
is_linked_worktree: true | false
is_detached_head: true
worktree_source: external | unknown
managed_by: host | user | unknown
cleanup_allowed: false
```

## 创建步骤

### 1. gitignore 验证

```bash
git check-ignore -q .worktrees 2>/dev/null || git check-ignore -q worktrees 2>/dev/null
```

若未被忽略，先把选定目录加入 `.gitignore`。不要把 worktree 内容暴露为可提交文件。

### 2. 创建 worktree

```bash
git worktree add .worktrees/<branch-name> -b <branch-name>
```

创建后，所有文件操作使用 `.worktrees/<branch-name>/` 的绝对路径（Bash 调用间 `cd` 不持久）。

创建成功后返回给后续收尾 Skill 的 worktree context 必须包含：

```yaml
path: <worktree-path>
is_linked_worktree: true
is_detached_head: false
worktree_source: power-agent
managed_by: using-git-worktrees
cleanup_allowed: true
```

如果创建因 sandbox/权限失败，停止并回报；不要尝试绕过限制，可退回当前工作区执行。

### 3. 项目环境准备

从主目录了解项目类型和依赖管理方式，自主判断如何 setup worktree 环境：

- **依赖锁文件**（如 `package-lock.json`、`pnpm-lock.yaml`、`uv.lock`）会被 git worktree 自动带过来，但 `node_modules/`、`.venv/` 等生成的目录不会
- 根据项目实际情况安装依赖（npm/pnpm/yarn/bun install、pip/uv/poetry install、go mod download 等）
- 若主目录有需要复用的构建产物、缓存、或者临时数据文件（如 `dist/`、`.cache/`, `project.db`），按需拷贝到 worktree
