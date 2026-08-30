---
name: harness-engineering-review
description: Harness Engineering 审查。审视 Agent 工作流、AGENTS.md、知识库与开发实践的约束、证据与可删机制，给出调整方案。
disable-model-invocation: true
---

# Harness Engineering Review

基于 OpenAI 团队的 Harness Engineering 实践经验，审视一个项目或工作流的真实环境、约束与证据，判断哪些机制值得保留、哪些可以删除。不套固定评分模板，不强制七个维度或任何输出格式——审查的价值在识别值得改变的事实，不在报告长得完整。

**原文参考：** [Harness engineering: leveraging Codex in an agent-first world](https://openai.com/index/harness-engineering/) — Ryan Lopopolo, OpenAI, Feb 11, 2026

## 核心判断

**人类掌舵，Agent 执行。** 人类的角色是设计环境、明确意图、构建反馈循环，而非直接写代码。审查围绕四类问题展开，顺序与深度随现场而定：

- **真实环境**：Agent 实际看到什么——`AGENTS.md` 是否可导航、关键指针是否有效、命令是否可直接执行、约束是否对 Agent 可见。
- **约束**：哪些规则靠 prompt 文字、哪些已由 lint/CI/hook 机械执行；只有 prompt 文本约束的高风险规则在哪里；破坏性操作有无确认。
- **证据**：反馈循环是否真实可运行（测试、CI、失败信息能否定位根因）；完成声明有无新鲜系统外证据；文档与代码现状是否一致。
- **可删机制**：哪些文档、追踪项、步骤或报告不再被消费——没有 consumer 的机制是负担不是资产。

## 审视方法

先读现场材料：`AGENTS.md`、`docs/` 结构、CI/lint 配置、测试与验证流程。用户提供了哪些就用哪些，缺材料时先指明缺口而不是硬凑判断。

每条发现都要落到可观察证据：文件路径、命令输出、diff、运行结果。没有证据的主张不算发现。

- **发现**按影响排序：哪些阻碍 Agent 正确工作，哪些只是低效，哪些可以安全删除。
- **下一步动作**按依赖排序，只写当前证据支持的；无法确定的保持开放。
- **不做的事**：不输出固定评分表、不设固定维度、不要求用户提供全套材料后才开始、不生成无人消费的长报告。判断收敛后直接给结论与理由，表达形式随读者需要。

## 使用方式

用户提供以下任意内容，即可开始审查：

- `AGENTS.md` 文件路径或内容
- 项目目录结构
- CI / lint / 测试配置
- 描述当前工作流

材料不足时，向用户要最影响判断的那一条，而不是清单式收集。
