<!-- verified: 2026-04-21 -->
<!-- scope: workflow, skills, gate-mechanism -->
<!-- status: active -->

# DD-006: Gate 机制重构

**状态：** active（supersedes DD-005）
**日期：** 2026-03-25
**影响文件：** `skills/exec-plan-runner/SKILL.md`, `docs/workflow.md`, `docs/architecture.md`

> **注意：** `feature-dev` 已移除（2026-04），原文中的 feature-dev 阶段引用为历史记录。

## 背景

DD-005 在所有"关键决策点"设置强制人工 Gate，包括实现阶段前必须等待批准。随着 worktree 沙盒机制成熟、Agent-to-Agent 审查循环建立，原有的"实现前必须批准"Gate 已不再必要，反而降低了 Agent 的自主性。

## 约束

- 规划阶段的方向决策必须保留人工控制（spec 批准、架构选择）
- 破坏性操作由 worktree 物理隔离
- 实现质量由 Agent 审查循环保障

## 决定

将 Gate 从"关键决策点人工审批"重构为"规划阶段锁定方向 + 实现阶段 Agent 自主闭环"。

### 三道防线模型

```
1. 规划 Gate → 人类锁定方向与架构（discuss spec 批准）
2. Sandbox 隔离 → worktree 物理限制破坏范围
3. Agent-to-Agent 审查 → 质量保障（风险分级 + 审查循环）

Escalation 仅作兜底：审查修复循环耗尽（3轮）后才触发
```

### Gate 变化对比

| Gate 点 | DD-005 | DD-006 |
|---------|--------|--------|
| discuss spec 批准 | 强制等待 | **保留** — 规划 Gate |
| exec-plan-runner 启动前 | 强制等待 | **弱化为轻量启动通知** |
| exec-plan-runner escalation | 歧义/破坏性/3轮失败 | **仅 3 轮失败时触发** |

## 后果

- `exec-plan-runner`：Escalation 条件精简，只保留"3 轮修复失败"
- Agent 在实现阶段有更大自主权，worktree 提供安全兜底
- 减少不必要的人工等待，提升 exec-plan-runner 的自主闭环能力
