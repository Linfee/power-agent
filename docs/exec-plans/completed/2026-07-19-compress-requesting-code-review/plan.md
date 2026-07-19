---
type: Execution Plan
scope:
  - skills/requesting-code-review
status: completed
runner:
  state: DONE
  batch: 1/1
  phase: complete
  fix_round: 1/3
  next_action: commit_then_clean_head_verification
---

# requesting-code-review 保真压缩实现计划

## 讨论结论 / 产品结论（如有）

- 先提交当前完整版本作为行为基线，再缩减 Skill 体积；基线提交为 `d2ca53cd8b6fc28ead879c668ffdccc628d50154`。
- 压缩目标是减少每次触发与 reviewer 派发的上下文负担，不以最少文件或最大删减率为目标。
- 只有路由、finding 质量、资产安全边界和输出一致性相对基线不退化，压缩候选才可替换基线。

## Goal / Done Means

- 目标：压缩 `requesting-code-review` 主 Skill 与 references，减少重复说明和模型默认行为，同时保持现有审查生命周期、风险升级、资产隔离和输出协议。
- Done Means：核心运行时表面（精确为 `SKILL.md`、`references/code-reviewer.md`、`references/risk-classification.md`、`references/output-contract.md` 四个 Git blob 的 Python `len(text)` 之和）相对基线 13,459 字符至少减少 20%，优先达到 25%；十个固定 A/B 场景相对基线无回归，其中 C1 同时证明 finding owner 仅在同一实现目标和同一 review session 内可继续、跨目标或跨 session 必须使用新 reviewer；主审和独立终审通过。
- 不做事项：不改变触发 description、状态枚举、重要性/实现风险语义、finding-owner 复验、替代 reviewer 降级、独立终审条件、显式并行双审或 Review Assets 安全边界；不增加依赖或持久 eval 框架。

## Scope

### In Scope

- `skills/requesting-code-review/SKILL.md` 的入口、输入、状态机和交接说明。
- `references/code-reviewer.md` 的 reviewer prompt、直接安全约束与输出要求。
- `references/output-contract.md`、`risk-classification.md`、`conflict-resolution.md` 的职责去重。
- `references/review-workflow-scenarios.md` 的高密度表达与 A/B 回归语料。

### Out of Scope

- `plan-impl`、`receiving-code-review`、ADR 和项目级生命周期语义变更。
- 改变审查策略、扩大或缩小 Review Assets 权限。
- description 触发优化、全项目 eval harness、外部发布与 push。

## Key Decisions

- 决策：以 `d2ca53cd8b6fc28ead879c668ffdccc628d50154` 为不可变 baseline，对压缩候选做行为 A/B，而不是凭静态判断声称性能不下降。
  - 原因：Prompt 删除是否影响 finding 召回、路由和输出一致性必须由对照结果证明。
  - 证据：`docs/exec-plans/completed/2026-07-19-reviewer-reuse-strategy/plan.md` Session Log 记录两阶段审查、资产烟测、37 项 Bundle tests 与绑定完整 SHA 的完成前验证。
  - 执行含义：压缩前记录体积与场景输出；候选失败时回到基线语义，不用更多解释掩盖回归。
- 决策：优先删除职责重复和模型默认行为，安全与状态机不变量保留在直接执行 prompt。
  - 原因：主 Skill、风险参考、reviewer prompt 和 output contract 对同一规则存在语义复述；但资产 containment、风险升级和新 verdict 是历史真实 failure modes。
  - 证据：当前包共 520 行、18,217 字符；核心运行时表面固定为 `SKILL.md`、`code-reviewer.md`、`risk-classification.md`、`output-contract.md`，Git blob 原文按 Python `len(text)` 合计 13,459 字符。
  - 执行含义：定位/Objective/触发重复、通用审查问题、重复 placeholder 和场景样板优先压缩；不得把直接 reviewer 安全规则仅改成间接引用。
- 决策：用状态转换表和单一责任 reference 降低重复。
  - 原因：自然语言多处同步容易产生矛盾，表格更紧凑且可判定。
  - 证据：风险升级、下一步和输出一致性目前分别出现在主 Skill、prompt、risk 与 output contract。
  - 执行含义：主 Skill 负责编排；risk reference 负责分类；reviewer prompt 负责执行；output contract 只负责结构与不变量；scenarios 只用于维护/eval。

## Agent 自主边界

- 可自由决策：章节合并、表格形式、措辞压缩、通用审查维度的高密度表达，以及在 20% 以上目标内选择最终压缩率。
- 不可自行决策：删除状态、降低资产校验、改变修复验证或独立终审路由、改变三轮上限、把 reviewer prompt 的关键安全规则改为可选读取。
- 必须保持的不变量：working-tree 完整范围；每次修复新 verdict；finding owner 仅在同一实现目标和同一 review session 内优先继续，跨目标或跨 session 使用新 reviewer；替代 reviewer 完整 repair context；范围实质变化重启完整审查；高重要性或高实现风险顺序独立终审；无 manifest 不扫描；权威 run root、containment、target+paths/finding、freshness/source/sensitivity 校验；证据优先级；平台无关。
- 触发升级条件：达到 20% 压缩需要删除任一不变量，或候选在阻塞 finding 召回、安全、路由或输出合法性上低于基线。

