---
type: Review Contract
scope:
  - development-planning-routing
---

# Review Contract

## Intent

- 将 exec-plan 的编写和实施限定为修改软件资产的开发工作，避免一般任务计划被错误带入开发生命周期。

## Scope

### In Scope
- 三个开发 planning / implementation Skill 的触发与准入边界。
- `dev-docs` / `dev-docs-maintain` 的直接开发计划交接。
- `discuss` / `systematic-debugging` 的上游开发计划交接与直接 references。
- `AGENTS.md`、README、架构/工作流/文档导航中的主链路路由说明。
- 非开发工作的明确去向。

### Out of Scope
- 新通用计划 Skill、历史计划迁移、开发审查或验证 Gate 变更。

## Acceptance

- [ ] 仅开发计划或开发实施请求会触发 `writing-plans`、`plan-impl` 或 `plan-impl-lightweight`。
- [ ] 非开发的需求讨论、文档共创、长期知识维护、诊断和普通任务清单均有明确且不冲突的去向。
- [ ] 项目级规则与所有主入口不再要求每个复杂任务都创建 exec-plan。
- [ ] 开发主链路仍为 `writing-plans → plan-impl`，且无需迁移历史 exec-plan。

### 非开发路由优先级

- 根因未知的异常先用 `systematic-debugging`；确认可执行修复边界后才交给开发实施。
- 修改软件资产时，`writing-plans → plan-impl` 优先于附带的文档更新；稳定知识沉淀在验证后按需交给 `dev-docs`。
- 仅维护项目长期知识时使用 `dev-docs` / `dev-docs-maintain`，优先于通用文档共创。
- 面向读者的文档成稿使用 `doc-coauthoring`；若范围/验收未定，先用 `discuss`。
- 无专长匹配的研究、运营和普通任务使用宿主原生清单或直接推进，不创建 exec-plan。

## Agent 自主边界

- 可自由决策：统一已有中文术语并删去误导性泛化触发词。
- 不可自行决策：不新增工作流类别或修改开发实施审查/验证机制。
- 必须保持的不变量：开发计划保留可执行、可验证的 plan package；非开发任务不写入 `docs/exec-plans/`；所有重叠任务按“当前主要交付物”的路由优先级选择单一主入口。

## Proof

- 主证明：定点检索与审查所有暴露 planning 入口的 Skill、`AGENTS.md`、README、architecture、workflow、docs index，并逐条核对非开发路由的入口、排除和交棒规则。
- 次证明：独立 reviewer 对路由优先级、交接完整性和误触发风险给出结论。
- 非证明：Markdown 文件存在或格式化通过。
- 已知未验证面：没有端到端 Skill 选择器可运行，不能直接测量运行时自动触发率。

## Blockers / Escalation

遇到以下情况必须停止并请求确认：

- 需要新增通用计划系统或改变当前开发执行的风险、审查、验证或分支策略。

## Risks

- 风险：开发描述过于口语化导致计划 Skill 未被选中。
  - 决策状态：可由仓库证据闭合。
  - 缓解方式：保留功能实现、bugfix、重构、工程迁移和软件资产等正向边界。
  - 执行期阻塞条件：发现无法靠现有边界区分的任务类别时停止扩展。

## Plan Review Gate

- Gate Revision：r4
- Plan Risk：medium
- Review Path：self-review + independent reviewer
- Plan Review Status：APPROVED
- Independent Review：approved
- Independent Review Basis：gate_revision=r4; kind=independent-review; record=history://开发计划路由审查

## Plan Review History

### Gate Revision r1

- Gate Revision：r1
- Independent Review：issues_found
- Independent Review Basis：gate_revision=r1; kind=independent-review; record=history://开发计划路由审查
- Finding：缺少处理重叠非开发任务的路由优先级、排除和交棒规则。

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
## Review Focus

- 审查路由是否以工作性质而非“计划”一词区分，非开发去向是否完整，且开发主链路是否保持无歧义。
