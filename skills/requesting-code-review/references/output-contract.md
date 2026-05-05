<!-- verified: 2026-05-05 -->
<!-- scope: code-review, contract -->

# 审查输出协议（Output Contract）

`requesting-code-review` 与审查子代理之间统一使用以下结构：

```yaml
status: 通过 | 通过_含建议 | 阻塞 | 需澄清
risk_level: 低风险 | 中风险 | 高风险
evidence:
  - source: string
    locator: string
    summary: string
blocking_issues:
  - severity: 严重 | 重要
    issue: string
    impact: string
    required_fix: string
advisories:
  - severity: 轻微
    suggestion: string
next_action: 继续流程 | 启动修复子代理 | 重新审查 | 升级处理
```

## 字段说明

- `status`
  - `通过`: 无阻塞问题，可继续。
  - `通过_含建议`: 无阻塞问题，但存在改进建议。
  - `阻塞`: 存在必须修复的问题。
  - `需澄清`: 信息不足或需求歧义，需补充后再判定。

- `risk_level`
  - 由编排器按 `references/risk-classification.md` 判定。

- `evidence`
  - 必须来自可追溯信号（diff、测试输出、日志、文件定位）。

- `blocking_issues`
  - 仅包含阻塞合并/继续执行的问题。
  - `severity` 仅允许 `严重 | 重要`。

- `advisories`
  - 非阻塞建议，不得与阻塞问题混写。

- `next_action`
  - `继续流程`: 继续后续流程。
  - `启动修复子代理`: 启动修复子代理。
  - `重新审查`: 修复后重新审查。
  - `升级处理`: 连续修复-复审耗尽后升级处理。

## 一致性约束

- `blocking_issues` 非空时，`status` 必须是 `阻塞`。
- `status=通过|通过_含建议` 时，`blocking_issues` 必须为空。
- `status=阻塞` 时，`next_action` 不能是 `继续流程`。
- `status=通过|通过_含建议` 时，`evidence` 不能为空。
