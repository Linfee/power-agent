

<!-- verified: 2026-03-25 -->
<!-- scope: harness-engineering -->

# Harness Engineering 体系设计

基于 OpenAI Harness Engineering 实践构建的 Agent 驱动开发体系。核心理念：**人类掌舵，Agent 执行**——人类的职责是设计意图、构建反馈循环，Agent 负责执行闭环。

**原始参考：** [Harness engineering: leveraging Codex in an agent-first world](https://openai.com/index/harness-engineering/) — Ryan Lopopolo, OpenAI, Feb 11, 2026

---

## 设计哲学

### 三个核心原则

**1. 仓库即唯一真相来源（Repo as SSOT）**
所有知识必须版本化、存储在仓库中。Agent 看不到的东西等同于不存在。架构决策写在 Slack 里、口头约定的规范、只存在聊天记录中的"为什么这样设计"——这些信息对 Agent 而言完全不可见。

**2. 目录式上下文（Context as Map, Not Encyclopedia）**
`AGENTS.md` 控制在 ~200 行，是一张**地图**而非百科全书。具体知识下沉到 `docs/` 的结构化文件中。当所有事情都标为重要，就没有什么重要。

**3. 机械化约束优于 Prompt 啰嗦**
核心规范靠 Linter/Test 强制执行，而非在 Prompt 中写 50 条"你应该如何写代码"。Linter 错误信息对 Agent 友好，含直接可执行的修复建议。

---

## 知识库结构

```
docs/
├── architecture.md          # 系统架构：模块划分、层级依赖、数据流
├── development.md           # 开发指南：环境搭建、构建命令、调试
├── workflow.md              # Skill 协调机制详解
├── harness-engineering.md   # 本文档：体系设计与参考
├── arch-decisions/        # 设计决策记录
│   └── index.md             # 决策索引（带验证状态）
├── exec-plans/              # 执行计划
│   ├── active/              # 进行中
│   └── completed/           # 已归档
└── specs/                   # 需求规格文档
```

**文档元信息（所有文档必须包含）：**

```markdown
<!-- verified: YYYY-MM-DD -->
<!-- scope: [architecture|frontend|backend|security|...] -->
<!-- status: accepted | proposed | superseded -->  <!-- 仅设计决策 -->
```

---

## 体系组件

架构分层、Skill 清单和协调机制见：
- [系统架构](architecture.md) — 模块划分、依赖方向、Gate 机制
- [工作机制与 Skill 协调](workflow.md) — 各 Skill 职责、产出物流转、反模式

## 关键设计决策

所有设计决策已独立建档，见 [设计决策索引](arch-decisions/index.md)。

核心决策概要：

| 决策 | DD 编号 |
| --- | --- |
| Skill 作为执行单元，人类是决策者 | [DD-001](arch-decisions/DD-001-skill-as-execution-unit.md) |
| 子代理一次性，避免上下文污染 | [DD-002](arch-decisions/DD-002-disposable-subagents.md) |
| 产出物作为协调介质 | [DD-003](arch-decisions/DD-003-artifacts-as-coordination.md) |
| AGENTS.md 精简（≤200 行） | [DD-004](arch-decisions/DD-004-lean-agents-md.md) |
| Gate 机制强制人工确认 | [DD-005](arch-decisions/DD-005-gate-mechanism.md) |