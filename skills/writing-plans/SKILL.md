---
name: writing-plans
description: |-
  执行计划编写 Skill。把需求、讨论结论或规格文档转成可执行 exec-plan；用户要求创建实现计划或任务拆解时触发。
  Triggers: 创建 exec-plan, 创建实现计划, writing-plans, 任务拆解, 实现计划.
---

# Writing Plans

把需求、讨论结论或规格文档转成可执行 exec-plan。计划应给强执行 Agent 清楚的目标、边界、关键决策与证明方式，避免把实现写成机械脚本。

---

## 目标

- 默认产出紧凑计划包：`plan.md` + `review-contract.md`。
- 将用户需求、已批准 `discuss` 结论或 spec 折叠进 `plan.md`，使它成为执行前唯一持久真源。
- 补齐实现级架构、API/模型、任务边界、验收标准、Proof Strategy、Agent 自主边界、风险与阻塞条件。
- 只在证据昂贵、任务图复杂、多 Agent 协作、上下文过大或可读性明显受损时，拆出可选 `context.md` / `tasks.md`。
- 通过独立 `tech-plan-reviewer` 审查计划质量；不要用 inline self-review 替代 sub-agent review loop。

## 何时使用 / 何时跳过

使用：

- 用户要求创建实现计划、exec-plan、任务拆解或实施计划。
- 已有 `discuss` / spec，需要转为可执行但不过度脚本化的实现计划。
- 需求跨模块、存在技术决策、验收或证明策略需要提前锁定。

跳过并说明去向：

- 单文件小改、拼写/文案/格式调整。
- 明确且局部的 bugfix，且无跨模块设计决策。
- 已有完整、可直接执行的任务清单且无新技术决策。

命中跳过条件时，建议直接实现；若需求仍不清晰，回到 `discuss`。

## 边界

- `discuss` 的上层技术方向是范围、验收与 planning 约束，不是完整实现设计。
- `writing-plans` 负责用仓库证据补齐实现级架构/API/模型/任务边界；不要把可由代码证据闭合的技术细节退回 `discuss`。
- 执行交给 `plan-impl`；本 skill 不直接修改业务代码。
- 不默认 strict TDD；只有用户明确要求 TDD / 先写失败测试 / Red-Green-Refactor 时，才把 strict TDD 写入 Proof Strategy。
- 不写逐行改动、机械步骤、私有 helper 设计、局部命名决策或每步几分钟的执行脚本。
- 不为简单任务强行 planning，不新增默认计划文档，不删除 `review-contract.md` 人审入口。

## 输入

最小输入：

1. 用户当轮需求与约束，或当前会话已批准的 `discuss` 结论。
2. 用户指定的 spec、issue、计划或设计文档。
3. 与目标直接相关的架构决策、模块文档与代码证据。

上下文获取按缺口升级：先定点读取，再按需启动 `explore` 子代理；只有复杂度或涉及范围超出当前证据时才升级。禁止无明确缺口的全仓探索。

## 输出

计划目录：`docs/exec-plans/active/YYYY-MM-DD-title/`

默认持久产物：

- `plan.md`：执行真源，承载需求结论、Goal / Done Means、Scope、Key Decisions、Agent 自主边界、Evidence Cache、Tasks、Proof Strategy、Blockers / Escalation、Risks / Rollback。
- `review-contract.md`：人类默认批准入口；短小、独立、可判定，覆盖 Intent、In / Out、Acceptance、Agent 自主边界、Proof、Blockers、Risks。

可选拆分产物：

- `context.md`：仅作高成本证据缓存，不是上下文百科。
- `tasks.md`：仅展开复杂任务图、多 Agent 分工或交接信息，不是执行脚本。

模板位置：

- `skills/writing-plans/references/plan-template.md`
- `skills/writing-plans/references/review-contract-template.md`
- `skills/writing-plans/references/context-template.md`
- `skills/writing-plans/references/tasks-template.md`
- `skills/writing-plans/references/plan-reviewer-prompt.md`

