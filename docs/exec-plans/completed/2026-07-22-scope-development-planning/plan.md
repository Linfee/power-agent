---
type: Execution Plan
scope:
  - skills/writing-plans
  - skills/plan-impl
  - skills/plan-impl-lightweight
  - skills/dev-docs
  - skills/dev-docs-maintain
  - skills/discuss
  - skills/systematic-debugging
  - AGENTS.md
  - docs/workflow.md
  - docs/architecture.md
  - docs/index.md
  - README.md
status: completed
runner:
  state: DONE
  batch: 4/4
  phase: complete
  fix_round: 0/0
  next_action: archived
---

# 限定开发计划工作流的适用范围

## 讨论结论 / 产品结论（如有）

- 用户指出：项目中的计划编写与计划实施只适用于开发计划，但当前泛化的触发词会让所有任务计划命中这些 Skill；需要修正路由与契约。

## Goal / Done Means

- 目标：将 `writing-plans`、`plan-impl` 及轻量执行路径明确限定为开发工作，避免普通任务计划误入 exec-plan 生命周期。
- Done Means：用户提出非开发的计划、清单或执行请求时，Skill description 与正文都不会把请求路由到 `docs/exec-plans` / `plan-impl`；开发任务仍保留完整 planning → implementation 交接。
- 不做事项：不新增通用计划 Skill，不修改已有历史 exec-plan，不改变开发执行的审查、验证或归档 Gate。

## Scope

### In Scope
- 收紧三个开发计划/实施 Skill 的 description、触发条件与准入说明。
- 同步 `dev-docs` / `dev-docs-maintain` 中直接指向 `writing-plans` 的交接，使其只委派软件资产变更的开发计划。
- 明确非开发工作按任务性质路由到 `discuss`、`doc-coauthoring`、`dev-docs` / `dev-docs-maintain`、`systematic-debugging` 或宿主原生任务清单。
- 同步 `discuss` 与 `systematic-debugging` 的直接交接；只有后续将修改软件资产时才交给开发计划链。
- 同步项目级 Agent 规则与面向用户的主链路文档。

### Out of Scope
- 新增或重写通用任务管理系统。
- 迁移、删除或修改已归档/进行中的 exec-plan。
- 改动任何业务代码、Git 工作流或分支策略。

## Key Decisions

- 决策：`writing-plans` 和 `plan-impl` 只服务会修改软件资产的开发工作，不以“计划”“任务拆解”等泛化词触发。
  - 原因：现有前置条件、Proof Block、代码审查和分支收尾均是开发生命周期契约，对研究、内容与运营工作不适用。
  - 证据：`skills/writing-plans/SKILL.md` 的输出固定为 `docs/exec-plans`；`skills/plan-impl/SKILL.md` 包含 worktree、review、verification 与 branch finalizing 状态机。
  - 执行含义：description、准入、跳过规则和项目级路由使用“开发/软件资产”作为正向条件，并列出非开发去向。
- 决策：非开发计划不引入新 Skill；按工作性质使用现有专长 Skill 或宿主原生任务清单。
  - 原因：通用清单无需被强制套入持久 exec-plan 及开发 Gate，已有 Skill 已覆盖需求、文档、知识维护和诊断。
  - 证据：`skills/discuss/SKILL.md`、`skill://doc-coauthoring` 与项目文档维护入口已定义这些职责。
  - 执行含义：路由表必须包含明确的“无匹配专长 → 原生任务清单 / 直接推进”分支。

### 非开发路由优先级

先按用户请求的**当前主要交付物**路由；每次只选一个主入口，后续状态改变时才交棒：

