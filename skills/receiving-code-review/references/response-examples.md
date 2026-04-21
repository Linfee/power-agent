# receiving-code-review 响应示例

## 1) accept 示例

```yaml
status: 成功
decision: 采纳
reason: "反馈指出空指针路径成立，且与现有防御模式一致。"
evidence:
  - source: "src/service/user.ts:87"
    note: "调用前未判空"
action:
  - type: 实施
    item: "在读取 profile 前增加空值分支并补测试"
blocking_issues: []
advisories: []
next_action: "实施并运行相关测试"
```

## 2) partial 示例

```yaml
status: 成功
decision: 部分采纳
reason: "命名问题成立，但建议的重构范围超出当前变更边界。"
evidence:
  - source: "src/api/order.ts:42"
    note: "变量名语义不清"
action:
  - type: 实施
    item: "仅修正命名，不扩展重构"
blocking_issues: []
advisories:
  - "后续单独提交重构 PR"
next_action: "实施可采纳部分并验证"
```

## 3) reject 示例

```yaml
status: 成功
decision: 驳回
reason: "建议会破坏已确定的数据兼容约束。"
evidence:
  - source: "docs/arch-decisions/DD-006-gate-restructuring.md:1"
    note: "现行约束禁止该变更方式"
action:
  - type: 暂缓
    item: "记录拒绝原因并回传审查者"
blocking_issues: []
advisories: []
next_action: "向审查者说明冲突证据"
```

## 4) clarify 示例（阻断）

```yaml
status: 阻塞
decision: 需澄清
reason: "反馈未指明具体失败场景，无法定位修复目标。"
evidence: []
action:
  - type: 请求澄清
    item: "请补充复现步骤与受影响模块"
blocking_issues:
  - "缺少可复现上下文"
advisories: []
next_action: "等待澄清后重新评估"
```
