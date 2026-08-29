---
type: Architecture
scope:
  - architecture
---

# 系统架构

Power-Agent 是面向前沿模型的 Constraint + Verification + Domain Knowledge pack，融合 superpowers 与 Harness Engineering。完整多阶段编排是 L2 升级能力，不是默认身份（[ADR-0009](adr/0009-lean-default-orchestration.md)）。

## 顶层架构

```mermaid
graph TB
    User[用户需求] --> D[需求分流]

    subgraph "规划层"
        D2[discuss 通用讨论]
        WP[writing-plans L2 计划]
        DD[dev-docs 长期知识维护]
        NATIVE[宿主原生任务清单]
    end

    subgraph "实现层"
        EP[implement L2 编排]
        POD[proof-oriented-development]
        DBG[systematic-debugging]
        WTG[working-tree gate]
        VBC[verification-before-completion]
    end

    subgraph "审查层"
        RCR[code-review 风险相称]
        HER[harness-engineering-review]
    end

    subgraph "基础设施层"
        WSK[writing-skills]
        FAB[finishing-a-development-branch]
        SPA[setup-power-agent]
        DDM[dev-docs-maintain]
    end

    D -->|根因未知| DBG
    D -->|需求未收敛| D2
    D -->|L0/L1 软件变更| POD
    D -->|L2 软件变更| WP
    D -->|长期项目知识| DD
    D -->|普通任务| NATIVE
    D2 -->|L0/L1 结论即做| POD
    D2 -->|L2 复杂工作| WP
    D2 -->|长期项目知识| DD
    D2 -->|普通工作| NATIVE
    WP --> EP

    EP --> POD
    EP -.->|L2/合并/高风险| RCR
    POD --> WTG
    POD -.->|升级审查| RCR
    POD -.->|L0 无合并意图且短证据自足| FAB
    RCR --> WTG
    EP -->|审查后| WTG
    WTG -->|clean && has_head| VBC
    WTG -->|dirty || !has_head| FAB
    VBC --> FAB
    User -.->|按需维护| DDM

    DBG -->|FIXABLE + granted + matching basis| POD
```

`systematic-debugging` 的 `missing | unknown | basis mismatch` 只保留 `FIXABLE` handoff 并请求最小授权，不进入 POD。

默认走 **L0/L1 → POD + 短证据**（完成声明仍须模型外新鲜证据；短证据豁免的是独立 VBC 编排，不豁免证据本身）。`writing-plans` 与 `implement` 构成 **L2** 软件资产变更链路。根因未知时 `systematic-debugging` 优先；长期项目知识由 `dev-docs` / `dev-docs-maintain` 维护；无专长匹配的普通任务不进入该链路。

## 模块划分

| 层级 | Skill | 职责 |
|------|-------|------|
| **规划层** | `discuss` | 通用讨论：任何需要想清楚再行动的问题（产品、架构、方案、营销等），行动前澄清与对齐；审查强度与决策权重相称，默认内联结论，按需落盘 spec/doc |
| | `writing-plans` | 为跨模块、多批次、跨会话或高风险的软件资产变更创建开发 compact exec-plan；所有开发计划 self-review，中/高风险增加独立 reviewer，`review-contract.md` 供人类按需审阅 |
| | `codebase-design` | 具体模块的结构深化判断：从消费者收窄接口、用删除测试评估深度，并以真实变化边界决定 seam / adapter；结论交给既有计划与 Proof |
| | `dev-docs` | 维护 `docs/` 中可长期复用的工程知识：稳定系统事实、边界、决策依据与集成参考；软件资产变更的实施、重构或迁移计划交给 `writing-plans` |
| **实现层** | `implement` | L2 开发计划的执行编排：准备（隔离工作区 + exec-plan Plan Review Gate）→ 批次调度与按需内审 → 风险相称审查 → working-tree gate → 验证 → 收尾；优先 team 模式，缺失 team 工具时回退并行或单实现子代理；实质 amendment 递增 revision 并重新进入风险审查 |
| | `proof-oriented-development` | 证明导向开发闭环：小步实现、最小相关验证、输出 Proof Block |
| | `systematic-debugging` | 探索式根因调查：可区分 feedback loop、因果证据、original/minimal repro、安全边界，以及与执行授权解耦的修复交接 |
| | `verification-before-completion` | 审计 Proof Block / 等价证据块、原始复现、临时产物和风险相称的性能/稳定性证据，输出 verification_evidence |
| **审查层** | `code-review` | 风险相称的全量审查编排（L2/合并/高风险或用户要求时）；修复验证、重要性分层与增强独立终审；评估内部与外部审查反馈 |
| | `harness-engineering-review` | Agent 工作流七维度审查 |
| **基础设施层** | `writing-skills` | Skill 创建、修改与契约审查 |
| | `finishing-a-development-branch` | dirty 工作区或无 HEAD 仓库的待提交提示，以及验证通过后的分支处置决策（merge/PR/保留/丢弃） |
| | `setup-power-agent` | 项目知识体系初始化 |
| | `dev-docs-maintain` | 按需检查既有 `docs/` OKF Bundle 健康状态，修复结构或知识漂移，并登记已完成验证到 verification ledger |

## 依赖方向

