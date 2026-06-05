<!-- verified: 2026-06-03 -->
<!-- scope: plan-impl-lightweight, stress-scenarios -->

# Lightweight Exec Path 压力场景

### 场景：局部文档或 Skill 小改

- 用户输入："把某个 Skill 的输出格式补充一个字段，并跑一下验证。"
- 无 Skill 易错行为：直接修改后声称完成，没有检查范围和验证证据。
- 期望行为：先做 scope_check，确认 allowed_scope 和验证方式明确；主代理直接执行；运行 targeted verify；输出 `DONE` 和证据。
- 验收点：结果包含 `LIGHTWEIGHT_OK`、验证命令摘要、修改文件列表，无 blocking issue。

### 场景：边界不清的中等任务

- 用户输入："顺手把执行流程也优化一下，相关地方你看着改。"
- 无 Skill 易错行为：把轻量任务扩大成跨文档/跨 Skill 大改，缺少用户决策。
- 期望行为：scope_check 返回 `ASK_USER` 或 `USE_FULL_RUNNER`，说明缺少目标行为、allowed_scope 或验收标准。
- 验收点：没有启动实现；下一步为 `ask_user` 或 `escalate_to_full`。

### 场景：发现共享改动面

- 用户输入："同时改两个独立功能，它们都要更新同一个 registry。"
- 无 Skill 易错行为：误判为可轻量并行，导致共享出口冲突。
- 期望行为：scope_check 识别共享出口文件风险，返回 `USE_FULL_RUNNER` 或建议先拆分/串行化，再交由完整 runner 或宿主编排能力处理。
- 验收点：输出风险原因，未进入 lightweight execute。

### 场景：一次修复后仍阻塞

- 用户输入："修这个局部 bug，测试已经给了。"
- 无 Skill 易错行为：多轮轻量修复，直到范围失控。
- 期望行为：第一次 targeted verify 失败且局部根因明确时允许 `fix_once`；第二次仍失败或 review 阻塞时返回 `path_decision=escalate_to_full`。
- 验收点：最多一次 fix loop；第二次失败后不继续轻量修复。
