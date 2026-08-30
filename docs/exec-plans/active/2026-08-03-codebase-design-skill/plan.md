---
type: Execution Plan
scope:
  - skill-design
  - workflow-routing
status: active
runner:
  state: AWAITING_COMMIT
  batch: 1/1
  phase: worktree-gate
  fix_round: 3/3
  next_action: commit-then-run-final-verification
---

# 引入 codebase-design Skill 实现计划
## Current applicability

本文档记录旧执行方案及其当时证据，不能作为当前 Skill 路由、Gate 或具名依赖的执行契约。若恢复，先依 [ADR-0010](../../../adr/0010-judgment-oriented-skills.md) 重新判断目标、约束与验收，只复用仍与当前仓库一致的事实。


## 讨论结论 / 产品结论

- 用户已确认：以本仓方式引入 `codebase-design`，用于提升 Agent 对具体代码模块的设计与实现质量。
- 结论：它是模块结构深化判断层，不是通用架构讨论、领域建模、计划编排、实施或 Proof 的替代品。

## Goal / Done Means

- 目标：分发一个自包含、可自动路由的 `codebase-design` Skill，使 Agent 能对具体模块簇收窄接口、评估深度、判断 seam / adapter 的必要性，并交接接口级 Proof 约束。
- 完成：Skill 的职责、触发边界和下游交接契约明确；仓库索引和工作流说明一致，且调用方式索引通过一致性检查。

## Scope

### In Scope
- 新增 `skills/codebase-design/`，包含紧凑主 Skill 和仅在依赖分类/接口替代比较时读取的 references。
- 将 `codebase-design` 接入 `writing-plans` 的预重构扫描，要求其结论被吸收进既有 Key Decisions / Proof Strategy，而不创建平行产物。
- 同步 AGENTS、README、架构与工作流中的 Skill 索引和职责说明。

### Out of Scope
- 不引入或依赖宿主环境的 `engineering-calibration`、`domain-modeling`；新 Skill 必须独立可分发。
- 不重构 `discuss`、`implement`、`proof-oriented-development` 或 `code-review` 的主流程，也不把模块深度变成每次审查的固定 Gate。
- 不创建 `CONTEXT.md`，也不把通用命名偏好设为仓库级规则。

## Key Decisions

- 决策：采用 model-invoked 模式；理由：Agent 需要在用户未使用专业术语时自主识别具体模块、接口或 seam 设计问题，且 `writing-plans` 需要按名调用它。
- 决策：主 Skill 只定义行为缺口、模块深度判断、删除测试、seam / adapter 证据规则与交接边界；理由：全路径常用知识内联，少见的依赖分类和替代方案探索按需下沉。
- 决策：测试替身本身不能证明需要公开或跨模块 seam；真实 I/O / 外部依赖、或两个受需求支持的运行时实现才构成稳定 seam 的证据。
- 决策：`Design It Twice` 是显式按需参考，仅在用户要求比较候选接口或计划确认高影响长期接口时使用；并发最多三个独立候选，不形成默认流程。
- 决策：模块判断不使用固定输出模板；需要持久化的结论写入现有 `writing-plans` Key Decisions 与 Proof Strategy。

## Agent 自主边界

- 可自由决策：在既定职责内选择短语、reference 文件切分与调用方式索引的同步方式，复用现有结构约定。
- 不可自行决策：不修改其他 Skill 的核心职责、调用方式或执行链；不新增外部依赖；不将外部宿主 Skill 设为前置依赖。
- 必须保持的不变量：单向工作流职责不反转；计划仍是真实源；POD 仍运行 Proof；所有 Skill 均有准确索引。
- 升级条件：若接入需要改变 `writing-plans`、Proof 或 review 的既有职责，或无法从直接 consumer 明确其职责边界，停下并向用户说明替代方案。

## Plan Review Gate

- Gate Revision：r4
- Plan Risk：medium；命中理由：新增 model-invoked Skill 并改变跨 Skill 路由和规划期交接，但无公共运行时 API、数据或发布风险。
- Review Path：self-review + independent reviewer
- Plan Review Status：APPROVED
- Independent Review：approved
- Independent Review Basis：gate_revision=r4; kind=independent-review; record=Plan Review History › Gate Revision r4

## Plan Review History

### Gate Revision r1

