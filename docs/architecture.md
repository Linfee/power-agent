---
type: Architecture
scope:
  - architecture
---

# 系统架构

Power-Agent 是一个 AI 编码 Agent 工作流插件系统，融合了 superpowers 和 Harness Engineering 两套方法论。

## 顶层架构

```mermaid
graph TB
    User[用户需求] --> D[需求分流]

    subgraph "规划层"
        D2[discuss 通用讨论]
        WP[writing-plans 开发计划创建]
        DD[dev-docs 长期知识维护]
        NATIVE[宿主原生任务清单]
    end

    subgraph "实现层"
        EP[implement 开发实施]
        POD[proof-oriented-development]
        DBG[systematic-debugging]
        WTG[working-tree gate]
        VBC[verification-before-completion]
    end

    subgraph "审查层"
        RCR[code-review]
        HER[harness-engineering-review]
    end

    subgraph "基础设施层"
        WSK[writing-skills]
        FAB[finishing-a-development-branch]
        SPA[setup-power-agent]
        DDM[dev-docs-maintain]
    end

    D -->|根因未知| DBG
    D -->|需求、范围或验收未收敛| D2
    D -->|软件资产变更| WP
    D -->|长期项目知识| DD
    D -->|普通任务| NATIVE
    D2 -->|复杂工作| WP
    D2 -->|结论即计划| EP
    D2 -->|长期项目知识| DD
    D2 -->|普通工作| NATIVE
    WP --> EP

    EP --> POD
    EP -.->|合并前强制审查| RCR
    POD --> RCR
    EP -->|审查通过后| WTG
    WTG -->|clean && has_head| VBC
    WTG -->|dirty || !has_head 待提交| FAB
    VBC --> FAB
    User -.->|按需维护| DDM

    DBG -->|FIXABLE + granted + matching basis| POD
```

`systematic-debugging` 的 `missing | unknown | basis mismatch` 只保留 `FIXABLE` handoff 并请求最小授权，不进入 POD。

`writing-plans` 与 `implement` 只构成软件资产变更的开发链路。根因未知时 `systematic-debugging` 优先；长期项目知识由 `dev-docs` / `dev-docs-maintain` 维护；无专长匹配的普通任务不进入该链路。

## 模块划分

| 层级 | Skill | 职责 |
|------|-------|------|
| **规划层** | `discuss` | 通用讨论：任何需要想清楚再行动的问题（产品、架构、方案、营销等），行动前澄清与对齐；审查强度与决策权重相称，默认内联结论，按需落盘 spec/doc |
| | `writing-plans` | 为跨模块、多批次、跨会话或高风险的软件资产变更创建开发 compact exec-plan；所有开发计划 self-review，中/高风险增加独立 reviewer，`review-contract.md` 供人类按需审阅 |
| | `dev-docs` | 维护 `docs/` 中可长期复用的工程知识：稳定系统事实、边界、决策依据与集成参考；软件资产变更的实施、重构或迁移计划交给 `writing-plans` |
| **实现层** | `implement` | 任何开发计划的执行编排：准备（隔离工作区 + exec-plan Plan Review Gate）→ 批次调度与单 reviewer 双 verdict 内审 → 全量审查 → working-tree gate → 验证 → 收尾；优先 team 模式，缺失 team 工具时回退并行或单实现子代理；实质 amendment 递增 revision 并重新进入风险审查 |
| | `proof-oriented-development` | 证明导向开发闭环：小步实现、最小相关验证、输出 Proof Block |
| | `systematic-debugging` | 探索式根因调查：可区分 feedback loop、因果证据、original/minimal repro、安全边界，以及与执行授权解耦的修复交接 |
| | `verification-before-completion` | 审计 Proof Block / 等价证据块、原始复现、临时产物和风险相称的性能/稳定性证据，输出 verification_evidence |
| **审查层** | `code-review` | 单主审多维审查、修复验证、重要性/实现风险分层与增强独立终审编排；评估内部与外部审查反馈 |
| | `harness-engineering-review` | Agent 工作流七维度审查 |
| **基础设施层** | `writing-skills` | Skill 创建、修改、契约审查与压力场景验证 |
| | `finishing-a-development-branch` | dirty 工作区或无 HEAD 仓库的待提交提示，以及验证通过后的分支处置决策（merge/PR/保留/丢弃） |
| | `setup-power-agent` | 项目知识体系初始化 |
| | `dev-docs-maintain` | 按需检查既有 `docs/` OKF Bundle 健康状态，修复结构或知识漂移，并登记已完成验证到 verification ledger |

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
implement（实现编排）
    │
    ├── proof-oriented-development（证明导向实现子代理）
    ├── scratch review artifacts（task brief / report / review package / optional review-assets manifest）
    ├── 单内部 reviewer（规格符合性 + 代码质量双 verdict；只读当前 manifest 命名资产）
    ├── code-review（主审 → 修复验证 → 按强度进入独立终审；无 manifest 不扫描 `.power-agent`）
    ├── working-tree gate（dirty / 无 HEAD 先提示提交；clean 且有 HEAD 进入最终验证）
    ├── verification-before-completion（Proof Block 审计与 verification_evidence）
    └── finishing-a-development-branch（分支收尾）

