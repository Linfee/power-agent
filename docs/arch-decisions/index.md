<!-- verified: 2026-03-25 -->
<!-- scope: arch-decisions -->

# 设计决策索引

本索引追踪 power-agent 项目的重要技术决策。

## 索引

| ID | 标题 | 状态 | 日期 | 文件 |
|----|------|------|------|------|
| DD-001 | Skill 作为执行单元 | ✅ 已验证 | 2026-03-25 | [DD-001](DD-001-skill-as-execution-unit.md) |
| DD-002 | 子代理一次性原则 | ✅ 已验证 | 2026-03-25 | [DD-002](DD-002-disposable-subagents.md) |
| DD-003 | 产出物作为协调介质 | ✅ 已验证 | 2026-03-25 | [DD-003](DD-003-artifacts-as-coordination.md) |
| DD-004 | AGENTS.md 精简结构 | ✅ 已验证 | 2026-03-25 | [DD-004](DD-004-lean-agents-md.md) |
| DD-005 | Gate 机制强制人工确认 | 🔄 superseded by DD-006 | 2026-03-25 | [DD-005](DD-005-gate-mechanism.md) |
| DD-006 | Gate 机制重构 | ✅ active | 2026-03-25 | [DD-006](DD-006-gate-restructuring.md) |

## 状态说明

| 状态 | 含义 |
|------|------|
| ✅ 已验证 | 决策已实施并经代码验证 |
| ⚠️ 待验证 | 决策已实施但需重新验证 |
| 📋 提议中 | 决策尚未最终确定 |
| 🔄 superseded | 决策已被新决策取代，不再适用 |

## 创建新决策

使用以下模板创建 `DD-NNN-title.md`：

```markdown
<!-- verified: YYYY-MM-DD -->
<!-- scope: [涉及范围] -->
<!-- status: proposed -->

# DD-NNN: [决策标题]

## 背景
[为什么需要做这个决策？]

## 约束
[必须满足的硬性条件]

## 方案对比
| 方案 | 优势 | 劣势 | 复杂度 |
|------|------|------|--------|
| A: ... | ... | ... | S/M/L |
| B: ... | ... | ... | S/M/L |

## 决定
[选择了哪个方案，为什么]

## 后果
[这个决策带来的影响]
```

创建后更新本索引。
