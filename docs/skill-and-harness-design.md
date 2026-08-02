---
type: Playbook
scope:
  - skill-design
---

# Skill 与 Harness 设计指南

基于 Anthropic/OpenAI Harness Engineering 实践提炼的 Skill 设计原则。

---

## Prompt 设计

**四区块结构**

| 区块 | 内容 |
|------|------|
| Role | 具体角色定义，避免"有帮助的助手"这类模糊表述 |
| Objective | 明确"做什么"和"不做什么" |
| Context & Tools | 只放运行时必要信息，其余 just-in-time 加载 |
| Constraints & Format | 规则冲突优先级必须显式声明 |

**核心原则**

- **正确高度**：具体到能指导行为，但不硬编码执行路径。把经验编码为边界条件（"文件不超过 400 行"）而非步骤（"先写测试再写实现"）
- **字面遵从**：Claude 4.7+ 不会自动泛化规则，需要广泛应用时必须显式声明范围
- **最小集**：从最小 prompt + 最强模型开始，只在 eval 显示失败模式时才加规则
- **软硬配合**：prompt 是软约束（模型可绕过），安全需求必须用 harness 硬约束兜底

## Skill 判据体系

Skill 结构、description、渐进披露、完成判据、切分与剪枝的判据 SSOT 是 `skills/writing-skills/references/criteria.md`（成本模型、五种失败模式诊断、运行裁决）。本文不复制其内容。

## Skill 行为验证

两层评测，各管一段：

- **路由评测集**（管触发）：description 改动必须过 `evals/writing-skills/` 的路由评测（标注集 + judge 流程）；没跑过的触发声明标"未验证"。调用方式（invocation mode）改动不在其覆盖内，靠 frontmatter 机械核对与速查表同步。
- **压力场景**（管行为）：对核心工作流 Skill，不只检查 Markdown 格式，还要验证它是否改变 Agent 行为。

最小压力场景包含：
- 用户输入：真实用户会如何触发。
- 无 Skill 易错行为：Agent 常见失败模式。
- 期望行为：使用 Skill 后应出现的决策、输出或文件变化。
- 验收点：可观察证据。

判据分歧用运行裁决：删掉争议句跑一次评测，行为没变就是 no-op。

优先覆盖：
- 上游/下游契约交接。
- 子代理任务卡是否缺字段。
- 完成声明是否缺验证证据。
- worktree / branch cleanup / destructive 操作。
- 多个 Skill 可能同时触发的冲突场景。

相关 Skill：`writing-skills`。

---

## 工具设计（ACI）

**最小工具集**

串行调用链可靠性按乘法衰减（90% × 7步 = 48%），所以：
- 从 3-5 个工具开始，合并优于增加
- 只在 eval 数据显示工作流缺口时才扩展

**描述写法**

```python
"description": (
    "Search file contents by keyword. "
    "Use when finding code across the codebase. "
    "Do NOT use for listing directories — use list_directory instead. "  # 负向引导
    "Example: search_files(query='def auth', path='src/')"               # 内嵌示例
)
```

**Schema 是 Poka-yoke**：用 `enum` 约束合法值，而非在描述里警告；用 Pydantic 自动生成 schema 防止漂移。

**返回值是 context 预算**：避免返回原始 UUID 和无关字段，实现分页默认值（10-20 条），截断时给出明确指引。

**错误消息是纠错机会**：结构性错误返回详细反馈供模型原地纠正，永久错误直接上报不重试。

---

**整体关系**：Prompt 定义意图（软约束），Harness 工程实现兜底（硬约束），工具设计决定 Agent 的实际能力边界。三者需要配合设计，不能孤立优化。
