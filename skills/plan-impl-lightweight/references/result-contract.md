# Lightweight Exec Result Contract

上游消费本结果时只依赖结构化字段，不依赖自由文本乐观声明。

```markdown
## Lightweight Exec Result

状态：DONE / DONE_WITH_CONCERNS / BLOCKED / UNKNOWN
path_decision：lightweight / escalate_to_full / ask_user
execution_mode：MAIN_AGENT / SINGLE_IMPLEMENTER / NONE

### Scope Check
- 结论：LIGHTWEIGHT_OK / USE_FULL_RUNNER / ASK_USER
- 原因：<一句话>
- allowed_scope：<文件/模块>
- forbidden_scope：<禁止范围>

### 证据
- [command / diff / test / review] <path、file:line 或 command>

### Verification
- 结论：PASSED / FAILED / INCONCLUSIVE
- 覆盖：<已覆盖行为>
- 未覆盖：<明确写出>

### Review
- 状态：self_reviewed / reviewer_done / blocked
- 摘要：<审查摘要>

### 阻塞项
- BI-xxx：<阻塞原因；无则写“无”>
  - 影响范围：<impact>

### 非阻塞建议
- <建议；无则写“无”>

### 下一步
- 动作：proceed / fix_once / ask_user / escalate_to_full
- 交棒给：orchestrator / plan-impl / systematic-debugging / user
```

## 消费规则

- `DONE`：`Scope Check=LIGHTWEIGHT_OK`，`Verification=PASSED`，review 已通过，证据非空，阻塞项为“无”。
- `DONE_WITH_CONCERNS`：验证已通过，review 已完成，但存在非阻塞建议或覆盖缺口；不得有 blocking issue。
- `BLOCKED`：阻塞项不能为空，下一步必须是 `ask_user`、`escalate_to_full` 或交给调试流程。
- `UNKNOWN`：用于超时、输出不可解析或异常终止；主代理必须先检查工作树残留，再决定 salvage、retry、revert 或升级。

## 与 plan-impl 的映射

- `path_decision=lightweight` 且 `状态=DONE/DONE_WITH_CONCERNS`：可并入当前批次结果；若该结果完成了整个实现目标，则进入 runner 的 `REVIEWING -> 工作区检查 -> VERIFYING`，不得直接跳到 VERIFYING。
- `path_decision=escalate_to_full`：回到完整 runner path，重新计算任务边界或创建 exec-plan。
- `path_decision=ask_user`：暂停实现，向用户请求缺失的目标、范围、验收或验证信息。
