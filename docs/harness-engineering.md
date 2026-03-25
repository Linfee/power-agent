<!-- verified: 2026-03-25 -->
<!-- scope: system-design -->

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

## 体系组件概览

### 核心工作流

```
discuss skill [需求]      → docs/specs/*.md
    ↓
/feature-dev [功能]       → 架构设计 → exec-plan
    ↓
exec-plan-runner          → TDD 子代理并行实现
    ↓
requesting-code-review    → 代码审查
    ↓
dev-docs-maintain         → 文档同步
```

**调试路径**: `systematic-debugging` → `test-driven-development` → `verification-before-completion`

### Skills 分层

| 层级           | Skills                                                                                                       | 职责                                 |
| -------------- | ------------------------------------------------------------------------------------------------------------ | ------------------------------------ |
| **编排层**     | `feature-dev`                                                                                                | 引导式开发，串联所有其他 Skill |
| **规划层**     | `discuss`, `writing-plans`, `dev-docs`                                                                       | 设计探索、计划创建、文档路由         |
| **实现层**     | `exec-plan-runner`, `test-driven-development`, `systematic-debugging`, `verification-before-completion`      | 计划执行、TDD、调试、验证            |
| **审查层**     | `requesting-code-review`, `receiving-code-review`                                                            | 代码审查编排、反馈评估               |
| **基础设施层** | `dispatching-parallel-agents`, `init-harness-engineering`, `harness-engineering-review`, `dev-docs-maintain` | 并行调度、初始化、审查、维护         |

**详细 Skill 协调机制见** [docs/workflow.md](workflow.md)

---

## 关键设计决策

| 决策 | 原因 |
|------|------|
| AGENTS.md 精简 | 防止上下文臃肿，保持 ≤200 行 |
| 子代理一次性 | 避免上下文污染，每次完整传入问题 |
| 产出物作为协调介质 | Skill 通过文件传话，不直接调用 |
| Gate 强制等待 | 关键决策点必须有人类确认 |
| 证据优先 | 没有运行验证不得声称完成 |

**所有设计决策见** [docs/arch-decisions/index.md](arch-decisions/index.md)

---

## 标准工作流

### 新项目接入

```
/init-harness-engineering → 并行扫描 → 构建 docs/ → 生成 AGENTS.md → 验证
```

### 功能开发生命周期

```
discuss (可选) → feature-dev → exec-plan-runner → code-review → dev-docs-maintain
```

### 调试路径

```
systematic-debugging → test-driven-development → verification-before-completion
```

---

## 反模式

| 反模式             | 正确做法                         |
| ------------------ | -------------------------------- |
| 巨型 AGENTS.md     | 精简 AGENTS.md + docs/ 分层    |
| 口头架构决策       | 立即写入 docs/arch-decisions/  |
| Prompt 规范啰嗦    | 转化为 Linter 规则 + 测试        |
| 跳过文档同步       | Phase 8 强制文档同步             |
| 并行有依赖的任务   | exec-plan-runner 依赖分析        |
| 未验证就声称完成   | 验证原则：未运行命令不得声称通过 |
| 重用子代理修复问题 | 每次启动新子代理，完整传入问题   |

**详细反模式分析见** [docs/workflow.md](workflow.md)