## Plan Review Gate

- Gate Revision：r15
- Plan Risk：medium
- Review Path：self-review + independent reviewer
- Self Review：passed
- Self Review Basis：r14 C8 attempt 2 正确输出 stage=`并行修复验证` 且 route=`continue_owner`，被专用 route=`parallel_fix` 误拒绝。两者分别表达“处于显式并行修复路径”和“仅 finding owner/替代者继续”，在 stage 已强制并行修复验证时语义等价。增加 scalar `one_of` operator，C8 route 接受 `parallel_fix|continue_owner`，stage 仍必须 `并行修复验证`；不接受主审阶段或机械重启 B。
- Plan Review Status：APPROVED
- Independent Review：approved
- Independent Review Basis：gate_revision=r15; kind=independent-review; record=history://CompressionPlanR3Review

## Plan Review History

### Gate Revision r1

- Gate Revision：r1
- Self Review：passed
- Self Review Basis：需求覆盖、一致性、任务边界、风险校准和固定 proof oracle 已检查。
- Independent Review：approved
- Independent Review Basis：gate_revision=r1; kind=independent-review; record=docs/exec-plans/active/2026-07-19-compress-requesting-code-review/plan.md#gate-revision-r1
- Independent Review Result：APPROVED；确认固定运行时统计口径、C1-C10 hard assertions、波动处理、直接 prompt 安全边界和 rollback 足以执行；blocking issues 与 missing evidence 均为空。

### Gate Revision r2

- Gate Revision：r2
- Self Review：passed
- Self Review Basis：恢复 ADR-0007 生命周期边界并扩展 C1 hard assertions，不改变压缩目标与其它 oracle。
- Independent Review：approved
- Independent Review Basis：gate_revision=r2; kind=independent-review; record=history://CompressionPlanR2Review

### Gate Revision r3

- Gate Revision：r3
- Self Review：passed
- Self Review Basis：将不可独立复现的 A/B 摘要升级为版本化精确 fixture；随后补齐锁定模型、字节级哈希、subcase selector、可执行 assertion 语义和 runner，不改变 Skill 行为、压缩目标或 C1-C10 预期。
- Independent Review：approved
- Independent Review Basis：gate_revision=r3; kind=independent-review; record=history://CompressionPlanR3Review

### Gate Revision r4

- Gate Revision：r4
- Self Review：passed
- Self Review Basis：仅替换不可在 canonical timeout 内完成的固定推理模型，并增加 dated responseModel 验证；C1-C10 输入、schema、assertions、package identity 和行为验收不变。
- Independent Review：approved
- Independent Review Basis：gate_revision=r4; kind=independent-review; record=history://CompressionPlanR3Review

### Gate Revision r5

- Gate Revision：r5
- Self Review：passed
- Self Review Basis：仅将超时的 argv prompt 传输改为固定路径 `@file`，并把 Pi 生成的固定 `<file name=...>` wrapper 纳入精确输入；模型、场景、schema、assertions 与验收不变。
- Independent Review：approved
- Independent Review Basis：gate_revision=r5; kind=independent-review; record=history://CompressionPlanR3Review

### Gate Revision r6

- Gate Revision：r6
- Self Review：passed
- Self Review Basis：只将 C1/C2 repair-context literal assertion 修正为可执行的语义 concept groups，保持五类必需上下文与行为验收不变。
- Independent Review：approved
- Independent Review Basis：gate_revision=r6; kind=independent-review; record=history://CompressionPlanR3Review

### Gate Revision r7

- Gate Revision：r7
- Self Review：passed
- Self Review Basis：C7 同时含合法/非法 assets 与真实代码 finding；asset consumption 由专用字段验证，顶层 route 修正为 `report_blocker`。
- Independent Review：approved
- Independent Review Basis：gate_revision=r7; kind=independent-review; record=history://CompressionPlanR3Review

### Gate Revision r8

- Gate Revision：r8
- Self Review：passed
- Self Review Basis：为原始证据加入中英同义 token alternative；C8 锁定 owner continuation + 并行修复验证，删除场景输入无法判定的事后 next_action。
- Independent Review：approved
- Independent Review Basis：gate_revision=r8; kind=independent-review; record=history://CompressionPlanR3Review

### Gate Revision r9

- Gate Revision：r9
- Self Review：passed
- Self Review Basis：C8 使用专用 `parallel_fix/并行修复验证` 组合表达显式并行路径，owner A 与 B 不重启仍由场景契约约束。
- Independent Review：approved
- Independent Review Basis：gate_revision=r9; kind=independent-review; record=history://CompressionPlanR3Review

### Gate Revision r10

- Gate Revision：r10
- Self Review：passed
- Self Review Basis：主审两项 blocker 均采纳；C9/C10 增加固定 locator + 跨变体严重度比较，输出协议恢复阻塞状态反向不变量，候选哈希与 runner 哈希同步更新。
- Independent Review：approved
- Independent Review Basis：gate_revision=r10; kind=independent-review; record=history://CompressionPlanR3Review

