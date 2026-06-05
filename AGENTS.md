# Power-Agent — Agent 指南

AI 编码 Agent 工作流插件系统，融合 superpowers + Harness Engineering 方法论。

## 快速参考

- **类型**: AI Agent Skill/Prompt 工程
- **Skills**: 16 个可复用 Skill
- **支持平台**: Claude Code, Cursor, Factory, Droid, Gemini

## 架构概览

四层架构：规划层 → 实现层 → 审查层 → 基础设施层。详见 [docs/architecture.md](docs/architecture.md)。

## 知识库导航

| 主题 | 位置 | 说明 |
|------|------|------|
| 系统架构 | [docs/architecture.md](docs/architecture.md) | 模块划分、依赖方向、子代理模式 |
| 开发指南 | [docs/development.md](docs/development.md) | 环境搭建、Skill 开发、文件命名 |
| 工作流机制 | [docs/workflow.md](docs/workflow.md) | Skill 协调、产出物流转、反模式 |
| Harness 体系 | [docs/harness-engineering.md](docs/harness-engineering.md) | 设计哲学、知识库结构、标准工作流 |
| Skill 设计 | [docs/skill-and-harness-design.md](docs/skill-and-harness-design.md) | Skill 结构规范、Harness 设计原则 |
| 设计决策 | [docs/arch-decisions/](docs/arch-decisions/index.md) | 重要技术决策索引 |
| 执行计划 | [docs/exec-plans/](docs/exec-plans/) | active/ 进行中，completed/ 已归档 |
| 需求结论 / Spec 文档 | discuss / 用户 | 默认内联需求结论；按需落盘 `docs/specs/` |

## 核心工作流

```
discuss skill [需求]      → 内联需求结论（按需 docs/specs/*.md）
    ↓
writing-plans             → compact exec-plan（plan.md + review-contract.md，按需 context/tasks）
    ↓
plan-impl          → BOOTSTRAP(using-git-worktrees) → 中小任务可走 plan-impl-lightweight → 优先 team 模式，缺失 team 工具时回退并行/单代理委派 → 内部审查 → 全量审查 → 验证 → 分支收尾
```

**调试路径**: `systematic-debugging` → `proof-oriented-development` → `verification-before-completion`

**最终验证前审查**: `requesting-code-review`（全量审查）在 `verification-before-completion` 前默认强制执行；合并/PR 前不得跳过未通过的审查结果，除非用户明确要求跳过并记录原因。`dev-docs-maintain`（文档维护）按需手动调用。

## Skill 速查

| Skill | 用途 | 触发词 |
|-------|------|--------|
| `discuss` | 需求讨论与 PRD 细化，必要时用 HTML 可视化辅助，默认产出内联需求结论，按需落盘 spec | '需求讨论', 'PRD 细化', '可视化讨论' |
| `writing-plans` | 创建包含验收与验证路径的 compact exec-plan | '创建实现计划', 'exec-plan' |
| `plan-impl` | 执行 exec-plan | 恢复执行 |
| `plan-impl-lightweight` | 中小任务轻量执行路径：scope_check、proof-oriented 实现、局部验证、有限 review/fix 循环、必要时升级完整 runner | '轻量执行', 'lightweight path', 'targeted verify' |
| `systematic-debugging` | 四阶段根因调试 | 'bug', '测试失败', 'debug' |
| `proof-oriented-development` | 证明导向开发闭环：小步实现、最小相关验证、交付 Proof Block | '实现功能', 'Proof Block', '最小有效验证', '目标验证' |
| `requesting-code-review` | 代码审查编排 | '代码审查', 'code review' |
| `receiving-code-review` | 审查反馈技术评估 | '收到审查', '审查反馈' |
| `verification-before-completion` | 完成前审计 Proof Block 并输出 verification_evidence | '验证完成', 'verification', 'Proof Block 审计' |
| `dev-docs` | 文档路由器 | '写文档', 'architecture' |
| `dev-docs-maintain` | 文档维护 | 手动调用 |
| `using-git-worktrees` | 隔离 worktree 准备 | 'worktree', '隔离执行' |
| `setup-power-agent` | 项目初始化 | 手动调用 |
| `harness-engineering-review` | 实践审查 | 'agent最佳实践' |
| `writing-skills` | 创建/修改/验证 Skill | '写skill', '修改skill' |
| `finishing-a-development-branch` | 分支收尾：merge/PR/保留/丢弃（plan-impl 自动调用） | 手动调用 |

## 约束（硬规则）

| 规则 | 说明 |
|------|------|
| 依赖方向 | 只能从上层指向下层，禁止反向 |
| 子代理一次性 | 不重用子代理，每次启动新代理 |
| 规划 Gate 与证据 Gate | discuss 需求结论批准保留强制 Gate；实现阶段使用轻量启动通知，完成声明依赖 Proof Block 与验证证据（DD-006） |
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
- Exec-plan: `YYYY-MM-DD-title/`

## 工作流约定

- 开始复杂任务（预估 >3 步）前，先在 `docs/exec-plans/active/` 创建执行计划
- 任务完成后，将 exec-plan 从 `active/` 移动到 `completed/`
- 上下文接近极限时，更新 exec-plan 进度并提醒用户
- 重大变更后，检查 docs/ 相关文档是否需要同步更新
- 需要文档维护时，按需手动调用 `dev-docs-maintain`
- 文档 verified 时间戳超过 30 天需验证，超过 90 天需修复

## 上游追踪

| 项目 | 来源 |
|------|------|
| superpowers | github.com/obra/superpowers |
| Harness Engineering | openai.com/index/harness-engineering |