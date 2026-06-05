# Context Map

## Contexts

- [{Context A}](./{path-to-context-a}/CONTEXT.md) - {一句话说明该 context 的职责}
- [{Context B}](./{path-to-context-b}/CONTEXT.md) - {一句话说明该 context 的职责}

## Relationships

- **{Context A} -> {Context B}**：{说明单向依赖、事件流或共享边界}
- **{Context A} <-> {Context C}**：{说明双向协作或共享模型}

## Usage

- 仅在仓库存在多个清晰 context 时创建本文件。
- 本文件位于仓库根目录，用来告诉 Agent 去哪里读各 context 的 `CONTEXT.md`。
- 若某个决策只影响单一 context，在该 context 下维护自己的 `docs/adr/`；系统级决策保留在根目录 `docs/adr/`。
