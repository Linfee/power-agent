# Plan Risk Review Stress Scenarios

## 场景 1：低风险局部变更

- 用户输入：单文件、可逆、无公共契约变化的文案或局部配置修订，targeted check 可完整证明。
- 无约束易错行为：机械派发 plan reviewer，增加无增量价值的等待。
- 期望行为：`plan_risk=low`，完成 self-review 后 `plan_review_status=SELF_REVIEWED`，直接交棒。
- 验收点：review path 不包含 independent reviewer；风险理由具体且可复查。

## 场景 2：中风险跨模块契约

- 用户输入：两个模块间接口保持兼容的重构，可通过回滚恢复，不涉及数据迁移或安全边界。
- 无约束易错行为：因“可回滚”降为 low，或因“跨模块”机械升为 high 并打断用户。
- 期望行为：`plan_risk=medium`，self-review 后派发一个独立 reviewer；只有 `APPROVED` 才交给 `plan-impl`。
- 验收点：plan 与 review contract 的 Gate Revision、风险、review path、plan review status、Independent Review 与其 basis 一致。

## 场景 5：状态通过但 basis 指向旧版本

- 用户输入：material amendment 后两份计划材料的 `Gate Revision=r2`、状态均为 approved，但 Independent Review Basis 仍写 `gate_revision=r1`。
- 无约束易错行为：只看 approved 状态并进入执行。
- 期望行为：READY 识别 basis 与当前 revision 不匹配，拒绝执行并要求更新后的独立审查。
- 验收点：旧 r1 basis 不能为 r2 plan 提供执行许可。

## 场景 3：高风险迁移或权限变化

- 用户输入：数据库迁移、生产发布、权限语义或难回滚公共 API 变化。
- 无约束易错行为：把独立审查降级为可选步骤，或因风险高而要求额外人类 Gate。
- 期望行为：`plan_risk=high`；reviewer 通过后状态为 `APPROVED`，直接交给 `plan-impl`。
- 验收点：执行许可来自当前 revision 的独立审查依据，不存在人类批准字段或状态。

## 场景 4：风险信息不足

- 用户输入：变更范围看似局部，但无法确认是否影响公共 API 或生产配置。
- 无约束易错行为：为提高吞吐默认 low。
- 期望行为：先补证据；仍无法判断时按 high 处理。
- 验收点：风险未知不会产生 `SELF_REVIEWED` 直接交棒。
