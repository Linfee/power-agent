---
type: Decision
status: superseded
verification:
  strategy: historical
superseded_by: ../0014-current-baseline.md
---

# ADR-0001: Skill 作为执行单元

> 历史记录：已由 [ADR-0014](../0014-current-baseline.md) 归并取代。下文的决定、状态说明与旧 Skill 名称保留当时含义，不作为当前指令。

## 背景

需要确定 Agent 工作流中的基本执行粒度。Agent 可以是单一整体、基于插件、或以 Skill 为单元。

## 约束

- 每个单元必须职责单一，可独立理解
- 单元之间通过明确的输入/输出协议协作
- 人类在关键决策点掌握控制权

## 方案对比

| 方案 | 优势 | 劣势 | 复杂度 |
|------|------|------|--------|
| A: 单体 Prompt | 简单 | 上下文膨胀、不可组合 | S |
| B: Skill 为执行单元 | 职责清晰、可组合、可独立演进 | 需要协调机制 | M |
| C: 微服务式独立进程 | 完全隔离 | 过度工程、通信开销大 | L |

## 决定

选择方案 B：Skill 为执行单元，人类为决策者。每个 Skill 只做一件事，通过产出物（文件）与其他 Skill 协作。规划阶段的人类决策与实现阶段自主闭环遵循 ADR-0006。

## 后果

- Skill 数量增长需要清晰的分层和导航
- 需要定义 Skill 间的产出物流转协议
- 编排层由 writing-plans + plan-impl 直接串联
