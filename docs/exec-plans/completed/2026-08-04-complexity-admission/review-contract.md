---
type: Review Contract
scope:
  - skill-design
  - workflow-policy
---

# 最小充分实现与复杂性准入 — Review Contract

## Intent

- 把 Ponytail 的 ordered ladder 与“当前证据购买复杂性”吸收到 Power-Agent 现有 planning/implementation 链路，同时拒绝独立 Skill、运行时模式、平行审查和常驻评测机制。

## Scope

### In Scope

- POD 内联最小充分实现梯子、停止规则、长期所有权证据来源与不可削减边界。
- writing-plans self-review 与 plan reviewer 增加条件性长期所有权证据准入。
- 新增短 ADR，并在 architecture 设计原则中登记。
- 运行预注册的一次性 baseline/candidate 对照，允许 null outcome 后撤销候选。

### Out of Scope

- 不修改 task reviewer、final code reviewer、workflow、AGENTS、codebase-design、engineering-calibration 或 verification 职责。
- 不新增 Skill、reference、script、Gate、状态、输出字段、mode、hook、debt/audit/gain 或常驻 eval。
- 不使用 LOC、token、成本或外部 benchmark 作为本次成功证明。

## Acceptance

- [ ] POD 的实现梯子只在满足当前契约、消费者、风险边界与 Proof 的方案间选择，并明确长期所有权证据与不可削减边界。
- [ ] writing-plans 对五类长期所有权执行条件性 self-review；plan reviewer 使用既有 schema 将缺证据、不必要/高风险和轻微取舍分别映射为 missing evidence、blocking 与 advisory。
- [ ] ADR 只记录维护决策和消费者投影，不成为 Skill 运行时依赖；architecture 仅增加一条原则。
- [ ] 排除文件零 diff，且没有新增共享 reference、检查脚本、路由、状态或评测基础设施。
- [ ] 预注册 baseline/candidate 对照未触发 null/regression 回滚；若触发则候选已撤销并如实记录结论。
- [ ] 相关结构检查、独立代码审查和完成前验证有新鲜证据。

## Agent 自主边界

- 可自由决策：在既定语义内压缩措辞、选择 ADR slug 与最小验证命令。
- 不可自行决策：扩大文件范围、改变 reviewer/schema/Gate、削减 security/correctness/Proof，或在回滚条件命中时保留候选。
- 必须保持的不变量：Skill 独立安装不依赖 ADR；codebase-design 继续裁决 seam/adapter；风险与证据优先于最小化。

## Proof

- 主证明：r4 分别在 POD、writing-plans 与 plan reviewer 的真实消费边界运行 baseline/candidate；每次只提供对应规则，使用固定场景、instruction 与 oracle。任一消费者回退即失败，三组 baseline 全部符合 oracle 即 null outcome。
- 预注册证据：用户要求 probe 使用 `smol`。v1 smol package 因非 ownership 的计划信息不足而在 instrument self-check 中作废，未运行 candidate；修正合同 `local://complexity-admission-probe-contract-r4-smol-v2.json` 已冻结，SHA-256=`eee150bbc9d65cf69dc9b4b85646b738a7e6e207984323fb46e5450a0793ac23`。R1–R4 现含具体路径、Acceptance、任务、Proof、Gate 与 review-contract；完整输出交接到 `local://complexity-admission-probe-results-r4-smol-v2.json`。此前 default/v1 输出不作为证据。
- Plan reviewer oracle：缺证据→`ISSUES_FOUND + missing_evidence`；证据表明不必要→`ISSUES_FOUND + blocking_issues`；合理依赖/边界/配置/生命周期→`APPROVED` 且无 missing/blocking，schema 不变。
- 次证明：目标文件结构与引用检查、排除文件零 diff、无新机制检查、独立代码审查。
- 非证明：LOC 减少、外部 Ponytail benchmark、仅阅读或 Prompt 快照。
- 已知未验证面：小样本不证明跨模型普遍收益，不恢复常驻 eval。

## Blockers / Escalation

遇到以下情况必须停止并请求确认：

- 需要新增运行时状态、独立 Skill/reference/script、修改 reviewer 职责或改变现有 Gate/schema。
- 无法产生可复查的 baseline/candidate 证据，或 probe/judge 无法按预注册标准裁决。
- 发现任务外并行改动会被覆盖。

## Risks

- 风险：最小化压力误杀必要抽象、依赖、配置、状态或 Proof。
  - 决策状态：可由预注册正反 probe 与现有 review/verification 闭合。
  - 缓解方式：五类探针同时包含应删除与应保留案例；任何回退即撤销。
  - 执行期阻塞条件：candidate 出现 acceptance/security/data/Proof 回退或错误 blocking。
- 风险：三个阶段投影发生语义漂移。
  - 决策状态：可由 ADR 消费者矩阵和同变更核对闭合。
  - 缓解方式：只共享两个语义原子，不复制完整段落或建立 shared reference。
  - 执行期阻塞条件：必须复制新的长规范才能保持一致。

## Plan Review Gate

- Gate Revision：r4
- Plan Risk：medium
- Review Path：self-review + independent reviewer
- Plan Review Status：APPROVED
- Independent Review：approved
- Independent Review Basis：gate_revision=r4; kind=independent-review; record=Plan Review History › Gate Revision r4

## Plan Review History

### Gate Revision r1

- Gate Revision：r1
- Independent Review：issues_found
- Independent Review Basis：gate_revision=r1; kind=independent-review; record=reviewer finding “Pre-register executable paired-probe fixtures before baseline”

### Gate Revision r2

- Gate Revision：r2
- Independent Review：issues_found
- Independent Review Basis：gate_revision=r2; kind=independent-review; record=reviewer finding “Probe real consumer boundaries independently”

### Gate Revision r3

- Gate Revision：r3
- Independent Review：issues_found
- Independent Review Basis：gate_revision=r3; kind=independent-review; record=reviewer finding “Use complete plan packages for plan-review probes”

### Gate Revision r4

- Gate Revision：r4
- Amendment Authorization：用户明确允许一次最终复审。
- Independent Review：approved；结论：APPROVED。三组 consumer-specific probes 与完整临时 package 契约可执行。
- Independent Review Basis：gate_revision=r4; kind=independent-review; record=Plan Review History › Gate Revision r4
- Execution Adjustment：用户要求 probe 使用 `smol`；场景、oracle、package 与回滚不变，default-model 输出不作为证据。

## Execution Disposition

- Outcome：`NULL_OUTCOME`。低成本 `smol` baseline 的三个 consumer 组共 14 个 case 全部符合冻结 oracle。
- Candidate：未生成；POD、writing-plans、plan reviewer、architecture、ADR 及明确排除文件均保持不变。
- 证据摘要：contract `eee150bb…ac23`；baseline results `695ee5b9…1275`；independent judgment `b1e4291b…a34f`。
- 契约满足：Acceptance 中候选行为项按 null-outcome 分支为 N/A；“若触发则候选已撤销并如实记录结论”已满足。

## Review Focus

- 判断新增规则是否对应本仓真实边际缺口，范围是否保持最小，null outcome 是否可执行，以及 Proof 是否能防止“为了少而削减正确性与证据”。
