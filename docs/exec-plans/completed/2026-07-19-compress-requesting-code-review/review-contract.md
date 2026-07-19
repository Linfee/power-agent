---
type: Review Contract
scope:
  - skills/requesting-code-review
---

# requesting-code-review 保真压缩 Review Contract

## Intent

- 以提交 `d2ca53c` 为行为基线，减少 `requesting-code-review` 运行时上下文和维护重复，不改变审查策略、安全边界或输出协议。

## Scope

### In Scope
- `requesting-code-review` 主 Skill、reviewer prompt、风险/输出/并行 references 和压力场景。
- baseline/candidate 定向 A/B，以及体积、路由、安全、finding 与输出合法性比较。

### Out of Scope
- 上游 `plan-impl`、reviewer 生命周期或 Review Assets 权限变更。
- description 触发优化、持久 eval harness、新依赖和 push。

## Acceptance

- [x] 核心运行时表面固定为 `SKILL.md`、`code-reviewer.md`、`risk-classification.md`、`output-contract.md` 四个 Git blob 的 Python `len(text)` 之和；相对基线 13,459 字符至少减少 20%，优先达到 25%。
- [x] 常规、增强、高实现风险升级、finding owner 仅在同一实现目标和同一 review session 内复验、跨目标或跨 session 使用新 reviewer、替代 reviewer、范围扩大和显式并行路径保持不变。
- [x] 无 manifest、不可信 run root、symlink/traversal/跨 run、scope/freshness/source/sensitivity 不匹配的资产继续被拒绝。
- [x] 每次修复产生新 verdict；主审阶段高实现风险不遗漏独立终审；独立终审保持独立。
- [x] 直接从版本化 `context.md` 加载精确 system、schema、C1-C10 prompts 与 hard assertions：C1-C8 路由/资产断言全部通过；C9-C10 的 blocker 召回与严重度不低于 baseline，control 不新增 blocker。
- [x] Bundle tests、结构检查、主审和独立终审通过。

## Agent 自主边界

- 可自由决策：章节合并、状态表格、通用问题压缩和 20% 以上的实际删减率。
- 不可自行决策：改变状态/字段、删减资产安全边界、改变 reviewer 生命周期、三轮上限或平台无关性。
- 必须保持的不变量：直接 reviewer prompt 保持关键安全与输出骨架自包含；finding owner 连续验证不跨实现目标或 review session；所有历史真实 failure modes 有 A/B 覆盖。

## Proof

- 主证明：完整 SHA `d2ca53cd8b6fc28ead879c668ffdccc628d50154` 与候选直接使用 `context.md#machine-readable-fixtures` 的相同 system、schema、十个 prompts、hard assertions 与 canonical package 算法；runner identity 按 `runner_contract.runner_identity` 的 exact regex group + UTF-8 bytes 复算；semantic failure 只允许一次 whole-pair retry，process/identity/JSON/schema infrastructure failure 另允许一次 whole-pair retry，同类第二次失败中止，禁止单边重试或有效样本挑选。
- 次证明：引用、枚举、placeholder、平台耦合、`git diff --check`、Bundle tests 和两阶段审查。
- 非证明：仅字符数、行数、格式、主观可读性或单独的运行时间不能证明性能保持。
- 已知未验证面：不做大样本统计显著性测试；运行时间只记录。

## Blockers / Escalation

遇到以下情况必须停止并请求确认：

- 达到压缩目标必须删除安全或审查路由不变量。
- 候选出现 baseline 没有的阻塞 finding 漏报或资产越界读取。
- 需要修改 `plan-impl` 等 Out of Scope 契约。

## Risks

- 风险：删除默认行为提示后 finding 召回下降。
  - 决策状态：通过真实缺陷 A/B 闭合。
  - 缓解方式：保留非默认边界、严重度和证据要求。
  - 执行期阻塞条件：候选漏报 baseline 的阻塞缺陷。
- 风险：去重造成间接 reference 漏读。
  - 决策状态：直接执行 prompt 的关键约束不下沉。
  - 缓解方式：只下沉解释性重复，输出骨架和安全算法保持自包含。
  - 执行期阻塞条件：字段、路由或安全断言失败。

## Plan Review Gate

- Gate Revision：r15
- Plan Risk：medium
- Review Path：self-review + independent reviewer
- Self Review：passed
- Self Review Basis：C8 route 允许 `parallel_fix|continue_owner` 等价编码，stage 仍严格为并行修复验证。
- Plan Review Status：APPROVED
- Independent Review：approved
- Independent Review Basis：gate_revision=r15; kind=independent-review; record=history://CompressionPlanR3Review

## Plan Review History

### Gate Revision r1

- Gate Revision：r1
- Self Review：passed
- Self Review Basis：固定核心统计口径、十个场景、逐类 hard assertions 和一次成对重跑规则。
- Independent Review：approved
- Independent Review Basis：gate_revision=r1; kind=independent-review; record=docs/exec-plans/active/2026-07-19-compress-requesting-code-review/plan.md#gate-revision-r1

