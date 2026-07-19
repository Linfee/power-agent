---
name: requesting-code-review
description: |-
  代码审查请求 Skill。编排全量代码审查并输出结构化发现；编码完成后、合并或 PR 前触发。
  Triggers: 代码审查, code review, 请求审查, 审查当前实现, 多角度 review, 双重审查, double review, 合并前审查, 全量审查.
---

# 请求代码审查

实现目标完成后、合并或 PR 前的全量审查编排器；不替代 `plan-impl` 的 batch 内审查或 `verification-before-completion`。

合并主分支或创建 PR 前默认必须执行；仅用户明确要求时可跳过，并记录原因。

## 输入与范围

- `REVIEW_SCOPE=commit_range|working_tree`；有任务相关未提交变更时必须用 `working_tree`。
- `BASE_SHA / HEAD_SHA`：commit range 必填；unborn working tree 可为 `not_applicable`。
- 需求/规格、变更摘要、关键文件。
- 可选 Review Assets：`REVIEW_ASSETS_MANIFEST`、权威 `REVIEW_RUN_ROOT`、`REVIEW_BASIS`、`ALLOWED_ASSET_SENSITIVITY`（默认 `normal`）；无 manifest 时前三项为 `not_applicable`。

缺失信息按需读取。`commit_range` 审查 `BASE_SHA..HEAD_SHA`，基线依次取 merge-base with `origin/main`、`origin/main`、最后才是 `HEAD~N`。`working_tree` 必须覆盖 staged、unstaged 和任务相关 untracked 文件；不得因 Base=Head 或空 commit diff 判定无变更。`.power-agent` 不属于可自由发现的 untracked 范围。

## 编排

1. 按 `risk-classification.md` 判定重要性；派一名主审按 `code-reviewer.md` 完成多维全量审查。
2. 阻塞 finding 先交 `receiving-code-review` 评估；实施 `采纳|部分采纳` 项并运行相关验证，再进入当前阶段的修复验证。
3. 修复验证仅在同一实现目标和同一 review session 内优先继续 finding owner；跨目标、跨 session 或 owner 不可继续时，必须派新的替代 reviewer，并完整提供原 finding/owner/证据、修复说明、可定位修复增量和新验证。每次都基于当前代码产生新 verdict。
4. 主审阶段收敛后：常规审查继续流程；增强审查派一个此前未参与该目标的 reviewer 做独立终审。终审 finding 由该终审 reviewer 优先验证；通过后不再回到主审。

### 强度与阶段

- 高重要性从主审起为 `增强`。低/中重要性初始为 `常规`，但初始主审或主审修复验证首次判定 `实现风险=高` 时，本轮及后续主审阶段立即升级并保持 `增强`；无阻塞必须 `进入独立终审`。
- `REVIEW_INTENSITY` 只是派发前强度；重要性、实现风险、有效强度是独立字段。
- `主审|独立终审` 审完整最终范围；`主审修复验证|终审修复验证|并行修复验证` 审原 finding、修复增量和受影响路径；`独立终审` 不得复述主审代替判断。
- 修复实质改变 Scope、Acceptance、公共契约、数据、权限、安全、并发或迁移边界时，停止窄验证，按当前范围重启完整主审并重新分级。
- 当前目标最多 3 轮修复-复审；仍阻塞且不收敛时升级处理。需求/基线不足则补齐后重启当前阶段的完整审查。
- 仅用户或上游契约明确要求时启用并行双审；两名 reviewer 各做完整审查，按 `conflict-resolution.md` 归并，不因每次修复机械重启双方。
- 使用平台可提供的 reviewer；无专用 reviewer 时给通用执行者完整模板。不得依赖特定 agent 名称、消息接口或私有续接机制。

## Review Assets

- manifest 为 `not_applicable` 时禁止扫描 `.power-agent`、`review-runs/` 或 `assets/`。
- 提供 manifest 时，先验证 `REVIEW_RUN_ROOT` 及父组件非 symlink、解析后仍是仓库内当前 run，且 manifest 的路径与解析结果都严格等于 `<REVIEW_RUN_ROOT>/review-assets.md`。
- 只读 manifest 显式列出的普通文件：path 必须位于同一 root 的 `assets/` 下，拒绝绝对路径、空段、`.`、`..`、symlink 和解析越界；scope 同时匹配当前 target 与 `paths=`/`finding=`；freshness 匹配 `REVIEW_BASIS`；source 可追溯；sensitivity 默认 `normal` 且已获当前派发授权。
- 任一校验缺失、未知、不可比较或失败时，不读、不采信、不扩扫，只报告 evidence gap；关键验收仅能依赖无效资产时返回 `需澄清`。无法给 working tree 提供可比较 snapshot 时不传 manifest。
- 证据优先级：当前代码/diff > 当前需求/exec-plan > 匹配当前 basis 的新验证 > repair context/findings > implementer report > 其它 review assets。

## 输出与路由

严格遵循 `output-contract.md`，输出 `状态 / 审查阶段 / 重要性等级 / 实现风险 / 审查强度 / 证据 / 阻塞问题 / 非阻塞建议 / 下一步`，不用 YAML。

- 阻塞 finding：`启动修复子代理`；范围/口径变化或信息补齐：`重新审查`；轮次耗尽：`升级处理`。
- 常规主审收敛：`继续流程`；增强主审收敛：`进入独立终审`；独立终审收敛：`继续流程`。
- 只有 `receiving-code-review=BLOCKED`、轮次耗尽或修复涉及破坏性/越权操作时询问用户。
- dirty 或无 HEAD 的仓库不得进入完成前验证；先走未提交分支收尾 Gate，clean HEAD 后再验证。

## References

- reviewer prompt：`references/code-reviewer.md`
- 重要性/实现风险：`references/risk-classification.md`
- 显式并行双审：`references/conflict-resolution.md`
- 输出协议：`references/output-contract.md`
- 维护/eval 场景：`references/review-workflow-scenarios.md`

上游为 `plan-impl`；下游依次为反馈处理、修复验证/独立终审、工作区 Gate 与完成前验证。`dev-docs-maintain` 仅在文档健康或验证登记需要时触发。