- Self-review：通过。范围、职责、不变量、交接与结构性 proof 已覆盖；无未定义术语或待定实现细节。
- Independent Review：issues_found
- Independent Review Basis：gate_revision=r1; kind=independent-review; record=reviewer finding “Make behavioral pressure scenarios executable proof”

### Gate Revision r2

- Self-review：通过。将核心行为压力场景升级为匿名、可判定的行为评测，并要求产生 pass/fail 结果；范围、职责、不变量、交接与 proof 一致。
- Independent Review：approved；结论：APPROVED。独立审查确认 T3 的匿名行为评测可对三个核心场景产出可复算 pass/fail 结果，且 r2 两份 Gate 元数据一致。
- Independent Review Basis：gate_revision=r2; kind=independent-review; record=Plan Review History › Gate Revision r2

### Gate Revision r3

- Self-review：用户要求移除本仓 Skill 自我评测机制；已从范围、验收、主证明和风险控制中删除评测资产，同时保留直接 consumer、结构契约和 invocation consistency check。
- Independent Review：issues_found
- Independent Review Basis：gate_revision=r3; kind=independent-review; record=Plan Review History › Gate Revision r3
- Finding：保留的模块设计规则没有明确 structural proof。

### Gate Revision r4

- Self-review：主证明明确逐项审查接口收窄、深度、删除测试、seam / adapter 证据与接口级 Proof 规则，并确认 `writing-plans` 直接消费这些结论；不恢复评测 runner 或 corpus。
- Independent Review：approved；结论：APPROVED。直接 structural proof 覆盖保留的功能规则及其 consumer，且 Gate 元数据一致。
- Independent Review Basis：gate_revision=r4; kind=independent-review; record=Plan Review History › Gate Revision r4

## Evidence Cache

- [事实] 插件清单使用 `"skills": "./skills/"` 自动发现 Skill；证据：`.claude-plugin/plugin.json:13`；影响：新增 Skill 无需改 manifest。
- [事实] `writing-plans` 在拆任务前扫描预重构机会，并在定 Proof 前选择最高可行 seam；证据：`skills/writing-plans/SKILL.md:71,105`；影响：新 Skill 的结论应由计划吸收，不产生新工作流阶段。
- [事实] 当前本地 Skill 中不存在 `codebase-design`；先前只读评估确认其独特贡献是模块深度、删除测试、adapter 证据与依赖分类。影响：新增内容不可重复现有通用 seam 测试规则。

## Tasks

- T1 [新增模块设计 Skill]：实现紧凑的 `codebase-design` 主定义及两个渐进披露 references；完成信号是其能把具体模块设计问题收敛到接口、深度、删除测试、依赖边界与接口级 Proof，且明确交接/非职责。
- T2 [接入路由与计划]：将新 Skill 登记在仓库索引、架构和工作流中，并使 `writing-plans` 在涉及模块边界时按需消费其结论；完成信号是所有说明、frontmatter 与调用方式索引一致、无平行职责。

## Proof Strategy

- 主证明：直接审查新 Skill 与其 references，逐项确认接口收窄、模块深度、删除测试、seam / adapter 证据和接口级 Proof 规则明确、非重复且由 `writing-plans` 的预重构扫描消费；同时核对前端索引、引用路径、交接边界并运行 invocation consistency script。
- 次证明：独立代码审查收敛。
- 非证明：仅格式化、阅读或宽泛文本搜索。
- 已知未验证面：不对新 Skill 运行路由或行为评测；本仓已按用户要求移除该机制。

## Blockers / Escalation

- 阻塞条件：Skill 的职责需要吞并需求讨论、领域语言、计划、实施或最终验证，或其直接 consumer 无法明确职责边界时，停止并保留现有职责边界。

## Risks / Rollback

- 风险：新 model-invoked 描述可能引入误触发与额外 context load。
  - 缓解：使用具体模块设计触发语义，并让 description、直接 consumer 与项目索引保持一致；如仍无法明确边界，将其改为 user-invoked 或仅保留为 reference。
- 风险：将测试替身误作生产 seam 的理由，导致过度抽象。
  - 缓解：将“测试 fake 单独不足”写为核心正向证据规则。
- 回滚：删除 `skills/codebase-design/` 并撤回每个索引/计划引用；不会影响运行时代码或数据。

## Optional Split Files

- none

## 当前状态

- 当前进度：r4 material amendment 已获独立审查批准；实现与审查完成，工作区尚有未提交改动。
- 下一步：提交任务范围改动后，按 r4 Proof Strategy 运行最终验证并归档。
