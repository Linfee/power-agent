---
name: dev-docs
description: "创建或更新 docs/ 下的开发文档，支持六种类型：architecture、arch-decision、exec-plan、domain、development、reference。收到 exec-plan 任务时委派给 writing-plans skill。Use when: 需要记录架构/决策/领域知识/开发指南，或创建实现计划。Triggers: 写文档, dev-docs, architecture, arch-decision, exec-plan, 架构文档, 决策记录, 领域文档."
disable-model-invocation: true
version: 1.0.0
---

# 创建开发文档

在项目的 `docs/` 知识库中创建结构化文档。所有文档服务于一个目标：让 Agent（和工程师）仅凭仓库内容就能理解全局。

---

## 文档类型识别

根据用户输入判断类型，类型不明确时询问：

| 类型            | 关键词                    | 输出位置                                 |
| --------------- | ------------------------- | ---------------------------------------- |
| exec-plan       | 计划/重构/迁移/实现/spec  | → **委派给 `writing-plans` skill**       |
| architecture    | 架构/模块/系统/组件       | `docs/architecture.md` 或 `docs/domain/` |
| arch-decision | 决策/选型/方案/权衡/DD    | `docs/arch-decisions/DD-NNN-title.md`  |
| domain          | 前端/安全/API/数据库/部署 | `docs/domain/[name].md`                  |
| development     | 开发/搭建/环境/命令       | `docs/development.md`                    |
| reference       | 参考/外部/集成/第三方     | `docs/references/[name].md`              |

---

## exec-plan 路径

**识别到 exec-plan 类型时，立即委派给 `writing-plans` skill，不在本 skill 内处理。**

将用户的原始需求和上下文完整传递给 writing-plans。

---

## 其他文档路径

### Step 1: 预检

1. 确认 `docs/` 目录存在，`AGENTS.md` 已加载
2. 按需加载相关文档（`docs/architecture.md`、`docs/arch-decisions/index.md` 等）

### Step 2: 代码分析

根据文档主题，启动 `explore` 子代理分析相关代码：
- 追踪与主题相关的代码路径、模块边界、依赖关系
- 收集关键文件列表、函数签名、数据流
- 识别现有约定和模式

### Step 3: 撰写文档

所有文档必须包含顶部元信息：

```markdown
<!-- verified: YYYY-MM-DD -->
<!-- scope: [对应范围] -->
<!-- author: agent -->
```

#### 模板：设计决策（arch-decision）

```markdown
<!-- verified: YYYY-MM-DD -->
<!-- scope: [涉及范围] -->
<!-- status: proposed -->

# DD-NNN: [决策标题]

## 背景
[为什么需要这个决策？当前痛点？]

## 约束
[必须满足的硬性条件]

## 方案对比
| 方案 | 优势 | 劣势 | 复杂度 |
|------|------|------|--------|
| A: ... | ... | ... | S/M/L |
| B: ... | ... | ... | S/M/L |

## 决定
[选择哪个方案，为什么]

## 后果
[影响和注意事项]
```

完成后更新 `docs/arch-decisions/index.md`。

#### 模板：领域文档（domain）

```markdown
<!-- verified: YYYY-MM-DD -->
<!-- scope: [领域名称] -->

# [领域名称]

## 概述
[这个领域负责什么]

## 架构
[模块组成、依赖关系，用 Mermaid 图表达]

## 关键约定
[本领域特有的规范和模式]

## 常见操作
[开发者日常需要做的事情]
```

#### 架构/开发/参考文档

按项目现有格式创建，包含 `<!-- verified: YYYY-MM-DD -->` 元信息。

### Step 4: 更新索引

1. arch-decision → 更新 `docs/arch-decisions/index.md`
2. 新增文档类型或路径 → 更新 `AGENTS.md` 的知识库导航

### Step 5: 输出

向用户报告：创建了什么、在哪个位置、是否需要更新 AGENTS.md 导航指针。