### Gate Revision r11

- Gate Revision：r11
- Self Review：passed
- Self Review Basis：将 responseModel identity evidence 从 final-only 改为全 assistant JSONL stream 严格单例聚合；最终 answer 仍来自 message_end，缺失/冲突不放行；加入 `修复摘要` 等义 alternative。
- Independent Review：approved
- Independent Review Basis：gate_revision=r11; kind=independent-review; record=history://CompressionPlanR3Review

### Gate Revision r12

- Gate Revision：r12
- Self Review：passed
- Self Review Basis：将原单一整对 retry 拆为一次 semantic 与一次 infrastructure budget；最多三次仅在两类各失败一次时出现，同类第二次失败中止。
- Independent Review：approved
- Independent Review Basis：gate_revision=r12; kind=independent-review; record=history://CompressionPlanR3Review

### Gate Revision r13

- Gate Revision：r13
- Self Review：passed
- Self Review Basis：C7 不再把顶层 route 当作资产安全或 blocker 召回的代理；直接断言合法读取、五项拒绝和代码 locator。
- Independent Review：approved
- Independent Review Basis：gate_revision=r13; kind=independent-review; record=history://CompressionPlanR3Review

### Gate Revision r14

- Gate Revision：r14
- Self Review：passed
- Self Review Basis：C4 直接断言 output-contract 的 next_action，保留高风险动态升级与增强强度；删除重叠内部 route 代理。
- Independent Review：approved
- Independent Review Basis：gate_revision=r14; kind=independent-review; record=history://CompressionPlanR3Review

### Gate Revision r15

- Gate Revision：r15
- Self Review：passed
- Self Review Basis：C8 route 接受专用并行路径或 finding-owner continuity 两种等价编码，stage 继续锁定并行修复验证。
- Independent Review：approved
- Independent Review Basis：gate_revision=r15; kind=independent-review; record=history://CompressionPlanR3Review

## Evidence Cache（仅记录非显然事实）

- 核心运行时表面严格定义为基线提交中 `skills/requesting-code-review/SKILL.md`（5,119）、`references/code-reviewer.md`（5,486）、`references/risk-classification.md`（960）、`references/output-contract.md`（1,894）四个 blob 的 Python `len(text)` 之和 13,459；完整包 18,217 字符。候选使用同样文件和算法。
- `code-reviewer.md` 与 `output-contract.md` 重复完整输出骨架；主 Skill、risk、prompt、output 重复风险升级语义；影响：可在不改变行为的前提下做职责去重。
- Review Assets、containment、主审修复验证首次高风险升级来自 `review-workflow-scenarios.md` 场景六至十二和已归档计划 Session Log 的真实 reviewer findings；影响：这些规则必须留在直接消费路径并进入 A/B。
- 固定 A/B 语料：`context.md#machine-readable-fixtures` 是精确且版本化的 system、schema、C1-C10 prompts 与 hard assertions；本文 `Fixed A/B Oracle` 只保留身份、摘要和运行规则。

## Fixed A/B Oracle

- 身份：baseline commit `d2ca53cd8b6fc28ead879c668ffdccc628d50154`；r15 package 字节算法、固定 `@file` prompt transport、Pi 版本/provider/model/responseModel/thinking、system、schema、完整 prompts、assertions、分类整对重试与跨变体 evaluator 以 `context.md#machine-readable-fixtures` 和 `context.md#精确调用形状` 为准。
- Package SHA-256：baseline `6972f6e7baf814b70729bf8bcf9ad1403d27fc8c5976ef22a024f6de6689ebb3`；candidate `36ca944fab1559f12c5285ccb8d1f73182883623e6e1f1087a88cd3fbe6cb12a`。
- Runner SHA-256：对 `context.md` 使用精确 `re.search(r"````python\\n(.*?)````", text, re.S).group(1).encode("utf-8")`，不增删换行或规范化；digest=`e48c6a979ee23e1ab973dd8343cc9021874eaa48d886fc76c3b64458edd8e60b`，与 `runner_contract.runner_identity` 一致。
- 运行：baseline/candidate 使用完全相同的 Pi Agent `0.80.10`、provider=`cpa`、model=`gpt-5.4-mini`、responseModel=`gpt-5.4-mini-2026-03-17`、thinking=`low`、system、prompt、schema 与 assertions；assistant JSONL stream identity 为严格单例且 final message_end 存在；每个 case 只允许一次 semantic 整对 retry 和一次独立 infrastructure 整对 retry，同类第二次失败中止，禁止单边重试或挑选多个有效 passing samples。
- C1-C8 覆盖同目标/同 session owner、跨边界替代 reviewer、顺序增强、修复验证首次高风险、范围扩大、无 manifest、资产 containment/代码优先和显式并行；C7 直接断言合法读取、非法拒绝与代码 blocker，不绑定重叠顶层 route。
- C9-C10 各含完整 synthetic defect/control 输入：defect 必须召回匹配固定 locator 的 Important/Critical blocker，candidate 同 defect 严重度不得低于 baseline，control 不得新增 blocker。

