---
name: setup-power-agent
description: |-
  项目初始化 Skill。补齐 AGENTS.md、docs/ 和 CONTEXT/ADR 项目记忆；初始化或更新项目 Harness 知识体系时触发。
  Triggers: 初始化 harness, setup-power-agent, AGENTS.md 初始化, docs 知识库初始化.
disable-model-invocation: true
---

# 项目 Harness 初始化

为当前项目构建 Agent 可读的知识体系：AGENTS.md 作为精简指南（~200行），具体知识下沉到结构化的 `docs/` 目录；领域语言与历史架构决策通过 `CONTEXT.md` / `CONTEXT-MAP.md` / `docs/adr/` 形成可持续维护的项目记忆。

**核心理念：** 给 Agent 一张地图，而非一本百科全书。仓库知识即唯一记录系统。

## 目标边界

### 做什么
- 初始化最小可用的 Harness 骨架：`AGENTS.md` 导航化 + `docs/` 基础结构。
- 初始化项目记忆骨架：根据仓库形态创建 `CONTEXT.md` 或 `CONTEXT-MAP.md`，并准备 `docs/adr/`。
- 在已有骨架上补齐缺失项并修复失效导航。

### 不做什么
- 不承担长期文档维护（交由 `dev-docs-maintain`）。
- 不执行大范围目录重排或风格重构。

## 必须项与建议项

**必须项：**
1. `AGENTS.md` 可读、可导航（建议 ≤ 200 行）。
2. `docs/architecture.md` 与 `docs/development.md` 存在。
3. 核心文档包含 `verified` 与 `scope` 元信息。
4. 项目记忆布局已初始化并写入 AGENTS/CLAUDE 入口：
   - 单 context：仓库根目录 `CONTEXT.md` + `docs/adr/`
   - 多 context：仓库根目录 `CONTEXT-MAP.md` + 各 context 的 `CONTEXT.md` + 根级 `docs/adr/`

**建议项：**
- `docs/adr/`
- `docs/exec-plans/`
- `docs/domain/`
- `docs/references/`

## 执行流程

1. **最小扫描**：识别项目类型、构建/测试命令、现有 docs 缺口，以及仓库是单 context 还是多 context。
2. **初始化/补齐**：先补必须项，再按需补建议项。
3. **初始化项目记忆**：
   - 单 context：创建根目录 `CONTEXT.md`
   - 多 context：创建根目录 `CONTEXT-MAP.md`，并为每个已确认的 context 创建对应 `CONTEXT.md`
   - 创建 `docs/adr/` 目录
   - 在 AGENTS/CLAUDE 入口中写明 `CONTEXT.md` / `CONTEXT-MAP.md` / `docs/adr/` 的用途与读取规则
4. **导航校验**：确认 `AGENTS.md` 指针有效。
5. **最小验证**：检查元信息、关键命令可执行性（如环境允许）。

## 项目记忆约定

### CONTEXT.md
- 用于记录项目或某个 context 的领域语言。
- 只收录该项目特有的业务术语、关系和边界，不收录通用编程概念。
- 术语定义保持简短、明确；存在同义词时，显式写出推荐词与避免词。

### CONTEXT-MAP.md
- 仅用于多 context 仓库，例如 monorepo、前后端分域仓库、多服务仓库。
- 文件位于仓库根目录，列出每个 context 的位置、职责以及它们之间的关系。
- 若仓库是单 context，不创建 `CONTEXT-MAP.md`。

### ADR
- ADR 存放在 `docs/adr/`，采用 `0001-slug.md` 命名。
- `setup-power-agent` 初始化时创建 `docs/adr/` 目录；ADR 文件仍只在真实决策出现时写入。
- 只记录难以逆转、没有上下文会显得反直觉、且确实存在权衡的决策。
- ADR 保持最小：标题 + 1 到 3 句上下文、决策与原因即可。

### 初始化到项目记忆
- 初始化时，AGENTS/CLAUDE 入口必须包含一段简短的“项目记忆”说明，明确告诉后续 Agent：
  - 到哪里读领域术语（`CONTEXT.md` / `CONTEXT-MAP.md`）
  - 到哪里读历史架构决策（`docs/adr/`）
  - 这是单 context 还是多 context 布局

参考模板：
- [references/context-template.md](./references/context-template.md)
- [references/context-map-template.md](./references/context-map-template.md)
- [references/adr-format.md](./references/adr-format.md)
- [references/domain-docs.md](./references/domain-docs.md)

## 更新模式（收窄）

当项目已有骨架时，仅允许：
1. 补齐缺失文件与最小结构。
2. 修复失效导航指针。
3. 刷新文档 `verified` 时间戳。
4. 补充缺失的项目记忆文件或入口说明，不重写已有术语与 ADR 内容。

不做持续园艺、归档搬运与大范围内容改写。

## 输出格式

完成任务后，用便于阅读的 Markdown 小节输出结果，不使用 YAML：

```markdown
## Harness 初始化结果

状态：DONE / DONE_WITH_CONCERNS / BLOCKED

### 证据
- [file / diff / command] <path 或 command>

### 阻塞项
- INIT-xxx：<阻塞原因>

### 非阻塞建议
- <建议内容>

### 下一步
- 动作：proceed / handoff-to-docs-maintain / clarify
- 负责人：user / orchestrator
```
