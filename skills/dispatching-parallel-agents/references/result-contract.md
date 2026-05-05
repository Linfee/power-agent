<!-- verified: 2026-05-05 -->
<!-- scope: dispatching-parallel-agents, result-contract -->

# Result Contract

用于并行子代理返回结果的统一输出协议。

```yaml
status: <DONE|PARTIAL|BLOCKED|FAILED>
evidence:
  checks: ["<已执行验证与结果摘要>"]
  artifacts: ["<关键文件/命令输出/定位信息>"]
blocking_issues:
  - issue: <阻塞描述>
    impact: <影响范围>
    required_unblock: <解除阻塞所需动作>
advisories:
  - <非阻塞建议>
next_action:
  owner: <orchestrator|implementer|reviewer|user>
  action: <下一步动作>
```

## 字段约束
- `status=DONE` 时，`evidence.checks` 不得为空。
- `status=BLOCKED` 时，`blocking_issues` 至少包含一项。
- `status=FAILED` 时，必须给出失败原因与建议处理路径。
- `advisories` 为可选；无建议时返回空数组。
- `next_action` 必须可执行，避免“继续处理”这类空泛表达。
