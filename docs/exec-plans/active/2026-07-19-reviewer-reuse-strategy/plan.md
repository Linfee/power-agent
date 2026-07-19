---
type: Execution Plan
scope:
  - code-review-workflow
status: active
runner:
  state: FINALIZING
  batch: 3/3
  phase: finalizing
  fix_round: 2/3
  next_action: commit_then_continue
---

# Reviewer 复用与风险分层审查策略实现计划

## 讨论结论 / 产品结论（如有）

- 一个 reviewer 在一次完整审查中覆盖需求符合、正确性、安全、维护性和测试等维度；多维审查不等于默认派发多个 reviewer。
- 修复后优先由提出问题的同一 reviewer 验证；运行时不能继续同一 reviewer 时，派新的替代 reviewer，并提供原 finding、修复说明、修复增量和验证证据。
- 高重要性或高实现风险在主审及其修复验证收敛后，再派一个此前未参与该目标审查的 reviewer 对最终变更做独立全量终审；常规审查在主审收敛后通过。
- Skill 只描述能力和降级语义，不写死 OMP、Codex、Claude Code 或任何具体 agent/message 工具名称。
- Reviewer 可以消费 `.power-agent` 中绑定当前 review session 的命名资产；编排器未提供 manifest 时不得扫描 `.power-agent`，资产只作为辅助证据。

## Goal / Done Means

- 目标：把当前“增强审查默认两个 reviewer、修复后重新双审”改为“单主审多维审查、同 reviewer 优先复审、高重要性或高实现风险稳定后独立终审”的平台无关工作流。
- Done Means：审查生命周期契约保持一致；新增按 review session 隔离的 Review Assets Manifest，内部 reviewer 与最终 reviewer 都只读取 manifest 明确列出的资产，检查 scope、freshness、source 与 sensitivity，且未提供 manifest 时不扫描 `.power-agent`；压力场景覆盖 reviewer 复用、替代降级、增强终审、显式并行双审和资产消费边界。
- 不做事项：不规定任何平台的 agent 名称、消息 API 或生命周期接口；不改变实现/修复子代理的一次性原则；不修改执行脚本。

## Scope

### In Scope
- `skills/requesting-code-review/` 主契约与 references。
- `skills/receiving-code-review/SKILL.md`、`skills/plan-impl/SKILL.md` 及内部 reviewer 交接说明。
- 新增 ADR supersede `docs/adr/0002-disposable-subagents.md`，并同步根 `AGENTS.md`、`docs/development.md`、`docs/harness-engineering.md` 中的一次性子代理原则。
- `docs/architecture.md`、`docs/workflow.md` 中审查流程描述。
- 新策略的压力场景。
- `.power-agent/review-runs/<run-id>/review-assets.md` 与同 run 的 `assets/` 辅助证据协议，以及内部/最终 reviewer 的可选 manifest 输入。

### Out of Scope
- 规划阶段 reviewer Gate。
- 具体平台的 agent adapter、调度脚本或能力探测实现。
- 实现/修复子代理复用。
- 重要性与实现风险的边界重定义。
- 不建立跨 review session 共享的 `.power-agent/assets/` 全局资产池。

## Key Decisions

- 决策：保留 `常规 / 增强` 审查强度，但将增强审查改为顺序主审与独立终审。
  - 原因：单 reviewer 已能覆盖全部审查维度；独立 reviewer 的价值是发现主审盲点，应审查稳定后的最终状态。
  - 证据：`skills/plan-impl/references/task-reviewer-prompt.md` 已由单 reviewer 同时输出规格与质量 verdict；用户本轮明确要求顺序增强审查。
  - 执行含义：低/中重要性且主审阶段实现风险非高时，主审收敛即通过；高重要性，或初始主审/主审修复验证任一时点判定高实现风险时，当前有效强度升级为增强，主审阶段收敛后进入独立终审。
- 决策：复审采用平台能力导向降级。
  - 原因：Skill 需要适用于不同 agent runtime，不能假设已有 reviewer 一定可恢复。
  - 证据：用户明确要求优先复用同一 reviewer，并在不支持复用时回退新 reviewer。
  - 执行含义：规则只描述“支持继续同一 reviewer”与“不支持时派替代 reviewer”，不出现具体工具调用。
- 决策：修复验证必须产生新 verdict，但默认是 focused verification，不机械重跑完整双审。
  - 原因：原 reviewer 已有 finding 上下文；只要范围未实质扩大，验证原问题、修复增量和影响边界即可。
  - 证据：`skills/requesting-code-review/references/conflict-resolution.md` 当前要求每轮重新双审，是本次要消除的重复成本来源。
  - 执行含义：范围实质扩大、风险升级或验收改变时重新完整主审，否则由原 reviewer 或替代 reviewer 验证修复。
