---
name: writing-plans
description: |-
  开发执行计划编写 Skill。把将修改软件资产的需求、讨论结论或规格文档转成可执行 exec-plan；用户要求创建开发实施计划、开发 exec-plan 或工程任务拆解时触发。
  Triggers: 创建开发 exec-plan, 创建开发实施计划, 开发任务拆解, writing-plans.
---

# Writing Plans

把会修改软件资产的需求、讨论结论或规格文档转成可执行 exec-plan。计划应给强执行 Agent 清楚的目标、边界、关键决策与证明方式，避免把实现写成机械脚本。

---

## 目标

- 默认产出紧凑计划包：`plan.md` + `review-contract.md`。
- 将用户需求、经独立审查通过的 `discuss` 结论或 spec 折叠进 `plan.md`，使它成为执行前唯一持久真源。
- 补齐实现级架构、API/模型、任务边界、验收标准、Proof Strategy、Agent 自主边界、风险与阻塞条件。
- 只在证据昂贵、任务图复杂、多 Agent 协作、上下文过大或可读性明显受损时，拆出可选 `context.md` / `tasks.md`。
- 所有计划先做 inline self-review，再按风险决定是否增加独立 `tech-plan-reviewer`。

## 适用范围与路由

### 使用

仅在后续工作会修改代码、测试、构建或运行配置、自动化、Skill/prompt 或开发工作流等软件资产时使用：

- 用户要求创建开发实施计划或开发 exec-plan。
- 已有 `discuss` / spec，需要为软件实现、重构、bugfix 或工程迁移形成可执行计划。
- 开发需求跨模块，或技术决策、验收、证明策略需要在实施前锁定。

“计划”“待办”或“任务拆解”本身不是触发条件；先按当前主要交付物选择入口：

| 当前主要交付物 | 去向 |
|---|---|
| 根因未知的错误、测试失败、性能退化或异常行为 | `systematic-debugging`；确认可执行修复边界后再进入开发实施。 |
| 项目 `docs/` 的长期系统知识、ADR、Playbook 或 reference | `dev-docs`；Bundle 健康、漂移或验证登记用 `dev-docs-maintain`。 |
| 面向读者的 RFC、proposal、spec 或其他实质文档成稿 | `doc-coauthoring`；范围、流程或验收未定时先用 `discuss`。 |
| 研究、运营、个人事务、信息整理或其他普通工作 | 宿主原生任务清单或直接推进，不创建 `docs/exec-plans`。 |

若开发变更附带文档更新，开发变更仍是主入口；实现验证后再按需交给 `dev-docs`。`discuss` 只有在结论将导向软件实施时才交给本 Skill。

### 开发路径中的跳过条件

- 单文件小改、拼写/文案/格式调整。
- 明确且局部的 bugfix，且无跨模块设计决策。
- 已有完整、可直接执行的开发任务清单且无新技术决策。

命中跳过条件时，直接实施；若开发需求仍不清晰，回到 `discuss`。

## 边界

- `discuss` 的上层技术方向是范围、验收与 planning 约束，不是完整实现设计。
- `writing-plans` 负责用仓库证据补齐开发实现级架构/API/模型/任务边界；不要把可由代码证据闭合的技术细节退回 `discuss`。
- 执行交给 `plan-impl`；本 Skill 不直接修改业务代码。
- 不默认 strict TDD；只有用户明确要求 TDD / 先写失败测试 / Red-Green-Refactor 时，才把 strict TDD 写入 Proof Strategy。
- 不写逐行改动、机械步骤、私有 helper 设计、局部命名决策或每步几分钟的执行脚本。
- 不为简单开发任务强行 planning，不新增默认计划文档，不删除 `review-contract.md` 人审入口。

## 输入

最小输入：

1. 用户当轮需求与约束，或当前会话经独立审查通过的 `discuss` 结论。
2. 用户指定的 spec、issue、计划或设计文档。
3. 与目标直接相关的架构决策、模块文档与代码证据。

