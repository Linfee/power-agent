---
name: setup-power-agent
description: 项目初始化。补齐 AGENTS.md、docs/ 和 CONTEXT/ADR 项目记忆；初始化或更新项目 Harness 知识体系时使用。
disable-model-invocation: true
---

# 项目 Harness 初始化

为当前项目构建 Agent 可读的最小知识体系：AGENTS.md 作为精简导航（~200行），具体知识下沉到结构化的 `docs/` 目录；领域语言与历史架构决策通过 `CONTEXT.md` / `CONTEXT-MAP.md` / `docs/adr/` 形成可持续维护的项目记忆。

**核心理念：** 给 Agent 一张地图，而非一本百科全书。仓库知识即唯一记录系统。

## 判断什么

### 最小骨架由什么构成

- 导航入口：`AGENTS.md` 可读、可导航（建议 ≤ 200 行）。已有 `CLAUDE.md` 就只编辑它，已有 `AGENTS.md` 就只编辑它；两者都不存在时询问用户创建哪一个，不同时创建两个。
- 基础结构：`docs/architecture.md` 与 `docs/development.md` 存在；`docs/` Knowledge Bundle 内的核心 Concept 使用具有非空 `type` 的 YAML frontmatter。
- 项目记忆：单 context 用根目录 `CONTEXT.md` + `docs/adr/`；多 context 用根目录 `CONTEXT-MAP.md` + 各 context 的 `CONTEXT.md` + 根级 `docs/adr/`。
- 验证状态：验证运行由 `docs/.okf/verification.json` ledger 维护，初始化不伪造验证历史。

### 哪些事实改变判断

- 仓库形态：是否多 context（monorepo、前后端分域、多服务）决定 CONTEXT 布局。
- 已有骨架的完整度：是初始化还是只补缺口；切换单/多 context 布局或推倒重来时才重跑本 Skill，日常调整直接编辑对应文件。

建议项（按项目真实需要决定，不为填满分类创建）：`docs/adr/`、`docs/domain/`、`docs/references/` 等目录，只有在有实际知识要放时创建。

## 项目记忆约定

### CONTEXT.md / CONTEXT-MAP.md / ADR

- `CONTEXT.md`：记录项目或某个 context 的领域语言——只收录该项目特有的业务术语、关系和边界，不收录通用编程概念；术语定义简短明确，存在同义词时显式写出推荐词与避免词。
- `CONTEXT-MAP.md`：仅用于多 context 仓库（monorepo、前后端分域、多服务），位于仓库根目录，列出每个 context 的位置、职责及关系；单 context 不创建。
- ADR：存放在 `docs/adr/`，`0001-slug.md` 命名；`type: Decision` + YAML `status`（`proposed` / `accepted` / `superseded`）。只记录难以逆转、无上下文会显得反直觉、且确实存在权衡的决策；保持最小：标题 + 1-3 句上下文、决策与原因。
- `docs/adr/` 目录在初始化时创建；ADR **文件**仍只在真实决策出现时写入，不预造空决策。

初始化时，AGENTS/CLAUDE 入口必须包含一段简短的“项目记忆”说明，告诉后续 Agent：到哪里读领域术语（`CONTEXT.md` / `CONTEXT-MAP.md`）、到哪里读历史架构决策（`docs/adr/`）、这是单还是多 context 布局，以及消费纪律：

- 产出物命名领域概念时使用 `CONTEXT.md` 的原词，不漂移同义词；所需概念不在词汇表时视为信号——重新考虑表述，或记录缺口交 `dev-docs`。
- 产出与既有 ADR 矛盾时显式声明（如“与 ADR-0007 冲突，但值得重开，因为…”），不静默覆盖。
- `CONTEXT.md` / `docs/adr/` 缺失时静默继续，不建议预先创建，由真实术语与决策出现时惰性补齐。

参考模板：[context-template](./references/context-template.md)、[context-map-template](./references/context-map-template.md)、[adr-format](./references/adr-format.md)、[domain-docs](./references/domain-docs.md)——按需取用，不是固定步骤。

## 要保护什么

- 不覆盖用户已有编辑：已有 block 就地更新，不重复追加、不重写已有术语与 ADR 内容。
- Bundle 外的 `AGENTS.md`、`CONTEXT.md`、`CONTEXT-MAP.md` 不机械添加 YAML frontmatter。
- 不为新 Concept 伪造验证状态：`timestamp` 表示语义变化时间；ledger 由维护 Skill 写。
- 不做持续园艺、归档搬运与大范围内容改写；汇总现状与缺口时先呈现并确认，探索已确定的项直接做，用户可修改后再写入。

## 与其他知识维护 Skill 的绑定

初始化只负责建出最小骨架。后续出现实际缺口时按需使用其他两者，不形成每次必跑的链：

- 需要持续语义写入/修订（ADR、领域表达、Reference）→ `dev-docs`
- 既有 Bundle 需要结构健康检查、漂移修复或验证登记 → `dev-docs-maintain`

初始化过程本身可独立完成，不需要调用其他 Skill；发现仓库已有 docs/ 结构或项目记忆时，沿用并只补缺口。

## 完成声明

以实际结果为准：列出创建/修改的文件与路径、完成的导航校验与最小验证（如环境允许）；未做的、跳过确认的项如实说明，不声称完成。合并/PR、对外宣称完成仍须与实际结果匹配的新鲜证据；涉及用户仓库写入的动作保持在用户目标与授权范围内。