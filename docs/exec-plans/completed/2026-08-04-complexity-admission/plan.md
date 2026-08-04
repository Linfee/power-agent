---
type: Execution Plan
scope:
  - skill-design
  - workflow-policy
status: completed
runner:
  state: DONE
  batch: 0/2
  phase: completed
  fix_round: 0/3
  next_action: none
---

# 最小充分实现与复杂性准入融合计划

## 讨论结论 / 产品结论

- 用户确认吸收 Ponytail 的“当前证据购买复杂性”与 ordered ladder，但不引入独立 Skill、mode、hook、命令族、debt/audit/gain 或常驻评测机制。
- 与 `kimi-worker` 收敛后，候选范围缩小为 planning 与 implementation 两个真实缺口：显式实现选型顺序，以及规划阶段对长期所有权的证据准入。
- 候选必须允许 null outcome：若 baseline 已稳定避免五类过度构建，或 candidate 造成 acceptance/security/Proof 回退，则撤销候选，不为完整性强行合入。

## Goal / Done Means

- 目标：在不新增工作流节点、状态、输出字段或共享 reference 的前提下，让计划与实现显式选择第一条满足当前契约的最小充分方案。
- 完成定义：候选只修改约定的三个 Skill/Prompt 文件、架构原则与短 ADR；一次性 baseline/candidate 对照未触发回滚条件；现有结构检查、独立代码审查与完成前验证通过。

## Scope

### In Scope

- 在 `proof-oriented-development` 内联最小充分实现梯子、停止规则、长期所有权证据来源与不可削减边界。
- 在 `writing-plans` self-review 中增加条件性的长期所有权证据检查。
- 在 plan reviewer 中用现有 `missing_evidence / blocking_issues / advisories` 表达准入判定，不改 schema。
- 新增短 ADR，记录维护决策、消费者投影与非目标；在 `docs/architecture.md` 增加一条设计原则。
- 运行一次性、会话级 baseline/candidate 对照；不持久化 eval runner、corpus 或 judge pipeline。

### Out of Scope

- 不修改 `skills/implement/references/task-reviewer-prompt.md`、`skills/code-review/references/code-reviewer.md`、`docs/workflow.md`、`AGENTS.md`。
- 不修改 `codebase-design`、`engineering-calibration`、`verification-before-completion` 的职责。
- 不新增 shared reference、检查脚本、frontmatter 字段、Gate、状态枚举、强度轴或运行时模式。
- 不以 LOC、token 或 diff 尺寸作为成功判据，不复制 Ponytail benchmark 数字。

## Key Decisions

- 决策：ADR 是维护决策真源，不是运行时规则入口；理由：Skill 需要独立安装，运行时不保证 `docs/adr/` 可达。执行含义：POD、writing-plans 与 plan reviewer 各自内联阶段特有投影。
- 决策：POD 内联完整操作梯子；理由：每条实现路径都需要该内容，按渐进披露规则不得下沉到永远必读的 reference。
- 决策：长期所有权只覆盖新依赖、跨模块边界、外部配置面、持久/跨请求共享状态，以及具有 init/cleanup/concurrency 语义的生命周期；局部变量、派生状态和普通内部 helper 不进入 Gate。
- 决策：所有权证据绑定当前需求、消费者或代码/运行边界，不绑定必须存在的 plan/brief；理由：POD 允许直接处理边界清楚的小改。
- 决策：plan reviewer 使用三层映射：缺证据为 `missing_evidence`；证据表明不必要或触及高风险边界为 `blocking_issue`；已有证据且仅剩轻微取舍为 `advisory`。
- 决策：task reviewer、final reviewer 与 workflow 保持不变；理由：现有独立判断、Extra、overdesign、Speculative Generality 与流程边界已经覆盖，不建立第二套约定。

## Agent 自主边界

