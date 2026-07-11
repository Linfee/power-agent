---
okf_version: "0.1"
title: Power-Agent Knowledge Bundle
description: Power-Agent 的长期工程知识入口与任务路由。
freshness:
  rules:
    - type: Decision
      strategy: historical
timestamp: 2026-07-10T00:00:00Z
---

# Power-Agent Knowledge Bundle

按任务读取最小必要文档；`docs/` 中除 `index.md` 与 `log.md` 外的 Markdown 均为带 YAML frontmatter 的 Concept Document。

## 系统与工作流

- [系统架构](architecture.md)：模块、依赖方向与工作流边界。
- [开发指南](development.md)：Skill 结构、文档元数据和开发约定。
- [工作机制](workflow.md)：Skill 协调、交接契约与 Gate。
- [Harness Engineering](harness-engineering.md)：Harness 设计原则与知识体系。
- [Skill 与 Harness 设计](skill-and-harness-design.md)：Skill、prompt 和 Harness 的设计规则。

## 决策与执行状态

- [架构决策记录](adr/)：耐久决策及其历史状态。
- [执行计划](exec-plans/README.md)：当前与归档 exec-plan 的入口。

## 文档维护入口

- 新建或修订稳定系统事实、领域边界、Playbook、Reference 或 ADR，使用 [`dev-docs`](../skills/dev-docs/SKILL.md)。
- 检查既有 Bundle 健康、验证 freshness、修复已发现漂移或登记验证，使用 [`dev-docs-maintain`](../skills/dev-docs-maintain/SKILL.md)；Concept 重组使用其 `full-maintain`。
- 实施计划和任务拆解交给 [`writing-plans`](../skills/writing-plans/SKILL.md)；普通 RFC、Proposal 和设计文档共创使用 `doc-coauthoring`。
- README、CHANGELOG、发布公告以及未改变稳定契约的私有实现调整不进入长期知识维护。裸“更新文档”且缺少变化事实、来源或消费场景时先补证据，不猜测写入。
- 验证运行状态由 `docs/.okf/verification.json` 维护；Git diff 或文档年龄不能单独证明 `fresh`，也不使用 HTML `verified` / `scope` 注释。