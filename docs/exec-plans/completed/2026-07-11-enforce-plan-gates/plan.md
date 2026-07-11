---
type: Execution Plan
scope:
  - skills/plan-impl
  - skills/dev-docs-maintain
  - skills/writing-plans
  - docs/workflow.md
  - docs/architecture.md
status: completed
---

# 强制计划 Gate 与修复 scope 来源推断

## Goal / Done Means

- 目标：使 `plan-impl` 在执行前和实质 amendment 后强制消费 `writing-plans` 的风险 Gate，并防止 `dev-docs-maintain` 将概念性 scope 错判为缺失 source。
- Done Means：pending 或不一致的 medium/high Gate 无法进入 `EXECUTING`；实质 amendment 会重新走相应 Gate；`docs/workflow` 这类概念 scope 不再使 Bundle scan 进入 `blocked`。
- 不做事项：不改变低风险计划的 self-review 路径、不改变最终全分支审查或 verification ledger 格式。

## Scope

### In Scope

- `plan-impl` 的 READY、状态转移、Plan Amendment 与压力场景。
- `dev-docs-maintain` 的 scope/source 推断、单测和文档说明。
- 主链路架构/流程文档中的 Gate 消费规则。

### Out of Scope

- 真实模型多轮 eval、计划文件的批量迁移、Git 提交/推送。

## Key Decisions

- 决策：Gate 由执行方在 READY 强制验证，而不信任调用方已正确路由。
  - 原因：直接调用或恢复 `plan-impl` 是现有入口，planning 侧提示不足以防绕过。
  - 证据：`skills/plan-impl/SKILL.md` 的 READY 尚未消费 Plan Risk；上轮审查发现该绕过路径。
  - 执行含义：medium/high 只有状态、独立审查与审计依据一致时才可执行。
- 决策：仅真实存在的 scope 路径或显式 glob 参与 source snapshot；概念性 scope 不推断为 source。
  - 原因：scope 可以表达知识边界，不能因路径形文本成为缺失来源。
  - 证据：`docs/exec-plans/completed/2026-07-11-adopt-review-artifacts/plan.md` 的 `docs/workflow` 使 scan blocked。
  - 执行含义：若要追踪不存在或必须存在的来源，文档须显式写入 `sources`。
- 决策：Gate basis 按状态绑定 revision 与稳定记录。
  - 原因：单独的 approved 文本或 revision 字符串无法证明它对应当前计划材料。
  - 证据：最终代码审查指出模板和自由文本 basis 无法判定旧审查是否覆盖当前 Gate。
  - 执行含义：pending/not_required 使用规范占位值；已出结论的 basis 必须包含 revision、记录类型和稳定位置。

## Agent 自主边界

- 可自由决策：文本组织、断言名称和现有单测内的最小 fixture 调整。
- 不可自行决策：放宽 high 独立审查要求、修改 ledger schema。
- 必须保持的不变量：low 路径不增加独立 reviewer；范围变化不允许沿用过期审查依据；scope 仍可追踪现存文件、目录和 glob。
- 触发升级条件：需要兼容没有 Gate 字段的 legacy plan，或必须改变风险等级枚举。

## Plan Review Gate

- Gate Revision：r4
- Plan Risk：medium
- Review Path：self-review + independent reviewer
- Plan Review Status：APPROVED
- Independent Review：approved
- Independent Review Basis：`gate_revision=r4; kind=independent-review; record=docs/exec-plans/active/2026-07-11-enforce-plan-gates/review-contract.md#gate-revision-r4`

### Self-Review 结论

- 需求覆盖：三个审查 finding 分别映射 T1、T2、T3 和对应 proof。
- 占位符：计划、review contract、状态枚举、scope/source 语义均已写明，无待补字段。
- 一致性：`plan.md` 与 `review-contract.md` 均为 medium / independent reviewer approved。
- 任务边界：T1/T2 共同维护 runner 状态契约，T3 独立维护 scanner 与文档；每项都有独立可观察证明。
- 风险校准：不涉及高风险边界；跨 Skill 契约维持 medium，缺失或冲突 Gate 一律停止执行。

## Evidence Cache（仅记录非显然事实）

