<!-- verified: 2026-06-05 -->
<!-- scope: development -->

# 开发指南

## 项目概述

Power-Agent 是一个 AI 编码 Agent 工作流插件系统，以 Markdown 文档和 Skill 定义为主，无传统编程语言依赖。

## 环境要求

- Git 版本控制
- 支持的 AI IDE：Claude Code、Cursor、Factory、Droid、Gemini

## 项目结构

```
power-agent/
├── docs/                     # 项目文档
│   ├── architecture.md       # 系统架构
│   ├── development.md        # 本文档
│   ├── workflow.md           # 工作机制与 Skill 协调
│   ├── harness-engineering.md # Harness Engineering 体系
│   ├── skill-and-harness-design.md # Skill 与 Harness 设计原则
│   ├── adr/                  # ADR 历史架构决策（0001-slug.md）
│   ├── domain/               # 领域/模块专题文档
│   ├── references/           # 外部依赖、集成、第三方参考
│   ├── exec-plans/           # 执行计划
│   │   ├── active/           # 进行中
│   │   └── completed/        # 已归档
│   └── specs/                # Spec 文档（YYYY-MM-DD-topic.md）
├── skills/                   # Skill 定义（16 个）
│   └── <skill-name>/
│       ├── SKILL.md          # 核心 skill 定义（必须）
│       └── references/       # 支撑文档、模板、prompt
├── AGENTS.md                 # Agent 快速参考（≤200 行）
├── CLAUDE.md                 # Claude Code 入口
├── GEMINI.md                 # Gemini 入口
├── .claude-plugin/           # Claude Code / Droid 插件清单
├── .cursor-plugin/           # Cursor 插件清单
├── .factory-plugin/          # Factory 插件清单
├── gemini-extension.json     # Gemini extension 清单
```

## Skill 开发

### Skill 结构

```
skills/
└── <skill-name>/
    ├── SKILL.md              # 核心 skill 定义（必须）
    └── references/           # 按需的支撑文档、模板、子代理 prompt
```

### SKILL.md 格式

```markdown
---
name: [skill-name]
description: |-
  [用途描述，中文]
  Triggers: [触发关键词，逗号分隔]
disable-model-invocation: [true|false]  # 可选，默认 false
---

# [Skill 标题]

[核心理念/铁律]

---

## Step N: [步骤名]
...

## 产出
## 交棒给
## 禁止事项
```

### Skill 行为验证


新增或重写核心 Skill 时，使用 `writing-skills`：

- 先写清楚触发场景、目标行为和无 Skill 时的失败模式。
- 为关键路径准备 2-3 个压力场景。
- 检查上游产物是否满足下游输入契约。
- 对规划类 Skill，区分人类审阅入口与 Agent 执行材料；例如 `writing-plans` 默认使用 `review-contract.md` 承载人类批准口径。
- 至少运行路径和引用检查；有条件时运行子代理 eval。

## 文档规范

### 元信息（ADR 除外，普通 docs 文档必须包含）

```markdown
<!-- verified: YYYY-MM-DD -->
<!-- scope: [范围] -->
```

ADR 是历史架构决策记录，不要求 `verified` / `scope` 元信息；需要表达状态时使用 `<!-- status: accepted | proposed | superseded -->`。

### 命名约定

| 类型 | 格式 |
|------|------|
| Skill 主文件 | `SKILL.md`（大写） |
| ADR | `0001-slug.md` |
| Spec | `YYYY-MM-DD-topic.md` |
| Exec-plan 目录 | `YYYY-MM-DD-title/` |

### 时间戳维护

- verified 超过 30 天：需验证内容是否仍准确
- verified 超过 90 天：必须修复或更新
- ADR 不刷新 verified；决策变化时新增 ADR 或标记 superseded

## 约束（硬规则）

| 规则 | 说明 |
|------|------|
| 依赖方向 | 只能从上层指向下层，禁止反向 |
| 子代理一次性 | 不重用子代理，每次启动新代理 |
| 并发限制 | 最大并行度 3 |
| 证据优先 | 没有运行验证不得声称完成 |
| 根因优先 | 没有根本原因分析没有修复 |