- 决策：并行双审仅保留为显式路径。
  - 原因：用户显式要求或确有独立专业审查边界时仍可能需要并行结果归并，但不应成为高重要性的默认行为。
  - 证据：现有 `conflict-resolution.md` 可保留为并行结果归并 reference。
  - 执行含义：主 Skill 仅在显式要求并行双审时引用冲突归并规则。
- 决策：以新 ADR supersede ADR-0002，将一次性原则限定为实现/修复子代理与跨目标复用。
  - 原因：ADR-0002 明确禁止与同一子代理多轮对话，直接冲突于同一 review session 优先继续 reviewer 的目标；accepted ADR 不能原地改写历史。
  - 证据：`docs/adr/0002-disposable-subagents.md:25-33`、`docs/development.md:121-132`。
  - 执行含义：保留干净实现/修复上下文；允许 reviewer 在同一目标内验证自己提出的 finding；新增 ADR-0007 supersede ADR-0002，并将 ADR-0002 frontmatter/status 标记为 `superseded`、以 `superseded_by` 指向 ADR-0007，同时保留正文历史。
- 决策：Review Assets 按 review session 隔离，并通过显式 manifest 交接。
  - 原因：允许 reviewer 使用测试日志、截图、trace、benchmark 等证据，同时避免扫描历史 run、误用过期资产或绑定具体平台工具。
  - 证据：当前 `review-artifact-protocol.md` 已将 scratch artifacts 放在 `.power-agent/review-runs/<run-id>/`，但最终 reviewer 没有统一资产输入；用户确认采用推荐方案。
  - 执行含义：每个 run 可选包含 `review-assets.md` 和 `assets/`；编排器显式传当前 review session 的权威 `review_run_root`，manifest 路径与解析结果必须严格位于该 root。manifest 至少声明 path、kind、purpose、scope、freshness、source，可选 sensitivity。`path` 必须是 root 下 `assets/` 内的普通文件相对路径；拒绝跨 run、绝对路径、`..` traversal、symlink 路径或解析后越界目标。缺少 manifest 时 reviewer 不扫描 `.power-agent`。
- 决策：资产是辅助证据，不替代代码、diff、需求或新鲜验证。
  - 原因：artifact 可重建且可能过期，implementer report 也只是待验证 claim。
  - 证据：`skills/plan-impl/references/review-artifact-protocol.md:21-26` 已定义 scratch artifact 非 durable source of truth。
  - 执行含义：字段必须可与当前派发输入比较：scope 同时绑定当前 task/batch/final review 目标及适用 `paths=` 或 `finding=`；freshness 绑定 reviewer 当前可见的 review basis（内部 review package、commit range 或编排器提供的 working-tree snapshot 标识）；source 给出可追溯生产者以及生成命令、报告或原始证据引用；sensitivity 缺省为 `normal`，`restricted` 只有当前派发显式授权时可读。字段缺失、未知、不可比较、不匹配，或文件缺失/越界时，reviewer 不读取或不采信该资产，只报告 evidence gap，且不自行扩大读取范围。

## Agent 自主边界

- 可自由决策：manifest 的 Markdown 字段组织、kind 枚举、压力场景表达和保持现有审查输出兼容的最小调整；不得改变 path/scope/freshness/source/sensitivity 的最小校验语义。
- 不可自行决策：不得建立全局共享资产池、允许 reviewer 扫描 `.power-agent`、把资产提升为 durable source of truth，或绑定具体平台工具。
- 必须保持的不变量：修复后产生新 verdict；独立终审 reviewer 保持独立；实现/修复子代理仍一次性；reviewer 只读当前 session manifest 明确列出的资产；无 manifest 时不扫描；代码/diff/需求优先于资产 claim。
- 触发升级条件：需要持久化敏感资产、资产必须跨 session 共享，或现有 scratch 安全边界无法表达 freshness/sensitivity。

## Plan Review Gate

- Gate Revision：r2
- Plan Risk：medium
- Review Path：self-review + independent reviewer
- Plan Review Status：APPROVED
- Independent Review：approved
- Independent Review Basis：gate_revision=r2; kind=independent-review; record=history://ReviewAssetsPlanR2

## Evidence Cache（仅记录非显然事实）

