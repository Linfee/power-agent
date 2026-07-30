---
type: Execution Plan
scope:
  - <affected-scope>
status: active
runner:
  state: READY
  batch: 0/0
  phase: ready
  fix_round: 0/0
  next_action: start
---

# [主题] 实现计划

> 默认持久化计划包为 `plan.md + review-contract.md`。`plan.md` 是单一事实源；只有在证据采集成本高、任务图复杂、多 Agent 协作、上下文过大或可读性明显受损时，才拆出 `context.md` / `tasks.md`。

## 讨论结论 / 产品结论（如有）

- [若当前会话已经形成产品、需求或取舍结论，写在这里；无则写 none]

## Goal / Done Means

- 目标：[一句话说明本次交付结果]
- Done Means：[完成时可观察到什么；不要只写“已实现 / 已添加 / 已支持”]
- 不做事项：[本次明确不追求什么；若无写 none]

## Scope

### In Scope
- [本次明确包含]

### Out of Scope
- [本次明确不包含]

## Key Decisions

- 决策：[结论]
  - 原因：[为什么这样定]
  - 证据：[路径:行号 / 文档位置 / 会话中已确认结论]
  - 执行含义：[它如何约束实现、范围或 proof]
- 决策：[结论]
  - 原因：[为什么这样定]
  - 证据：[路径:行号 / 文档位置 / 会话中已确认结论]
  - 执行含义：[它如何约束实现、范围或 proof]

## Agent 自主边界

- 可自由决策：[执行 Agent 可以自己决定什么]
- 不可自行决策：[哪些范围、协议、关键 UX、权限、发布/迁移或风险等级不能擅自改变]
- 必须保持的不变量：[执行期间必须始终成立的契约]
- 触发升级条件：[遇到什么情况必须 BLOCKED 并请求用户 / 人类确认]

## Plan Review Gate

- Gate Revision：r1；每次 material amendment 递增。
- Plan Risk：low / medium / high
- Review Path：self-review / self-review + independent reviewer
- Plan Review Status：SELF_REVIEWED / PENDING_INDEPENDENT_REVIEW / APPROVED / ISSUES_FOUND
- Independent Review：not_required / pending / approved / issues_found
- Independent Review Basis：[not_required 时写 not_required；pending 时写 pending；approved / issues_found 时写 `gate_revision=rN; kind=independent-review; record=<稳定位置>`]

## Evidence Cache（仅记录非显然事实）

- [事实]；证据：[路径:行号 或文档位置]；影响：[它如何约束范围、设计或 proof]
- [事实]；证据：[路径:行号 或文档位置]；影响：[它如何约束范围、设计或 proof]
- 不要把仓库常识、顺手可读到的显然上下文或大段代码摘录堆在这里。

## Tasks

- T1 [任务名]：[目标 + 主要触点 + 完成信号]
- T2 [任务名]：[目标 + 主要触点 + 完成信号]
- 只保留足以指导执行和判断串并行/交接的信息；不要展开成机械微步骤。
- 若任务图复杂、需要多 Agent 协作或需要独立交接，再拆出 `tasks.md` 并在此引用。

## Proof Strategy

- 主证明：[behavior_or_characterization / targeted_command / structure_or_diff / strict_tdd（仅用户明确要求）]；涉及测试时先点名接缝（在哪一层观察行为）
- 次证明：[补充证据；若无写 none]
- 非证明：[不能单独作为完成证明的检查；若无写 none]
- 已知未验证面：[允许不覆盖的范围及原因；若无写 none]
- 失败解释：[主证明失败意味着什么，应退回检查哪里]

## Blockers / Escalation

- 阻塞条件：[必须停止并请求确认的情况]
- 升级对象：[用户 / 指定人类审阅者 / 上一级 planning 流程]
- 升级时携带材料：[最小必要证据、关键 diff、失败信号或待确认决策]

## Risks / Rollback

- 风险：[高风险点或越权风险；若无写 none]
  - 失败信号：[什么现象说明方向错了]
  - 缓解方式：[如何降低风险]
  - 回滚方式：[失败时回到什么状态]

## Optional Split Files（如有）

- `context.md`：[仅当需要沉淀高成本证据、大量非显然事实或长上下文时使用]
- `tasks.md`：[仅当需要复杂任务图、多 Agent 分工或独立交接时使用]
- 若拆分，`plan.md` 仍是单一事实源；外部文件只做补充，不得与本文件冲突。

## 当前状态

- 当前进度：[待开始 / 进行中 / 已完成]
- 下一步：[从哪个任务或 proof 开始]
