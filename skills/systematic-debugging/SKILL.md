---
name: systematic-debugging
description: |-
  探索式根因调查 Skill。以区分性证据、安全边界和最小修复交接推进 bug、测试失败、性能退化或意外行为。
  Triggers: 根因未明, 复现不稳, 测试失败, 性能退化, slow, 意外行为, debug, 调试.
---

# systematic-debugging

在允许边界内自由调查，把问题推进到有证据支持的下一状态。不要把调查写成固定步骤，也不要在证据不足时输出根因或修复结论。

## 核心不变量

- 自主选择信息增益最高且风险合理的调查；高歧义时保留主要竞争性解释，避免过早收敛。
- 实际观察才是证据。静态可疑点、时间相关性和计划运行的命令只能产生假设。
- 根因必须闭合“触发条件 → 第一处偏离 → 传播路径 → 可观察症状”，且主要替代解释已被区分性证据排除。
- 原始错误的语义、一次成功与失败运行的差分，或跨组件关键边界的 ingress/egress 差分，任一项只要能区分解释，就是高密度证据；不以更多日志替代它。
- 修复边界应落在产生偏离或拥有相关不变量的位置，不在下游掩盖症状。

## 调查内核：建立可区分的反馈循环

先确认报告信号对应真实行为或外部副作用，而非日志、监控或观测伪影。优先建立或选择一个已实际执行或观察、能区分当前主要解释的 observation loop，并记录：

- 精确症状，以及能捕获该症状的成功/失败判据；
- 已知重复性或复现率，而非暗示稳定性；
- 任何人可重做该观察所需的条件；
- 与当前不确定性相称的迭代成本和局限。

本地命令不是唯一形式；生产或外部问题可使用脱敏日志、trace、事件、快照或真实副作用构成可重放、可比较的 observation boundary。不能稳定复现时如实记录局限；不要把未运行命令当作证据。

默认调查路径为：确认信号 → 建立并收紧 loop → 复现并按需最小化 → 保留竞争解释 → 执行信息增益最高的单个探针 → 闭合因果链 → 形成 handoff。可依据证据偏离，不把它当固定阶段或 Gate。

高歧义时用 `explanation → prediction → probe → observation → verdict` 管理竞争解释；每次 probe 对应可证伪 prediction，并只改变一个与该 prediction 相关的变量。不规定候选数量。若构造 `minimal_repro`，逐项移除输入、调用者、配置或步骤并复验；剩余元素应当都是 load-bearing，且 minimal 不能替代 original。

## 性能与不稳定性

性能验收，或改动可能影响延迟、吞吐、资源、hot path、算法复杂度、查询、序列化、I/O、并发、缓存或内存/CPU 时，路由至 `references/performance-and-flakiness.md`。功能正确不能替代同 workload、环境和口径下的性能证据；证据强度、样本和可接受判据随风险决定。

不稳定问题须以频率、触发条件和受控变量描述；单次绿色不是稳定性修复的证明。没有合理性能影响面且无性能验收时，记录 `not_applicable`，不要求 benchmark。

## 安全与授权边界

探索不得绕过安全控制、扩大权限、访问无关敏感数据，或执行未经授权的生产、破坏性和不可逆操作。证据引用和输出必须排除或脱敏密钥、凭证与隐私数据。需要越界时输出 `BLOCKED`，说明最小授权、风险和安全替代路径；临时观测还必须最小化、可清理。

## 上下文与参考

从当前最小证据集开始，仅在能区分解释时 JIT 加载更多上下文，不默认加载完整历史。

- `references/root-cause-tracing.md`：原始错误、运行差分与关键边界追踪第一处偏离。
- `references/building-feedback-loops.md`：按场景构造、收紧反馈循环并管理临时 instrumentation。
- `references/performance-and-flakiness.md`：性能影响面与不稳定复现的测量型证据。
- `references/defense-in-depth.md`：根因修复后判断哪些责任边界需要额外防护。
- `references/condition-based-waiting.md`：处理依赖固定 sleep 的时序不稳定。
- `references/condition-based-waiting-example.ts`：条件轮询示例。
- `references/find-polluter.sh`：在其运行环境假设成立时辅助定位顺序依赖或状态污染。

## 状态契约