- 最新主 Skill 已区分重要性、实现风险与审查强度，但增强审查仍等同双审；证据：`skills/requesting-code-review/SKILL.md:74-80`；影响：保留三个维度，只改变增强审查时序。
- 当前归并规则要求每次修复后重新双审；证据：`skills/requesting-code-review/references/conflict-resolution.md:35-40`；影响：必须将该 reference 限定为显式并行双审，并把修复验证规则移回主 Skill。
- 当前内部 task/batch reviewer 已单次覆盖规格与质量双 verdict；证据：`skills/plan-impl/SKILL.md:163-170`；影响：新策略应复用单 reviewer 多维审查模型并补齐 reviewer 生命周期。
- 根 `AGENTS.md:68` 的“子代理一次性”会禁止同一 review session 继续 reviewer；影响：需限定为不跨目标复用，并明确同一 finding 修复验证例外。
- accepted ADR-0002 禁止与同一子代理多轮对话；证据：`docs/adr/0002-disposable-subagents.md:25-33`；影响：必须新增 ADR-0007、将 ADR-0002 标记为 superseded 并建立双向元数据，再同步所有直接引用。
- 当前最终审查 Skill 没有统一 `.power-agent` 资产输入，内部 reviewer 也只接收 brief/report/package/repair context；影响：需要同时扩展 artifact protocol、两个 reviewer prompt 和主 Skill 的最小输入，而不是允许自由扫描目录。

## Tasks

- T1 全量审查策略：更新 `requesting-code-review` 主契约、风险分级、reviewer prompt、输出协议、并行双审归并边界和压力场景，使常规、增强、显式并行路径可判定。
- T2 交接与生命周期：同步 `receiving-code-review`、`plan-impl` 内部复审和项目级规则；新增 ADR-0007 supersede ADR-0002，将 ADR-0002 的 YAML status 改为 `superseded` 并添加 `superseded_by`，明确同 reviewer 优先、替代 reviewer 降级、独立终审全新、实现/修复子代理仍一次性。
- T3 文档与验证：同步 architecture、workflow、development、harness-engineering，运行定点结构/引用检查与场景核对，完成独立最终审查并修复发现。
- T4 Manifest 契约：在 `review-artifact-protocol.md` 定义 per-run `review-assets.md`、`assets/`、字段最小语义、普通文件与解析后路径约束、证据优先级和 sensitivity 默认拒绝边界。
- T5 Reviewer 接入：为内部 reviewer 和 `requesting-code-review` 最终 reviewer 增加可选 `review_assets_manifest`、权威当前 `review_run_root`、可比较的 review basis 与受限资产授权输入；明确只读命名资产、无 manifest 不扫描、字段缺失/未知/不匹配、跨 run、文件缺失/过期/越界时只报告 evidence gap。
- T6 文档与验证：同步 plan-impl/requesting-code-review 主链路、architecture/workflow/development 和压力场景，运行 manifest 字段与 containment 断言、旧行为排除检查、主审与独立终审。

## Proof Strategy

- 主证明：逐项核对四个压力场景：常规审查修复后同 reviewer 通过；增强审查主审收敛后独立终审；运行时不支持 reviewer 继续时替代 reviewer 复审；显式并行双审仍可归并。
- 次证明：定点搜索确认主链路不再存在“高重要性直接双审”“每次修复后必须重新双审”，检查所有 reference 路径、阶段字段和上下游交接一致，并确认 ADR-0007 的 `supersedes` 与 ADR-0002 的 `status: superseded` / `superseded_by` 双向闭合、直接引用已更新。
- 非证明：只确认文件存在、Markdown 可解析或宽泛搜索到新关键词不能单独证明工作流正确。
- 已知未验证面：不运行真实跨平台 sub-agent 生命周期 eval；以平台无关契约和回退压力场景证明。
- 失败解释：旧规则仍在主链路可达位置出现，或任一场景无法唯一推导下一步时，返回对应契约文件修正。
- 资产协议主证明：场景验证无 manifest 不扫描；有效 manifest 只读权威当前 run `assets/` 下的普通文件；旧 run、manifest/asset symlink、绝对、traversal、解析后越界、过期、target+paths/finding scope 不匹配或未授权 restricted 资产均不读取/不采信；最终 reviewer 可消费显式有效资产但保持独立判断。
- 资产协议次证明：检查 path、kind、purpose、target+paths/finding scope、freshness、source 与可选 sensitivity 的最小语义，权威 run root 与 review basis 可比较，低/中重要性的初始主审或主审修复验证发现高实现风险时确定升级增强并进入独立终审，reference 路径存在、平台名称缺失和文档一致性。

## Blockers / Escalation

- 阻塞条件：需要写死具体平台 API 才能表达 reviewer 继续；新流程需要破坏现有状态协议；无法保证独立终审 reviewer 未参与此前审查。
- 升级对象：用户。
- 升级时携带材料：冲突字段、相关 Skill 交接链路和最小替代方案。

