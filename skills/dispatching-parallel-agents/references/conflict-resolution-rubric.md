<!-- verified: 2026-05-05 -->
<!-- scope: dispatching-parallel-agents, conflict-resolution -->

# Conflict Resolution Rubric

用于主代理在并行结果汇总阶段进行冲突检测与归并。

## 1) 冲突检测
出现以下任一情况即判定为冲突：
- 目标文件重叠且改动语义不一致。
- 公共接口签名不一致。
- 数据模型或协议字段定义不一致。
- 同一验证目标得出互斥结论。

## 2) 归并优先级
冲突裁决按以下优先级执行：
1. 正确性与安全性
2. 用户明确要求
3. 与现有模式一致性
4. 风格偏好

## 3) 状态归并
- 任一关键子任务 `FAILED`：总体为 `FAILED`。
- 无 `FAILED` 但存在关键 `BLOCKED`：总体为 `BLOCKED`。
- 全部 `DONE` 且无冲突：总体为 `DONE`。
- 其余情况：总体为 `PARTIAL`。

## 4) 证据门槛
- 子任务 `status=DONE` 但证据缺失：降级为 `PARTIAL`。
- 汇总结论必须引用对应 `evidence`，不得仅凭口头描述。

## 5) 失败归并输出
当总体非 `DONE` 时，主代理必须输出：
- `blocking_issues`（按影响范围排序）
- `next_action`（明确 owner 与动作）
- 是否需要新一轮分发（是/否 + 理由）
