---
name: dev-docs-maintain
description: 扫描并维护 docs/ 知识库，识别过期、缺失或失效内容并修复。适合手动调用 `/dev-docs-maintain [聚焦范围]`，如 `architecture` 或 `仅检查 arch-decisions`。
disable-model-invocation: true
---

# 文档园丁（Doc Gardening）

扫描项目的 `docs/` 知识库，对照实际代码状态，识别过期、不准确或缺失的文档，并修复。

**核心理念：** 文档腐化是不可避免的。定期修剪比一次性大清理高效得多。

## 执行流程

### Step 0: 确定聚焦范围

如果用户未提供参数，按以下优先级自动推断聚焦范围：
1. 检查 `docs/exec-plans/active/` — 如果有活跃的 exec-plan，优先维护其涉及的领域
2. 检查 git 近期变更（`git log --oneline -20` + `git diff --stat HEAD~10`） — 识别近期改动集中的模块
3. 检查文档新鲜度 — 优先处理 verified 时间最久的文档
4. 以上均无明确信号时，执行全量扫描

将推断结果简要告知用户后继续执行。

### Step 1: 健康检查

扫描以下内容并生成健康报告：

**结构完整性：**
- [ ] `AGENTS.md` 存在且 ≤ 200 行
- [ ] `docs/` 目录存在
- [ ] `docs/architecture.md` 存在
- [ ] `docs/development.md` 存在
- [ ] `AGENTS.md` 中的导航指针全部指向有效文件

**文档新鲜度：**
- 读取每个文档的 `<!-- verified: YYYY-MM-DD -->` 元信息
- 标记超过 30 天未验证的文档为 ⚠️ 待检查
- 标记超过 90 天未验证的文档为 ❌ 可能过期

**执行计划状态：**
- `docs/exec-plans/active/` 中是否有已完成但未归档的计划
- 是否有长期未更新的活跃计划

### Step 2: 代码对照验证

并行启动 explore 子代理，将文档描述与实际代码对照：

**代理任务：**
- 对照 `docs/architecture.md` 中描述的模块划分，检查是否有新增/移除/重组的模块
- 对照 `docs/development.md` 中的命令，检查是否仍然可用
- 对照 `docs/domain/` 下各文档，检查所描述的约定是否与代码一致
- 检查 `AGENTS.md` 中的构建/测试/lint 命令是否仍然正确

**每个子代理返回：**
- 与代码不一致的文档内容（引用具体文件路径和行号）
- 代码中新增但文档未覆盖的重要模块/组件
- 文档中提到但代码已删除/重命名的内容

### Step 3: 修复

根据验证结果，按优先级修复：

**P0 — 立即修复（不准确的信息会误导 Agent）：**
- AGENTS.md 中的错误命令或指针
- architecture.md 中已不存在的模块
- development.md 中失效的构建/测试命令

**P1 — 当次修复（信息缺失会导致 Agent 缺乏上下文）：**
- 新增模块未记录在 architecture.md
- 新引入的重要约定未记录
- 过期的设计决策未标记为 superseded

**P2 — 记录 TODO（改进项，不阻塞）：**
- 文档格式不统一
- 缺少 Mermaid 架构图
- 缺少 verified 元信息

### Step 4: 归档与清理

- 将 `docs/exec-plans/active/` 中已完成的计划移动到 `docs/exec-plans/completed/`
- 更新已修复文档的 `<!-- verified: YYYY-MM-DD -->` 时间戳
- 更新 `docs/arch-decisions/index.md` 中的验证状态

### Step 5: 报告

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
- 可配合 exec-plan 完成时运行，确保文档同步
- 如果只想检查不修复，在参数中说明"仅检查"