上下文获取按缺口升级：先定点读取，再按需启动 `explore` 子代理；只有复杂度或涉及范围超出当前证据时才升级。禁止无明确缺口的全仓探索。

## 输出

计划目录：`docs/exec-plans/active/YYYY-MM-DD-title/`

默认持久产物：

- `plan.md`：执行真源，承载需求结论、Goal / Done Means、Scope、Key Decisions、Agent 自主边界、Plan Review Gate、Evidence Cache、Tasks、Proof Strategy、Blockers / Escalation、Risks / Rollback。
- `review-contract.md`：人类按需审阅入口；短小、独立、可判定，覆盖 Intent、In / Out、Acceptance、Agent 自主边界、Proof、Blockers、Risks。
- `plan.md`、`review-contract.md` 与存在的 `context.md` / `tasks.md` 都是 `docs/` Concept，必须以合法 YAML frontmatter 开始并具有非空 `type`；分别使用 `Execution Plan`、`Review Contract`、`Evidence Cache`、`Task Graph`。`scope` 只记录实际覆盖范围，验证运行状态由 `docs/.okf/verification.json` ledger 表示，不写 HTML header 或历史验证日期。执行中的 `plan.md` 仅通过 frontmatter 的 `runner` mapping 保存可恢复 runner state，不使用 HTML 注释。

可选拆分产物：

- `context.md`：仅作高成本证据缓存，不是上下文百科。
- `tasks.md`：仅展开复杂任务图、多 Agent 分工或交接信息，不是执行脚本。

模板位置：

- `skills/writing-plans/references/plan-template.md`
- `skills/writing-plans/references/review-contract-template.md`
- `skills/writing-plans/references/context-template.md`
- `skills/writing-plans/references/tasks-template.md`
- `skills/writing-plans/references/plan-reviewer-prompt.md`
- `skills/writing-plans/references/risk-review-stress-scenarios.md`

若模板缺失，按上述文档契约生成最小合格版本。`plan.md` 仍是单一事实源；可选文件不得新增方向或与 `plan.md` 冲突。

## 流程

### Step 0: 准入与充分性检查

1. 判断是否应进入 planning；命中跳过条件则退出并给出去向。
2. 判断是否需要拆为多个 plan。独立子系统多、候选任务过多、依赖链深、关键未决策项多，或调查升至复杂级别仍难收敛时，先做母 plan / 子 plan / 集成验收 plan 的边界设计。
3. 确认业务目标、范围边界、完成定义、非功能约束是否足够。缺口会改变用户目标、范围、验收或上层方案时，先升级到用户或 `discuss`；实现级缺口由本 skill 基于证据补齐。
4. 只补当前计划需要的证据，并记录上下文充分性结论。
5. 按最高命中项确定 `plan_risk`：
   - `low`：单模块、可逆、无公共契约/数据/权限/并发变化，targeted proof 足以判定完成。
   - `medium`：跨模块或存在非平凡接口/兼容性决策，但可安全回滚，不触及下列高风险边界。
   - `high`：破坏性或难回滚操作、公共 API 破坏、身份/权限/隐私/支付、安全、Schema/迁移、数据一致性、并发语义、生产发布或关键 UX 决策。
   - 无法根据现有证据判断风险时，不得默认为低风险；先补证据，仍不清楚则按 `high` 处理。

### Step 1: 生成计划包

创建 `plan.md` 与 `review-contract.md`，并从模板保留各自的 YAML frontmatter。只有在 `plan.md` 承载不足时才拆出 `context.md` / `tasks.md`，并在 `plan.md` 写明拆出理由；拆出文件也必须保留相应的 YAML `type`。

计划必须锁定：目标、In / Out Scope、关键技术决策、Agent 自主边界、任务图、Proof Strategy、阻塞/升级条件、风险/回滚。
`plan.md` 与 `review-contract.md` 必须以同名字段记录并一致表达 `Gate Revision`、`Plan Risk`、`Review Path`、`Plan Review Status`、`Independent Review` 与 `Independent Review Basis`。Independent Review 的 approved/issues_found basis 必须绑定当前 revision 的稳定 history。material amendment 必须递增 Gate Revision、保留旧 history 并重新进入相应 Gate。

