---
name: requesting-code-review
description: |-
  代码审查请求 Skill。编排全量代码审查并输出结构化发现；编码完成后、合并或 PR 前触发。
  Triggers: 代码审查, code review, 请求审查, 审查当前实现, 多角度 review, 双重审查, double review, 合并前审查, 全量审查.
---

# 请求代码审查

在实现阶段完成后，组织一次面向整个变更范围的审查；进入合并或 PR 前默认必须执行。

本 Skill 是审查编排器，不是审查员本体。

---

## requesting-code-review

代码审查编排器，负责：
- 收集最小审查上下文
- 对变更进行重要性分级，并消费 reviewer 对实现风险的独立判断
- 根据重要性与实现风险选择常规或增强审查
- 编排主审、修复验证、独立终审与显式并行双审

---

## Objective

### 做什么
- 在功能完成后或合并/PR 前发起全量审查（功能级别，不是 batch 级别）
- 用统一且人类可读的输出格式生成可消费结果
- 对阻塞问题给出明确下一步动作

### 不做什么
- 不替代 `plan-impl` 的 batch 内部审查循环
- 不承担最终验证职责（由 `verification-before-completion` 负责）
- 不承担文档维护职责（由 `dev-docs-maintain` 负责）
- 不在主 Skill 内嵌长 prompt 模板与命令菜单

---

## Context & Tools

### 最小输入
- `BASE_SHA` / `HEAD_SHA`：`commit_range` 时必填；unborn 仓库的 `working_tree` 审查可为 `not_applicable`。
- `REVIEW_SCOPE`：`commit_range` 或 `working_tree`；存在本任务未提交改动时必须使用 `working_tree`。
- 需求或规格摘要（验收口径）
- 关键变更文件列表
- 变更摘要（实现了什么）
- `REVIEW_ASSETS_MANIFEST`：可选，当前 review session 的显式 manifest 路径；未提供时为 `not_applicable`。
- `REVIEW_RUN_ROOT`：提供 manifest 时必填，指向当前 review session 的权威 `.power-agent/review-runs/<run-id>`；未提供 manifest 时为 `not_applicable`。
- `REVIEW_BASIS`：提供 manifest 时必填；`commit_range` 使用当前 `BASE_SHA..HEAD_SHA`，`working_tree` 使用绑定本次 staged、unstaged 与任务相关 untracked 范围的 snapshot 标识。
- `ALLOWED_ASSET_SENSITIVITY`：默认仅 `normal`；读取 `restricted` 资产必须在当前派发中显式授权。

缺失信息按需读取，不预加载冗长上下文。

### 审查范围
- `commit_range`：审查 `BASE_SHA..HEAD_SHA`。
- `working_tree`：审查 staged、unstaged，以及 `git status --short` 中与本任务相关的 untracked 文件；不得因 `BASE_SHA=HEAD_SHA` 得到空 diff 就判定无变更。`.power-agent` scratch artifacts 不属于可自由发现的 untracked 范围，只有显式 manifest 中通过校验的命名资产可读。
- dirty 工作区进入提交前审查时必须使用 `working_tree`；提交后的复审才可切换为 `commit_range`。

### 基线选择优先级
仅 `commit_range` 使用以下优先级；`working_tree` 不因仓库尚无 HEAD 而阻塞：

1. `git merge-base HEAD origin/main`
2. `origin/main`
3. `HEAD~N`（仅当前两者不可用时）

### 模板与规则引用
- 审查模板：`references/code-reviewer.md`
- 重要性与实现风险校准：`references/risk-classification.md`
- 显式并行双审归并：`references/conflict-resolution.md`
- 输出协议：`references/output-contract.md`
- 压力场景：`references/review-workflow-scenarios.md`

---

## Constraints & Format

### 分层审查派发
- 每个实现目标先派一名主审 reviewer，按 `references/code-reviewer.md` 的全部维度做完整审查；多维审查不等于必须派发多名 reviewer。
- `审查强度=常规`：只有主审阶段的有效强度始终为常规时，主审及其修复验证无阻塞后才可继续流程。
- `审查强度=增强`：主审及其修复验证无阻塞后，必须派一名此前未参与该目标审查的 reviewer，对最终变更范围做独立全量终审。
- 高重要性从主审开始即标记为增强审查；低或中重要性的主审阶段若以证据判定 `实现风险=高`，则升级为增强审查。主审阶段包括初始主审及其修复验证。
- `REVIEW_INTENSITY` 是派发前的初始强度。低或中重要性的主审或主审修复验证一旦返回 `实现风险=高`，编排器必须立即把本轮有效审查强度记录为 `增强`；当前 verdict 及后续主审修复验证均输出 `审查强度=增强`，无阻塞时强制 `下一步=进入独立终审`，不得沿常规路径继续。
- 只有用户或上游契约明确要求并行双审时，才同时派发两个独立 reviewer，并按 `references/conflict-resolution.md` 归并。
- 使用运行平台可提供的 reviewer；没有专用 reviewer 时使用通用执行者并提供审查模板。不得依赖特定 agent 名称、消息接口或平台私有复用机制。

