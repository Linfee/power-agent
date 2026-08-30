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

- [系统架构](architecture.md)：Skill 边界、独立性与知识子系统。
- [开发指南](development.md)：Skill 结构、文档元数据和验证入口。
- [工作方式](workflow.md)：判断导向协作、证据与反模式。
- [Harness Engineering](harness-engineering.md)：环境、知识与验证设计。
- [Skill 与 Harness 设计](skill-and-harness-design.md)：如何维护可迁移判断。

## 决策与执行状态

- [架构决策记录](adr/)：耐久决策及其历史状态。
- [执行计划](exec-plans/README.md)：当前与归档 exec-plan 的入口。

## 文档维护入口

- 新建或修订稳定系统事实、领域边界、Playbook、Reference 或 ADR，使用 [`dev-docs`](../skills/dev-docs/SKILL.md)。
- 扫描 Bundle、验证 freshness、修复结构或漂移、登记验证，使用 [`dev-docs-maintain`](../skills/dev-docs-maintain/SKILL.md)。
- 初始化发现语义缺口、语义写入需要机械验证、或维护发现知识缺口时，这三个知识维护能力可按需协作；它们不形成固定链。
- 软件资产变更、研究、运营或普通清单各自从当前目标选择适当 Skill 或直接行动；没有固定的“必须交给”路由。
- 验证运行状态由 `docs/.okf/verification.json` 维护；Git diff 或文档年龄不能单独证明 `fresh`，也不使用 HTML `verified` / `scope` 注释。