若模板缺失，按上述文档契约生成最小合格版本。`plan.md` 仍是单一事实源；可选文件不得新增方向或与 `plan.md` 冲突。

## 流程

### Step 0: 准入与充分性检查

1. 判断是否应进入 planning；命中跳过条件则退出并给出去向。
2. 判断是否需要拆为多个 plan。独立子系统多、候选任务过多、依赖链深、关键未决策项多，或调查升至复杂级别仍难收敛时，先做母 plan / 子 plan / 集成验收 plan 的边界设计。
3. 确认业务目标、范围边界、完成定义、非功能约束是否足够。缺口会改变用户目标、范围、验收或上层方案时，先升级到用户或 `discuss`；实现级缺口由本 skill 基于证据补齐。
4. 只补当前计划需要的证据，并记录上下文充分性结论。

### Step 1: 生成计划包

创建 `plan.md` 与 `review-contract.md`。只有在 `plan.md` 承载不足时才拆出 `context.md` / `tasks.md`，并在 `plan.md` 写明拆出理由。

计划必须锁定：目标、In / Out Scope、关键技术决策、Agent 自主边界、任务图、Proof Strategy、阻塞/升级条件、风险/回滚。

### Step 2: 审查循环

默认使用 `skills/writing-plans/references/plan-reviewer-prompt.md` dispatch `tech-plan-reviewer` 子代理审查；平台没有专用角色时，使用通用子代理并粘贴该 prompt。

保留 sub-agent review loop：reviewer 只审查计划是否足够让下游执行，不重写实现方案。

审查结果为：`status`、`evidence`、`blocking_issues`、`missing_evidence`、`advisories`、`next_action`。

- `APPROVED`：进入交棒。
- `ISSUES_FOUND`：主代理补证据、边界、依赖或验收，再发起下一轮审查。
- 同类 blocking issue 连续出现且无收敛时，才向用户升级；升级前应已完成至少一轮 reviewer 审查并尝试补证据。

### Step 3: 交棒

最终回复至少包含：

- `Plan Path`
- `Review Contract Path`
- `Optional Split Docs`：无则写 `none`
- `Human Review Request`：默认只审 `review-contract.md`
- `Scope Summary`
- `Key Technical Decisions`
- `Task Graph Summary`
- `Open Risks`
- `Next Step`：通常为 `plan-impl [plan-path]`

禁止只给“已生成计划，请查看”。禁止要求人类逐行审完整执行材料，除非用户明确要求完整审查。

## 质量门槛

- 验收标准必须可观察、可验证、可判定；不要只写“已实现 / 已添加 / 已支持”。
- Key Decisions 必须有证据、理由与执行含义；未经确认的假设不得写成既定事实。
- Agent 自主边界必须包含：可自由决策、不可自行决策、必须保持的不变量、触发升级条件。
- Proof Strategy 必须区分主证明、次证明、non-proof、已知未验证面和失败解释；lint、typecheck、格式化、构建成功或宽泛文本搜索不能单独作为完成证明。
- 任务是可独立验证的行为增量或结构增量；不要跨越多个无强依赖子系统，也不要细到逐行改动或私有 helper。
- 高风险且不可逆、权限/安全/隐私/并发语义、公共 API、数据模型、迁移、发布或关键 UX 决策，必须在计划阶段闭合或写入阻塞/升级条件。
- 最终计划不得残留 `TBD`、`TODO`、`待补充`、`稍后实现`、未定义术语、未定义文件/命令，或“添加适当错误处理 / 写相关测试”这类泛化占位。
- 人类默认只审 `review-contract.md` 中的 Intent、范围边界、Acceptance、Proof、Agent 自主边界、Blockers 和 Risks；不要要求人类逐行审技术方案、任务拆解或文件路径枚举。

## 交棒

交给 `plan-impl` 的材料必须让执行 Agent 明确：要达成什么、边界在哪、哪些可自主发挥、如何证明完成、何时停止。`plan.md` 是执行材料；`review-contract.md` 是人审入口；`context.md / tasks.md` 只在必要时作为辅助材料。