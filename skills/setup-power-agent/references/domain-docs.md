# Domain Docs And Project Memory

初始化项目时，把以下约定写入项目记忆入口（通常是 `AGENTS.md` 或 `CLAUDE.md` 的相关段落）：

- 领域术语存放在 `CONTEXT.md`；若仓库有多个 context，则由根目录 `CONTEXT-MAP.md` 指向各自的 `CONTEXT.md`。
- 历史架构决策存放在 `docs/adr/`，采用 `0001-slug.md` 命名；目录由 `setup-power-agent` 初始化，ADR 文件只在真实决策出现时写入。
- Agent 在处理架构、诊断、规划或大改动前，应先读取相关 context 文档与 ADR。

推荐写入的一段简述：

```md
### 项目记忆

领域语言记录在 `CONTEXT.md`；多 context 仓库使用根目录 `CONTEXT-MAP.md` 指向各 context 的 `CONTEXT.md`。历史架构决策记录在 `docs/adr/`。处理架构、诊断和大范围改动前，优先读取这些文件。
```

`docs/domain/project-memory.md` 可采用以下结构：

```md
---
type: Domain
scope:
  - project-memory
---

# Domain Docs

## Layout

- Single-context: root `CONTEXT.md` + root `docs/adr/`
- Multi-context: root `CONTEXT-MAP.md` + per-context `CONTEXT.md` + root `docs/adr/`

## Consumer rules

- 先判断当前工作涉及哪个 context。
- 有 `CONTEXT-MAP.md` 时，先读它，再读相关 context 的 `CONTEXT.md`。
- 做架构判断前，先读相关 ADR。
```

`AGENTS.md`、`CONTEXT.md` 与 `CONTEXT-MAP.md` 位于 Bundle 外；不要仅为了元数据而给它们添加 YAML frontmatter。
