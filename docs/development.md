<!-- verified: 2026-03-25 -->
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
├── .claude-plugin/           # Claude Code 插件配置
│   └── plugin.json
├── .cursor-plugin/           # Cursor 插件配置
│   └── plugin.json
├── .factory-plugin/          # Factory 插件配置
│   └── plugin.json
├── docs/                     # 项目文档
│   ├── architecture.md       # 系统架构
│   ├── development.md        # 本文档
│   ├── harness-engineering.md
│   ├── workflow.md
│   ├── arch-decisions/     # 设计决策
│   ├── exec-plans/           # 执行计划
│   └── specs/                # Spec 文档
├── skills/                   # Skill 定义（14个）
│   ├── feature-dev/
│   ├── discuss/
│   ├── writing-plans/
│   ├── exec-plan-runner/
│   └── ...
├── README.md                 # 中文主文档
└── README-en.md              # 英文文档
```

## Skill 开发

### Skill 结构

每个 Skill 遵循统一结构：

```
skills/
└── <skill-name>/
    ├── SKILL.md              # 核心 skill 定义（必须）
    ├── <辅助文档>.md         # 按需的支撑文档
    ├── scripts/              # 按需的脚本工具
    └── templates/            # 按需的模板文件
```

### SKILL.md 格式

```markdown
---
name: [skill-name]
description: [用途描述，中文]
triggers: [触发关键词，逗号分隔]
disable-model-invocation: [true|false]  # 可选
---

# [Skill 标题]

[核心理念/铁律]

---

## Step 1: [步骤名]
...

## 产出
## 交棒给
## 禁止事项
## 依赖 Skills
```

### 文件命名约定

| 类型 | 约定 | 示例 |
|------|------|------|
| Skill 主文件 | `SKILL.md` (大写) | `/skills/feature-dev/SKILL.md` |
| 辅助文档 | 小写 + 连字符 | `spec-reviewer-prompt.md` |
| 设计决策 | `DD-NNN-title.md` | `DD-001-use-postgres.md` |
| Spec 文档 | `YYYY-MM-DD-topic.md` | `2026-03-25-auth-system.md` |
| Exec-plan | `YYYY-MM-DD-title.md` | `2026-03-25-add-user-api.md` |

### 文档元信息

所有文档必须包含顶部元信息：

```markdown
<!-- verified: YYYY-MM-DD -->
<!-- scope: [architecture|frontend|backend|security|...] -->
<!-- status: [proposed|accepted|superseded] -->  <!-- 仅设计决策 -->
```

## 常用 Skill 入口

| 场景 | 命令 |
|------|------|
| 功能开发 | `/feature-dev [功能描述]` |
| 需求讨论 | `discuss` skill |
| 创建 exec-plan | `writing-plans` skill |
| 执行 exec-plan | `exec-plan-runner` skill |
| 调试 | `systematic-debugging` skill |
| 文档维护 | `dev-docs-maintain` skill |

## 版本控制

- 使用 Git
- 主分支：`main`
- 提交前确保文档 verified 时间戳更新

## 贡献流程

1. 创建功能分支
2. 开发 Skill 或修改文档
3. 更新相关 docs/ 文档
4. 提交变更
5. 合并到 main

## 上游追踪

| 上游项目 | 版本 | 来源 |
|----------|------|------|
| superpowers | v5.0.5 | https://github.com/obra/superpowers |
| Harness Engineering | 2026年2月 | https://openai.com/index/harness-engineering/ |