## Risks / Rollback

- 风险：同 reviewer 复审被误解为沿用旧 verdict。
  - 失败信号：规则允许不读取修复增量或不产生新结论。
  - 缓解方式：明确复审基于最终代码、修复增量、影响边界和新验证证据产生新 verdict。
  - 回滚方式：恢复当前审查契约文件。
- 风险：项目级例外导致 reviewer 被跨目标长期复用。
  - 失败信号：规则没有限定同一实现目标和同一 review session。
  - 缓解方式：明确禁止跨目标复用，只有同一目标的 finding 验证可继续原 reviewer。
  - 回滚方式：恢复原一次性规则并只保留替代 reviewer 路径。
- 风险：manifest 指向旧 run、目录外路径或敏感资产。
  - 失败信号：reviewer 可读取未列出、跨 run、绝对路径或 scope/freshness 不匹配的文件。
  - 缓解方式：仅允许 manifest 所在 run 内的相对路径；声明 source/freshness/sensitivity；不满足时拒绝作为证据并报告缺口。
  - 回滚方式：将 manifest 输入设为 `not_applicable`，恢复仅使用现有 review package 的路径。

## Optional Split Files（如有）

- `context.md`：none
- `tasks.md`：none

## 当前状态

- 当前进度：资产协议主审与独立终审均已收敛；工作树保持 dirty/uncommitted。
- 下一步：提交当前变更后重新通过 WORKTREE_GATE，绑定新 HEAD 运行 `verification-before-completion`，通过后归档 exec-plan。

## Session Log

### 2026-07-19

- 实现：全量审查改为单主审多维审查、finding owner 优先复验、不可继续时替代 reviewer 降级，以及高重要性/高实现风险顺序独立终审；新增 ADR-0007 并 supersede ADR-0002。
- 验证：审查工作流结构与压力场景断言全部通过；主审修复项 5/5 断言通过；`git diff --check` 通过；`skills/dev-docs-maintain/scripts/test_bundle_status.py` 37 tests 通过；docs bundle scan structural findings=0。
- 审查：主审提出 3 个阻塞 finding，均由原主审复验关闭；全新 reviewer 独立终审通过，下一步为继续流程。
- 收尾：工作树 dirty，按 `WORKTREE_GATE` 保持 active/uncommitted；未运行绑定 clean HEAD 的 `verification-before-completion`，未归档计划。
- Material amendment：用户确认按推荐方案允许 reviewer 使用当前 review session 的显式 `.power-agent` assets；Gate Revision 从 r1 递增为 r2，清除旧 independent-review basis，重新进入 medium 风险计划审查。
- 计划审查：r2 独立 reviewer 首轮发现 containment 与字段校验语义不足；修订 path/scope/freshness/source/sensitivity 契约后由同 reviewer 复验通过，依据 `history://ReviewAssetsPlanR2`。
- 资产验证：结构与文档断言通过；无 manifest reviewer 未扫描或读取 `.power-agent`；有效 manifest 烟测只读取一个通过 scope/freshness/source/sensitivity 与 containment 校验的普通文件，并拒绝 stale、symlink、traversal、restricted 四类条目，依据 `history://AssetsNoManifestSmoke` 与 `history://AssetsManifestSmoke`。
- 回归检查：`git diff --check` 无输出；`test_bundle_status.py` 运行 37 tests，结果 OK；本次 Skill 契约未出现 OMP、Codex、Claude Code 或私有 agent/message API。
- 主审：发现两个直接 reviewer prompt 未在读取 manifest 前拒绝 manifest/父路径 symlink；同步主 Skill 与场景后，原主审通过结构断言和实际 manifest symlink 烟测确认修复，`状态=通过`、`审查阶段=主审修复验证`、`下一步=进入独立终审`，依据 `history://ReviewAssetsPrimary`。
- 独立终审：全新 reviewer 发现高实现风险在主审修复验证首次出现时可能漏掉终审、scope 未强制 target+paths/finding 双匹配、manifest 未绑定权威当前 run root；修复后又发现修复验证风险升级仍只覆盖初始主审。全部同步到主 Skill、prompts、risk/output contracts、plan-impl、docs 与场景十一/十二后，原终审 reviewer 以 `审查阶段=终审修复验证` 返回 `状态=通过`、`下一步=继续流程`，依据 `history://ReviewAssetsFinal`。
- 最终状态：新增 Review Assets Manifest 契约已通过无 manifest、有效/无效资产、manifest symlink、跨 run/metadata/风险升级结构场景与两阶段全量审查；clean-HEAD 完成前验证仍需提交后执行。
