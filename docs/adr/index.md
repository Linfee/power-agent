---
type: Reference
---

# 架构决定

## 当前基线

[ADR-0014：当前工程能力、调用与分发基线](0014-current-baseline.md)合并此前 13 份 ADR 中仍有效的决定：能力与调用边界、授权内推进、证明与审查、状态与知识、插件和 hook。日常维护不需要串读旧记录；事实和操作入口见[文档首页](../index.md)。

## 历史归档

以下记录均为 `superseded`，原始正文和旧取代链保留在 `archive/`，并与 ADR-0014 建立双向关系。旧名称、固定 Gate、层级和独立安装要求不再作为当前指令。

| 记录 | 当时议题 |
|---|---|
| [ADR-0001](archive/0001-skill-as-execution-unit.md) | Skill 执行单元 |
| [ADR-0002](archive/0002-disposable-subagents.md) | 子代理一次性原则 |
| [ADR-0003](archive/0003-artifacts-as-coordination.md) | 文件产物协调 |
| [ADR-0004](archive/0004-lean-agents-md.md) | Agent 入口精简 |
| [ADR-0005](archive/0005-gate-mechanism.md) | 人工 Gate |
| [ADR-0006](archive/0006-gate-restructuring.md) | Gate 与自主实现 |
| [ADR-0007](archive/0007-reviewer-session-continuity.md) | Reviewer 上下文连续性 |
| [ADR-0008](archive/0008-complexity-admission.md) | 复杂性与实现选择顺序 |
| [ADR-0009](archive/0009-lean-default-orchestration.md) | L0/L1/L2 默认分层 |
| [ADR-0010](archive/0010-judgment-oriented-skills.md) | 判断导向与独立安装 |
| [ADR-0011](archive/0011-knowledge-navigation-lifecycle.md) | 知识导航初始化与演进 |
| [ADR-0012](archive/0012-matt-led-skill-fusion.md) | Matt 主干融合与整包组合 |
| [ADR-0013](archive/0013-skill-invocation-and-hook-boundaries.md) | 调用范围收敛与薄 hook |

新决定沿用后续编号；被取代的记录保留历史与双向关系，不重新编号或静默改写过去的决定。
