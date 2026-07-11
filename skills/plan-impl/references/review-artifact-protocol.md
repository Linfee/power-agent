# Review Artifact Protocol

内部实现与审查优先通过文件交接高体积内容，避免把任务全文、Proof Block 和 diff 复制进 orchestrator 或 reviewer prompt。

## Workspace

短期产物位于当前 worktree 根目录：

```text
.power-agent/review-runs/<run-id>/
├── task-<id>-brief.md
├── task-<id>-report.md
├── review-<scope>.diff
├── review-findings.md
└── progress.md
```

使用 `scripts/review-workspace [run-id]` 创建自忽略目录。目录权限遵循当前用户 umask，脚本额外使用 `umask 077`；已存在或经过 symlink 的 run-id 一律拒绝，不复用、不覆盖。

这些文件是可重建的 scratch artifacts，不是 durable source of truth：

- 不进入 commit，不在 `docs/` 中登记为 Concept。
- `git clean -fdx` 可能删除它们；恢复时以 exec-plan Session Log、当前 Git 状态和已有代码为准。
- 不写入 token、密码、认证头、私有 URL query、原始生产数据或其它不应落盘的敏感信息。
- 不自动清理来源不明或仍被当前执行引用的 artifact。

## Handoff Contract

### Implementer

输入：

- `task_brief_path`：当前任务的完整要求和边界。
- `report_path`：实现者写入完整 Proof Block 和实现报告的位置。

返回消息只包含：

- `status`
- `report_path`
- 一行验证摘要
- concerns 或 blocker

### Reviewer

输入：

- `task_brief_path`
- `report_path`
- `review_package_path`
- 绑定当前任务的全局约束

reviewer 一次读取 review package，并分别给出规格符合性和代码质量 verdict。不要把完整 artifact 内容再次粘贴进 prompt。

## Review Package

使用：

```bash
skills/plan-impl/scripts/review-package --base <BASE_SHA> [--output <file>] [-- <path>...]
```

package 包含：

- 相对 `BASE_SHA` 的工作树状态；
- tracked staged + unstaged 的 net diff stat 和完整 diff；
- untracked 文件列表及其 diff；
- 生成时的显式 path scope。

Power-Agent 的实现子代理不创建 commit，因此 package 默认比较 `BASE_SHA` 与当前工作树，不假设 `HEAD~1` 或 per-task commit。

范围规则：

- 串行且任务边界清楚时，可以生成 task-level package。
- 并行或共享文件 batch 默认生成 batch-level package。
- 当前工作树含目标外未提交变更时，必须传入显式 path scope；无法隔离目标范围时停止审查并返回 `BLOCKED`。
- path scope 始终相对仓库根目录解释，即使从子目录调用脚本。
- path scope 按 literal path 解释，不执行 Git pathspec magic；文件名中的 `:`、`*`、`?` 或 `[` 不得扩大审查范围。
- `--output` 省略时，脚本自动创建新的 scratch workspace；显式输出文件已存在时拒绝覆盖。显式输出位于仓库内时，该路径必须已被 Git ignore，防止 package 在生成时把自身递归纳入。

## Durable Progress

scratch `progress.md` 可记录细粒度任务和 artifact 路径；exec-plan 的 runner state 与 Session Log 继续记录粗粒度、可版本化恢复点。两者冲突时，以 exec-plan、Git 状态和实际代码证据为准。