### Step 2: Self-Review 与风险驱动 Gate

所有风险等级先执行 inline self-review：

1. **需求覆盖**：Goal、Scope、Acceptance 和每个已确认要求是否都有对应 task/proof。
2. **占位符扫描**：不得残留质量门槛中列出的模糊词、未定义字段或未来补充项。
3. **一致性**：Key Decisions、任务依赖、接口名、Agent 边界、Proof 和 rollback 是否互相冲突。
4. **任务边界**：每个任务是否值得独立验证和审查；setup/config/docs 是否已并入真正需要它们的任务。
5. **风险校准**：`plan_risk` 是否漏掉公共契约、数据、权限、安全、并发、迁移、发布或不可逆影响。

发现问题直接修订并重新运行 self-review。self-review 不能把未知事实改写成已确认结论。

随后按风险进入 Gate：

- `low`：self-review 通过即可交棒，不派发独立 plan reviewer。
- `medium`：self-review 后使用 `skills/writing-plans/references/plan-reviewer-prompt.md` 派发一个独立 `tech-plan-reviewer`；平台没有专用角色时使用通用 reviewer。
- `high`：先执行 `medium` 的独立审查；reviewer 通过后直接交棒。

独立 reviewer 只审查计划是否足够让下游执行，不重写实现方案。结果为：`status`、`evidence`、`blocking_issues`、`missing_evidence`、`advisories`、`next_action`。

- `APPROVED`：中/高风险进入交棒。
- `ISSUES_FOUND`：主代理补证据、边界、依赖或验收，再重新 self-review 和独立审查。
- 同类 blocking issue 连续出现且无收敛时向用户升级；最多 3 轮，不用更多 reviewer 掩盖计划缺口。
- 高风险用户要求修改时，修订后重新 self-review 和独立审查。

状态映射：

- `low` self-review 通过：`plan_review_status=SELF_REVIEWED`。
- `medium|high` self-review 通过但独立 reviewer 尚未返回：`plan_review_status=PENDING_INDEPENDENT_REVIEW`。
- `medium` reviewer 通过：`plan_review_status=APPROVED`。
- `medium|high` reviewer 发现问题：`plan_review_status=ISSUES_FOUND`。
- `high` reviewer 通过：`plan_review_status=APPROVED`。

### Step 3: 交棒

最终回复至少包含：

- `Plan Path`
- `Review Contract Path`
- `Plan Risk`：`low / medium / high` 与命中理由
- `Review Path`：`self-review / self-review + independent reviewer`
- `Plan Review Status`：`SELF_REVIEWED / PENDING_INDEPENDENT_REVIEW / APPROVED / ISSUES_FOUND`
- `Optional Split Docs`：无则写 `none`
- `Review Contract`：供人类按需阅读，不构成执行 Gate
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
- `plan_risk` 必须有证据和命中理由；风险未知不能降级为 `low`。
- 最终计划不得残留 `TBD`、`TODO`、`待补充`、`稍后实现`、未定义术语、未定义文件/命令，或“添加适当错误处理 / 写相关测试”这类泛化占位。
- 人类默认只审 `review-contract.md` 中的 Intent、范围边界、Acceptance、Proof、Agent 自主边界、Blockers 和 Risks；不要要求人类逐行审技术方案、任务拆解或文件路径枚举。

## 交棒

交给 `plan-impl` 的材料必须让执行 Agent 明确：要达成什么、边界在哪、哪些可自主发挥、如何证明完成、何时停止。`plan.md` 是执行材料；`review-contract.md` 是按需人审入口；`context.md / tasks.md` 只在必要时作为辅助材料。高风险计划需完成独立审查并记录可定位依据。
