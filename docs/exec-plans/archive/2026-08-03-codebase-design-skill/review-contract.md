---
type: Review Contract
scope:
  - skill-design
  - workflow-routing
---

# 引入 codebase-design Skill — Review Contract

> **归档，不再作为活动状态，历史状态保留。** 当前入口见[文档索引](../../../index.md)与 [ADR-0014](../../../adr/0014-current-baseline.md)；下文不授权恢复旧任务。

## Current applicability

本文档是旧计划的审阅快照，不定义当前运行时 Gate、固定审阅路径或 Skill 依赖。相关旧收尾由 [ADR-0012](../../../adr/archive/0012-matt-led-skill-fusion.md) 取代，不重新触发本文的 commit 或评审步骤。


## Intent

- 为本仓增加一个自包含的模块结构深化 Skill：它帮助 Agent 判断具体模块的接口深度、删除价值与 seam / adapter 必要性，并把结论交给既有计划和 Proof 流程。

## Scope

### In Scope
- 新增本地 `codebase-design` Skill 与必要 references。
- 在 `writing-plans` 的预重构扫描中按需使用该 Skill。
- 同步所有本仓 Skill 索引，并完成调用方式一致性核对。

### Out of Scope
- 不引入宿主环境 Skill 依赖，不改变通用架构/领域建模/实施/Proof/审查职责，不创建默认多代理设计流程。

## Acceptance

- [ ] `codebase-design` 对具体模块簇的接口、深度、删除测试、seam / adapter 与接口级 Proof 提供明确且非重复的判断规则。
- [ ] 新 Skill 的触发、调用方式、索引、工作流连接和 `writing-plans` 消费方式无冲突；调用方式一致性检查通过，且审查未留下阻塞问题。

## Agent 自主边界

- 可自由决策：沿用本仓语言和结构约定完成 Skill、references 与调用方式索引同步。
- 不可自行决策：不扩大到外部依赖、核心流程重写或调用方式变更。
- 必须保持的不变量：计划、Proof 和最终审查的现有归属不变；模块设计结论没有新的持久化真源。

## Proof

- 主证明：直接审查新 Skill 与 references，逐项确认接口收窄、模块深度、删除测试、seam / adapter 证据和接口级 Proof 规则明确、非重复，并由 `writing-plans` 预重构扫描消费；调用方式一致性脚本通过。
- 次证明：关键交接和结构性职责经独立审查确认。
- 非证明：仅格式化、阅读或宽泛文本搜索。
- 已知未验证面：不对新 Skill 运行路由或行为评测；本仓已按用户要求移除该机制。

## Blockers / Escalation

遇到以下情况必须停止并请求确认：

- 实现要求改变 `writing-plans`、Proof、审查或领域建模的既有责任边界。
- Skill 的职责无法从直接 consumer 与现有工作流边界明确。

## Risks

- 风险：误触发或仅由测试驱动的过度 seam。
  - 决策状态：已由仓库证据闭合。
  - 缓解方式：精确触发语义、“测试替身单独不足”规则以及与直接 consumer、项目索引的一致性。
  - 执行期阻塞条件：需要用模糊关键词或改变职责边界才能说明其用途。

## Plan Review Gate

- Gate Revision：r4
- Plan Risk：medium
- Review Path：self-review + independent reviewer
- Plan Review Status：APPROVED
- Independent Review：approved
- Independent Review Basis：gate_revision=r4; kind=independent-review; record=Plan Review History › Gate Revision r4

## Plan Review History

### Gate Revision r1

- Gate Revision：r1
- Independent Review：issues_found
- Independent Review Basis：gate_revision=r1; kind=independent-review; record=reviewer finding “Make behavioral pressure scenarios executable proof”

### Gate Revision r2

- Gate Revision：r2
- Independent Review：approved；结论：APPROVED。独立审查确认匿名行为评测已成为三个核心场景的可执行主证明，且 Gate 元数据一致。
- Independent Review Basis：gate_revision=r2; kind=independent-review; record=Plan Review History › Gate Revision r2

### Gate Revision r3

- Gate Revision：r3
- Independent Review：issues_found
- Independent Review Basis：gate_revision=r3; kind=independent-review; record=Plan Review History › Gate Revision r3
- Amendment：用户要求删除本仓 Skill 自我评测机制；移除其范围、验收与证明，并保留结构契约和调用方式一致性检查。
- Finding：保留的模块设计规则缺少明确 structural proof。

### Gate Revision r4

- Gate Revision：r4
- Independent Review：approved；结论：APPROVED。直接 structural proof 覆盖保留的功能规则及其 `writing-plans` consumer。
- Independent Review Basis：gate_revision=r4; kind=independent-review; record=Plan Review History › Gate Revision r4
- Amendment：主证明改为逐项直接审查保留的设计规则及其 `writing-plans` consumer，不恢复评测机制。

## Review Focus

- 确认范围没有把设计判断扩张为新流程、结构性验收能证明职责与交接边界，以及 model-invoked 成本受到精确触发语义和直接 consumer 约束。
