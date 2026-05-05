<!-- verified: 2026-05-05 -->
<!-- scope: development -->

# 开发指南

## 项目概述

Power-Agent 是一个 AI 编码 Agent 工作流插件系统，以 Markdown 文档和 Skill 定义为主，无传统编程语言依赖。

## 环境要求

- Git 版本控制
- 支持的 AI IDE：Claude Code、Cursor、Factory

## 项目结构

```
power-agent/
├── docs/                     # 项目文档
│   ├── architecture.md       # 系统架构
│   ├── development.md        # 本文档
│   ├── workflow.md           # 工作机制与 Skill 协调
│   ├── arch-decisions/       # 设计决策（DD-NNN-title.md）
│   ├── exec-plans/           # 执行计划
│   │   ├── active/           # 进行中
│   │   └── completed/        # 已归档
│   └── specs/                # Spec 文档（YYYY-MM-DD-topic.md）
├── skills/                   # Skill 定义（16 个）
│   └── <skill-name>/
│       ├── SKILL.md          # 核心 skill 定义（必须）
│       └── references/       # 支撑文档、模板、prompt
├── AGENTS.md                 # Agent 快速参考（≤200 行）
├── VERSION                   # Skill 版本号
└── scripts/
    └── sync-version.sh       # 版本同步脚本
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
description: [用途描述，中文]
triggers: [触发关键词，逗号分隔]
version: [x.y.z]
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

### 提交前版本同步

修改 Skill 内容后，提交前必须：

```bash
# 1. 更新 VERSION 文件
# 2. 运行同步脚本
bash scripts/sync-version.sh
# 3. 确认输出"版本同步完成"
```

### Skill 行为验证

新增或重写核心 Skill 时，使用 `writing-skills`：

- 先写清楚触发场景、目标行为和无 Skill 时的失败模式。
- 为关键路径准备 2-3 个压力场景。
- 检查上游产物是否满足下游输入契约。
- 至少运行路径、版本或引用检查；有条件时运行子代理 eval。

## 文档规范

### 元信息（所有文档必须包含）

```markdown
<!-- verified: YYYY-MM-DD -->
<!-- scope: [范围] -->
```

### 命名约定

| 类型 | 格式 |
|------|------|
| Skill 主文件 | `SKILL.md`（大写） |
| 设计决策 | `DD-NNN-title.md` |
| Spec | `YYYY-MM-DD-topic.md` |
| Exec-plan 目录 | `YYYY-MM-DD-title/` |

### 时间戳维护

- verified 超过 30 天：需验证内容是否仍准确
- verified 超过 90 天：必须修复或更新

## 约束（硬规则）

| 规则 | 说明 |
|------|------|
| 依赖方向 | 只能从上层指向下层，禁止反向 |
| 子代理一次性 | 不重用子代理，每次启动新代理 |
| 并发限制 | 最大并行度 3 |
| 证据优先 | 没有运行验证不得声称完成 |
| 根因优先 | 没有根本原因分析没有修复 |
