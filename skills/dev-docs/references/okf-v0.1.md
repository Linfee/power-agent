# OKF 规范概述

版本：OKF v0.1-compatible
目标：定义一套符合 Open Knowledge Format（OKF）思想的知识库组织规范，使任意文档集合可以被整理为结构清晰、可迁移、可检索、可交叉引用的 Markdown 知识库。

## 目录

- [1. 核心模型](#1-核心模型)
- [2. Bundle 结构](#2-bundle-结构)
- [3. Concept Document 格式](#3-concept-document-格式)
- [4. Frontmatter 字段](#4-frontmatter-字段)
- [5. Body 规范](#5-body-规范)
- [6. 链接规范](#6-链接规范)
- [7. index.md](#7-indexmd)
- [8. log.md](#8-logmd)
- [9. Citations](#9-citations)
- [10. 合规标准](#10-合规标准)
- [11. 普通文档转 OKF 的整理规则](#11-普通文档转-okf-的整理规则)
- [12. 最小模板](#12-最小模板)
- [13. 一句话原则](#13-一句话原则)

---

## 1. 核心模型

```text
Bundle = 一个目录树
Concept = 一个知识单元
Concept Document = 一个描述 Concept 的 Markdown 文件
Concept ID = 文档相对路径去掉 .md
Relation = Markdown 内部链接
Evidence = Citations 引用
```

除 `index.md`、`log.md` 外，所有 `.md` 文件都是 Concept Document。

---

## 2. Bundle 结构

推荐结构：

```text
bundle/
├── index.md
├── log.md
├── <concept>.md
├── <domain>/
│   ├── index.md
│   ├── log.md
│   └── <concept>.md
└── references/
    └── <source>.md
```

约束：

- `index.md`：目录索引。
- `log.md`：目录变更日志。
- 其他 `.md`：知识概念文档。
- 目录只表示组织方式，不承担严格语义。
- 跨目录分类用 `tags` 和 Markdown 链接表达。

---



## 3. Concept Document 格式

每个普通 `.md` 文件必须符合：

```markdown
---
type: <Type>
title: <Title>
description: <One-line summary>
resource: <Canonical URI>
tags: [tag1, tag2]
timestamp: <ISO 8601 datetime>
---

# Overview

正文。
```

硬约束：

- 必须有 YAML frontmatter。
- frontmatter 必须位于文件顶部。
- 必须有非空 `type`。
- body 使用标准 Markdown。
- 文件路径即 Concept ID，应保持稳定。

---



## 4. Frontmatter 字段


| 字段            | 要求     | 说明                   |
| ------------- | ------ | -------------------- |
| `type`        | MUST   | 概念类型，唯一必填字段          |
| `title`       | SHOULD | 人类可读标题               |
| `description` | SHOULD | 一句话摘要                |
| `resource`    | MAY    | 被描述资源的 canonical URI |
| `tags`        | SHOULD | 横向分类标签，YAML list     |
| `timestamp`   | MAY    | 内容语义更新时间，ISO 8601    |
| custom fields | MAY    | 扩展字段，消费者应保留          |


`type` 无全局枚举，允许自定义。推荐值：

```text
Concept
Term
Metric
Rule
Process
Playbook
Decision
Reference
Data Table
Dataset
API Endpoint
System
Service
Domain
```

消费者必须容忍未知 `type` 和未知字段。

---



## 5. Body 规范

body 不强制 schema，但应结构化。常用章节：

```markdown
# Overview
# Definition
# Schema
# Examples
# Relationships
# Notes
# Citations
```

约定：

- `# Schema`：字段、列、参数、结构。
- `# Examples`：SQL、API、配置、用例。
- `# Relationships`：与其他 Concept 的关系。
- `# Citations`：来源证据。

---



## 6. 链接规范

内部链接使用标准 Markdown。

推荐使用 bundle-root absolute path：

```markdown
[Orders Table](/tables/orders.md)
```

允许相对路径：

```markdown
[Orders Table](../tables/orders.md)
```

链接语义由上下文文字表达，不定义 typed edge。

```markdown
This metric is calculated from [Orders Table](/tables/orders.md).
This API is governed by [Auth Rule](/rules/auth.md).
```

消费者可将内部链接解析为 directed untyped graph。

Broken link 不应导致整个 Bundle 失效，但应被记录为待修复问题。

---



## 7. [index.md](http://index.md)

`index.md` 用于目录导航。

格式：

```markdown
# <Directory Title>

* [Concept A](concept_a.md) - one-line description.
* [Subdirectory](subdirectory/) - one-line description.
```

规则：

- 可出现在任意目录。
- 普通目录 `index.md` 不需要 frontmatter。
- 根目录 `index.md` 可声明版本：

```markdown
---
okf_version: "0.1"
---

# Knowledge Bundle
```

---



## 8. [log.md](http://log.md)

`log.md` 记录当前目录作用域内的变更。

格式：

```markdown
# Directory Update Log

## 2026-06-25

* **Creation**: Added [Orders Table](/tables/orders.md).
* **Update**: Refined [Weekly Active Users](/metrics/wau.md).
* **Deprecation**: Deprecated [Old Revenue Metric](/metrics/old_revenue.md).
```

规则：

- 日期倒序。
- 日期格式：`YYYY-MM-DD`。
- 条目前缀为约定，可自定义。
- 常用前缀：`Creation`、`Update`、`Correction`、`Move`、`Rename`、`Deprecation`、`Removal`。

---



## 9. Citations

凡是从外部资料、原始文档、系统定义、业务规则、数据口径、API 文档中整理出的声明，都应在 `# Citations` 中保留来源。

格式：

```markdown
# Citations

[1] [Source Document](/references/source.md)
[2] [External Docs](https://example.com/docs)
```

`references/` 下的来源文件如果是 `.md`，也应是普通 Concept Document：

```markdown
---
type: Reference
title: CRM API Documentation
description: Source material for CRM API behavior.
resource: https://example.com/crm/api/docs
tags: [reference, crm, api]
---

# Summary

来源摘要。

# Citations

[1] [Original](https://example.com/crm/api/docs)
```

---



## 10. 合规标准

最小合规：

```text
1. Bundle 是目录树。
2. 普通知识文件是 .md。
3. 除 index.md / log.md 外，每个 .md 都有 YAML frontmatter。
4. 每个 Concept Document 都有非空 type。
5. index.md / log.md 如存在，遵守其约定格式。
```

推荐合规：

```text
1. 每个 Concept 有 title / description / tags。
2. 有底层资源的 Concept 有 resource。
3. 外部来源进入 Citations。
4. 重要目录有 index.md。
5. 重要变更进入 log.md。
6. 内部链接优先使用 /path/to/file.md。
7. 文件路径稳定、可读、无临时命名。
```

消费者容错：

```text
不得因缺少可选字段、未知 type、未知字段、broken link、缺少 index.md、缺少 log.md、缺少 Citations 而拒绝整个 Bundle。
```

---



## 11. 普通文档转 OKF 的整理规则



### 11.1 切分

```text
一个稳定知识概念 = 一个 Concept Document
多个主题混在一个文档中 → 拆分
多个文档重复描述同一概念 → 合并
合并后保留来源 → Citations
```



### 11.2 映射

原始标题 → title
核心摘要 → description
内容类型 → type
主题/领域/系统 → tags
稳定覆盖范围 → YAML `scope`
概念生命周期 → YAML `status`
freshness 策略 → YAML `verification`
原始来源 → Citations / references
文档间依赖 → Markdown links



### 11.3 类型选择


| 内容   | type           |
| ---- | -------------- |
| 术语   | `Term`         |
| 概念   | `Concept`      |
| 指标   | `Metric`       |
| 规则   | `Rule`         |
| 流程   | `Process`      |
| 操作手册 | `Playbook`     |
| 决策记录 | `Decision`     |
| 数据表  | `Data Table`   |
| 数据集  | `Dataset`      |
| API  | `API Endpoint` |
| 系统   | `System`       |
| 服务   | `Service`      |
| 外部资料 | `Reference`    |




### 11.4 关系表达

关系不写成 schema 字段，写进正文链接语境：

```markdown
- Calculated from [Events Table](/tables/events.md).
- Governed by [Refund Rule](/rules/refund.md).
- Used by [Revenue Dashboard](/dashboards/revenue.md).
- Implements [Payment Process](/processes/payment.md).
```

### 11.5 元数据弃用边界

YAML frontmatter 是 Concept Document 元数据的唯一权威。旧 HTML header metadata（包括 `verified`、`scope` 与 `status`）已经弃用：生产者和消费者都不得创建、解析、复制或将其用作 YAML 的迁移输入。移除旧标记时，必须从当前正文和权威来源建立所需 YAML 字段；旧 `verified` 日期不得写入验证登记。

---



## 12. 最小模板

```markdown
---
type: <Type>
title: <Title>
description: <One-line summary>
resource: <Optional URI>
tags: [tag1, tag2]
timestamp: <ISO 8601 datetime>
---

# Overview

<What this concept is.>

# Details

<Important structured content.>

# Relationships

- Related to [Another Concept](/path/to/concept.md).

# Citations

[1] [Source](/references/source.md)
```

---



## 13. 一句话原则

```text
Every concept is a Markdown file.
Every concept has frontmatter.
Every concept has a type.
Links form the graph.
Citations preserve provenance.
Index enables navigation.
Log preserves change history.
```
