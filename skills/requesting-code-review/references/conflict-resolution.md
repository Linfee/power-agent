<!-- verified: 2026-04-21 -->
<!-- scope: code-review, conflict-resolution -->

# 双审冲突归并规则

用于 `risk_level=高风险` 时两个独立审查结果的合并。

## 归并步骤

1. 先按 `file + line + category` 对问题去重。
2. 同一问题取更高 `severity`。
3. 汇总所有阻塞问题后生成统一 `blocking_issues`。
4. 根据下述判据确定统一 `status` 与 `next_action`。

## 判据

- 任一审查出现 `严重` 阻塞：
  - `status=阻塞`
  - `next_action=启动修复子代理`

- 无 `严重`，但任一审查出现 `重要` 阻塞：
  - `status=阻塞`
  - `next_action=启动修复子代理`

- 双方均无阻塞，且至少一方存在 advisory：
  - `status=通过_含建议`
  - `next_action=继续流程`

- 双方均无阻塞且无 advisory：
  - `status=通过`
  - `next_action=继续流程`

- 双方结论证据不足或需求口径冲突：
  - `status=需澄清`
  - `next_action=重新审查`

## 轮次控制

- 每次修复后必须重新双审，不复用旧结论。
- 连续修复-复审 3 轮后仍为 `阻塞`：
  - `status=阻塞`
  - `next_action=升级处理`