- `writing-plans` 已定义 low / medium / high 的状态映射及独立审查要求；证据：`skills/writing-plans/SKILL.md` Step 2；影响：runner 必须消费而不能重解释这些状态。
- `plan-impl` 的首次执行和恢复都经过 BOOTSTRAP / READY；证据：`skills/plan-impl/SKILL.md` State Machine 与 BOOTSTRAP / READY；影响：同一 Gate 校验必须覆盖两个入口。
- `scope_declares_source` 目前将 path-shaped value 直接作为 source；证据：`skills/dev-docs-maintain/scripts/bundle_status.py`；影响：conceptual `docs/workflow` 会进入 missing source，而真实 path、directory、glob 仍需保持跟踪。

## Tasks

- T1：在 READY、恢复路径与状态转移中定义并强制校验 plan/review-contract Gate；唯一稳定 record 是 `review-contract.md` 的追加式 `Plan Review History / Gate Revision rN`，完成信号是 low/medium/high 的允许/拒绝矩阵可由规则与压力场景逐项核对，且 basis 必须同时通过状态、Gate Revision、记录类型、同一 record 位置与 history 字段一致性。
- T2：定义 material Plan Amendment（Scope、Acceptance、风险等级、关键决策或 Agent 自主边界变化），冻结未启动任务，将两份材料的 `Gate Revision` 从 rN 同步递增到 rN+1，保留不可改写的 rN history、追加 rN+1 history、作废旧 basis、重新 self-review 并按重评风险重入独立审查；非实质变更仅在不改变上述边界时保留现有 Gate。
- T3：收紧 scope/source 推断，补回归测试与文档，并同步主链路说明。

## Proof Strategy

- 主证明：`bundle_status.py` 单测分别覆盖 conceptual path-shaped scope 不阻塞、现存文件/目录 scope 与匹配 glob 仍追踪 source change；定向 scan 证明现有 `docs/workflow` scope 不再 blocked。
- 次证明：Gate truth table 覆盖 low 可执行、medium pending/contract conflict 拒绝、medium approved 可执行、high pending/basis 缺失拒绝、high approved + matching basis 可执行；approved 但 basis=pending、旧 revision、不可定位/不同 record、history 字段不一致，或 amendment 后沿用 rN/history rN 均拒绝；material amendment 同步递增 rN+1、保留 rN history、追加 rN+1 history 并重新进入对应 Gate，非实质 amendment 保持 Gate。规则、stress scenario、workflow/architecture 必须引用同一矩阵。
- 补充证明：全量文档 Skill 单测、documentation eval 与 review-package 自测。
- 非证明：仅阅读 Skill 文本。
- 已知未验证面：不运行真实模型的 Gate 遵从性 eval。
- 失败解释：Gate 契约冲突回到 T1/T2；scope 测试或 scan 失败回到 T3。

## Blockers / Escalation

- 阻塞条件：发现 legacy plan 必须无条件继续执行，或 Gate 状态无法在两份计划文件间一致表达。
- 升级对象：用户。
- 升级时携带材料：冲突计划样例、Gate 字段、最小兼容方案和验证结果。

## Risks / Rollback

- 风险：过严 Gate 阻断旧计划。
  - 失败信号：READY 无法判定现有计划的 Gate。
  - 缓解方式：明确缺失/冲突时回到 `writing-plans` 的最小修订路径。
  - 回滚方式：恢复本次 Skill/文档改动，不改现有 plan 内容。
- 风险：scope 不再追踪已删除的隐式文件路径。
  - 失败信号：需要探测的来源只写在 scope 中且不存在。
  - 缓解方式：明确要求这类来源写入 `sources`。
  - 回滚方式：恢复原推断规则。

## 当前状态

- 当前进度：完成。
- 下一步：已归档至 `docs/exec-plans/completed/`。

## Session Log

- 完成计划风险 Gate 的 READY / amendment 消费、scope/source 推断修复及直接文档同步。
- 后续取消人类显式批准 Gate：`discuss`、`writing-plans`、`plan-impl`、模板、压力场景与主流程文档统一改为独立审查放行；`review-contract.md` 仅保留按需审阅职责。
- 验证：`python3 -m unittest skills/dev-docs-maintain/scripts/test_bundle_status.py`（37 tests）；`python3 -m unittest evals/documentation-skills/test_run_pi_eval.py`（18 tests）；`bash skills/plan-impl/scripts/test-review-package.sh`。
