# Context Map

## Contexts

- [{Context A}](./{path-to-context-a}/CONTEXT.md) - {一句话说明该 context 的职责}
- [{Context B}](./{path-to-context-b}/CONTEXT.md) - {一句话说明该 context 的职责}

## Relationships

- **{Context A} -> {Context B}**：{说明单向依赖、事件流或共享边界}
- **{Context A} <-> {Context C}**：{说明双向协作或共享模型}

## Usage

- 仅在多个清晰 context 需要跨域导航、且既有文档尚未提供该导航时创建；只列真实存在的文档。
- 沿用仓库既有导航位置；没有约定时可放在根目录，指向各 context 的领域文档，不要求每处都新建 `CONTEXT.md`。
- 决策历史沿用既有 ADR 布局；有真实知识需要时再新增记录，不为每个 context 预建 ADR 目录。

> 保留有实际内容的章节。位于 `docs/` Knowledge Bundle 外的 `CONTEXT-MAP.md` 不机械添加 YAML frontmatter。