| 优先级 | 判定 | 主入口 | 明确排除 / 交棒 |
|---|---|---|---|
| 1 | 根因未知的错误、测试失败、性能退化或异常行为 | `systematic-debugging` | 不直接进入 exec-plan；仅在返回可执行修复边界后，按修复范围直接实施或交给开发计划链。 |
| 2 | 要修改代码、测试、构建/运行配置、自动化、Skill/prompt 或开发工作流等软件资产 | `writing-plans → plan-impl`（复杂）或开发轻量路径（明确局部） | 即使最终还要更新项目文档，开发变更是主交付；稳定知识沉淀在实现验证后按需交给 `dev-docs`。 |
| 3 | 只新建/修订项目 `docs/` 中长期复用的稳定系统知识、边界、ADR、playbook 或 reference | `dev-docs`；健康检查、漂移修复或 verification ledger 用 `dev-docs-maintain` | 不进入 exec-plan；若文档本身需要面向读者共同起草且不属于项目知识 Bundle，转 `doc-coauthoring`。 |
| 4 | 面向读者的 RFC、proposal、spec 或其他实质文档成稿 | `doc-coauthoring` | 不进入 exec-plan；若目标先是澄清产品范围、流程或验收，先转 `discuss`。 |
| 5 | 需求、范围、验收、用户流程或产品取舍尚未收敛 | `discuss` | 仅在结论决定后续软件实现时才交给 `writing-plans`。 |
| 6 | 研究、运营、个人事务、信息整理或其他无专长匹配的普通任务 | 宿主原生任务清单或直接推进 | 不创建 `docs/exec-plans`，不调用开发实施状态机。 |

优先级只解决重叠时的入口；它不把所有后续活动收进同一个 Skill。上游状态明确后，应以表中指定的交棒规则切换。

## Agent 自主边界

- 可自由决策：在现有主链路文档中采用最少且一致的适用范围措辞。
- 不可自行决策：不创建通用计划 Skill，不改变开发工作流的风险 Gate、审查强度或历史计划。
- 必须保持的不变量：开发任务仍使用 `writing-plans → plan-impl`；非开发任务不会创建 `docs/exec-plans`。
- 路由优先级必须保持：根因未知的诊断优先于开发实施；软件资产变更优先于附带文档；项目长期知识优先于通用文档共创；需求收敛优先于文档成稿；无专长匹配的普通工作使用宿主原生清单。
- 触发升级条件：若当前配置机制无法表达基于任务性质的触发边界，或发现其他默认路由仍把泛化计划导向 exec-plan，则停下并报告额外影响面。

## Plan Review Gate

- Gate Revision：r4
- Plan Risk：medium
- Review Path：self-review + independent reviewer
- Plan Review Status：APPROVED
- Independent Review：approved
- Independent Review Basis：gate_revision=r4; kind=independent-review; record=history://开发计划路由审查

## Evidence Cache（仅记录非显然事实）

- `writing-plans` description 包含“任务拆解”；证据：`skills/writing-plans/SKILL.md:3-5`；影响：泛化计划请求会命中开发计划 Skill。
- `plan-impl` 包含 worktree、审查、验证、分支收尾状态机；证据：`skills/plan-impl/SKILL.md:10-40, 44-82`；影响：不能用于不产生代码变更的普通任务。
- 项目规则将所有复杂任务要求为 exec-plan；证据：`AGENTS.md:96-99`；影响：必须限定为复杂开发任务，否则正文边界会被项目级规则推翻。

## Tasks

- T1 收紧开发计划 Skill：更新 `writing-plans` 的 description、准入、跳过与非开发路由；完成信号是泛化任务计划不再触发 exec-plan。
- T2 收紧实施 Skill：更新 `plan-impl` 与 `plan-impl-lightweight` 的输入/准入、跳过与路由；完成信号是只有开发 exec-plan 或开发实现任务进入执行状态机。
- T3 同步直接交接与项目入口：更新 `discuss`、`systematic-debugging`、`dev-docs` / `dev-docs-maintain` 及其直接 references，以及 `AGENTS.md`、README 与架构/流程/文档导航；使用同一优先级表表达开发范围与非开发去向。完成信号是所有主入口给出相同的入口、排除与交棒规则。
- T4 验证契约：检查 description、路由优先级表、四个直接交接及其直接 references 与现有开发主链路仍一致；完成信号是文本结构与引用检查无旧的泛化默认表述或相互冲突的非开发入口。

## Proof Strategy

