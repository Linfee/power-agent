---
type: Review Contract
scope:
  - plan-gate-enforcement
status: completed
---

# Review Contract：强制计划 Gate 与 scope 来源推断

## Intent

- 让计划风险 Gate 在 `plan-impl` 的实际执行入口不可绕过，并修复 docs scope 被误判为 source 的扫描阻塞。

## Scope

### In Scope

- READY/Plan Amendment Gate 消费、scope/source 推断、直接文档与压力场景同步。

### Out of Scope

- 生产操作、Git 历史、ledger schema、真实模型评测。

## Acceptance

- [ ] medium/high 计划在 Gate pending、缺失或与 review contract 冲突时不能进入 EXECUTING。
- [ ] 实质 amendment 会重新计算风险并使旧审查依据失效。
- [ ] 概念性 `docs/workflow` scope 不再产生 `missing_sources`，现有文件、目录和匹配 glob scope 仍可被追踪。

## Agent 自主边界

- 可自由决策：最小文本和单测调整。
- 不可自行决策：放宽高风险独立审查要求、改变 ledger schema。
- 必须保持的不变量：low 自查路径、source 显式声明优先、最终全分支审查不变。

## Proof

- 主证明：bundle-status 定向单测与实际 Bundle scan。
- 次证明：Gate/stress scenario 结构检查、现有文档 Skill eval 与 review-package 自测。
- 非证明：仅检查文件存在。
- 已知未验证面：真实模型执行 Gate 的行为 eval。

## Blockers / Escalation

- legacy plan 必须无 Gate 继续执行，或两份计划文件无法表达同一 Gate 状态时停止并请求用户决定。

## Risks

- 风险：旧计划缺少 Gate 字段会被暂停。
  - 决策状态：可由仓库证据闭合。
  - 缓解方式：回到 writing-plans 最小补齐 Gate 字段。
  - 执行期阻塞条件：缺失或冲突的 Gate 不得执行。

## Plan Review Gate

- Gate Revision：r4
- Plan Risk：medium
- Review Path：self-review + independent reviewer
- Plan Review Status：APPROVED
- Independent Review：approved
- Independent Review Basis：`gate_revision=r4; kind=independent-review; record=docs/exec-plans/active/2026-07-11-enforce-plan-gates/review-contract.md#gate-revision-r4`

## Plan Review History

### Gate Revision r1

- Gate Revision：r1
- Independent Review：approved
- Independent Review Basis：`gate_revision=r1; kind=independent-review; record=docs/exec-plans/active/2026-07-11-enforce-plan-gates/review-contract.md#gate-revision-r1`

### Gate Revision r2

- Gate Revision：r2
- Independent Review：issues_found
- Independent Review Basis：`gate_revision=r2; kind=independent-review; record=docs/exec-plans/active/2026-07-11-enforce-plan-gates/review-contract.md#gate-revision-r2`

### Gate Revision r3

- Gate Revision：r3
- Independent Review：issues_found
- Independent Review Basis：`gate_revision=r3; kind=independent-review; record=docs/exec-plans/active/2026-07-11-enforce-plan-gates/review-contract.md#gate-revision-r3`

### Gate Revision r4

- Gate Revision：r4
- Independent Review：approved
- Independent Review Basis：`gate_revision=r4; kind=independent-review; record=docs/exec-plans/active/2026-07-11-enforce-plan-gates/review-contract.md#gate-revision-r4`

## Review Focus

- 独立 reviewer 只判断本计划能否以最小改动闭合上述三个缺陷；不审具体实现逐行细节。