- 可自由决策：在不改变语义的前提下收敛中文措辞、选择 ADR slug、确定 architecture 原则的链接表达，以及选择最小结构检查命令。
- 不可自行决策：扩大到新 Skill/reference/script、修改 reviewer/workflow、弱化 Proof/security/correctness、改变 plan reviewer schema，或在探针失败/null outcome 时保留候选。
- 必须保持的不变量：`codebase-design` 独占 seam/adapter 裁决；Power-Agent 的契约、风险、Proof、review、verification 优先于最小化；Skill 独立安装不依赖 ADR 可达。
- 升级条件：候选需要新增运行时状态、跨 Skill 共享规范文件、现有 reviewer 新职责或评测基础设施时停止并重新计划。

## Plan Review Gate

- Gate Revision：r4
- Plan Risk：medium
- Review Path：self-review + independent reviewer
- Plan Review Status：APPROVED
- Independent Review：approved
- Independent Review Basis：gate_revision=r4; kind=independent-review; record=Plan Review History › Gate Revision r4

## Plan Review History

### Gate Revision r1

- Self-review：通过。目标、范围、长期所有权边界、三层 reviewer 判定、null outcome、回滚条件和不修改文件均可判定；无 TODO/TBD 或未定义输出字段。
- Independent Review：issues_found
- Independent Review Basis：gate_revision=r1; kind=independent-review; record=reviewer finding “Pre-register executable paired-probe fixtures before baseline”
- Finding：五类只有抽象分类，缺少固定输入、逐例预期和 baseline 前的稳定交接位置，主证明不可审计。

### Gate Revision r2

- Self-review：通过。补充固定 shared instruction、五个完整输入、逐例 retain/reject oracle、临时合同/结果位置与 hash 不变式。
- Independent Review：issues_found
- Independent Review Basis：gate_revision=r2; kind=independent-review; record=reviewer finding “Probe real consumer boundaries independently”
- Finding：把 planning、plan review 与 implementation 三个消费边界合并为同一 arm，无法证明 T2 的 self-review 与三层 verdict 映射。

### Gate Revision r3

- Self-review：通过。按真实消费者拆分三组 invocation，每组只读取自己的运行规则。
- Independent Review：issues_found
- Independent Review Basis：gate_revision=r3; kind=independent-review; record=reviewer finding “Use complete plan packages for plan-review probes”
- Finding：plan reviewer 的 mini plan 不是其真实 PLAN_DIR_PATH 输入，无法隔离长期所有权 verdict。

### Gate Revision r4

- Amendment Authorization：用户明确选择“允许一次最终复审”，授权在三轮上限后补齐完整临时 plan package 并进行一次终局复审。
- Self-review：通过。R1–R4 均为 frontmatter、必需章节、review-contract、Gate/self-review 完整且仅 ownership 条件不同的临时 package；路径与文件 hash 已冻结在 r4 contract。
- Independent Review：approved；结论：APPROVED。三组 consumer-specific probes、四个完整临时 plan packages、hash、oracle、null/hard-fail 与回滚契约可执行且无缺口。
- Independent Review Basis：gate_revision=r4; kind=independent-review; record=Plan Review History › Gate Revision r4
- Execution Adjustment：用户要求测试避免昂贵的 `gpt-5.6-sol`；probe 模型改为 `smol`，场景、oracle、package 与回滚不变。此前 default-model baseline 输出废弃，不参与任何对照或结论。

## Evidence Cache

- `skills/proof-oriented-development/SKILL.md:24-34` 已规定每个增量的实现与 Proof 循环，但未定义实现选型顺序。
- `skills/writing-plans/SKILL.md:77-93` 已有 self-review 与 medium/high 独立 Gate，但未点名新依赖和外部配置面的当前证据要求。
- `skills/codebase-design/SKILL.md:24-41` 已通过删除测试与真实 effect/消费者证据裁决模块、seam 和 adapter，不应被新规则复述。
- `skills/code-review/references/code-reviewer.md:48-55` 已检查 unjustified abstraction、overdesign、Speculative Generality 与 Middle Man，不需要新审查维度。
- `skills/writing-skills/SKILL.md:50-57` 要求所有路径必需内容内联、只补真实行为缺口并最小修改文件，约束本次不新增 shared reference。

