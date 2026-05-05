---
name: dev-docs-maintain
description: |-
  手动或收尾后按需扫描 docs/ 文档和知识库，识别并修复过期、缺失或失效内容
  Triggers: 文档维护, docs 过期, dev-docs-maintain, doc gardening.
version: 1.2.4
disable-model-invocation: true
---

# 文档园丁（Doc Gardening）

扫描项目的 `docs/` 知识库，对照实际代码状态，识别过期、不准确或缺失的文档，并修复。

**核心理念：** 文档腐化是不可避免的。定期修剪比一次性大清理高效得多。

## 模式

- `check-only`：只检查并输出问题，不写文件。
- `fix-safe`：仅修复 P0/P1 的明确错误。
- `full-maintain`：在 `fix-safe` 基础上可执行归档与索引同步。

未显式指定时默认 `fix-safe`。

## 优先级定义

- **P0**：文档存在错误信息或导航指针失效，直接影响 Agent 执行。
- **P1**：内容已过期或与代码现状不符，影响理解但不致命。
- **P2**：缺失内容或可补充完善，不影响现有执行。

## 执行流程

1. **确定范围**
   - 用户指定范围优先；未指定时仅做最小自动推断（文档新鲜度 + 最近变更）。
2. **健康检查**
   - 结构完整性：必须项文件是否存在（`AGENTS.md`、`docs/architecture.md`、`docs/development.md`）
   - `verified` 新鲜度：> 30 天需验证标记（P1），> 90 天视为失效须修复（P0）
   - 导航指针有效性：`AGENTS.md` 中所有文件路径可解析（失效为 P0）
3. **代码对照验证**
   - 对照 `architecture/development/domain` 文档与代码现状，输出带路径与行号证据。
4. **按模式执行**
   - `check-only`：跳过写入。
   - `fix-safe`：只修 P0/P1。
   - `full-maintain`：可追加 exec-plan 归档与 arch-decision 索引状态同步。
5. **报告**
   - 输出统一 contract 与修复摘要。

### 输出格式

完成任务后，用便于阅读的 Markdown 小节输出结果，不使用 YAML：

```markdown
## 文档维护结果

状态：DONE / DONE_WITH_CONCERNS / BLOCKED

### 证据
- [file / diff / command] <path 或 command>

### 阻塞项
- DOCM-xxx：<阻塞原因>

### 非阻塞建议
- <建议内容>

### 下一步
- 动作：proceed / rerun / clarify
- 负责人：user / orchestrator
```

输出简洁的修复报告：

```
## 文档健康报告

### 扫描范围
[扫描了哪些文件]

### 修复项
| 文件 | 问题 | 操作 | 优先级 |
|------|------|------|--------|
| docs/architecture.md | 新增 auth 模块未记录 | 已补充 | P1 |
| AGENTS.md | test 命令已变更 | 已更新 | P0 |
| ... | ... | ... | ... |

### 待处理（P2）
- [ ] ...

### 下次建议关注
- ...
```

## 使用建议

- 建议每次重大功能完成后运行一次
- 可在 exec-plan 完成后按需运行，确保文档同步
- exec-plan-runner 或 finishing-a-development-branch 只给出 docs 更新提醒，不自动把本 Skill 纳入固定主流程
- 如果只想检查不修复，在参数中说明"仅检查"
