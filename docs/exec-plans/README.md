# 执行计划目录

## 进行中

`active/` 目录存放当前进行中的执行计划。每个计划是一个子目录，包含：
- `plan.md` — 计划概述、目标、架构方案
- `context.md` — 关键上下文、约束、相关文件
- `tasks.md` — 任务列表（带依赖关系和状态）

## 已归档

`completed/` 目录存放已完成的执行计划（含 Session Log）。

## 命名约定

```
docs/exec-plans/
├── active/
│   └── YYYY-MM-DD-feature-name/
│       ├── plan.md
│       ├── context.md
│       └── tasks.md
└── completed/
    └── YYYY-MM-DD-feature-name/
        ├── plan.md
        ├── context.md
        ├── tasks.md
        └── session-log.md  # 归档时添加
```
