---
name: writing-plans
description: |-
  开发执行计划编写 Skill。把将修改软件资产的需求、讨论结论或规格文档转成可执行 exec-plan；用户要求创建开发实施计划、开发 exec-plan 或工程任务拆解时触发。
  Triggers: 创建开发 exec-plan, 开发任务拆解, writing-plans.
---

# Writing Plans

把会修改软件资产的需求、讨论结论或规格文档转成可执行 exec-plan。计划给强执行 Agent 清楚的目标、边界、关键决策与证明方式，不写成机械脚本。

## 什么时候用

仅在后续工作会修改代码、测试、构建或运行配置、自动化、Skill/prompt 或开发工作流等软件资产时使用：用户要求创建开发实施计划；已有 `discuss` 结论或 spec 需要落成可执行计划；开发跨模块，或技术决策、验收、证明策略需要在实施前锁定。

exec-plan 服务跨模块、多批次、跨会话或高风险工作；边界清楚的中等偏小工作不需要它——`discuss` 结论交 `proof-oriented-development` 或主代理直做。已是多任务且用户要编排时才交 `implement`。

命中以下跳过条件时直接实施（`proof-oriented-development`），不强行 planning：单文件小改、拼写/文案/格式调整；明确且局部的 bugfix 且无跨模块设计决策；已有完整可执行的任务清单且无新技术决策（清单本身可交 `implement`，不必先写 exec-plan）。需求仍不清晰时回 `discuss`。

非开发工作（研究、运营、普通清单、长期文档维护、读者文档）按主要交付物路由到对应 Skill 或直接推进，不创建 `docs/exec-plans`。

## 边界

- `discuss` 定范围、验收与 planning 约束，不是完整实现设计；实现级架构/API/模型/任务边界由本 Skill 用仓库证据补齐，不要把代码证据能闭合的细节退回 `discuss`。
- 执行交给 `implement`（它也接受非 exec-plan 的计划）；本 Skill 不直接修改业务代码。
- 不默认 strict TDD；只有用户明确要求时才写入 Proof Strategy。
- 不写逐行改动、机械步骤、私有 helper 设计、局部命名决策或每步几分钟的执行脚本；不删除 `review-contract.md` 人审入口。

## 输入

最小输入：用户当轮需求与约束（或当前会话经独立审查通过的 `discuss` 结论）；用户指定的 spec、issue、计划或设计文档；与目标直接相关的架构决策、模块文档与代码证据。

上下文按缺口获取：先定点读取，复杂度或涉及范围超出当前证据时再启动探索子代理；禁止无明确缺口的全仓探索。

## 输出

计划目录：`docs/exec-plans/active/YYYY-MM-DD-title/`

默认产物：

- `plan.md`：执行真源，承载讨论结论、Goal / Done Means、Scope、Key Decisions、Agent 自主边界、Evidence Cache、Tasks、Proof Strategy、Blockers / Escalation、Risks / Rollback。
- `review-contract.md`：人类按需审阅入口与 **唯一 Gate**：Intent、In / Out、Acceptance、Agent 自主边界、Proof、Blockers、Risks、Plan Review Gate。

可选拆分（只在证据昂贵、任务图复杂、多 Agent 协作、上下文过大或可读性明显受损时）：

- `context.md`：高成本证据缓存，不是上下文百科。
- `tasks.md`：复杂任务图、多 Agent 分工或交接信息，不是执行脚本。

所有产物都是 `docs/` Concept，以合法 YAML frontmatter 开始并具有非空 `type`（分别用 `Execution Plan`、`Review Contract`、`Evidence Cache`、`Task Graph`）；执行中的 `plan.md` 仅通过 frontmatter 的 `runner` mapping 保存恢复状态，不使用 HTML 注释。模板在 `references/plan-template.md`、`review-contract-template.md`、`context-template.md`、`tasks-template.md`；模板缺失时按上述契约生成最小合格版本。`plan.md` 是单一事实源，可选文件不得新增方向或与之冲突。

## 流程

### Step 0：准入与充分性检查

1. 命中跳过条件则退出并给出去向。
2. 独立子系统多、候选任务过多、依赖链深或关键未决策项多时，先做母 plan / 子 plan / 集成验收 plan 的边界设计。
3. 确认业务目标、范围边界、完成定义、非功能约束是否足够。缺口会改变用户目标、范围、验收或上层方案时，升级到用户或 `discuss`；实现级缺口由本 Skill 基于证据补齐。
4. 只补当前计划需要的证据，并记录上下文充分性结论。
5. 按最高命中项定 `plan_risk`：
   - `low`：单模块、可逆、无公共契约/数据/权限/并发变化，targeted proof 足以判定完成。
   - `medium`：跨模块或存在非平凡接口/兼容性决策，但可安全回滚，不触及 high 的边界。
   - `high`：破坏性或难回滚操作、公共 API 破坏、身份/权限/隐私/支付、安全、Schema/迁移、数据一致性、并发语义、生产发布或关键 UX 决策。
   - 无法判断风险时不得默认为 low；先补证据，仍不清楚按 `high` 处理。

### Step 1：生成计划包

创建 `plan.md` 与 `review-contract.md` 并保留各自 frontmatter；`plan.md` 承载不足时才拆 `context.md` / `tasks.md`，并在 `plan.md` 写明拆出理由。

计划必须锁定：目标、In / Out Scope、关键技术决策、Agent 自主边界、任务图、Proof Strategy、阻塞/升级条件、风险/回滚。

拆任务前先扫描预重构机会：能让变更变容易的小重构，先做或并入首个任务。

涉及新模块、模块拆分/合并、接口变化、port、seam 或 adapter 时，按需调用 `codebase-design`：将其模块边界、删除测试和 seam 证据吸收进 Key Decisions / Proof Strategy，不创建平行设计产物。

