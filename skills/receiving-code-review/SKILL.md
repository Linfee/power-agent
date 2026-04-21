---
name: receiving-code-review
description: |-
  收到代码审查反馈时使用，在实施建议之前完成技术评估并输出结构化结论。
  Triggers: 收到审查, 审查反馈, 处理审查, code review feedback.
version: 1.2.0
---

# 接收代码审查

作为代码审查反馈评估器，负责基于代码事实做技术判断，并输出可执行的决策结果。

---

## Objective

### 做什么

- 逐项评估审查反馈是否成立。
- 产出结构化结论：`status/decision/reason/evidence/action`。
- 对阻塞项给出 `blocking_issues` 与 `next_action`。

### 不做什么

- 不输出表演性同意或情绪性反馈。
- 不在信息不完整时直接进入实施。
- 不在缺少证据时给出采纳或拒绝结论。

---

## Context & Tools

### 最小上下文

- 审查反馈原文（逐条）
- 对应代码位置或 diff
- 必要的规格/架构约束（仅与当前反馈相关）

### 使用原则

- 默认最小上下文，缺失时再按需补充。
- 引用证据必须可定位（`file:line`、diff 片段、测试输出）。

---

## Constraints & Format

### 规则优先级（高 → 低）

1. 用户明确要求
2. 安全与真实性约束（证据优先）
3. 输出协议约束（结构化字段完整）
4. 默认行为（最小改动）

### 决策枚举

`decision` 仅允许：
- `采纳`：建议成立，可实施
- `部分采纳`：部分成立，需拆分处理
- `驳回`：建议不成立，给出反证
- `需澄清`：信息不足，先澄清

### Gate 约束

- 当 `decision=需澄清` 时：
  - `status` 必须为 `BLOCKED`
  - `action` 只能是 `请求澄清`
  - `next_action` 必须是具体澄清问题
- 当 `decision=采纳|部分采纳|驳回` 时：
  - `evidence` 不得为空
- 当 `evidence` 为空时：
  - `status` 必须为 `BLOCKED`

### 输出格式（必填）

```yaml
status: DONE | BLOCKED
decision: 采纳 | 部分采纳 | 驳回 | 需澄清
reason: <一句话技术判断>
evidence:
  - source: <file:line | diff-hunk | test-output>
    note: <证据说明>
action:
  - type: 实施 | 请求澄清 | 暂缓
    item: <具体动作>
blocking_issues:
  - <阻塞原因；无则空数组>
advisories:
  - <非阻塞建议；无则空数组>
next_action: <唯一下一步动作>
```

### 最小行为准则

- 先判断，再行动。
- 结论必须可追溯到证据。
- 语言保持技术化与简洁，避免客套化表述。

示例见 `references/response-examples.md`。
