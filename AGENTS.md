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
| ADR | [docs/adr/](docs/adr/) | 历史架构决策记录 |
| 执行计划 | [docs/exec-plans/](docs/exec-plans/) | active/ 进行中，completed/ 已归档 |
| 需求结论 / Spec 文档 | discuss / 用户 | 默认内联需求结论；按需落盘 `docs/specs/` |

## 核心工作流

```
discuss skill [需求]      → 内联需求结论（按需 docs/specs/*.md）
    ↓
writing-plans             → compact exec-plan（plan.md + review-contract.md，按需 context/tasks）→ low self-review / medium/high 独立 reviewer
    ↓
plan-impl          → BOOTSTRAP(using-git-worktrees) → 中小任务可走 plan-impl-lightweight → 优先 team 模式，缺失 team 工具时回退并行/单代理委派 → scratch artifacts + 单 reviewer 双 verdict → 全量审查 → 验证 → 分支收尾
```

**调试路径**: `systematic-debugging` → `proof-oriented-development` → `verification-before-completion`

**最终验证前审查**: `requesting-code-review`（全量审查）在 `verification-before-completion` 前默认强制执行；合并/PR 前不得跳过未通过的审查结果，除非用户明确要求跳过并记录原因。`dev-docs-maintain`（文档维护）是按需触发的普通 Skill，不是每次开发执行的固定阶段。

## Skill 速查

| Skill | 用途 | 触发词 |
|-------|------|--------|
| `discuss` | 需求讨论与 PRD 细化，必要时用 HTML 可视化辅助，默认产出内联需求结论，按需落盘 spec | '需求讨论', 'PRD 细化', '可视化讨论' |
| `writing-plans` | 创建包含验收与验证路径的 compact exec-plan | '创建实现计划', 'exec-plan' |
| `plan-impl` | 执行 exec-plan | 恢复执行 |
| `plan-impl-lightweight` | 中小任务轻量执行路径：scope_check、proof-oriented 实现、局部验证、有限 review/fix 循环、必要时升级完整 runner | '轻量执行', 'lightweight path', 'targeted verify' |
| `systematic-debugging` | 探索式根因调查：以因果证据、安全边界和风险相称的性能/稳定性证据约束修复交接 | 'bug', '测试失败', '性能退化', 'flaky', 'debug' |
| `proof-oriented-development` | 证明导向开发闭环：小步实现、最小相关验证、交付 Proof Block | '实现功能', 'Proof Block', '最小有效验证', '目标验证' |
| `requesting-code-review` | 代码审查编排 | '代码审查', 'code review' |
| `receiving-code-review` | 审查反馈技术评估 | '收到审查', '审查反馈' |
| `verification-before-completion` | 完成前审计 Proof Block 并输出 verification_evidence | '验证完成', 'verification', 'Proof Block 审计' |
| `dev-docs` | 长期开发知识回写 | '文档知识沉淀', '系统事实回写', '架构事实更新', '领域知识维护', 'ADR 依据记录', '集成参考沉淀', 'dev-docs' |
| `dev-docs-maintain` | Docs Bundle 健康检查、漂移修复与验证登记 | 'docs 健康检查', '知识库体检', 'OKF Bundle 检查', '验证登记', 'verification ledger', '文档漂移修复', 'dev-docs-maintain' |
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
| 规划审查与证据 Gate | discuss / writing-plans 通过独立审查交棒；实现阶段使用轻量启动通知，完成声明依赖 Proof Block 与验证证据（ADR-0006） |
| 证据优先 | 没有运行验证不得声称完成 |
| 根因优先 | 没有根本原因分析没有修复 |
| 并发限制 | 最大并行度 3 |

## 文档规范

**YAML frontmatter（仅 `docs/` Knowledge Bundle 内的 Concept Document）**:
```yaml
---
type: Concept # 替换为能表达文档用途的非空类型
scope:
  - architecture
status: active # 按生命周期需要添加
---
```

`docs/` 中除 `index.md` / `log.md` 外的 Concept 必须有非空 `type`；`scope` 和 `status` 仅在有实际语义时填写。验证运行状态由 `docs/.okf/verification.json` ledger 维护，不写入 Concept。Bundle 外的 `AGENTS.md`、`CONTEXT.md` / `CONTEXT-MAP.md` 不应机械添加 frontmatter。ADR 使用 `type: Decision`，并以 YAML `status` 表示 `accepted`、`proposed` 或 `superseded` 等历史状态。

**命名约定**:
- Skill 主文件: `SKILL.md` (大写)
- ADR: `0001-slug.md`
- Spec: `YYYY-MM-DD-topic.md`
- Exec-plan: `YYYY-MM-DD-title/`

## 工作流约定

- 开始复杂任务（预估 >3 步）前，先在 `docs/exec-plans/active/` 创建执行计划
- 任务完成后，将 exec-plan 从 `active/` 移动到 `completed/`
- 上下文接近极限时，更新 exec-plan 进度并提醒用户
- 重大变更后，检查 docs/ 相关文档是否需要同步更新
- 需要文档维护时，由 `dev-docs-maintain` 按需触发；它不是每次开发的固定阶段
- ADR 保留历史决策与 YAML lifecycle status；决策过期时用新 ADR supersede
- Concept 的验证运行状态以 `docs/.okf/verification.json` ledger 为准；来源变化或策略到期时运行验证，不把旧日期迁入文档

## 上游追踪

| 项目 | 来源 |
|------|------|
| superpowers | github.com/obra/superpowers |
| Harness Engineering | openai.com/index/harness-engineering |