| 状态 | 进入判据 | 必要输出 | 下一步 |
|---|---|---|---|
| `INVESTIGATING` | 尚无足够区分性证据 | 当前证据、主要解释、关键证据缺口 | 继续调查 |
| `HYPOTHESIS_VERIFIED` | 关键因果解释已被支持，但修复边界或交接尚未闭合 | 因果解释、证据引用、剩余不确定性 | 闭合 handoff |
| `FIXABLE` | 因果链闭合，主要替代解释已排除且 handoff 完整 | canonical handoff、执行授权状态 | 按授权路由 |
| `BLOCKED` | 外部依赖、安全、授权或环境边界阻止继续调查 | 已排查证据、阻塞项、最小解除条件 | 解除调查阻塞 |
| `ESCALATE` | 证据表明局部修复边界不成立，需要架构或设计决策 | 最小 architectural_finding、证据、待决策项 | `discuss` / `writing-plans` |

`ESCALATE` 由证据触发，不使用固定失败次数；`architectural_finding` 仅说明为何局部不变量、所有权或边界不足以解决症状。高影响故障可提出可回滚的临时缓解，但必须明确根因状态；缓解不能标记为 `FIXABLE` 或根因修复。

## 输出与修复交接

使用简洁 Markdown 输出。所有状态必须包含：

- `status`
- `evidence_refs`：可复查的已运行命令、日志、trace、测试、diff 或观测路径，并说明其支持或排除了什么
- `causal_explanation`：当前工作假设、最可信解释或已验证因果链

`FIXABLE` 的 canonical handoff 还必须包含：

- `fix_boundary`：允许修改与禁止修改的范围
- `target_behavior`：修复后应恢复或建立的可观察行为
- `verification_path`：映射 `original_repro`（报告的失败/观测及可重复条件）和存在时的 `minimal_repro`；修复后必须复验 original，并在 minimal 存在时也复验，二者不得互相替代
- `execution_authorization`：`granted | missing | unknown`
- `execution_authorization_basis`：授权来源、覆盖的动作与 `fix_boundary`，以及生产、破坏性、配置等专项确认是否满足；`missing|unknown` 时记录具体缺口

`granted` 仅在 `execution_authorization_basis` 可引用当前用户请求或已授权任务卡，并明确覆盖 exact `fix_boundary`、动作类型及所需专项确认时成立；明确只授权诊断或尚未授予实施权限时为 `missing`；无法确认授权来源或范围时为 `unknown`。只有 `granted` 且 basis 与当前动作匹配时可进入实施，另外两种状态保留 `FIXABLE` handoff 并请求最小授权。

`remaining_uncertainty` 在 `HYPOTHESIS_VERIFIED` 时必填，在其它状态可选；`bug_class` 和 `recommended_proof_strategy` 始终可选。剩余不确定性不得动摇 `FIXABLE` 的因果链、修复边界或验证判据。Proof strategy 最终由 `proof-oriented-development` 决定；strict TDD 仅在用户明确要求时启用。

`verification_path` 应使交接者能区分并执行：

- 原始失败的运行或等价外部观测；
- 为诊断构造的最小复现（如有）；
- 修复后的 original 与 minimal 双重复验；
- 性能或稳定性触发时相称的测量或重复观察。

没有构造 minimal 时明确其不存在；不得为满足字段而编造最小复现。


若本调查创建过临时 instrumentation、探针、配置、数据或文件，所有终止状态都必须以 `temporary_artifacts` 逐项记录：位置或标识、敏感性/安全影响、disposition（`removed | retained`）、保留原因（仅 retained）、责任人和处置验证；已删除也要记录。创建者负责清理或记录，后续 POD 消费未闭合项，VBC 最终审计。未创建时可省略该字段；无法判断且可能影响安全或交接时写 `unknown`。


`BLOCKED` 必须说明已排查证据、阻塞项和最小解除条件，并保留已经证实的因果解释及已明确的 handoff；外部或环境问题还须给出可回滚缓解（如适用）和后续观测。缺少实施授权不把已闭合诊断降为 `BLOCKED`；只有继续调查本身需要越权动作时才使用该状态。计划执行但尚未运行的命令只能写入下一步，不能放入 `evidence_refs`。

## 路由与机制化

- `FIXABLE + execution_authorization=granted + matching basis`：交给 `proof-oriented-development`，由其建立 Proof Plan、实施修复并输出 Proof Block。
- `FIXABLE + execution_authorization=missing|unknown|basis mismatch`：保留 canonical handoff，请求覆盖 exact fix boundary 和动作类型的最小授权。
- 修复完成声明前：交给 `verification-before-completion` 审计新鲜证据。
- 调用方应机制化校验状态枚举、`FIXABLE` 条件必填字段、授权 basis 与当前动作的匹配、执行路由和安全工具权限；因果是否充分仍由模型基于证据判断。