### Reviewer 生命周期与降级
- 修复阻塞问题后，优先由提出该 finding 的 reviewer 做修复验证；这属于同一实现目标和同一 review session，不得把 reviewer 复用于其它目标。
- 运行时支持继续同一 reviewer 时，向其提供修复说明、修复增量和新验证证据；若运行时不支持、原 reviewer 不可用或无法继续，则派一名新的替代 reviewer，并同时提供原 finding、原证据、修复说明、修复增量和新验证证据。
- 修复验证必须检查原 finding 是否关闭、修复增量及受影响路径是否引入新阻塞问题，并产生新的 verdict；不得沿用旧结论。
- 修复导致范围实质扩大、验收改变，或引入新的公共契约、数据、权限、安全、并发或迁移边界时，停止窄范围修复验证，重新发起完整主审并重新校准审查强度。
- 独立终审发现问题后，优先由该终审 reviewer 验证其 findings；无法继续时使用相同的替代 reviewer 降级规则。终审通过后不再回到主审重复审查。

### 显式并行双审
仅在用户或上游契约明确要求时启用；并行 reviewer 各自做完整多维审查，不按维度拆分职责。结果与后续修复验证按 `references/conflict-resolution.md` 处理。

### Review Assets
- manifest 为 `not_applicable` 时，reviewer 不得扫描 `.power-agent`、`review-runs/` 或 `assets/`。
- 提供 manifest 时，先确认 `REVIEW_RUN_ROOT` 及其父路径均非 symlink、解析后仍是仓库内当前 run，并确认 manifest 路径与解析结果都严格等于 `<REVIEW_RUN_ROOT>/review-assets.md`；随后只读该 root `assets/` 下显式列出且通过校验的普通文件：拒绝绝对、空段、`.`、`..`、symlink 和解析后越界路径；scope 必须同时匹配当前 final review 目标及当前受影响的 `paths=` 或 `finding=`，freshness 必须匹配 `REVIEW_BASIS`，source 必须可追溯，sensitivity 必须被当前派发允许。
- 字段缺失、未知、不可比较、不匹配，或文件缺失/越界时，不读取或不采信该资产，只报告 evidence gap，不扩大目录范围。无法提供可比较的 working-tree snapshot 时，不向该 reviewer 传 manifest。
- 事实优先级：当前代码/Git diff > 当前需求/exec-plan > 与当前 basis 匹配的新验证证据 > repair context/findings > implementer report > 其它 review assets。

### 输出格式（必须遵循）

严格遵循 `references/output-contract.md`；主结果必须包含 `状态 / 审查阶段 / 重要性等级 / 实现风险 / 审查强度 / 证据 / 阻塞问题 / 非阻塞建议 / 下一步`，不使用 YAML。

### 行动规则
- `阻塞问题` 非空：`下一步` 只能是 `启动修复子代理`、`重新审查` 或达到轮次上限后的 `升级处理`。
- 主审或独立终审发现阻塞问题时，先交给 `receiving-code-review` 评估；其输出 `状态=DONE` 后，实施所有 `决策=采纳|部分采纳` 的阻塞项、运行相关验证，再进入当前阶段的修复验证。
- 有效审查强度仍为常规时，主审修复验证无阻塞后 `下一步=继续流程`；一旦因高实现风险升级为增强，不再适用常规路径。
- 增强审查的主审修复验证无阻塞后，`下一步=进入独立终审`；独立终审无阻塞后才能 `继续流程`。
- 每次修复后必须产生新的修复验证结论；优先继续原 reviewer，不能继续时使用携带完整修复上下文的新 reviewer。
- 当前实现目标累计修复-复审最多 3 轮；连续 3 轮仍阻塞且无收敛时，`下一步=升级处理`。
- 只有 `receiving-code-review` 输出 `状态=BLOCKED`、修复-复审达到轮次上限，或修复涉及破坏性/越权操作时，才能升级询问用户。

---

## 何时触发

**必须：**
- 合并到主分支或创建 PR 前默认执行全量审查；只有用户明确要求跳过时才能跳过，并记录跳过原因
- 一个实现目标完成且准备进入分支处置或交付时

**按重要性触发：**
- 复杂重构完成后
- 复杂 bug 修复后
- 需要独立视角做质量把关时

---

## 工作流定位

- 上游：`plan-impl`（已完成 batch 内审查）
- 本 Skill：做收尾阶段全量审查编排
- 下游：`receiving-code-review`（评估与采纳反馈）→ 修复采纳项 → 原 reviewer 优先验证或替代 reviewer 降级 → 增强审查进入全新 reviewer 独立终审 → 工作区检查；dirty 或仓库尚无 HEAD 时先提示提交，clean 且有 HEAD 后进入 `verification-before-completion`
- `dev-docs-maintain` 是在 docs 健康检查、漂移修复或 verification ledger 登记需要时按需触发的普通 Skill，不是每次代码审查后的固定步骤。