Gate 只写在 `review-contract.md`（`Plan Risk`、`Review Path`、`Plan Review Status`、`Independent Review`、按需 `Gate Revision` / 历史）。`plan.md` 不复制这些字段。material amendment 只改 contract 的 Gate 并追加历史，然后按风险重入审查。

### Step 2：Self-Review 与风险驱动 Gate

所有风险等级先 inline self-review，逐项检查：

1. **需求覆盖**：Goal、Scope、Acceptance 和每个已确认要求都有对应 task/proof。
2. **占位符扫描**：不残留 `TBD`、`TODO`、未定义术语，或“添加适当错误处理 / 写相关测试”这类泛化占位。
3. **一致性**：Key Decisions、任务依赖、接口名、Agent 边界、Proof 和 rollback 不互相冲突。
4. **任务边界**：每个任务值得独立验证和审查；setup/config/docs 已并入真正需要它们的任务。
5. **风险校准**：`plan_risk` 是否漏掉公共契约、数据、权限、安全、并发、迁移、发布或不可逆影响。
6. **长期所有权证据（条件性）**：仅当计划引入长期所有权——新依赖、跨模块边界、外部配置面、持久/跨请求共享状态、具有 init/cleanup/concurrency 语义的生命周期——时，Key Decisions 必须为每一项给出当前需求、真实消费者或代码/运行边界证据，并说明 ordered ladder（不新增，复用仓库已有实现/函数/API/模块 → stdlib/平台原生 → 已有依赖 → 满足当前契约的最小直接实现）中更早层级为何不充分；缺证据不得交棒。证据购买的是长期所有权类别本身：运行边界已直接要求外部配置、共享状态或生命周期时，该类别视为已有证据购买，不要求计划提前选择私有实现机制/库（如具体 pool 实现来源），除非计划本身另行引入新依赖或跨模块边界。Key Decisions / Evidence Cache 中具体、无保留、未冲突的已确认需求、提供方约束或仓库事实本身即为当前证据，不要求外链或额外 grep 审计来源；仅当事实缺失、被标为 unknown/unconfirmed 或与计划其它证据冲突时才需要补充 source pointer。已确认的提供方约束（如"提供方要求官方 SDK"）本身说明 stdlib、已有依赖或手写直接实现不满足契约，不得把手写 direct 实现当作更早 ladder 层级的替代。局部变量、派生状态与普通内部 helper 不进入该检查；安全、正确性与 Proof 不可作为可删复杂度。

发现问题直接修订并重跑 self-review；self-review 不能把未知事实改写成已确认结论。

随后按风险进 Gate：

- `low`：self-review 通过即可交棒（`plan_review_status=SELF_REVIEWED`，Independent Review 为 `not_required`）。
- `medium / high`：self-review 后用 `references/plan-reviewer-prompt.md` 派一个独立 tech-plan-reviewer（平台没有专用角色时用通用 reviewer）。reviewer 只审计划是否足够让下游执行，不重写实现方案。
- reviewer `APPROVED` → 置 `APPROVED` 并交棒；`ISSUES_FOUND` → 补证据、边界、依赖或验收后重新 self-review 和独立审查。同类 blocking issue 连续出现且无收敛时向用户升级；最多 3 轮，不用更多 reviewer 掩盖计划缺口。高风险计划用户要求修改时，修订后重新走完 self-review 和独立审查。

### Step 3：交棒

最终回复至少包含：Plan Path、Review Contract Path、Plan Risk（含命中理由）、Review Path、Plan Review Status、Optional Split Docs（无则 none）、Scope Summary、Key Technical Decisions、Task Graph Summary、Open Risks、Next Step（通常为 `implement [plan-path]`）。

禁止只给“已生成计划，请查看”。人类默认只审 `review-contract.md` 中的 Intent、范围边界、Acceptance、Proof、Agent 自主边界、Blockers 和 Risks；不要求逐行审技术方案或任务拆解，除非用户明确要求。

## 质量门槛

- 验收标准必须可观察、可验证、可判定；不写“已实现 / 已添加 / 已支持”。
- Key Decisions 有证据、理由与执行含义；未经确认的假设不写成既定事实。
- Agent 自主边界包含：可自由决策、不可自行决策、必须保持的不变量、触发升级条件。
- Proof Strategy 区分主证明、次证明、non-proof、已知未验证面和失败解释；lint、typecheck、格式化、构建成功或宽泛文本搜索不能单独作为完成证明。
- 先勾画测试接缝再定 Proof：优先复用仓库已有接缝、选尽可能高层、理想数量一个；新接缝开在尽可能高的位置，与用户确认。测试写法参照仓库同类测试，复用既有约定。
- 任务尺寸三判据：纵向切穿所需各层（而非某一层的水平切片）、可独立演示或验证、单个全新上下文可承载；不跨无强依赖子系统，也不细到逐行改动或私有 helper。
- 爆炸半径大的机械性重构（改共享符号、改列名）塞不进纵向切片时，用 expand–contract：新旧并存 → 按爆炸半径分批迁移（每批一个任务，批间保持可验证）→ 删除旧路径。
- 高风险且不可逆、权限/安全/隐私/并发语义、公共 API、数据模型、迁移、发布或关键 UX 决策，必须在计划阶段闭合或写入阻塞/升级条件。
- 交棒材料要让执行 Agent 明确：要达成什么、边界在哪、哪些可自主发挥、如何证明完成、何时停止。`plan.md` 是执行材料；`review-contract.md` 是按需人审入口和唯一 Gate。

## References

- `references/plan-template.md`、`review-contract-template.md`、`context-template.md`、`tasks-template.md`：计划包模板。
- `references/plan-reviewer-prompt.md`：medium/high 独立审查 prompt。
