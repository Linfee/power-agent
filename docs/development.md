---
type: Playbook
scope:
  - development
---

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
├── skills/                   # Skill 定义（13 个）
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

### Skill 设计与维护

新增或重写核心 Skill 时，使用 `writing-skills`：

- 先写清楚触发场景、目标行为和无 Skill 时的行为缺口。
- 维护上游产物与下游输入契约的一致性。
- 对规划类 Skill，区分人类按需阅读入口与 Agent 执行材料；例如 `writing-plans` 默认使用 `review-contract.md` 提供压缩审阅面，但它不构成执行 Gate。
- 计划审查按风险分层：低风险只做 self-review，中/高风险增加独立 reviewer。
- 高体积、可重建的 task brief、实现报告和 review diff 使用 `.power-agent/review-runs/` scratch artifacts 交接；截图、日志、trace、benchmark 等 reviewer 资产按 run 放入 `assets/`，只通过 `review-assets.md` 显式命名，并由当前 review session 的权威 run root 约束，同时绑定 target+paths/finding scope、freshness、source 与 sensitivity。它们不进入 commit，也不替代 exec-plan Session Log；无 manifest 时不得扫描目录。
- 运行与当前改动直接相关的路径和引用检查；调用方式改动额外运行 `scripts/check-invocation-consistency.sh`，description 改动运行 `scripts/check-description-length.py`（硬上限约 110 token，目标 ~100）。

### 共享 reference 文件

同一 reference 被多个 skill 使用时（当前：`okf-v0.1.md` 同时存在于 `dev-docs` 与 `dev-docs-maintain`），每个 skill 各存一份以保持独立可安装，不做跨 skill 相对引用。修改任一副本后必须同步其余副本；`scripts/check-shared-references.sh` 校验一致性，漂移时非零退出。

## 文档规范

### YAML frontmatter（ADR 除外，普通 docs Concept 必须包含）

```yaml
---
type: Concept # 替换为能表达文档用途的非空类型
scope:
  - src/area/**
status: active # 仅在生命周期有实际语义时添加
---
```

验证运行状态不写入 Concept；由 `docs/.okf/verification.json` ledger 维护。ADR 是历史架构决策记录，使用 `type: Decision` 和 YAML `status`（如 `accepted`、`proposed`、`superseded`）。

### 命名约定

| 类型 | 格式 |
|------|------|
| Skill 主文件 | `SKILL.md`（大写） |
| ADR | `0001-slug.md` |
| Spec | `YYYY-MM-DD-topic.md` |
| Exec-plan 目录 | `YYYY-MM-DD-title/` |

### 验证维护

- 来源变化或 freshness 策略到期时，运行文档验证并更新 `docs/.okf/verification.json`。
- 不将历史验证日期迁入 Concept frontmatter 或 ledger。
- ADR 使用历史策略；决策变化时新增 ADR 或以 YAML status 标记 superseded。

## 约束（硬规则）

| 规则 | 说明 |
|------|------|
| 依赖方向 | 只能从上层指向下层，禁止反向 |
| 子代理生命周期 | 实现/修复子代理与跨目标调用保持一次性；同一 review session 内优先由原 reviewer 验证其 findings，不能继续时使用携带完整修复上下文的新 reviewer |
| 证据优先 | 没有运行验证不得声称完成 |
| 根因优先 | 没有根本原因分析没有修复 |
