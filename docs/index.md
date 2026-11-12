---
okf_version: "0.1"
title: Power-Agent Knowledge Bundle
description: Power-Agent 的长期工程知识入口与任务路由。
freshness:
  rules:
    - type: Decision
      strategy: historical
timestamp: 2026-11-11T09:00:51Z
---

# Power-Agent Knowledge Bundle

按当前任务读取最少必要知识。本仓库采用 Bundle；除 `index.md` 与 `log.md` 外的 Concept 有非空 `type`，普通业务项目不因此必须迁移成 Bundle。

## 当前架构与开发

- [系统架构](architecture.md)：Matt 主干的 25 项能力、整包具名组合与状态边界。
- [工作方式](workflow.md)：授权内连续推进、任务图、真实证据与必要人工决定。
- [开发指南](development.md)：安装路径、元数据、脚本与验证入口。
- [宿主兼容性](../skills/setup-power-agent/references/agent-compatibility.md)：六种宿主的整包安装、常驻规则加载条件和验证边界。
- [Skill 设计](skill-and-harness-design.md)：行为缺口、渐进披露和有效对照。
- [Harness Engineering](harness-engineering.md)：环境、知识与机械化。
- [ADR-0013](adr/0013-skill-invocation-and-hook-boundaries.md)：当前模型可见入口、内部依赖与 hook 增强边界；其余融合原则沿用 [ADR-0012](adr/0012-matt-led-skill-fusion.md)。

## 融合契约与历史

- [融合设计](specs/2026-11-11-matt-power-agent-fusion.md)：每个 Skill 的来源、保留判断、融合、删除和验收。
- [迁移计划](exec-plans/active/2026-11-11-matt-power-agent-fusion/plan.md)：依赖、切换、授权与验收；本次实施状态只在计划指向的本地 tracker。
- [ADR 历史](adr/)与[执行计划导航](exec-plans/README.md)：保留历史决定、计划和证据，不反向改写旧名称。

## 知识维护入口

- 最小 Agent 入口、选定 tracker 和领域指针：[`setup-power-agent`](../skills/setup-power-agent/SKILL.md)。
- 体系初始化或真实检索路径优化：[`knowledge-navigation`](../skills/knowledge-navigation/SKILL.md)。
- 稳定事实、术语、决定的语义写入：[`dev-docs`](../skills/dev-docs/SKILL.md)，领域意义按需消费 `domain-modeling`。
- 扫描、漂移核对和安全验证登记：[`dev-docs-maintain`](../skills/dev-docs-maintain/SKILL.md)。

能力可按需具名组合，不是固定全跑。执行状态只在选定 tracker；仓库保存知识，handoff 引用权威指针。Bundle 的验证运行状态在 `docs/.okf/verification.json`，文档年龄、Git diff 或模型自报不能证明 fresh。