- 主证明：定点检索与审查所有暴露 planning 入口的 Skill、`discuss` / `systematic-debugging` / `dev-docs` / `dev-docs-maintain` 的直接交接及 references、`AGENTS.md`、README、architecture、workflow、docs index；逐条核对路由优先级表的入口、排除与交棒规则一致。
- 次证明：独立 reviewer 对路由优先级、交接完整性和误触发风险给出结论。
- 非证明：仅凭 plan 文件生成或 Markdown 格式化成功。
- 已知未验证面：不运行全量 agent 触发评测；当前仓库没有覆盖这些三个 Skill 路由的专用可执行 eval。
- 失败解释：若仍存在将一般计划/任务拆解直接映射到 exec-plan 的默认描述或规则，则触发边界未真正收紧。

## Blockers / Escalation

- 阻塞条件：需要新增通用计划 Skill，或改动当前范围外的宿主级系统 prompt，才能表达路由边界。
- 升级对象：用户。
- 升级时携带材料：无法消除的入口、当前触发表述和可选的最小方案。

## Risks / Rollback

- 风险：过度收紧后，用户用非“开发”词描述的软件工作时可能不触发该链路。
  - 失败信号：Skill description 未包含软件资产、功能实现、bugfix、重构或工程迁移等清晰正向示例。
  - 缓解方式：保留面向开发产物与实施计划的正向触发词，正文允许依据任务实质判断。
  - 回滚方式：恢复本次各 Skill 与主链路文档的改动。
- 风险：路由表与既有文档维护/需求讨论职责重叠。
  - 失败信号：同一重叠任务在两个入口都被默认接管，或缺少从诊断到实施、从需求到实施的交棒条件。
  - 缓解方式：以“当前主要交付物”判定，并通过优先级表定义入口、排除与明确交棒；所有主入口复用同一规则。
  - 回滚方式：恢复本次路由说明。

## Optional Split Files（如有）

- `context.md`：none
- `tasks.md`：none

## 当前状态

- 当前进度：已完成。
- 下一步：无。

## Plan Review History

### Gate Revision r1

- Gate Revision：r1
- Independent Review：issues_found
- Independent Review Basis：gate_revision=r1; kind=independent-review; record=history://开发计划路由审查
- Finding：非开发路由没有互斥优先级、排除或交棒规则，无法验证重叠任务不会被多个入口默认接管。

### Gate Revision r2

- Gate Revision：r2
- Independent Review：approved
- Independent Review Basis：gate_revision=r2; kind=independent-review; record=history://开发计划路由审查

### Gate Revision r3

- Gate Revision：r3
- Independent Review：approved
- Independent Review Basis：gate_revision=r3; kind=independent-review; record=history://开发计划路由审查

### Gate Revision r4

- Gate Revision：r4
- Independent Review：approved
- Independent Review Basis：gate_revision=r4; kind=independent-review; record=history://开发计划路由审查

## Session Log

- 2026-07-22：基于用户明确问题创建执行计划；r1 独立审查发现重叠非开发路由缺少优先级，已新增基于当前主要交付物的路由表并进入 r2 修复验证。
- 2026-07-22：r2 修复验证通过；同一独立 reviewer 确认路由优先级表为重叠任务提供单一入口、排除与交棒，开发链路保持完整。
- 2026-07-22：发现 `dev-docs` / `dev-docs-maintain` 的直接计划交接仍使用泛化“任务拆解”表述；纳入必要路由修正，Gate 递增至 r3。
- 2026-07-22：r3 独立审查通过；`dev-docs` / `dev-docs-maintain` 已纳入 metadata scope，计划可实施。
- 2026-07-22：主审发现 `discuss` 与 `systematic-debugging` 的无条件交接会绕过非开发路由；将其与直接 reference 同步纳入 r4。
- 2026-07-22：r4 独立审查通过；四个直接交接及其 references 已进入实施和验证范围。
- 2026-07-22：实施完成。开发计划/实施 Skill、四个直接交接及主链路文档均限制为软件资产变更；非开发路由已明确。验证：两轮 `uv run --no-project python evals/documentation-skills/test_run_pi_eval.py` 均为 18 tests OK，`git diff --check` 无输出；主审修复验证与最终路由复审均通过。
