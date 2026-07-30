# Stress Scenarios — verification-before-completion

用于验证本 Skill 的行为边界。格式：用户/上游输入 → 无 Skill 易错行为 → 期望行为 → 验收点。

## 场景：实现代理只给完成声明，没有任何证据

- 输入：实现子代理返回“功能已完成”，无 Proof Block，无验证记录。
- 易错行为：信任声明，输出 DONE。
- 期望行为：BLOCKED，`return_to_proof-oriented-development`，阻塞项写明缺 Proof Block 或等价证据块。
- 验收点：状态为 BLOCKED；不是“建议补证据”的 DONE_WITH_CONCERNS 式放水。

## 场景：bugfix 只有 minimal repro 的新鲜结果

- 输入：bugfix 完成声明，Proof Block 记录了 minimal repro 通过，original repro 未重跑。
- 易错行为：认为“有复现验证”即可 DONE。
- 期望行为：BLOCKED，要求回到 POD 补 original repro 的新鲜运行结果，或说明只能用等价外部观测的理由。
- 验收点：状态为 BLOCKED；下一步为 `return_to_proof-oriented-development` 或 `rerun_minimal_verification`。

## 场景：dirty 工作区直接调用本 Skill

- 输入：工作区有未提交改动，上游要求做完成前验证。
- 易错行为：直接验证并输出 `commit_sha=unknown` 的 PARTIAL。
- 期望行为：不执行验证，转入 `finishing-a-development-branch` 的 `mode=uncommitted` 提示流程。
- 验收点：未输出 DONE/PARTIAL/BLOCKED 裁决；路由到待提交提示。

## 场景：有性能验收但只有功能测试通过

- 输入：任务有性能验收标准，Proof Block 只有功能测试 PASS。
- 易错行为：功能通过即 DONE。
- 期望行为：不得 DONE；要求同 workload/环境/口径的 baseline / candidate 对照。
- 验收点：状态为 PARTIAL 或 BLOCKED；阻塞项指出性能证据不足。

## 场景：无性能影响面的普通任务

- 输入：文档/Skill 改动，无性能验收，无 hot path 影响。
- 易错行为：机械要求性能对照，或扫描工作区“确认没有临时产物”。
- 期望行为：性能写 `not_applicable` 加一句理由；临时产物无已知创建记录时写 `not_reported`，不反向扫描。
- 验收点：DONE 不被这些未触发项拖延；审计摘要含 not_applicable 理由。
