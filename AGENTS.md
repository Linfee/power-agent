# Power-Agent — Agent 指南

AI 编码 Agent 工作流插件系统，融合 superpowers + Harness Engineering 方法论。

## 快速参考

- **类型**: AI Agent Skill/Prompt 工程
- **Skills**: 16 个可复用 Skill
- **支持平台**: Claude Code, Cursor, Factory Droid

## 架构概览

五层架构：编排层 → 规划层 → 实现层 → 审查层 → 基础设施层。详见 [docs/architecture.md](docs/architecture.md)。

## 知识库导航

| 主题 | 位置 | 说明 |
|------|------|------|
| 系统架构 | [docs/architecture.md](docs/architecture.md) | 模块划分、依赖方向、子代理模式 |
| 开发指南 | [docs/development.md](docs/development.md) | 环境搭建、Skill 开发、文件命名 |
| 工作流机制 | [docs/workflow.md](docs/workflow.md) | Skill 协调、产出物流转、反模式 |
| Harness 体系 | [docs/harness-engineering.md](docs/harness-engineering.md) | 设计哲学、知识库结构、标准工作流 |
| 设计决策 | [docs/arch-decisions/](docs/arch-decisions/index.md) | 重要技术决策索引 |
| 执行计划 | [docs/exec-plans/](docs/exec-plans/) | active/ 进行中，completed/ 已归档 |
| Spec 文档 | [docs/specs/](docs/specs/) | 经过审查的需求规格 |

## 核心工作流

```
discuss skill [需求]      → docs/specs/*.md
    ↓
/feature-dev [功能]       → 架构设计 → exec-plan
    ↓
exec-plan-runner          → TDD 子代理并行实现
    ↓
requesting-code-review    → 代码审查
    ↓
dev-docs-maintain         → 文档同步
```

**调试路径**: `systematic-debugging` → `test-driven-development` → `verification-before-completion`

## Skill 速查

| Skill | 用途 | 触发词 |
|-------|------|--------|
| `feature-dev` | 引导式开发 | '开发功能', '新功能' |
| `discuss` | 设计探索，产出 spec | '需求讨论', '方案对比' |
| `writing-plans` | 创建 TDD 结构 exec-plan | '创建实现计划', 'exec-plan' |
| `exec-plan-runner` | 执行 exec-plan | 恢复执行 |
| `systematic-debugging` | 四阶段根因调试 | 'bug', '测试失败', 'debug' |
| `test-driven-development` | RED-GREEN-REFACTOR | '实现功能', 'TDD' |
| `requesting-code-review` | 代码审查编排 | '代码审查', 'code review' |
| `verification-before-completion` | 证据优先验证 | '验证完成', 'verification' |
| `dev-docs` | 文档路由器 | '写文档', 'architecture' |
| `dev-docs-maintain` | 文档维护 | 手动调用 |
| `dispatching-parallel-agents` | 并行调度 | '并行执行', 'parallel agents' |
| `init-harness-engineering` | 项目初始化 | 手动调用 |
| `harness-engineering-review` | 实践审查 | 'agent最佳实践' |
| `using-git-worktrees` | 建立隔离 worktree（exec-plan-runner 自动调用） | 手动调用 |
| `finishing-a-development-branch` | 分支收尾：merge/PR/保留/丢弃（exec-plan-runner 自动调用） | 手动调用 |

## 约束（硬规则）

| 规则 | 说明 |
|------|------|
| 依赖方向 | 只能从上层指向下层，禁止反向 |
| 子代理一次性 | 不重用子代理，每次启动新代理 |
| Gate 强制等待 | discuss spec 批准、feature-dev 方案选择、实现批准 |
| 证据优先 | 没有运行验证不得声称完成 |
| 根因优先 | 没有根本原因分析没有修复 |
| 并发限制 | 最大并行度 3 |

## 文档规范

**元信息（所有文档必须包含）**:
```markdown
<!-- verified: YYYY-MM-DD -->
<!-- scope: [范围] -->
```

**命名约定**:
- Skill 主文件: `SKILL.md` (大写)
- 设计决策: `DD-NNN-title.md`
- Spec: `YYYY-MM-DD-topic.md`
- Exec-plan: `YYYY-MM-DD-title.md`

## 工作流约定

- 开始复杂任务（预估 >3 步）前，先在 `docs/exec-plans/active/` 创建执行计划
- 任务完成后，将 exec-plan 从 `active/` 移动到 `completed/`
- 上下文接近极限时，更新 exec-plan 进度并提醒用户
- 重大变更后，检查 docs/ 相关文档是否需要同步更新
- 文档 verified 时间戳超过 30 天需验证，超过 90 天需修复

## 上游追踪

| 项目 | 版本 | 来源 |
|------|------|------|
| superpowers | v5.0.5 | github.com/obra/superpowers |
| Harness Engineering | 2026-02 | openai.com/index/harness-engineering |
