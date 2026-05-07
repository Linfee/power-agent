---
name: using-git-worktrees
description: |-
  在大型功能、exec-plan 执行或高风险改动前检测/准备隔离工作区；先用宿主原生能力，最后才回退 git worktree。
  Triggers: worktree, 隔离执行, exec-plan BOOTSTRAP, 高风险改动.
version: 1.2.5
---

# Using Git Worktrees

确保实现工作发生在合适的隔离工作区中。核心原则：**先检测现状，再使用宿主能力，最后才手动创建 git worktree。**

---

## Objective

### 做什么
- 判断当前是否已经处于隔离 worktree。
- 在需要隔离时，优先使用宿主环境提供的原生 worktree/工作区能力。
- 没有原生能力时，安全地回退到 `git worktree`。
- 建立最小基线证据，避免把既有失败误认为新改动导致。

### 不做什么
- 不在已经隔离的 worktree 中再创建嵌套 worktree。
- 不绕过宿主环境的原生 worktree 管理能力。
- 不在用户或项目未要求隔离时擅自创建长期工作区。
- 不清理由宿主环境或用户创建、来源不明的 worktree。

---

## 使用入口

以下场景默认需要使用本 Skill：
- 执行 `exec-plan-runner` 的 BOOTSTRAP 阶段。
- 跨模块功能、重构、迁移或高风险修复。
- 用户明确要求隔离分支、worktree、沙盒执行。

以下场景通常不需要：
- 单文件文案/格式调整。
- 只读审查或只读调研。
- 当前会话已经明确在专用 worktree 中。

---

## Step 0: 检测当前隔离状态

先运行最小检测：

```bash
git rev-parse --show-toplevel
GIT_DIR=$(cd "$(git rev-parse --git-dir)" 2>/dev/null && pwd -P)
GIT_COMMON=$(cd "$(git rev-parse --git-common-dir)" 2>/dev/null && pwd -P)
git rev-parse --show-superproject-working-tree 2>/dev/null
git branch --show-current
```

判定：
- `GIT_DIR != GIT_COMMON` 且不是 submodule：已经在 linked worktree，跳过创建。
- `GIT_DIR == GIT_COMMON` 或处于 submodule：视为普通 checkout，可按需要创建隔离 worktree。
- detached HEAD：记录为宿主/外部管理工作区，收尾时不能假设可直接 merge 当前分支。
- 已存在或外部管理的工作区默认 `worktree_source=external|unknown`，`cleanup_allowed=false`。

输出当前路径、分支状态、是否 linked worktree、是否 detached HEAD、是否需要创建新 worktree，以及 provenance 字段。

---

## Step 1: 确认是否需要创建

如果用户、AGENTS.md、exec-plan 或上游 Skill 已明确要求隔离，则视为已授权创建。

否则先简短询问：

> 是否需要我先创建隔离 worktree 来保护当前分支？

用户拒绝时，在当前工作区继续，并在报告中记录“未创建隔离 worktree”。

---

## Step 2: 优先使用宿主原生能力

如果当前运行环境提供原生 worktree/工作区工具，应优先使用它，例如：
- Codex / 编排器提供的 worktree 创建工具。
- IDE 或 harness 自带的隔离工作区命令。
- 用户指定的项目级 worktree 入口。

只在没有原生能力时进入 Step 3。不要同时使用原生工具和 `git worktree add`，否则宿主环境可能无法追踪清理状态。

---

## Step 3: git worktree 回退

详细手动 fallback 步骤见 `references/manual-worktree-setup.md`。本节保留关键决策与输出契约，避免调用方复制 worktree 规则。

目录选择优先级：
1. 用户或项目文档明确指定的位置。
2. 已存在的 `.worktrees/`。
3. 已存在的 `worktrees/`。
4. 已存在的 `~/.config/power-agent/worktrees/<project>/`。
5. 默认 `.worktrees/<branch-name>/`。

项目内目录必须先确认已被忽略：

```bash
git check-ignore -q .worktrees 2>/dev/null || git check-ignore -q worktrees 2>/dev/null
```

若未忽略，先把对应目录加入 `.gitignore`，再创建 worktree。

创建：

```bash
git worktree add <worktree-path> -b <branch-name>
```

创建成功后记录：

```yaml
path: <worktree-path>
is_linked_worktree: true
is_detached_head: false
worktree_source: power-agent
managed_by: using-git-worktrees
cleanup_allowed: true
```

未创建、已存在或外部管理的工作区必须记录：

```yaml
path: <current-path 或 none>
is_linked_worktree: true | false
is_detached_head: true | false
worktree_source: external | unknown | none
managed_by: host | user | unknown | none
cleanup_allowed: false
```

若遇到权限或 sandbox 拒绝，停止创建并回退为“当前工作区执行”，不要尝试绕过限制。

---

## Step 4: 基线检查

按项目现有约定选择最小基线检查：
- 文档/Skill 变更：路径检查、版本同步脚本、相关 grep。
- 代码变更：目标测试优先，再按风险追加 lint/build。
- 前端可视变更：在项目工具允许时补浏览器或截图验证。

如果基线失败：
- 记录失败命令与摘要。
- 判断是否是既有失败。
- 无法判断时先升级给用户或回到 `systematic-debugging`，不要把失败吞掉。

---

## 输出格式

```markdown
## Worktree 准备结果

状态：READY / SKIPPED / BLOCKED

### 环境
- repo：<path>
- worktree：已存在 / 已创建 / 未创建 / 外部管理
- path：<当前执行工作区绝对路径；无则写 none>
- branch：<branch 或 detached>
- is_linked_worktree：true / false
- is_detached_head：true / false
- worktree_source：power-agent / external / unknown / none
- managed_by：using-git-worktrees / host / user / unknown / none
- cleanup_allowed：true / false

### 证据
- [command] <命令与摘要>

### 阻塞项
- <无或具体阻塞>

### 下一步
- <继续执行 / 在当前工作区执行 / 需要用户决策>
```

---

## References

- `references/manual-worktree-setup.md`
  - 触发：Step 3 git worktree fallback，且没有宿主原生 worktree 工具可用
  - 用途：手动创建 worktree、记录 provenance、准备项目环境
