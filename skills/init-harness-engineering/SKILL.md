---
name: init-harness-engineering
description: |-
  初始化或更新项目的 AGENTS.md 与 docs/ 知识库结构，使项目符合 Harness Engineering 最佳实践。
  Triggers: 初始化 harness, init-harness-engineering, AGENTS.md 初始化, docs 知识库初始化.
version: 1.2.4
disable-model-invocation: true
---

# 项目 Harness 初始化

为当前项目构建 Agent 可读的知识体系：AGENTS.md 作为精简指南（~200行），具体知识下沉到结构化的 `docs/` 目录。

**核心理念：** 给 Agent 一张地图，而非一本百科全书。仓库知识即唯一记录系统。

## 目标边界

### 做什么
- 初始化最小可用的 Harness 骨架：`AGENTS.md` 导航化 + `docs/` 基础结构。
- 在已有骨架上补齐缺失项并修复失效导航。

### 不做什么
- 不承担长期文档维护（交由 `dev-docs-maintain`）。
- 不执行大范围目录重排或风格重构。

## 必须项与建议项

**必须项：**
1. `AGENTS.md` 可读、可导航（建议 ≤ 200 行）。
2. `docs/architecture.md` 与 `docs/development.md` 存在。
3. 核心文档包含 `verified` 与 `scope` 元信息。

**建议项：**
- `docs/arch-decisions/`
- `docs/exec-plans/`
- `docs/domain/`
- `docs/references/`

## 执行流程

1. **最小扫描**：识别项目类型、构建/测试命令、现有 docs 缺口。
2. **初始化/补齐**：先补必须项，再按需补建议项。
3. **导航校验**：确认 `AGENTS.md` 指针有效。
4. **最小验证**：检查元信息、关键命令可执行性（如环境允许）。

## 更新模式（收窄）

当项目已有骨架时，仅允许：
1. 补齐缺失文件与最小结构。
2. 修复失效导航指针。
3. 刷新文档 `verified` 时间戳。

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
