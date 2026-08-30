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
├── review-assets.md          # optional
├── assets/                   # optional, named reviewer evidence only
├── repair-context.md
└── progress.md
```

使用 `scripts/review-workspace [run-id]` 创建自忽略目录。目录权限遵循当前用户 umask，脚本额外使用 `umask 077`；已存在或经过 symlink 的 run-id 一律拒绝，不复用、不覆盖。

这些文件是可重建的 scratch artifacts，不是 durable source of truth：

- 不进入 commit，不在 `docs/` 中登记为 Concept。
- `git clean -fdx` 可能删除它们；恢复时以 exec-plan Session Log、当前 Git 状态和已有代码为准。
- 不写入 token、密码、认证头、私有 URL query、原始生产数据或其它不应落盘的敏感信息。
- 不自动清理来源不明或仍被当前执行引用的 artifact。

## Review Assets Manifest

Reviewer 只有在编排器显式传入当前 review session 的 `review-assets.md` 时才可消费辅助资产；未传入时以 `not_applicable` 表示，并且不得扫描 `.power-agent`、`review-runs/` 或 `assets/` 寻找证据。

Manifest 中每个资产条目至少包含：

- `path`：相对当前 run 根目录的 `assets/<name>` 普通文件路径；
- `kind`：资产类型，例如 log、screenshot、trace、benchmark 或 report；
- `purpose`：该资产要帮助判断的具体问题；
- `scope`：绑定当前 task、batch 或 final review 目标，并注明适用路径或 finding；
- `freshness`：绑定当前 reviewer 可比较的 review basis；
- `source`：可追溯的生产者，以及生成命令、报告或原始证据引用；
- `sensitivity`：可选，`normal | restricted`，省略时按 `normal` 处理。

最小 Markdown 形状：

```markdown
# Review Assets

- path: assets/test-output.txt
  kind: log
  purpose: 证明目标场景的验证结果
  scope: final:<target-id>; paths=skills/example/**
  freshness: <与本次 review_basis 完全一致的标识>
  source: producer=<role>; command=<可复现命令或 report 引用>
  sensitivity: normal
```

`kind` 的词表和字段排版可扩展，但上述字段语义不得改变。

编排器同时传入 `review_run_root`、`review_basis` 和 `allowed_asset_sensitivity`：

- `review_run_root` 是当前 review session 的权威 run 根目录，必须是仓库内 `.power-agent/review-runs/<run-id>` 的非 symlink 目录；未提供 manifest 时写 `not_applicable`；
- 内部审查的 basis 是当前 `review_package_path`；
- committed 最终审查的 basis 是当前 `BASE_SHA..HEAD_SHA`；
- working-tree 最终审查使用绑定本次 staged、unstaged 与任务相关 untracked 范围的 snapshot 标识；无法提供可比较 snapshot 时不得给该审查传资产 manifest；
- `allowed_asset_sensitivity` 默认仅允许 `normal`；读取 `restricted` 必须在当前派发中显式授权。

读取前逐项校验：

1. `review_run_root` 及其父组件不得为 symlink，解析后必须仍是仓库内当前 run；manifest 的路径与解析结果都必须严格等于 `<review_run_root>/review-assets.md`；
2. 资产路径必须以 `assets/` 开始，且不是绝对路径，不含空段、`.` 或 `..` traversal；manifest、资产路径组件与目标文件不得为 symlink，目标必须是普通文件，解析后仍严格位于 `<review_run_root>/assets/`；
3. scope 必须同时匹配当前派发目标，以及当前受影响的 `paths=` 条目或 `finding=` 标识；freshness 必须匹配 `review_basis`；source 必须可追溯；sensitivity 必须在当前允许集合内；
4. 字段缺失、值未知、无法比较、不匹配，或文件缺失/越界时，不读取或不采信该资产，只报告 evidence gap；不得通过目录遍历补找替代文件。

资产只读且只提供辅助证据。事实优先级为：当前代码与 Git diff > 当前需求、exec-plan 或 task brief > 与当前 basis 匹配的新验证证据 > repair context 与 review findings > implementer report > 其它 review assets。资产 claim 与更高优先级事实冲突时，以更高优先级事实为准。

## Handoff Contract

### Implementer

输入：

- `task_brief_path`：当前任务的完整要求、边界和 Agent 自主边界。
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
- `repair_context_path`：仅 `fix_verification` 必填；首次审查写 `not_applicable`
- `review_assets_manifest_path`：当前 session 的显式 manifest，未提供时写 `not_applicable`
- `review_run_root`：当前 review session 的权威 run 根目录；无 manifest 时写 `not_applicable`
- `review_basis`：当前 review package、commit range 或 working-tree snapshot 标识
- `allowed_asset_sensitivity`：默认 `normal`，只有当前派发明确授权时才包含 `restricted`

reviewer 一次读取 review package；有 manifest 时只读取通过上述校验的命名资产。`fix_verification` 还必须读取 repair context；不要把完整 artifact 内容再次粘贴进 prompt。

### Repair Context

每轮修复后生成新的 `repair-context.md`，至少包含：

- 原 findings、提出者与原始证据；
- 修复说明；
- 修复增量的文件、hunk 或其它可定位范围；
- 与当前代码匹配的新验证证据。

原 reviewer 可继续时和替代 reviewer 降级时使用同一份 repair context。缺失字段时不得进入 `fix_verification`；修复导致范围、验收或关键风险边界实质变化时，丢弃窄范围 repair context，重新执行完整审查。

## Review Package

使用：

```bash
skills/implement/scripts/review-package --base <BASE_SHA> [--output <file>] [-- <path>...]
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