```
用户需求
    │
    ├─ L0/L1（默认）──────────────────────────────┐
    │                                            ▼
    │                              proof-oriented-development
    │                                → 短证据（写在回复/commit，非口头宣称）
    │                                →（升级）风险相称 code-review
    │                                → 有合并/对外宣称完成意图时：工作区检查 + VBC → 收尾
    │                                → 无合并意图且短证据自足时可收束（证据仍须外置）
    │
    └─ L2（跨模块/多会话/高风险）
            │
            ▼
        discuss / 直接描述（按需）
            │
            ▼
        writing-plans
            │
            ▼
        docs/exec-plans/active/
            │
            ▼
        implement（编排）
            │
            ├── proof-oriented-development
            ├── scratch artifacts（多 agent / 审查时）
            ├── 按需批次审查
            ├── code-review（风险相称；合并/高风险）
            ├── working-tree gate
            ├── verification-before-completion
            └── finishing-a-development-branch

L0/L1 不经 exec-plan Gate，不默认双重审查。L2/合并/高风险路径上 code-review 在完成验证前执行；用户明确跳过时记录原因。`dev-docs-maintain` 按需触发，不是固定主流程。
```

**硬规则：** 依赖只能从上层指向下层，禁止反向依赖。

## 产出物流转

| 产出物 | 生产者 | 消费者 | 位置 |
|--------|--------|--------|------|
| 讨论结论 / Spec 文档 | `discuss` | 建议去向：L0/L1 → POD 直做；L2 → `writing-plans` / `implement`；长期知识 → `dev-docs` / `dev-docs-maintain`；普通工作不建 exec-plan | 默认内联传递；按需 `docs/specs/YYYY-MM-DD-*.md` |
| Compact 开发 exec-plan（`plan.md + review-contract.md`，按需 `context.md/tasks.md`） | `writing-plans` | 人类默认审 `review-contract.md`；`implement` 必读两份材料并在准备阶段校验 Gate，按需读取拆分材料 | `docs/exec-plans/active/`（仅 L2） |
| Scratch review artifacts | `implement` / 实现子代理 | 单内部 reviewer（启用时）/ 显式接收 manifest 的最终 reviewer | `.power-agent/review-runs/<run-id>/`（自忽略、per-run、可重建；多 agent 或 L2 审查时） |
| 代码变更 | 实现路径（POD / `implement` 子代理） | 启用时的内部 reviewer / `code-review`（L2、合并/高风险时） | Git working-tree diff |
| Session Log | `implement` | 归档（L2 执行） | `docs/exec-plans/completed/` |
| 分支处置结论 | `finishing-a-development-branch` | implement / 用户 | 结构化输出 |

## 子代理模式

**核心原则：** 实现/修复子代理与跨目标调用保持一次性；reviewer 仅可在同一实现目标和同一 review session 内优先验证自己的 findings。运行时不能继续原 reviewer 时，使用携带完整修复上下文的新 reviewer。详见 [ADR-0007](adr/0007-reviewer-session-continuity.md)。

| 子代理类型 | 用途 | 调用者 |
|----------|------|--------|
| `explore` | 代码探索，返回关键文件列表 | discuss, dev-docs |
| `tech-plan-reviewer` | 讨论结论审查；中/高风险计划审查 | discuss, writing-plans |
| 实现/修复子代理 | POD 增量实现与修复；每轮使用新子代理 | implement |
| 审查子代理 | 单 reviewer 多维主审；同 session 修复验证；增强审查使用全新 reviewer 独立终审 | implement, code-review |
| 验证子代理 | 最终验证 | implement |

**并发：** 控制 mutation boundary；默认并发上限 3，超过则分批；并行探索可以，写冲突要收敛。

## Gate 机制

| Gate 位置 | 触发条件 | 动作 |
|-----------|---------|------|
| discuss 最终审查 | 讨论结论完成 + 审查强度与决策权重相称（实质行动/不可逆决策派独立 reviewer） | 建议去向：直接实施 / `writing-plans` / `dev-docs` |
| writing-plans 风险审查 | 开发 exec-plan 的 low=self-review；medium/high=独立 reviewer 通过 | 交给 `implement` |
| implement 准备 | 首次执行或恢复执行前 | 只校验 `review-contract.md` 的 Gate；medium/high 未 approved、缺失或非法时不得执行 |
| implement 执行中 | 3 轮修复失败，或计划前提假设失效 | Escalate 给用户 |
| finishing-a-development-branch | 丢弃路径（破坏性操作） | 要求明确确认 |

## 设计原则

详见 [ADR 目录](adr/)。核心原则概要（默认解读以 [ADR-0009](adr/0009-lean-default-orchestration.md) 为准）：

1. **约束与验证优先，编排按需** — 产品是 Constraint + Verification + Domain Knowledge pack；完整 `plan → implement → 多审 → VBC` 是 L2，不是默认身份（ADR-0009）
2. **Skill 是执行单元；人类保留意图与不可逆决策**（ADR-0001）
3. **产出物按需协调** — 跨会话/高风险/人审才落 durable artifact；同会话 L0/L1 以代码与短证据交接（ADR-0003 经 0009 限定）
4. **仓库是工程 canonical store** — 不变量与决策 versioned 可达；外部权威源须 machine-legible，不靠聊天记忆冒充规范
5. **AGENTS.md 是目录，不是百科全书**（ADR-0004）
6. **机械化约束优于 Prompt 啰嗦** — 证据/测试/hook > 文字规则；给约束不给剧本
7. **证据优先且外置于模型** — 没有新鲜验证不得声称完成；短 Proof 默认，长 Proof 条件触发
8. **上下文 pull-based** — 大块经按需引用加载；scratch review artifacts 仅多 agent / L2 审查启用
9. **启用审查时：实现/修复一次性，Reviewer 同会话连续**（ADR-0007）— 不强制 L0 启用审查
10. **契约优先，层级最小** — 先满足当前契约与 Proof，再选 L0→L1→L2 上最早充分层级；长期所有权由当前证据购买（ADR-0008）
11. **Harness ablation** — 模型/宿主升级后先删不再承重的默认组件，再加编排