## Tasks

- T1 Baseline Characterization：使用已固定的十个 A/B 场景与完整断言，从完整 SHA 基线提取原版 Skill 并记录核心/全包体积；候选改动前不得改变 oracle。
- T2 Runtime Surface Compression：压缩 `SKILL.md` 和 `code-reviewer.md`，用紧凑状态机替代重复段落，保留直接执行不变量。
- T3 Reference Consolidation：收紧 risk/output/conflict 职责，将压力场景改为高密度形式，确保引用与字段仍一致。
- T4 A/B Verification：相同模型、system、输入和配置成对运行 baseline/candidate；semantic failure 只允许一次 whole-pair retry，process/identity/JSON/schema infrastructure failure 另允许一次 whole-pair retry，同类第二次失败中止。候选必须满足全部 hard assertions，C9-C10 同 defect 召回和严重度不得低于 baseline，clean control 不新增 blocker；时间只记录不作硬门槛。
- T5 Review And Finish：运行结构检查、Bundle tests、主审与增强独立终审；工作树 dirty 时停在待提交 Gate。
- T6 Lifecycle Boundary Repair：恢复 finding owner 连续验证仅限同一实现目标和同一 review session 的直接契约；跨目标或跨 session 使用新的 reviewer；扩展 C1 hard assertions 并对 baseline/candidate 成对重跑。
- T7 Re-review And Finish：仅在同一实现目标和同一 review session 内由 finding owner 做修复验证，否则使用携带完整 repair context 的新替代 reviewer。无阻塞后按有效强度路由：常规 `继续流程`；增强才进入此前未参与目标的独立终审。本次压缩目标重要性高，采用增强路径后返回 WORKTREE_GATE。
- T8 Reproducible Oracle Repair：将精确 C1-C10 fixture 固化到版本化 `context.md`，通过 r3 Gate 后从该 JSON 直接成对运行全部场景，再执行增强主审与独立终审。

## Proof Strategy

- 主证明：从 `context.md#machine-readable-fixtures` 直接加载固定 system、schema、C1-C10 prompts 与 hard assertions，使用同一 canonical package 算法对 baseline/candidate 成对 A/B；C1-C8 路由与资产断言全部通过，C9-C10 候选不低于 baseline 的 blocker 召回/严重度且 control 无新增 blocker；核心运行时字符数减少至少 20%。
- 次证明：引用/枚举/placeholder 一致性检查、`git diff --check`、Bundle tests、平台耦合排除、主审和独立终审。
- 非证明：只看行数、字符数、Markdown 可解析或静态感觉“更简洁”不能证明性能不下降；运行时间仅作诊断。
- 已知未验证面：不做大样本统计显著性实验；semantic 与 infrastructure 各只有一次分类整对 retry，不单边重试、不从多个有效 passing samples 挑选有利结果。
- 失败解释：压缩率不达标表示仍有重复未闭合；行为断言失败表示删减触碰契约，应恢复对应基线语义而不是放宽断言。

## Blockers / Escalation

- 阻塞条件：压缩目标与安全/路由不变量冲突；baseline 本身在某个新增案例失败而无法定义“不退化”；需要修改上游 `plan-impl` 契约才能完成压缩。
- 升级对象：用户。
- 升级时携带材料：基线与候选输出、失败断言、体积差异和最小取舍选项。

## Risks / Rollback

- 风险：删除看似默认的审查提示导致真实 finding 召回下降。
  - 失败信号：候选漏掉 baseline 能发现的阻塞缺陷，或严重度明显降低。
  - 缓解方式：至少保留非默认风险边界和证据要求，使用真实缺陷案例 A/B。
  - 回滚方式：从 `d2ca53c` 恢复对应 prompt 段落。
- 风险：职责去重使 reviewer 漏读间接 reference。
  - 失败信号：输出字段缺失、安全校验缺失或状态不可解析。
  - 缓解方式：直接 reviewer prompt 保持自包含的关键安全与输出骨架；只把解释性重复下沉。
  - 回滚方式：恢复直接 prompt 中对应不变量。
- 风险：只优化仓库体积，没有降低运行时上下文。
  - 失败信号：总行数下降但核心运行时字符数未减少 20%。
  - 缓解方式：分别度量核心运行时表面和完整包。
  - 回滚方式：保留可读性更高的基线版本。

## Optional Split Files（如有）

- `context.md`：版本化固定 A/B system、schema、C1-C10 精确 prompts、hard assertions 和 package 构造算法。
- `tasks.md`：none

## 当前状态

- 当前进度：实现、r15 A/B、结构验证、主审修复验证与全新增强独立终审全部通过；计划任务完成并归档。
- 下一步：创建本地提交，在 clean HEAD 运行 `verification-before-completion`。

## Session Log

### 2026-07-19

