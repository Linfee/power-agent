# Project Docs Profile

仅供明确采用 Power Bundle 的项目使用；普通项目沿用自己的文档协议。完整格式背景见 [OKF 参考](okf-v0.1.md)。验证状态由实际核验决定，必要时按项目已有工具记录。

## Bundle 边界

采用本协议时，`docs/` 是 Bundle；其中 `index.md` 是导航入口，`log.md` 可选，其余 Markdown 是 Concept。仓库根入口和 Bundle 外文件不自动纳入。根 index 可以是普通 Markdown；只有声明 freshness 策略才需要 YAML frontmatter。Concept 顶部 YAML 必须是可解析的 mapping，`type` 非空；未知 type 和字段保留。不要把现有普通 docs 当成待迁移 Bundle，也不要为单篇文档创建 Bundle。

## 知识粒度与字段

知识位置遵循现有布局：正文描述当前事实，决策记录保存理由，任务状态放 tracker。一个概念按实际读者、共同变化的内容和来源划界；常常一起消费的碎片可以合并，不同生命周期或使用场景可拆分。

```yaml
---
type: Architecture
sources:
  - src/service.ts
---
```

除 `type` 外，`title`、`description`、`tags`、`timestamp`、`owners`、`scope`、`sources` 和 `verification` 按实际需要使用，不填虚构值。`timestamp` 只表示正文语义变化，不证明验证；`scope` 和 `sources` 只表达真实覆盖范围与来源。索引策略及完整 source/scope 语义由项目采用的工具或约定说明。没有实际核验时保留未验证状态，不凭修改时间或结构成功标为已验证。

内部关系用 Markdown 链接，来源须支撑对应声明；敏感资料不写入引用。索引在导航变化时更新，必要时记录有长期意义的变化。

## ADR 写入

何时记录、内容与术语由 `domain-modeling` 判断；此处只约束 Bundle 格式。沿用项目已有 ADR 位置和编号（使用编号时按现有最大编号继续），只为真实决定创建记录。Bundle 中 ADR 是 Concept，使用 `type: Decision`、`verification.strategy: historical` 与 `status: proposed`、`accepted` 或 `superseded`。不把无 frontmatter 的裸模板直接写进 Bundle：

```yaml
---
type: Decision
status: proposed
verification:
  strategy: historical
---
```

接受时更新状态；已授权取代时保留旧决定，旧 ADR 设 `superseded` 并以相对路径写 `superseded_by`，新 ADR 用相对路径的 `supersedes` 反向指回。两个字段都可使用单条路径或非空路径列表，以支持合并决定并保留原取代链。每个替代目标须是 Bundle 内可解析的 Decision，且其 `supersedes` 包含旧 ADR 的路径；列表不能包含空值或无效路径。非 Bundle 项目沿用自己的生命周期格式。

## 渐进迁移

仅对已采用 Bundle 的项目，在已授权的相关写入中处理不合规元数据；不批量移动或重写已有文档。旧 HTML header metadata 不再作为 YAML 的输入；需要相应值时依据当前正文和权威来源重建，不伪造验证日期。移动、拆分、合并或删除按实际证据和授权处理，并修复入链；未知字段、旧记录和有效知识不自动清除。