## Tasks

- T1 [建立决策与实现准则]：新增短 ADR；在 POD 内联 ordered ladder、停止条件、长期所有权证据来源和不可削减边界；完成信号是规则自包含且不依赖 ADR 运行时可达。
- T2 [增加规划准入]：在 writing-plans self-review 与 plan reviewer 中加入阶段特有的证据检查和三层 verdict 映射；完成信号是 low 路径由 self-review 覆盖，medium/high 路径无法带着未解释的长期所有权交棒，且 schema 不变。
- T3 [同步架构并验证]：architecture 增加一条原则，运行预注册 baseline/candidate 对照、结构检查与审查；完成信号是无 null/regression 回滚触发，scratch 已删除且排除文件零 diff。

## Proof Strategy

- 主证明：分别在 POD、writing-plans 与 plan reviewer 的真实消费边界运行同模型、同输入的 baseline/candidate；每次 invocation 只提供该消费者自己的规则。独立 reviewer 根据完整匿名输出和下方 oracle 裁决，不以 LOC 为指标。
- Arm 规则：baseline 使用改动前目标文件，candidate 使用候选文件；模型、场景、consumer instruction 与顺序完全一致，每个 invocation 使用独立上下文。

### 固定场景目录（r3）

- **P1 已有能力复用**：`仓库已有 src/time/formatDate.ts 导出 formatDate，并被三个调用方使用。任务是在第四个调用方按完全相同规则格式化日期；没有行为扩展或公共 API 变化。` Oracle：复用现有函数；新 helper/module/dependency/config/state 均为 reject。
- **P2 stdlib/native 足够**：`现代 Web 应用只支持具备 <input type="date"> 的浏览器。任务是在一个表单增加日期选择；没有自定义日历外观、日期范围或旧浏览器要求。` Oracle：采用平台原生控件；date-picker 依赖、自建日历、额外配置或状态均为 reject。
- **P3 合理的新依赖与边界**：`两个独立模块必须调用 AcmePay 外部 API。仓库没有客户端；提供方要求使用尚未安装的官方 SDK 完成签名与重试；两个消费者需要一致的错误映射。` Oracle：官方 SDK 与窄共享 adapter/boundary 为 retain；手写签名、重复集成或拒绝必要边界为失败。
- **P4 合理的配置与生命周期**：`长运行服务在启动时创建共享 worker pool。部署方必须按环境配置 endpoint 与 timeout；并发请求共享该 pool，进程关闭时必须清理。` Oracle：外部配置面、共享生命周期状态以及 init/cleanup/concurrency 语义为 retain；硬编码、每请求重建或省略 cleanup 为失败。
- **P5 安全与 Proof 护栏**：`上传处理器接收不可信文件名并写入指定根目录。必须拒绝路径穿越、保留 I/O 错误语义，且完成条件要求实际运行一个对抗性检查。` Oracle：信任边界校验、错误处理和 runnable Proof 为 retain；直接 join、吞错或仅声称测试为失败。

### Consumer A — POD implementation probe

- 规则输入：仅 `skills/proof-oriented-development/SKILL.md`。
- 固定 instruction：`只决定实现形状，不编辑文件。说明采用的方案、引入的长期所有权、每项所有权的当前需求/消费者/代码运行边界证据、更早层级为何不充分，以及必须实际运行的 Proof。不要增加场景未要求的能力。`
- 场景：P1–P5。逐例必须符合场景 Oracle；P5 还必须保留实际运行而非口头声明的 Proof。

### Consumer B — writing-plans self-review probe

- 规则输入：仅 `skills/writing-plans/SKILL.md`。
- 固定 instruction：`基于场景给出最小 Key Decisions 与 self-review 结论，不设计私有 helper 或编辑文件。若引入长期所有权，指出当前需求/消费者/代码运行边界证据及更早层级不充分理由；缺证据时明确计划不能交棒。`
- 场景：P1–P5。P1/P2 不得计划新增长期所有权；P3/P4 必须在 Key Decisions 保留并举证必要所有权；P5 不得把安全与 Proof 当作可删复杂度。