code-review 在最终验证前默认强制执行；合并/PR 前不得跳过未通过的审查结果，除非用户明确要求跳过。`dev-docs-maintain` 是按需触发的既有 `docs/` Bundle 健康检查、漂移修复和 verification ledger 登记入口，不属于 implement 的固定主流程。
```

**硬规则：** 依赖只能从上层指向下层，禁止反向依赖。

## 产出物流转

| 产出物 | 生产者 | 消费者 | 位置 |
|--------|--------|--------|------|
| 讨论结论 / Spec 文档 | `discuss` | 建议去向：结论即计划 → `implement`；复杂工作 → `writing-plans`；长期知识 → `dev-docs` / `dev-docs-maintain`；普通工作不建 exec-plan | 默认内联传递；按需 `docs/specs/YYYY-MM-DD-*.md` |
| Compact 开发 exec-plan（`plan.md + review-contract.md`，按需 `context.md/tasks.md`） | `writing-plans` | 人类默认审 `review-contract.md`；`implement` 必读两份材料并在准备阶段校验 Gate，按需读取拆分材料 | `docs/exec-plans/active/` |
| Scratch review artifacts | `implement` / 实现子代理 | 单内部 reviewer / 显式接收 manifest 的最终 reviewer | `.power-agent/review-runs/<run-id>/`（自忽略、per-run、可重建；资产只通过 `review-assets.md` 命名） |
| 代码变更 | `implement` 子代理 | 单内部 reviewer / `code-review`（最终验证前） | Git working-tree diff |
| Session Log | `implement` | 归档 | `docs/exec-plans/completed/` |
| 分支处置结论 | `finishing-a-development-branch` | implement / 用户 | 结构化输出 |
| Skill 压力场景 | `writing-skills` | Skill 作者 / reviewer | Skill 修改说明或 docs |

## 子代理模式

**核心原则：** 实现/修复子代理与跨目标调用保持一次性；reviewer 仅可在同一实现目标和同一 review session 内优先验证自己的 findings。运行时不能继续原 reviewer 时，使用携带完整修复上下文的新 reviewer。详见 [ADR-0007](adr/0007-reviewer-session-continuity.md)。

| 子代理类型 | 用途 | 调用者 |
|----------|------|--------|
| `explore` | 代码探索，返回关键文件列表 | discuss, dev-docs |
| `tech-plan-reviewer` | 讨论结论审查；中/高风险计划审查 | discuss, writing-plans |
| 实现/修复子代理 | POD 增量实现与修复；每轮使用新子代理 | implement |
| 审查子代理 | 单 reviewer 多维主审；同 session 修复验证；增强审查使用全新 reviewer 独立终审 | implement, code-review |
| 验证子代理 | 最终验证 | implement |

**并发限制：** 最大并行度 3，超过则分批。

## Gate 机制

| Gate 位置 | 触发条件 | 动作 |
|-----------|---------|------|
| discuss 最终审查 | 讨论结论完成 + 审查强度与决策权重相称（实质行动/不可逆决策派独立 reviewer） | 建议去向：直接实施 / `writing-plans` / `dev-docs` |
| writing-plans 风险审查 | 开发 exec-plan 的 low=self-review；medium/high=独立 reviewer 通过 | 交给 `implement` |
| implement 准备 | 首次执行或恢复执行前 | 校验两份计划材料同名的 Gate Revision、风险状态和 revision-bound basis；medium/high pending、缺失、冲突或 basis 不匹配时不得执行 |
| implement 执行中 | 3 轮修复失败，或计划前提假设失效 | Escalate 给用户 |
| finishing-a-development-branch | 丢弃路径（破坏性操作） | 要求明确确认 |

## 设计原则

详见 [ADR 目录](adr/)。核心原则概要：

1. **Skill 是执行单元，人类是决策者**（ADR-0001）
2. **产出物是协调介质** — 跨阶段状态通过文件传递，编排调用必须保留明确契约（ADR-0003）
3. **仓库是唯一真相来源** — Agent 看不到的内容不存在
4. **AGENTS.md 是目录，不是百科全书**（ADR-0004）
5. **机械化约束优于 Prompt 啰嗦** — 证据/测试 > 文字规则
6. **证据优先** — 没有新鲜验证不得声称完成
7. **上下文按需交接** — 大段任务、报告和 diff 通过 scratch artifacts 传递；review assets 按 run 隔离，只通过显式 manifest 交接，无 manifest 不扫描
8. **实现/修复一次性，Reviewer 同会话连续** — reviewer 只在同一目标内验证自己的 findings，不能继续时回退新 reviewer（ADR-0007）
