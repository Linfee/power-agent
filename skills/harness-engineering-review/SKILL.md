---
name: harness-engineering-review
description: Harness Engineering 审查。审查 Agent 工作流、AGENTS.md、知识库和开发实践，给出调整方案。
disable-model-invocation: true
---

# Harness Engineering Review

基于 OpenAI 团队的 Harness Engineering 实践经验，审查项目和工作流中不符合最佳实践的部分，并给出调整方案。

**原文参考：** [Harness engineering: leveraging Codex in an agent-first world](https://openai.com/index/harness-engineering/) — Ryan Lopopolo, OpenAI, Feb 11, 2026

## 核心原则

**人类掌舵，Agent 执行。** 人类的角色是设计环境、明确意图、构建反馈循环，而非直接写代码。

## 审查维度

执行审查时，覆盖以下七个维度并给出证据：
1. AGENTS.md 结构（Context Management）
2. Agent 可见性（Agent Legibility）
3. 约束机制化（Enforced Architecture & Taste）
4. 反馈循环质量（Feedback Loop）
5. 知识维护（Documentation Gardening）
6. 技术债管理（Garbage Collection）
7. 代码模式一致性（Code Pattern Consistency）

详细检查项、反模式与示例统一下沉到 `references/`。审查开始前先读取 `references/` 中对应维度的检查项文档，再逐维度执行。

---

## 审查报告格式

完成审查后，用便于阅读的 Markdown 小节输出结果，不使用 YAML：

```markdown
## 审查结果

状态：DONE / DONE_WITH_CONCERNS / BLOCKED

### 证据
- [file / diff / command / review] <path 或 command>

### 阻塞项
- HER-xxx：<阻塞原因>
  - 影响范围：<impact>

### 非阻塞建议
- <建议内容>

### 下一步
- 动作：proceed / split / rerun / escalate
- 负责人：user / orchestrator
```

并附结构化报告：

```
## Harness Engineering 审查报告

### 总体评分
| 维度 | 状态 | 优先级 |
|------|------|--------|
| AGENTS.md 结构 | ✅优 / ⚠️需改进 / ❌缺失 | P0/P1/P2 |
| Agent 可见性 | ... | ... |
| 约束机制化 | ... | ... |
| 反馈循环质量 | ... | ... |
| 知识维护 | ... | ... |
| 技术债管理 | ... | ... |
| 代码模式一致性 | ✅优 / ⚠️需改进 / ❌缺失 | P0/P1/P2 |

### blocking_issues
1. [问题描述]（含证据路径）

### advisories
- [非阻塞建议]

### next_action
- [按依赖顺序列出 P0 -> P1 -> P2]
```

说明：不使用“<1天/1-5天”时间分桶，统一使用 `P0/P1/P2 + 依赖关系`。

## 使用方式

用户提供以下任意内容，即可开始审查：
- AGENTS.md 文件路径或内容
- 项目目录结构（`ls` 或 `tree` 输出）
- 描述当前工作流

若用户未提供，主动询问以下信息：
1. AGENTS.md 当前内容
2. 项目是否有 `docs/` 或知识库目录
3. 当前代码审查和 lint 流程
