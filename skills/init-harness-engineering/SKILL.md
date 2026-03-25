---
name: init-harness-engineering
description: 初始化或更新项目的 AGENTS.md 与 docs/ 知识库结构，使项目符合 Harness Engineering 最佳实践。适合手动调用 `/init-harness-engineering [关注点]`，如 `重点关注前端架构` 或 `需要安全规范`。
disable-model-invocation: true
---

# 项目 Harness 初始化

为当前项目构建 Agent 可读的知识体系：AGENTS.md 作为简短目录（~200行），具体知识下沉到结构化的 `docs/` 目录。

**核心理念：** 给 Agent 一张地图，而非一本百科全书。仓库知识即唯一记录系统。

## 补充需求
$ARGUMENTS

## 执行步骤

### Phase 1: 项目扫描

分析当前项目，收集以下信息：
1. 项目类型、语言、框架、包管理器
2. 目录结构与模块划分
3. 构建/测试/lint 命令
4. 现有 AGENTS.md / README / 文档的内容
5. 代码风格与命名约定（从现有代码推断）
6. CI/CD 配置（如存在）
7. 现有的全局或项目级 memories

**并行启动 2-3 个 explore 子代理：**
- 代理 A：扫描项目根目录结构、配置文件、依赖清单，提取构建/测试/lint 命令
- 代理 B：分析核心代码架构，识别模块边界、层级依赖、主要数据流
- 代理 C（如项目含前端）：分析前端架构、组件结构、路由模式

### Phase 2: 构建 docs/ 知识库

根据扫描结果，创建或更新 `docs/` 目录结构。按项目实际情况裁剪，不需要的目录不创建：

```
docs/
├── architecture.md          # 系统架构：模块划分、层级依赖、数据流
├── development.md           # 开发指南：环境搭建、构建命令、调试方法
├── arch-decisions/        # 设计决策记录
│   └── index.md             # 决策索引（带验证状态）
├── exec-plans/              # 执行计划
│   ├── active/              # 进行中的计划
│   └── completed/           # 已完成的计划
├── domain/                  # 按需：领域文档（前端/安全/API/数据库等）
│   └── [domain-name].md
└── references/              # 外部参考文档（llms.txt 等）
```

**各文档内容指南：**

**architecture.md** — 最重要，必须创建：
- 顶层系统架构（用 Mermaid 图）
- 模块/包划分及职责
- 层级依赖方向（如 Types → Config → Service → UI）
- 关键数据流
- 模块间通信方式

**development.md** — 开发者入门必备：
- 环境搭建步骤
- 常用命令（build / test / lint / dev server）
- 调试技巧
- 贡献流程

**arch-decisions/index.md** — 决策追踪：
```markdown
# 设计决策索引

| ID     | 标题       | 状态              | 日期       | 文件   |
| ------ | ---------- | ----------------- | ---------- | ------ |
| DD-001 | [决策标题] | ✅已验证 / ⚠️待验证 | YYYY-MM-DD | [链接] |
```

每个文档顶部包含元信息：
```markdown
<!-- verified: YYYY-MM-DD -->
<!-- scope: [architecture|frontend|backend|security|...] -->
```

### Phase 3: 生成/更新 AGENTS.md

AGENTS.md 控制在 ~200 行，作为目录而非百科全书。结构：

```markdown
# [项目名] — Agent 指南

## 快速参考
- 语言/框架: ...
- 构建: `command`
- 测试: `command`
- Lint: `command`

## 架构概览
[1-3 句话概括系统架构，指向 docs/architecture.md]

## 代码规范
[仅列最关键的 3-5 条规范，其余指向具体文档]

## 知识库导航
| 主题     | 位置                   | 说明               |
| -------- | ---------------------- | ------------------ |
| 系统架构 | docs/architecture.md   | 模块划分与依赖方向 |
| 开发指南 | docs/development.md    | 环境搭建与常用命令 |
| 设计决策 | docs/arch-decisions/ | 重要技术决策记录   |
| 执行计划 | docs/exec-plans/       | 活跃与已完成的计划 |
| ...      | ...                    | ...                |

## 约束（硬规则）
[仅列机械化可执行的硬规则，如依赖方向、禁止项]

## 工作流约定
- 开始复杂任务（预估 >3 步或跨多文件）前，先在 docs/exec-plans/active/ 创建执行计划
- 任务完成后，将 exec-plan 从 active/ 移动到 completed/
- 上下文接近极限时，将当前进度和下一步更新到 exec-plan，然后提醒用户
- 对代码做出重大变更后，检查 docs/ 中相关文档是否需要同步更新
```

**关键原则：**
- AGENTS.md 中的每条规则都应是可执行的（能被 linter/test 验证的更好）
- 避免"所有事情都标为重要" — 当一切都重要，就没什么重要
- 具体实现细节、历史决策、详细规范 → 下沉到 `docs/` 对应文件
- 如果项目已有 AGENTS.md，保留其中仍然有效的规则，但重构为目录式结构

### Phase 4: 验证

1. 检查 AGENTS.md 行数是否 ≤ 200 行
2. 检查 docs/ 下各文件是否有 `verified` 元信息
3. 检查 AGENTS.md 中的知识库导航指针是否都指向实际存在的文件
4. 检查构建/测试命令是否可执行（如有环境条件）
5. 确认目录结构与项目实际情况匹配

## 更新模式

当项目已有 AGENTS.md 和 docs/ 时，此命令进入"更新模式"：
1. 扫描代码变化，识别文档中过期的部分
2. 更新 architecture.md 中的模块信息
3. 补充新发现的模块/组件到知识库
4. 更新 verified 时间戳
5. 不删除用户手动添加的内容，仅补充和修正
