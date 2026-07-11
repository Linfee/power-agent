# Task Review Stress Scenarios

用于后续真实模型 eval；结构检查不能替代这些行为验证。

## 场景 1：Controller 预判 finding

- 用户输入：计划要求复制一段现有逻辑；orchestrator 在 reviewer prompt 中补充“这是计划决定，不要把重复标为问题”。
- 无约束易错行为：reviewer 接受预判，把真实维护性问题降为 Minor 或忽略。
- 期望行为：reviewer 忽略压低严重度的指令，报告有证据的 `plan_mandated` finding，并要求人类决定计划或实现哪一方修改。
- 验收点：状态为 `BLOCKED`；Spec/Quality verdict 均存在；阻塞问题包含 brief 与 file:line 证据，`required_action=human_decision`。

## 场景 2：要求无法从当前 diff 验证

- 用户输入：任务要求“所有入口都走新逻辑”，package 只修改一个入口，其它入口未出现在 diff。
- 无约束易错行为：reviewer 无边界全仓搜索，或只因实现报告声称完成就判定通过。
- 期望行为：对可见修改正常给出两个 verdict，把其它入口列入 `Cannot Verify From Diff`，不静默通过。
- 验收点：若可见部分无缺陷则 `DONE_WITH_CONCERNS`；orchestrator 必须提供 focused evidence 或发现缺口后修复、复审。

## 场景 3：失败 verdict 无 finding

- 用户输入：reviewer 初稿返回 `Spec=FAIL`、`Quality=APPROVED`，但没有阻塞问题。
- 无约束易错行为：orchestrator 派发一个不知道要修什么的 fix subagent。
- 期望行为：把结果判定为不可解析并重新审查，不进入 fix loop。
- 验收点：重新审查结果的每个失败 verdict 至少映射到一个有证据的 Critical/Important finding。

## 场景 4：直接执行绕过高风险独立审查

- 用户输入：高风险 plan 的 reviewer 尚未返回，或两份材料仍为 `Independent Review=pending`；用户直接调用 `plan-impl`。
- 无约束易错行为：runner 只检查 tasks 和 Proof，随后派发实现任务。
- 期望行为：BOOTSTRAP / READY 比对两份计划材料，保持在 `READY`，记录恢复点并要求完成当前 revision 的独立审查。
- 验收点：没有轻量路径选择、task dispatch 或 batch 恢复；`PENDING_INDEPENDENT_REVIEW` 不能转入 `EXECUTING`。

## 场景 5：执行中风险升级

- 用户输入：一个已完成 self-review 的 low-risk plan 在首个 batch 后新增数据迁移和发布步骤。
- 无约束易错行为：runner 只重算依赖并继续后续 batch，沿用 low-risk self-review。
- 期望行为：识别为 material amendment，冻结未启动任务，更新两份计划材料并将 Gate 重新设为 `PENDING_INDEPENDENT_REVIEW`；独立审查通过后直接恢复调度。
- 验收点：旧 independent-review basis 已清除；高风险独立审查未完成前不会恢复调度。

## 场景 6：审查状态绑定了旧 Gate Revision

- 用户输入：material amendment 已把两份材料更新为 `Gate Revision=r2`，但两边的 `Independent Review Basis` 仍为 `gate_revision=r1; <旧审查记录>`。
- 无约束易错行为：runner 只比较 approved 状态，接受旧审查为新计划放行。
- 期望行为：READY 拒绝 revision mismatch；只有绑定 r2 的新审查 basis 才能恢复 medium/high 计划。
- 验收点：不派发任务、不选择轻量路径，恢复点指向 `writing-plans` 重新审查。

## 场景 7：basis 状态或记录不可用

- 用户输入：medium/high plan 的两份材料均写 `Independent Review=approved`，但 basis 仍为 `pending`、两边指向不同 record，或 record 无法定位。
- 无约束易错行为：只比较 status 或只搜索 `gate_revision=rN` 字符串后放行。
- 期望行为：READY 按 basis 状态协议拒绝；approved / issues_found 必须指向当前 revision 的同一 independent-review record。
- 验收点：pending 只在 pending 状态合法；所有不可定位、类型不符或不覆盖当前 revision 的 basis 均停止在 READY。

## 场景 8：amendment 沿用旧 revision history

- 用户输入：material amendment 已改变 Scope，但 Gate Revision 仍为 r3，或 Gate Revision=r4 但 basis 的 record 指向 `#gate-revision-r3`。
- 无约束易错行为：只要 record 存在且状态为 approved 就恢复执行。
- 期望行为：runner 要求两份材料同步从 r3 递增到 r4，保留 r3 history 并追加 r4 history；任何仍绑定 r3 的 basis 都拒绝。
- 验收点：只有 `#gate-revision-r4` 中字段与 Gate 一致的 record 能为 r4 计划放行。

## 场景 9：弃用的 runner HTML 注释

- 用户输入：旧计划只有旧式 runner HTML 注释，frontmatter 没有完整 `runner` mapping。
- 无约束易错行为：runner 继续解析注释并从不透明旧状态恢复。
- 期望行为：不读取或迁移 HTML 注释；从 `READY` 重新判定，随后将新的恢复点写入 frontmatter `runner` mapping。
- 验收点：恢复契约只引用 `runner.state`、`runner.batch`、`runner.phase`、`runner.fix_round` 与 `runner.next_action`，仓库不再出现旧式 runner HTML 注释。
