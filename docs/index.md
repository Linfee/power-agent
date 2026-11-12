---
okf_version: "0.1"
title: Power-Agent Knowledge Bundle
description: Power-Agent 当前版本的架构、开发与决定入口。
freshness:
  rules:
    - type: Decision
      strategy: historical
timestamp: 2026-11-12
---

# Power-Agent Knowledge Bundle

以当前 Skill、代码和调用元数据为准，按任务选择下列材料。当前产品基线为 0.2.0；安装到某个宿主的副本和版本须另行确认。本仓库采用 Bundle，普通业务项目不因此必须迁移成 Bundle。

## 当前架构与开发

- [系统架构](architecture.md)：Matt 主干的 24 项能力、整包具名组合与状态边界。
- [工作方式](workflow.md)：授权内连续推进、任务图、真实证据与必要人工决定。
- [开发指南](development.md)：安装路径、元数据、脚本与验证入口。
- [宿主兼容性](agent-compatibility.md)：六种宿主的整包安装、常驻规则加载条件和验证边界。
- [Skill 设计](skill-and-harness-design.md)：行为缺口、渐进披露和有效对照。
- [Harness Engineering](harness-engineering.md)：环境、知识与机械化。
- [ADR-0014](adr/0014-current-baseline.md)：唯一现行决定基线，集中说明能力、自动与手动调用、授权、知识和 hook 的取舍；不需要叠加旧 ADR 才能恢复当前规则。

## 历史记录

- [ADR 导航](adr/index.md)：当前仅维护 ADR-0014；ADR-0001 至 0013 已归并取代，归档正文已移除。
- 旧融合设计、评估和执行计划不再保存在仓库；需要追溯时检索 Git 历史。

## 知识维护入口

- 最小 Agent 入口、选定 tracker 和领域指针：[`setup-power-agent`](../skills/setup-power-agent/SKILL.md)。
- 体系初始化或真实检索路径优化（手动调用）：[`knowledge-navigation`](../skills/knowledge-navigation/SKILL.md)。
- 稳定事实、术语、决定的语义写入与核验：[`dev-docs`](../skills/dev-docs/SKILL.md)，领域意义按需消费 `domain-modeling`。
- 能力按需组合，不是固定全跑。仓库保存知识，计划和 handoff 引用任务的权威状态；历史 `.scratch/` 路径不保证可恢复。文档年龄、Git diff、结构通过和模型复述不能证明内容正确或行为收益；关键声明须对照权威来源。
