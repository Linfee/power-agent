---
type: Reference
scope:
  - exec-plans
---

# 执行计划目录

## 进行中

`active/` 目录存放当前进行中的执行计划。每个计划是一个子目录，默认包含：
- `plan.md` — 执行真源，包含目标、Scope、关键决策、任务、Proof Strategy、阻塞/升级条件和风险
- `review-contract.md` — 人类默认审阅面，聚焦意图、范围、验收、证明策略、Agent 自主边界和高风险项

复杂计划可按需拆出：
- `context.md` — 大体量背景、约束、相关文件
- `tasks.md` — 复杂任务图（带依赖关系和状态）

## 已归档

`completed/` 目录存放已完成的执行计划。Session Log 保留在 exec-plan 文件的 `## Session Log` section 中，不另建独立日志文件。

## 命名约定

```
docs/exec-plans/
├── active/
│   └── YYYY-MM-DD-feature-name/
│       ├── plan.md
│       ├── review-contract.md
│       ├── context.md        # 可选
│       └── tasks.md          # 可选
└── completed/
    └── YYYY-MM-DD-feature-name/
        ├── plan.md
        ├── review-contract.md
        ├── context.md        # 可选
        └── tasks.md          # 可选
```