### Consumer C — independent plan-reviewer probe

- 规则输入：仅 `skills/writing-plans/references/plan-reviewer-prompt.md`；实际替换 `PLAN_DIR_PATH` 并读取下列临时完整 package，使用其现有 YAML schema。
- **R1 missing evidence**：`local://complexity-admission-probes-r4-smol-v2/R1`；除 date-fns 所有权证据外，路径、Acceptance、任务、Proof、Gate 与 review-contract 均具体合法。Oracle：`ISSUES_FOUND`，`missing_evidence` 非空，要求补证或删除；不得仅 advisory。
- **R2 blocking**：`local://complexity-admission-probes-r4-smol-v2/R2`；Evidence Cache 已确认官方 SDK 约束与两个具体消费者，但 Key Decisions 选择重复手写集成。Oracle：`ISSUES_FOUND`，`blocking_issues` 非空。
- **R3 justified dependency/boundary**：`local://complexity-admission-probes-r4-smol-v2/R3`；官方 SDK、窄 adapter、具体路径、Acceptance 与 Proof 完整。Oracle：`APPROVED`，无 missing/blocking；轻微 advisory 允许。
- **R4 justified config/lifecycle**：`local://complexity-admission-probes-r4-smol-v2/R4`；部署配置、共享 pool、具体路径、Acceptance 与生命周期 Proof 完整。Oracle：`APPROVED`，无 missing/blocking；轻微 advisory 允许。
- 预注册交接：v1 smol package 因非 ownership 的计划信息不足而在 instrument self-check 中作废，未运行 candidate。修正合同冻结在 `local://complexity-admission-probe-contract-r4-smol-v2.json`，model=`smol`，SHA-256=`eee150bbc9d65cf69dc9b4b85646b738a7e6e207984323fb46e5450a0793ac23`；完整输出写入 `local://complexity-admission-probe-results-r4-smol-v2.json`。此前 default/v1 输出全部废弃；任何文件缺失、baseline 后修改或 hash 不匹配时立即中止。
- 通过条件：candidate 修复 baseline 中可定位的 oracle 失败，三个消费者均无回退；Null outcome：baseline 的 A/B/C 全部符合 oracle，则不实施或撤销候选；硬失败：candidate 任一 oracle 失败，立即撤销候选。
- 次证明：检查 plan reviewer schema 未变、排除文件零 diff、无新 Skill/reference/script/Gate/state；运行仓库已有的 invocation/shared-reference 等相关结构检查。
- 非证明：仅阅读、仅格式化、LOC 减少、Ponytail 外部 benchmark、未运行命令或 Prompt 快照。
- 已知未验证面：小样本只作为采用闸，不证明跨模型普遍收益；不恢复本仓已删除的常驻 eval 机制。

## Blockers / Escalation

- 候选要求改变公共路由、Gate、输出 schema、Skill 调用方式或 reviewer 职责时停止并回 `writing-plans`。
- 无法在会话内形成可复查的 baseline/candidate 完整输出，或 judge 无法按预注册标准稳定区分合理与过度所有权时，不得声称行为收益。
- 发现目标文件存在用户并行修改时，不覆盖；重新读取并最小适配。

## Risks / Rollback

- 风险：新增最小化压力可能误删必要设计或把合理所有权当作缺陷。
  - 缓解：契约/消费者/风险/Proof 高于 ladder；预注册正反案例；任一回退即撤销。
- 风险：相同概念在三个阶段投影后发生语义漂移。
  - 缓解：ADR 登记消费者与两个共享语义原子；同一变更检查全部投影，但不复制长篇规范。
- 风险：一次性探针误被当作普遍有效性证明。
  - 缓解：只作采用/非回归闸；null outcome 明确允许“不改”。
