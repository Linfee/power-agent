<!-- verified: 2026-06-05 -->
<!-- scope: architecture -->

# 系统架构

Power-Agent 是一个 AI 编码 Agent 工作流插件系统，融合了 superpowers 和 Harness Engineering 两套方法论。

## 顶层架构

```mermaid
graph TB
    User[用户需求] --> D[discuss 需求讨论]

    subgraph "规划层"
        D2[discuss 需求讨论]
        WP[writing-plans 计划创建]
        DD[dev-docs 文档路由]
    end

    subgraph "实现层"
        EP[plan-impl 计划执行]
        LEP[plan-impl-lightweight 轻量执行路径]
        POD[proof-oriented-development]
        DBG[systematic-debugging]
        VBC[verification-before-completion]
    end

    subgraph "审查层"
        RCR[requesting-code-review]
        RRC[receiving-code-review]
        HER[harness-engineering-review]
    end

    subgraph "基础设施层"
        WGT[using-git-worktrees]
        WSK[writing-skills]
        FAB[finishing-a-development-branch]
        SPA[setup-power-agent]
        DDM[dev-docs-maintain]
    end

    D2 --> WP
    WP --> EP

    EP --> LEP
    EP --> POD
    EP --> VBC
    LEP --> POD
    LEP --> VBC
    EP -.->|合并前强制审查| RCR
    EP --> FAB
    User -.->|按需维护| DDM

    DBG --> POD
    DBG --> VBC
```

## 模块划分

| 层级 | Skill | 职责 |
|------|-------|------|
| **规划层** | `discuss` | 需求讨论与 PRD 细化，必要时用 HTML 可视化辅助，默认产出内联需求结论，按需落盘 spec/doc |
| | `writing-plans` | 需求结论 / spec / 用户描述 → compact exec-plan，并提供人类默认审阅入口 `review-contract.md` |
| | `dev-docs` | 文档路由器，委派或创建文档 |
| **实现层** | `plan-impl` | 状态机编排，驱动全生命周期；优先使用 team 模式，缺失 team 工具时回退并行或单实现子代理 |
| | `plan-impl-lightweight` | 中等偏小任务的轻量执行路径：scope_check、proof-oriented 实现、局部验证、有限 review/fix 循环、必要时升级完整 runner |
| | `proof-oriented-development` | 证明导向开发闭环：小步实现、最小相关验证、输出 Proof Block |
| | `systematic-debugging` | 四阶段根因优先调试 |
| | `verification-before-completion` | 审计 Proof Block / 等价证据块，补充最小验证，输出 verification_evidence |
| **审查层** | `requesting-code-review` | 风险分级全量审查编排 |
| | `receiving-code-review` | 审查反馈技术评估 |
| | `harness-engineering-review` | Agent 工作流七维度审查 |
| **基础设施层** | `using-git-worktrees` | 隔离工作区检测、创建与基线准备 |
| | `writing-skills` | Skill 创建、修改、契约审查与压力场景验证 |
| | `finishing-a-development-branch` | 分支处置决策器（merge/PR/保留/丢弃） |
| | `setup-power-agent` | 项目知识体系初始化 |
| | `dev-docs-maintain` | 文档维护（Doc Gardening） |

## 依赖方向

```
用户需求
    │
    ▼
discuss / 直接描述
    │
    ▼
writing-plans（规划）
    │
    ▼
docs/exec-plans/active/
    │
    ▼
plan-impl（实现编排）
    │
    ├── using-git-worktrees（隔离工作区）
    ├── plan-impl-lightweight（中小任务轻量执行路径）
    ├── proof-oriented-development（证明导向实现子代理）
    ├── 内部审查 prompt（规格符合性 + 代码质量）
    ├── verification-before-completion（Proof Block 审计与 verification_evidence）
    ├── requesting-code-review（合并前全量审查）
    └── finishing-a-development-branch（分支收尾）

requesting-code-review 在合并/PR 前默认强制执行，除非用户明确要求跳过；dev-docs-maintain 是按需手动文档维护入口，不属于 plan-impl 的固定主流程。
```

**硬规则：** 依赖只能从上层指向下层，禁止反向依赖。

## 产出物流转

| 产出物 | 生产者 | 消费者 | 位置 |
|--------|--------|--------|------|
| 需求结论 / Spec 文档 | `discuss` | `writing-plans` | 默认内联传递；按需 `docs/specs/YYYY-MM-DD-*.md` |
| Compact exec-plan（`plan.md + review-contract.md`，按需 `context.md/tasks.md`） | `writing-plans` | 人类默认审 `review-contract.md`；`plan-impl` 必读 `plan.md + review-contract.md`，并按需读取拆分材料 | `docs/exec-plans/active/` |
| 代码变更 | `plan-impl` 子代理 | runner 内部审查 prompt / `requesting-code-review`（合并前） | Git diff |
| Session Log | `plan-impl` | 归档 | `docs/exec-plans/completed/` |
| 分支处置结论 | `finishing-a-development-branch` | plan-impl / 用户 | 结构化输出 |
| Skill 压力场景 | `writing-skills` | Skill 作者 / reviewer | Skill 修改说明或 docs |

## 子代理模式

**核心原则：** 子代理是一次性的，主代理不与同一子代理进行多轮对话。

| 子代理类型 | 用途 | 调用者 |
|----------|------|--------|
| `explore` | 代码探索，返回关键文件列表 | discuss, dev-docs |
| `tech-plan-reviewer` | 需求结论 / 计划审查 | discuss, writing-plans |
| 实现子代理 | POD 增量实现 | plan-impl |
| 审查子代理 | 代码审查（风险分级 1-2 个并行） | plan-impl, requesting-code-review |
| 验证子代理 | 最终验证 | plan-impl |

**并发限制：** 最大并行度 3，超过则分批。

## Gate 机制

| Gate 位置 | 触发条件 | 动作 |
|-----------|---------|------|
| discuss Step 最终 | 需求结论完成 + 独立 reviewer 审查通过 | 等待用户批准（强制 Gate） |
| plan-impl 启动前 | 准备实现 | 轻量启动通知（非强制 Gate，worktree 沙盒隔离兜底）（DD-006） |
| plan-impl 执行中 | 3 轮修复失败，或计划前提假设失效 | Escalate 给用户 |
| finishing-a-development-branch | 丢弃路径（高风险操作） | 要求明确确认 |

## 设计原则

详见 [设计决策索引](arch-decisions/index.md)。核心原则概要：

1. **Skill 是执行单元，人类是决策者**（DD-001）
2. **产出物是协调介质** — 跨阶段状态通过文件传递，编排调用必须保留明确契约（DD-003）
3. **仓库是唯一真相来源** — Agent 看不到的内容不存在
4. **AGENTS.md 是目录，不是百科全书**（DD-004）
5. **机械化约束优于 Prompt 啰嗦** — 证据/测试 > 文字规则
6. **证据优先** — 没有新鲜验证不得声称完成