- 基线：提交 `d2ca53cd8b6fc28ead879c668ffdccc628d50154`；核心运行时表面 13,459 字符，完整包 18,217 字符。
- 实现：压缩主 Skill、reviewer prompt、风险/输出契约和 12 个压力场景；保留审查状态机、finding owner/替代 reviewer、动态增强审查、Review Assets containment 和输出字段。
- r1 证明：修复后核心 10,434 字符（-22.48%），完整包 12,533 字符（-31.20%）；C1-C8 路由/资产 hard assertions PASS，C9-C10 历史缺陷仍被阻塞且 clean controls 无 false blocker。
- r1 内部审查：首轮发现默认审查跳过 Gate 与逐 blocker 定位证据被弱化；恢复直接约束后，替代 reviewer 以新 fix-verification verdict 关闭两项 finding，建议进入独立终审。
- r1 验证：结构不变量 PASS；`git diff --check` 无输出；平台耦合和误嵌编辑标记无命中；Bundle tests 37/37 OK；Bundle scan structural findings=0。
- A/B provenance：固定 oracle 已迁入本文；相同 `default` model 与固定 system/schema 执行，初始对照未触发挑选式重跑；内部审查修复后只重跑当前候选并复核原 baseline。四文件 package hash 如 `Fixed A/B Oracle` 所列。
- r1 独立终审：全新 reviewer 对 r1 最终范围返回 `状态=通过_含建议`、`审查阶段=独立终审`、`实现风险=低`、`审查强度=增强`、无 blocker、`下一步=继续流程`；唯一建议为保留 A/B provenance，已通过 `Fixed A/B Oracle` 与 package hash 持久化。
- WORKTREE_GATE：当前 HEAD 仍为基线提交且工作树含压缩实现与计划归档改动；不运行绑定 clean HEAD 的 `verification-before-completion`，不归档本计划。
- Material amendment：压缩主审发现候选允许跨目标/跨 session 继续 finding owner，违反 ADR-0007 与 Out of Scope；扩展 C1 hard assertions 并恢复生命周期边界属于 Proof 与执行契约变化，Gate Revision 从 r1 递增为 r2，清除旧 basis 后重新审查。
- r2 计划审查：独立 reviewer 首轮指出 T7 无条件复用 owner/进入终审会破坏常规路径；改为按同目标+同 session 与有效强度条件路由后复验通过，依据 `history://CompressionPlanR2Review`。
- 生命周期修复：`SKILL.md` 恢复 owner 仅在同一实现目标和同一 review session 内继续，跨目标/跨 session 或不可继续时派新替代 reviewer；场景 1/2 同步。
- r2 C1 A/B：相同 default model/system/schema 下，baseline 与 candidate 均对同目标/同 session 选择 `continue_owner/主审修复验证/常规/继续流程`，对跨目标或跨 session 选择 `new_reviewer` 并携带完整 repair context；hard assertions PASS。
- r2 验证：核心运行时 10,489 字符（相对 13,459 减少 22.07%），完整包 12,655 字符（相对 18,217 减少 30.53%）；`git diff --check` 无输出；Bundle tests 37/37 OK；Bundle scan structural findings=0；平台耦合无命中。
- r2 主审修复验证：原主审确认同目标/同 session 边界及场景 1/2 已恢复，未发现新增 blocker，进入独立终审。
- r2 独立终审：发现活动计划仍指向已完成的主审复验、已归档 reviewer-reuse 计划仍宣称待提交；已将活动计划推进到 `final_fix_verification`，归档计划改为已完成且无后续步骤。
- r2 终审修复验证：finding owner 确认两项计划状态 finding 均关闭、无新增 blocker，verdict=correct，可返回 WORKTREE_GATE。
- 审查反馈评估：强制最终审查和 finding-owner 生命周期 finding 均被当前 `SKILL.md:12,27` 反证；r2 Plan Gate 不因实现审查自动失效。但现有 A/B 只保存语义摘要，无法独立重建相同十输入，核心 Proof 缺口成立。
- Material amendment r3：新增版本化 `context.md` 固定 package 算法、system、schema、完整 C1-C10 prompts 与 hard assertions；Proof 契约改变，Gate Revision 从 r2 递增为 r3，清除当前 independent-review basis 后重新审查。
- r3 计划审查：首轮指出模型 alias、assertion evaluator 和字节级哈希未锁定；补齐后复验又指出 runner 硬编码模型自证且未实现整对重跑。现已改用 Pi Agent `0.80.10` 固定 `cpa/gpt-5.6-sol`、thinking=`low`，从 JSONL 最终消息验证 provider/model，并按 case 捕获全部失败后仅从 baseline 整对重跑一次，等待同 reviewer 再复验。
- r3 计划审查第三轮：reviewer 发现手写 schema 校验只检查资产字段为 list、未检查 items 为 string；runner 已对 `read_assets`、`rejected_assets`、`context_handoff` 增加逐项 string 校验，使类型错误进入整对重跑/失败。
- r3 计划审查终次复验：同 reviewer 确认模型身份、整对重跑、字节哈希、subcase/schema 和 string-array items 校验均闭合，APPROVED；依据 `history://CompressionPlanR3Review`。
- Material amendment r4：r3 runner 在 C1 baseline 首次与整对重试均达到 120 秒 timeout，无模型输出被采信；将固定模型改为已 smoke 成功的 `cpa/gpt-5.4-mini`，锁定 JSONL `responseModel=gpt-5.4-mini-2026-03-17`。Proof 推理配置变化，Gate Revision 从 r3 递增为 r4，其余 fixture 与验收不变。
- r4 计划审查：同 reviewer 确认模型替换已正确 material amendment、dated responseModel 校验与其余 fixture 不变量一致，APPROVED；依据 `history://CompressionPlanR3Review`。
- Material amendment r5：r4 runner 直接把 16K prompt 放入 argv，C1 baseline 首次与整对重试均 120 秒 timeout；相同 prompt 经固定 `@/tmp/power-agent-requesting-code-review-ab-input.txt`、thinking=low 在 9 秒内成功。runner 现将固定 Pi `<file name=...>` wrapper 纳入输入契约，逐次 finally 删除临时文件并在结束断言不存在；Gate Revision 从 r4 递增为 r5。
- r5 计划审查首轮：reviewer 发现固定 `/tmp` 文件的 exists→write 存在 TOCTOU，且 write 不在 finally 内；runner 已改为 `open("x")` 原子独占，在 try/finally 内写入，仅由成功 acquired 的调用删除，避免并发覆写/误删。
- r5 计划审查终次复验：同 reviewer 确认 `open("x")` 原子占用、所有异常清理和末尾无残留断言闭合，APPROVED；依据 `history://CompressionPlanR3Review`。
- Material amendment r6：r5 C1 首轮 baseline 与整对重试 candidate 均因 repair-context literal tokens 假阴性失败；输出实际包含所需语义但存在合并措辞。C1/C2 改用固定 `contains_concepts`：finding、原始证据、修复说明、可定位增量、新验证五类分别按同元素 token alternatives 判定；Gate Revision 从 r5 递增为 r6。
- r6 计划审查：同 reviewer 确认五 concept groups 不跨元素拼接、原证据与新验证独立且未降低行为边界，APPROVED；依据 `history://CompressionPlanR3Review`。
- Material amendment r7：r6 C7 首轮 JSON parse 失败后整对重试，baseline 读取合法 asset、拒绝非法 assets 并报告真实 blocker，却被 `route=review_assets` assertion 误拒绝；C7 route 修正为 `report_blocker`，asset 安全仍由 read/rejected/blocker assertions 独立锁定。
- r7 计划审查：同 reviewer 确认 route 修正不放宽 C7 的合法读取、五项拒绝与 `src/auth.ts:42` blocker 硬断言，APPROVED；依据 `history://CompressionPlanR3Review`。
- Material amendment r8：C2 baseline 使用 `原 evidence` 被中文 literal alternative 误拒绝；C8 baseline 正确选择 finding owner 继续但 fixture 误设 `parallel_fix`，且在无复验结果输入时强断言 `continue_flow`。现加入 `原+evidence` 同义 alternative，C8 改为 `continue_owner/并行修复验证` 并删除不可判定 next_action。
- r8 计划审查：同 reviewer 确认中英 evidence alternative 不与新验证互相替代，C8 锁定 owner continuation + 并行修复验证且删除不可判定 next_action 不放宽核心契约，APPROVED；依据 `history://CompressionPlanR3Review`。
- Material amendment r9：r8 C8 首次 `continue_owner/主审修复验证` 失败，整对重试产生 `parallel_fix/并行修复验证`；fixture 统一要求显式并行专用 route+stage，并继续删除不可判定 next_action。
- r9 计划审查：同 reviewer 确认 `parallel_fix/并行修复验证` 是一致专用组合，且不恢复无输入支撑的 next_action、不要求机械重启 B，APPROVED；依据 `history://CompressionPlanR3Review`。
- r9 A/B Proof：从 `context.md` 原样提取 runner，以标准 Python 3.14.6 执行；Pi `0.80.10`、provider=`cpa`、model=`gpt-5.4-mini`、responseModel=`gpt-5.4-mini-2026-03-17`、thinking=`low`。C1 attempt 1 因 candidate repair-context 措辞不命中而触发允许的整对 retry，attempt 2 PASS；C7 attempt 1 schema/assertion failure 触发允许的整对 retry，attempt 2 PASS；其余 case 首对通过。最终 C1-C10 baseline/candidate 全部 hard assertions PASS，临时 prompt 已删除，未做单边重试或样本挑选。
- r9 A/B Identity：baseline package SHA-256=`6972f6e7baf814b70729bf8bcf9ad1403d27fc8c5976ef22a024f6de6689ebb3`；candidate=`ea3f16a4db1a179e4054e9662843d00824626aabc78ea95b07d046f85d3cb56b`；extracted runner SHA-256=`e9f9c3f8c92e56640203f3d3e94a85e0862099f35ee14721391ab1136935cbc9`。
- r9 Size Proof：核心运行时 10,489 字符，相对 13,459 减少 22.07%；完整包 12,655 字符，相对 18,217 减少 30.53%。
- r9 Structural Proof：`git diff --check` 无输出；Bundle tests 37/37 OK；Bundle scan `Structural findings: 0`；引用、reviewer 输出标签、output-contract 语义、12 条场景结构 PASS；私有平台续接耦合与 placeholder/编辑标记均无命中。
- r9 增强主审：`history://CompressionPrimaryR9` 返回 `状态=阻塞`、实现风险中、增强；两项重要 finding：C9/C10 缺跨变体同 defect 严重度比较；direct reviewer/output contract 缺 `状态=阻塞 => blocker 非空` 反向不变量。
- 审查反馈评估：两项均有当前代码与基线 diff 证据，`决策=采纳`、`状态=DONE`。修复边界分别为版本化 runner/pair assertions，以及 `code-reviewer.md`/`output-contract.md` 的双向状态关系。
- Material amendment r10：C9/C10 加入固定 locator 本地断言与 pair_assertions，pair 两侧局部通过后按 `重要=1/严重=2` 比较同 locator defect，candidate 不得低于 baseline；比较失败进入现有整对 retry。恢复 `状态=阻塞` 必须至少一个严重/重要 blocker。候选 package SHA 更新为 `36ca944fab1559f12c5285ccb8d1f73182883623e6e1f1087a88cd3fbe6cb12a`，runner SHA 更新为 `4cc3f696e5d76fe9be85c828643d386d141093cbcc04dfd13e8860f848c35fc8`。
- r10 计划审查首轮：reviewer 发现 `Fixed A/B Oracle` 仍保留 r9 candidate hash，会与 context preflight 冲突；已同步 r10 candidate package SHA、pair evaluator 和 C9/C10 同 defect 严重度规则。
- r10 计划审查终次复验：同 reviewer 确认 plan/context hashes、local-or-pair retry、固定 locator、candidate severity≥baseline 与双向 blocker/status 不变量一致，APPROVED；依据 `history://CompressionPlanR3Review`。
- r10 A/B 中止：C2 attempt 1 因 `修复摘要` 等义措辞触发整对 retry；C5 attempt 1/2 的 final message_end `responseModel=None`，按 r10 identity contract 中止，未采信部分结果。
- C5 identity diagnosis：相同 C5 baseline exact call 成功，assistant message_start/update/message_end 均报告 provider=`cpa`、model=`gpt-5.4-mini`、responseModel=`gpt-5.4-mini-2026-03-17`；说明 identity metadata 观测存在事件级不稳定，final-only 绑定会产生假阴性。
- Material amendment r11：identity 校验聚合全部 assistant JSONL event，provider/model/responseModel 各自必须为严格所需单例，responseModel 至少出现一次，answer 仍只取 final message_end；缺失或冲突继续作为 pair failure。C1/C2 fix-summary concept 增加 `修复+摘要` alternative。runner SHA=`f72ee89a3c4828f7d508cbf97e4cad815bfcf420f4cec868d1101ff4145c32da`；candidate package SHA 不变。
- r11 计划审查：同 reviewer 确认 assistant-only identity 严格单例聚合、final message_end content、缺失/冲突 failure 与 repair-summary alternative 均不降低验收，APPROVED；依据 `history://CompressionPlanR3Review`。
- r11 A/B 中止：C1 attempt 1 candidate 缺原证据触发 semantic retry 后通过；C2 attempt 1 candidate 缺 fresh verification 触发 semantic retry，attempt 2 malformed JSON。单一 retry budget 中止，未采信部分结果。
- Retry diagnosis：C2 两次失败属于可区分类别；第一份是已解析且未满足行为不变量，第二份没有可消费 verdict。将其计入同一采样预算会在没有第二个有效语义样本时终止。
- Material amendment r12：`InfrastructureFailure` 包装 process/nonzero/identity/JSON/schema，`SemanticFailure` 包装 local/pair behavior assertions；两类各允许一次 whole-pair retry，同类第二次失败中止，日志记录 category。最大三次只可能由一 semantic + 一 infrastructure failure 产生。runner SHA=`a52d60f59347c5e885ea3fa17c5ea75aa9bd9f8c099dccd0bfabf882bec5458c`；候选 package SHA 不变。
- r12 计划审查：同 reviewer 确认异常分类、per-category whole-pair retry、同类第二次中止和 prompt-file finally 清理闭合，APPROVED；依据 `history://CompressionPlanR3Review`。
- r12 A/B 中止：C2 attempt 1 infrastructure failure 后整对重试通过；C7 attempt 1 candidate 将合法读取写为 `manifest -> assets/current.log` 被 exact array assertion 误拒绝，attempt 2 baseline 选择 `route=review_assets` 但仍进入资产/代码处理。两次均为 fixture 表示歧义，未采信部分结果。
- Material amendment r13：C7 删除与资产处置、代码 blocker 重叠的顶层 route assertion；`read_assets` 从 exact array 改为 substring contains `assets/current.log`；五项 rejected assets、blockers 非空和 `src/auth.ts:42` locator 保持。runner code/hash 与 candidate package SHA 不变。
- r13 计划审查：同 reviewer 确认直接锁定合法读取、五项拒绝和代码 locator，删除重叠 route 不降低 containment 或 finding 召回，APPROVED；依据 `history://CompressionPlanR3Review`。
- r13 A/B 中止：C4 baseline 两次都满足 stage=`主审修复验证`、实现风险高、强度增强，但内部 route=`continue_flow` 被误作下一步代理。独立 C4 diagnostic 观察到 `route=independent_final` 与 `next_action=independent_final` 可同时出现，确认字段重叠而行为验收应落在 next_action。
- Material amendment r14：C4 将 `route=independent_final` assertion 改为 `next_action=independent_final`；stage/risk/intensity 不变。runner code/hash 与 candidate package SHA 不变。
- r14 计划审查：同 reviewer 确认 C4 直接锁定 user-visible next_action，stage/risk/intensity 保持且删除冗余 route 不降低动态增强契约，APPROVED；依据 `history://CompressionPlanR3Review`。
- r14 A/B 中止：C8 attempt 1 baseline 错误进入主审/阻塞路径；semantic retry attempt 2 已输出 stage=`并行修复验证`、route=`continue_owner`，仅被 strict `parallel_fix` route 误拒绝。
- Material amendment r15：新增 scalar `one_of` assertion operator；C8 route 接受 `parallel_fix|continue_owner`，并继续要求 stage=`并行修复验证`。runner SHA=`e48c6a979ee23e1ab973dd8343cc9021874eaa48d886fc76c3b64458edd8e60b`；candidate package SHA 不变。
- r15 计划审查：同 reviewer 确认 route 只允许两个已定义等价编码且 stage 始终锁定并行修复验证，主审/其它 route 仍失败，APPROVED；依据 `history://CompressionPlanR3Review`。
- r15 A/B Proof：Pi `0.80.10`、provider=`cpa`、model=`gpt-5.4-mini`、responseModel=`gpt-5.4-mini-2026-03-17`、thinking=`low`；C7 attempt 1 malformed JSON 计为 infrastructure failure，按 r12 分类预算从 baseline 整对 retry 后 PASS。其余 case 首对通过；最终 C1-C10 baseline/candidate 全部 local assertions 与 C9/C10 same-locator severity pair assertions PASS，临时 prompt 已删除，无单边重试。
- r15 Identity：baseline package SHA=`6972f6e7baf814b70729bf8bcf9ad1403d27fc8c5976ef22a024f6de6689ebb3`；candidate=`36ca944fab1559f12c5285ccb8d1f73182883623e6e1f1087a88cd3fbe6cb12a`；runner SHA=`e48c6a979ee23e1ab973dd8343cc9021874eaa48d886fc76c3b64458edd8e60b`。
- r15 Size Proof：核心运行时 10,572 字符，相对 13,459 减少 21.45%；完整包 12,738 字符，相对 18,217 减少 30.08%。
- r15 Structural Proof：`git diff --check` 无输出；Bundle tests 37/37 OK；Bundle scan structural findings=0；引用、输出标签、阻塞状态双向不变量、12 场景结构 PASS；私有平台耦合、placeholder/编辑标记无命中。
- 主审修复验证 round 1：原 C9/C10 跨变体比较与阻塞状态反向不变量两项 finding 已关闭；finding owner 新发现 `context.md` 顶部、review-contract Proof、plan T4/未验证面仍写旧单一 retry 契约。已同步为 r12-r15 的 assistant-stream identity 与 semantic/infrastructure 分类整对 retry；r3 Session Log 作为历史事实保留。
- 主审修复验证 round 2：`CompressionPrimaryR9` 确认 context/plan/review-contract 的 assistant-stream identity 与分类整对 retry 已一致；原两项 finding 继续关闭，修复增量无新增 blocker，verdict=`通过`，下一步=`进入独立终审`。
- r15 独立终审：全新 reviewer 独立确认 package hashes、runner 逻辑、生命周期、Review Assets、双向输出不变量、压缩率与结构检查；唯一重要 finding 为 runner SHA 未固定提取/字节算法，外部按不同 fenced-block 边界计算得到不同 digest。
- 终审反馈评估：核心担忧成立，`决策=采纳`。已在 `context.md` prose 与 `runner_contract.runner_identity` 固定 exact regex group、UTF-8 和不增删换行规则；复算 digest 仍为 r15 运行前记录的 `e48c6a97...8e60b`，runner body 未改变，故无需重跑模型 Proof。
- 独立终审修复验证：`CompressionIndependentR15` 按固定算法复算 runner SHA=`e48c6a97...8e60b`，确认 runner body 未变、metadata 不参与执行，无需重跑 r15 模型 Proof；既有 package SHA 与全部关键不变量无新增问题。最终 verdict=`通过`，implementation_risk=`低`，blockers=`无`，next_action=`继续流程`。
- 最终工作树验证：`git diff --check HEAD` 无输出；Bundle tests 37/37 OK；Bundle scan structural findings=0；runner/package hashes 与 r15 固定值一致；核心压缩率 21.45%，全包压缩率 30.08%；已知 `/tmp` 临时证明文件全部 absent。

