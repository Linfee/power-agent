---
name: code-review
description: |-
  代码审查 Skill。编码完成后、合并或 PR 前编排全量审查；收到审查反馈（内部 finding、外部 reviewer、PR 评论）时评估采纳/驳回/澄清。
  Triggers: 代码审查, code review, 审查反馈, 双重审查, 合并前审查, 全量审查.
---

# 代码审查

实现目标完成后、合并或 PR 前的全量审查编排器，同时负责评估审查反馈。不替代 `implement` 的批次内审查，也不替代 `verification-before-completion`。

合并主分支或创建 PR 前默认必须执行；仅用户明确要求时可跳过，并记录原因。

## 输入与范围

- `REVIEW_SCOPE=commit_range|working_tree`；有任务相关未提交变更时必须用 `working_tree`，且覆盖 staged、unstaged 和任务相关 untracked 文件；不得因 Base=Head 或空 commit diff 判定无变更。`.power-agent` 不属于可自由发现的 untracked 范围。
- `BASE_SHA / HEAD_SHA`：commit range 必填；基线依次取 merge-base with `origin/main`、`origin/main`、最后才是 `HEAD~N`；unborn working tree 可为 `not_applicable`。
- **先定死审查基点再派发**：commit_range 确认 ref 可解析、diff 非空；working_tree 以 `git status` + diff + 已确认的任务相关 untracked 判定非空——基点错误要在这里失败，不要在 reviewer 内部失败。
- 需求/规格按序查找：commit message 的 issue 引用 → 用户提供的路径 → `docs/` 或 `specs/` 下匹配文档 → 问用户；确实没有时向用户确认后按无 spec 审查。缺失信息按需读取。
- 可选 Review Assets：`REVIEW_ASSETS_MANIFEST`、权威 `REVIEW_RUN_ROOT`、`REVIEW_BASIS`、`ALLOWED_ASSET_SENSITIVITY`（默认 `normal`）；无 manifest 时前三项写 `not_applicable`。

## 编排

1. 按 `references/risk-classification.md` 判定重要性；派一名主审按 `references/code-reviewer.md` 完成多维全量审查。
2. 有阻塞 finding：按下方「反馈评估」逐项处理，实施 `采纳|部分采纳` 项并运行相关验证，然后进入修复验证。
3. 修复验证在同一实现目标、同一 review session 内优先由原 finding owner 继续；跨目标、跨 session 或 owner 不可继续时派新 reviewer，并提供完整的原 finding/证据、修复说明、修复增量和新验证。每次修复验证都基于当前代码产生新 verdict，不沿用旧结论。
4. 修复实质改变 Scope、Acceptance、公共契约、数据、权限、安全、并发或迁移边界时，停止窄验证，按当前范围重启完整主审并重新分级。
5. 当前目标最多 3 轮修复-复审；仍阻塞且不收敛时升级处理。需求/基线不足则补齐后重启当前阶段的完整审查。

### 强度与终审

- 高重要性从主审起就是 `增强`；低/中重要性初始为 `常规`，但主审或主审修复验证首次判定 `实现风险=高` 时立即升级并保持 `增强`。
- 常规主审收敛 → `继续流程`；增强主审收敛 → 派一个此前未参与该目标的 reviewer 做 `独立终审`，终审 finding 由终审 reviewer 优先验证，通过后不再回到主审。
- 只有用户或上游契约明确要求时才启用并行双审：两名 reviewer 各做完整审查，按 `references/conflict-resolution.md` 归并，不因每次修复机械重启双方。
- 用平台可用的 reviewer；没有专用 reviewer 时给通用执行者完整模板。不依赖特定 agent 名称、消息接口或私有续接机制。

## 反馈评估

收到审查反馈（本 Skill 的阻塞 finding、外部 reviewer 或 PR 评论）时，逐项基于代码事实做技术判断，不输出表演性同意：

- `decision` 仅允许：`采纳`（建议成立，可实施）、`部分采纳`（部分成立，需拆分）、`驳回`（不成立，给出反证）、`需澄清`（信息不足）。
- `需澄清` 时状态必须为 BLOCKED，下一步是具体澄清问题；`采纳 | 部分采纳 | 驳回` 必须附可定位证据（file:line、diff 片段、测试输出）。
- 评估通过后：实施所有 `采纳 | 部分采纳` 的阻塞项，运行相关验证，然后进入当前审查阶段的修复验证（优先原 reviewer；替代 reviewer 带完整修复上下文）。不得要求用户决定是否继续。
- 只有反馈超出授权范围、修复涉及破坏性/越权操作，或修复-复审达到轮次上限时，才请求用户介入。

反馈示例见 `references/response-examples.md`。

## Review Assets

manifest 为 `not_applicable` 时，禁止扫描 `.power-agent`、`review-runs/` 或 `assets/`。

提供 manifest 时按以下原则校验；任一校验缺失、未知或失败就不读、不采信、不扩扫，只报告 evidence gap；关键验收只能依赖无效资产时返回 `需澄清`：

- `REVIEW_RUN_ROOT` 解析后必须严格为当前 run 的 `.power-agent/review-runs/<run-id>`，root 及父组件均非 symlink；manifest 必须严格等于该 root 的 `review-assets.md`。
- 只读 manifest 显式列出的普通文件：位于同一 root 的 `assets/` 下，拒绝绝对路径、空段、`..`、symlink 和解析越界；scope 匹配当前 target 与 paths/finding；freshness 匹配 `REVIEW_BASIS`；source 可追溯；sensitivity 已获当前派发授权。
- 无法给 working tree 提供可比较 snapshot 时，不传 manifest。

证据优先级：当前代码/diff > 当前需求/exec-plan > 匹配当前 basis 的新验证 > repair context/findings > implementer report > 其它 review assets。

## 输出与路由

严格遵循 `references/output-contract.md`：输出 `状态 / 审查阶段 / 重要性等级 / 实现风险 / 审查强度 / 证据 / 阻塞问题 / 非阻塞建议 / 下一步`，不用 YAML。

- 阻塞 finding → `启动修复子代理`；范围/口径变化或信息补齐 → `重新审查`；轮次耗尽 → `升级处理`。
- 常规主审收敛 → `继续流程`；增强主审收敛 → `进入独立终审`；独立终审收敛 → `继续流程`。
- 只有反馈评估为 BLOCKED、轮次耗尽或修复涉及破坏性/越权操作时才询问用户。
- dirty 或无 HEAD 的仓库不得进入完成前验证；先走未提交分支收尾 Gate，clean HEAD 后再验证。

## References

- reviewer prompt：`references/code-reviewer.md`
- 反馈评估示例：`references/response-examples.md`
- 重要性/实现风险：`references/risk-classification.md`
- 显式并行双审：`references/conflict-resolution.md`
- 输出协议：`references/output-contract.md`
- 审查生命周期：`references/review-lifecycle.md`

上游为 `implement`；下游依次为反馈评估、修复验证/独立终审、工作区 Gate 与完成前验证。`dev-docs-maintain` 仅在文档健康或验证登记需要时触发。
