---
name: dispatching-parallel-agents
description: |-
  当任务可独立并行时，分发子代理并按统一协议汇总结果。
  Triggers: 并行执行, 独立任务, parallel agents, 并行子代理, 多任务编排.
version: 1.2.0
---

# dispatching-parallel-agents

作为并行任务编排器。识别可并行任务、定义子任务协议、分发执行、汇总并处理冲突。

## Objective

### 做什么
- 仅在任务彼此独立时进行并行分发。
- 为每个子代理提供结构化任务卡。
- 要求子代理按统一输出协议返回结果。
- 对冲突与失败进行显式归并，给出下一步动作。

### 不做什么
- 不要求子代理返回冗长推理过程。
- 不在同一批次并行处理存在共享改动面或顺序依赖的任务。

## Context & Tools

### 适用条件
- 存在 2+ 个可以独立理解与执行的任务。
- 任务之间无共享改动面、无顺序依赖。

### 不适用条件
- 任务本质上是同一根因链路。
- 汇总前必须先完成统一前置步骤。
- 需要强一致的全局状态才能正确决策。

### 上下文策略
- 给子代理必要的上下文，避免子代理自行摸索和返工
- 任务卡与输出协议使用 references 文档，避免在本文件重复展开。

## Constraints & Format

### 输入协议（子任务卡）
每个子任务必须包含以下字段：
- `goal`
- `scope`
- `blocked_by`
- `expected_output`
- `constraints`
- `verification`

任务卡模板：`references/task-card-template.md`

### 输出协议（子代理返回）
每个子代理必须返回以下字段：
- `status`: `DONE | PARTIAL | BLOCKED | FAILED`
- `evidence`
- `blocking_issues`
- `advisories`
- `next_action`

输出模板：`references/result-contract.md`

### 汇总与归并规则
- 使用 `references/conflict-resolution-rubric.md` 检查冲突与归并。
- 任一关键子任务 `FAILED` 或 `BLOCKED` 时，总状态不得为 `DONE`。
- 子代理返回缺少必填字段时，按 `PARTIAL` 处理并补发。

### 并发限制
- 单批次最大并行度为 3。
- 超过 3 个任务时分批执行，不得合并原子任务规避限制。
