# 设计决策索引

本目录记录 Power-Agent 的重要技术决策（Architecture Decision Records）。

## 决策列表

| 编号 | 标题 | 状态 | 日期 |
|------|------|------|------|
| [DD-001](DD-001-skill-as-execution-unit.md) | Skill 作为执行单元 | accepted | 2026-03 |
| [DD-002](DD-002-disposable-subagents.md) | 子代理一次性原则 | accepted | 2026-03 |
| [DD-003](DD-003-artifacts-as-coordination.md) | 产出物作为协调介质 | accepted | 2026-03 |
| [DD-004](DD-004-lean-agents-md.md) | AGENTS.md 精简结构 | accepted | 2026-03 |
| [DD-005](DD-005-gate-mechanism.md) | Gate 机制强制人工确认 | superseded by DD-006 | 2026-03 |
| [DD-006](DD-006-gate-restructuring.md) | Gate 机制重构 | **active** | 2026-03 |

## 当前生效的核心决策

1. **Skill 是执行单元**（DD-001）：每个 Skill 只做一件事
2. **子代理一次性**（DD-002）：不重用，每次干净启动
3. **产出物是协调介质**（DD-003）：通过文件"传话"，不直接调用
4. **AGENTS.md 是目录**（DD-004）：≤200 行，具体内容下沉到 docs/
5. **规划 Gate + 实现自主**（DD-006）：规划阶段人类锁定方向，实现阶段 Agent 自主闭环
