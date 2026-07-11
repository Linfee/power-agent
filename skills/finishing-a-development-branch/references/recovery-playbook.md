# 失败恢复模板

## 常见阻塞

1. 缺少验证证据
- 现象：`status=BLOCKED`，`blocking_issues.code=verification_missing`
- 建议：先运行验证流程并提供绑定当前 SHA 的结果

2. Base branch 无法确定
- 现象：`status=BLOCKED`，`blocking_issues.code=base_branch_unresolved`
- 建议：由用户明确指定 base branch

3. destructive 确认失败
- 现象：`status=CANCELLED`
- 建议：重新选择非 destructive 路径，或使用精确确认输入

## 最小恢复输出

恢复后应返回：
- 更新后的 `status`
- 清空或缩减后的 `blocking_issues`
- 明确 `next_action`