- 回滚：仅撤销本计划创建或修改的候选文件；不使用 reset/clean，不触碰任务外改动。

## Optional Split Files

- none

## Execution Result

- Outcome：`NULL_OUTCOME`。`smol` baseline 的 POD P1–P5、writing-plans P1–P5、plan reviewer R1–R4 全部符合预注册 oracle；按计划不生成 candidate，也不修改 Skill、reviewer、architecture 或新增 ADR。
- 成本调整：用户要求普通测试避免昂贵的 `gpt-5.6-sol`；此前 default-model 输出与首版不完整 smol package 均作废，未参与裁决。
- Contract：`local://complexity-admission-probe-contract-r4-smol-v2.json`；SHA-256 `eee150bbc9d65cf69dc9b4b85646b738a7e6e207984323fb46e5450a0793ac23`。
- Baseline results：`local://complexity-admission-probe-results-r4-smol-v2.json`；SHA-256 `695ee5b99a5a79724865d158b2105f0f1b04889970ea37fa0ee871b527c51275`。
- Independent judgment：`local://complexity-admission-baseline-judgment-r4-smol-v2.md`；SHA-256 `b1e4291b15226d234bd9367f52aa59a0d52f92e88517920a1ca554f45f0ba34f`；`baseline_all_pass=true`、`null_outcome=true`。
- 标签说明：results JSON 的规范键为 `pod`、`planner`、`plan_reviewer`；independent judgment 展示层将 A/B 写作 planner/POD，与本计划 probe 章节的 A=POD、B=writing-plans 顺序相反。case 内容、输出映射与 oracle 核对无误，不影响 14/14 verdict。

## Proof Block

### 目标约束
- 只在 baseline 暴露可定位缺口时引入复杂性准入规则；null outcome 必须保持候选文件零改动。

### 验收标准
- 三个真实消费者的 baseline 全部按固定 oracle 裁决；若全通过，则不运行 candidate 并归档计划。

### 最小验证命令
- 会话级 `completion(..., model="smol")`：按冻结 contract 运行 14 个独立 baseline invocation，并由独立 smol judge 逐例裁决。

### 运行结果
- 状态：PASS
- 关键输出：14/14 baseline cases PASS；`baseline_all_pass=true`；`null_outcome=true`。

### 实现摘要
- 未修改任何候选 Skill、Prompt、架构文档或 ADR；仅保留本 exec-plan 作为真实决策记录。

### 风险说明
- 小样本不证明 Power-Agent 在所有模型和仓库中不会过度构建；它只证明本次预注册场景没有足够证据购买新的跨 Skill 规则。

### 未验证项
- 未运行 candidate，原因是 null-outcome 合同明确禁止在 baseline 全部通过后继续。

### 临时产物处置
- 上述 `local://` contract、packages、results 与 judgment 在独立审查消费后全部删除；不进入仓库或常驻 eval。

## Completion Verification Evidence

- 状态：`DONE`；`passed=true`；Proof Block 审计：`accepted`。
- `commit_sha`：`5f1923bc68756c277cadaded189b4cdbe88611a4`。
- `verified_at`：`2026-08-04T23:27:44Z`。
- `git status --short`：退出码 0、无输出；验证时工作区 clean。
- `git diff --name-only HEAD^ HEAD`：仅包含本计划的 `plan.md` 与 `review-contract.md`，candidate 目标未进入提交。
- `bash scripts/check-invocation-consistency.sh`：退出码 0，调用方式标志与速查表登记一致。
- `bash scripts/check-shared-references.sh`：退出码 0，共享 reference 文件一致。
- 阻塞项：无。

## 当前状态

- 当前进度：`NULL_OUTCOME` 已由 baseline 14/14、常规独立主审与 clean-HEAD 完成前验证闭合；candidate 目标零改动，会话 scratch 已清空。
- 下一步：none；计划归档到 `docs/exec-plans/completed/2026-08-04-complexity-admission/`。
