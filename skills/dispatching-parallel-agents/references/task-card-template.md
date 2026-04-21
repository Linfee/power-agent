# Task Card Template

用于并行子任务分发的最小输入协议。

```yaml
goal: <一句话目标，说明要完成什么>
scope:
  files: ["<允许修改的文件或目录>"]
  boundaries: ["<禁止触达的边界>"]
blocked_by: ["<前置任务ID，可空数组>"]
expected_output:
  type: <code|analysis|review|mixed>
  artifacts: ["<预期产物，如 patch/结论/报告>"]
constraints:
  must_follow: ["<必须满足的约束>"]
  must_not: ["<明确禁止项>"]
verification:
  required_checks: ["<最低验证要求，如 test target / lint 命令 / 证据类型>"]
```

## 填写要求
- `goal` 必须可验证，避免模糊目标。
- `scope.files` 必须尽量具体，防止改动面漂移。
- `blocked_by` 非空时不得提前执行。
- `constraints` 仅写对本任务有影响的约束，不复制全局规则。
- `verification.required_checks` 需与 expected_output 对齐。