### Gate Revision r2

- Gate Revision：r2
- Self Review：passed
- Self Review Basis：恢复同目标/同会话边界并扩展 C1，不改变其它压缩验收。
- Independent Review：approved
- Independent Review Basis：gate_revision=r2; kind=independent-review; record=history://CompressionPlanR2Review

### Gate Revision r3

- Gate Revision：r3
- Self Review：passed
- Self Review Basis：将 A/B 语义摘要升级为版本化精确 fixture，并补齐模型、字节哈希和 assertion 执行语义，不改变行为验收。
- Independent Review：approved
- Independent Review Basis：gate_revision=r3; kind=independent-review; record=history://CompressionPlanR3Review

### Gate Revision r4

- Gate Revision：r4
- Self Review：passed
- Self Review Basis：仅替换超时模型并增加 responseModel 身份验证，不改变 C1-C10 或行为验收。
- Independent Review：approved
- Independent Review Basis：gate_revision=r4; kind=independent-review; record=history://CompressionPlanR3Review

### Gate Revision r5

- Gate Revision：r5
- Self Review：passed
- Self Review Basis：仅改变 prompt 传输并固定 Pi file wrapper 与临时文件处置，不改变行为验收。
- Independent Review：approved
- Independent Review Basis：gate_revision=r5; kind=independent-review; record=history://CompressionPlanR3Review

### Gate Revision r6

- Gate Revision：r6
- Self Review：passed
- Self Review Basis：只修正 C1/C2 repair-context assertion 语义，不降低五类必需上下文要求。
- Independent Review：approved
- Independent Review Basis：gate_revision=r6; kind=independent-review; record=history://CompressionPlanR3Review

### Gate Revision r7

- Gate Revision：r7
- Self Review：passed
- Self Review Basis：仅修正 C7 顶层处置 route，保持 Review Assets containment 与 blocker assertions 不变。
- Independent Review：approved
- Independent Review Basis：gate_revision=r7; kind=independent-review; record=history://CompressionPlanR3Review

### Gate Revision r8

- Gate Revision：r8
- Self Review：passed
- Self Review Basis：修复语义同义词与 C8 可观察行为边界，不放宽 B 不机械重启的核心契约。
- Independent Review：approved
- Independent Review Basis：gate_revision=r8; kind=independent-review; record=history://CompressionPlanR3Review

### Gate Revision r9

- Gate Revision：r9
- Self Review：passed
- Self Review Basis：仅统一 C8 route 与 stage 的并行语汇，不恢复不可判定 next_action。
- Independent Review：approved
- Independent Review Basis：gate_revision=r9; kind=independent-review; record=history://CompressionPlanR3Review

### Gate Revision r10

- Gate Revision：r10
- Self Review：passed
- Self Review Basis：主审两项 blocker 的最小修复；跨变体比较纳入整对 retry，输出双向不变量恢复。
- Independent Review：approved
- Independent Review Basis：gate_revision=r10; kind=independent-review; record=history://CompressionPlanR3Review

### Gate Revision r11

- Gate Revision：r11
- Self Review：passed
- Self Review Basis：只修正模型身份 observation boundary 与等义词假阴性，不降低 identity、pair retry 或行为验收。
- Independent Review：approved
- Independent Review Basis：gate_revision=r11; kind=independent-review; record=history://CompressionPlanR3Review

### Gate Revision r12

- Gate Revision：r12
- Self Review：passed
- Self Review Basis：分类 retry 不增加 semantic 样本选择次数，只隔离不可解析/身份/进程噪声。
- Independent Review：approved
- Independent Review Basis：gate_revision=r12; kind=independent-review; record=history://CompressionPlanR3Review

### Gate Revision r13

- Gate Revision：r13
- Self Review：passed
- Self Review Basis：只消除 C7 表示层假阴性，不放宽 containment、拒绝类别或 finding 召回。
- Independent Review：approved
- Independent Review Basis：gate_revision=r13; kind=independent-review; record=history://CompressionPlanR3Review

### Gate Revision r14

- Gate Revision：r14
- Self Review：passed
- Self Review Basis：只消除 C4 route/next_action 表示重复，不放宽动态增强或独立终审要求。
- Independent Review：approved
- Independent Review Basis：gate_revision=r14; kind=independent-review; record=history://CompressionPlanR3Review

### Gate Revision r15

- Gate Revision：r15
- Self Review：passed
- Self Review Basis：route 同义不放宽阶段；主审/并行双 reviewer 重启仍失败。
- Independent Review：approved
- Independent Review Basis：gate_revision=r15; kind=independent-review; record=history://CompressionPlanR3Review

## Review Focus

- 20% 压缩目标是否明确作用于运行时表面，而非只压场景文档。
- A/B 是否足以保护历史真实 failure modes、finding 质量和资产安全边界。
- 哪些内容可以视为模型默认行为，哪些必须保留在直接 reviewer prompt。
- finding owner 复验是否被严格限定在同一实现目标和同一 review session，且 C1 对跨目标/跨 session 路径有可判定 hard assertion。
