# Plan Amendment — 执行中需求变更

用户在执行中追加或修改需求时：

1. 暂停新 batch 派发。
2. 判定 material：Scope、Acceptance、Plan Risk、Key Decisions、Agent 自主边界、Proof、Blockers / Escalation、Risks / Rollback 任一变化都是 material；只修文案才是 non-material。
3. 记录到 Session Log（变更内容、material 判定、影响范围、时间）。
4. non-material：重算依赖图与 batch 划分，保留现有 Gate。
5. material：冻结未启动任务，更新 `plan.md` 的执行内容，并只在 `review-contract.md` 递增 Gate Revision、保留不可改写的 rN history、追加 rN+1。重评风险并重新 self-review——重评为 `low`：置 `Plan Review Status=SELF_REVIEWED`、`Review Path=self-review`、`Independent Review=not_required`；重评为 `medium / high`：置 `Plan Review Status=PENDING_INDEPENDENT_REVIEW`、`Review Path=self-review + independent reviewer`、`Independent Review=pending` 并重新独立审查。相应 Gate 通过前不得恢复调度。

非 exec-plan 的计划没有 Gate 字段：material amendment 时直接向用户确认变更后的范围与验收，再继续调度。

已在跑的子代理允许完成后再判定是否保留产出，但其产出不作为恢复调度的许可。
