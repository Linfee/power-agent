---
type: Execution Plan
scope:
  - evals/**
  - skills/**
  - scripts/**
  - docs/**
  - .gitignore
status: active
runner:
  state: AWAITING_COMMIT
  batch: 2/2
  phase: worktree-gate
  fix_round: 1/3
  next_action: commit-then-run-final-verification
---

# 移除 Skill 评测机制实现计划

## 讨论结论 / 产品结论

- 用户明确要求：完全删除本仓的 eval 机制。
- 保留目标项目的普通验证、Proof Block、代码审查和文档健康检查；它们不是本仓 Skill 的 eval 基础设施。

## Goal / Done Means

- 目标：移除本仓用于评估 Skill 路由、行为或工作流遵循的资产、执行入口和强制流程。
- Done Means：`evals/`、eval 专用脚本、路由评测方法与压力场景资产不存在；所有仍在维护的 Skill、工作流文档和 active plan 均不再要求或引用这些机制。
- 不做事项：不删除目标项目的测试/验证指导、Proof Block、review、文档 scanner 或历史完成计划中对已发生评测的事实记录。

## Scope

### In Scope
- 删除整个 `evals/`（包含路由、行为、文档和 codebase-design 评测资产、基线、快照与缓存），并从 `.gitignore` 删除其专属忽略规则。
- 删除 `routing-eval.md` 与作为本仓 Skill 自我评测 corpus 的压力场景 reference；若其中承载仍需保留的运行时规则，先迁入对应主 Skill 或一般 reference，再删除场景文件。
- 移除 `writing-skills` 中的路由评测、压力场景、无操作运行裁决及其完成门槛；保留准确性、单一职责、渐进披露、调用方式与其机械一致性检查。
- 同步 live Skill 文档、架构/开发/工作流文档与 active `codebase-design-skill` plan/review contract，使其不引用被移除资产或将评测作为验收/主证明。

### Out of Scope
- 删除普通代码测试、项目验证、Proof Block、最终验证、代码审查或 docs scanner。
- 改写 `docs/exec-plans/completed/` 的历史事实。
- 删除仅记录外部项目评测研究的 `docs/references/superpowers-and-mattpocock-evaluations.md`。

## Key Decisions

- 决策：按“Skill 自我评测机制”而非“所有验证活动”定义删除范围。
  - 原因：用户要求完全删除 eval 机制，但普通验证与审查承担目标项目/交付物正确性，不是 Skill 路由或行为的判分系统。
  - 证据：`evals/` 存放路由、行为、文档与 codebase-design corpus/runner；`skills/writing-skills/references/criteria.md` 将路由评测与压力场景定义为两层评测。
  - 执行含义：删除 eval 专属资产和契约，保留 Proof、review、scanner 与目标项目测试指导。
- 决策：当前 active `codebase-design-skill` plan 是 live consumer，必须 material amendment；completed plans 保留历史记录。
  - 原因：该 active plan 将路由/行为评测作为 scope、acceptance 与主证明；删除资产后原验收不可成立。其 invocation consistency script 是普通结构检查，继续保留。
  - 证据：`docs/exec-plans/active/2026-08-03-codebase-design-skill/{plan,review-contract}.md`；`scripts/check-invocation-consistency.sh` 只核对 frontmatter 与 `AGENTS.md` 索引。
  - 执行含义：在同一改动中更新其当前范围、证明和状态，不重写归档计划，也不删除一致性检查。

## Agent 自主边界

- 可自由决策：识别 eval 专属 reference 的所有直接 consumer，采用最小删除或文档改写消除悬挂引用。
- 不可自行决策：不得删除普通验证、review、Proof、docs scanner，或改写 completed plan 的历史结论。
- 必须保持的不变量：所有剩余 Markdown 链接有效；active plan 与 review contract 的同名 Gate 字段一致；不存在可执行或强制性的本仓 Skill eval 路径。
- 触发升级条件：某个候选删除项是普通生产/目标项目验证所需，或删除将改写用户未授权的外部/生产配置。

## Plan Review Gate

- Gate Revision：r3
- Plan Risk：medium
- Review Path：self-review + independent reviewer
- Plan Review Status：APPROVED
- Independent Review：approved
- Independent Review Basis：gate_revision=r3; kind=independent-review; record=review-contract.md#gate-revision-r3

## Evidence Cache

- [事实] `evals/` 含 `writing-skills`、`documentation-skills`、`codebase-design` 的 runner、corpus、baseline、snapshot 与缓存；`.gitignore` 有对应 sealed baseline 忽略规则；影响：删除目录和过期根配置，避免残留可运行 eval 或其配置。
- [事实] `writing-skills`、`development.md`、`skill-and-harness-design.md`、`workflow.md` 和 active codebase plan 直接要求路由评测/压力场景；影响：删除资产后必须同步这些 live consumer。
- [事实] `check-invocation-consistency.sh` 与 `check-shared-references.sh` 分别核对索引一致性和共享 reference 漂移，未运行 judge/corpus/model；影响：作为普通结构检查保留。

## Tasks

- T1 [删除评测资产]：删除 `evals/`、路由评测 reference 与评测用途的压力场景 reference；先迁出任何仍承担普通运行时契约的规则。完成信号是这些 eval 路径均不存在、保留的规则不再以场景 corpus 形式存在。
- T2 [移除评测契约]：更新 Skill 文本、`.gitignore`、live 架构/开发/工作流文档，删除对路由评测、压力场景、eval runner 和 baseline 的要求与链接；保留 invocation/shared-reference consistency scripts 的普通维护职责。完成信号是保留文档不含已删除路径或强制评测语言。
- T3 [修订在途计划]：对 active `codebase-design-skill` plan/review contract 做 material amendment，去除评测资产与评测验收，保留 Skill 的功能目标、必要的结构一致性证明与 invocation consistency check；完成信号是两份材料 Gate revision/history 和范围/Proof 一致。

## Proof Strategy

- 主证明：使用删除/consumer manifest 对 live `skills/`、`docs/`、`scripts/` 与根配置做定点引用搜索；确认每个删除路径、路由评测和压力场景要求均已移除，保留的验证术语和 consistency scripts 不引用删除资产。
- 次证明：读取 `evals/` 与所有删除路径确认不存在；复读改写后的 active plan/review contract，确认 Gate 字段与范围一致，并核对受影响的剩余 Markdown 引用可解析。
- 非证明：只删除目录、Markdown 格式化或宽泛搜索到“评测”一词；completed plan 和外部研究笔记中的历史陈述不构成 live mechanism。
- 已知未验证面：不运行已被删除的 eval，也不验证这些 Skill 在真实模型中的行为；这是用户要求的机制移除结果。
- 失败解释：若仍有 live reference 或剩余执行入口，说明删除不完整；若普通验证被误删，说明删除范围越界。

## Blockers / Escalation

- 阻塞条件：发现资产同时是普通项目验证的唯一入口，且无法从仓库证据区分其归属。
- 升级对象：用户。
- 升级时携带材料：该路径、直接 consumer、删除影响与保守替代范围。

## Risks / Rollback

- 风险：当前 active `codebase-design-skill` 计划的已批准评测 Gate 被删除后不再表达真实验收。
  - 失败信号：plan/review contract 对 Scope、Proof 或 Gate revision 不一致。
  - 缓解方式：以 material amendment 同步两份材料，并保留 prior revision history。
  - 回滚方式：从版本控制恢复删除的资产与对应文档改动。
- 风险：删除过宽，误伤普通验证。
  - 失败信号：剩余 Skill 或文档出现失效引用，或删除项被识别为目标项目测试/扫描器。
  - 缓解方式：只删除本计划枚举的 eval 专属资产，以定点引用搜索复核。
  - 回滚方式：从版本控制恢复误删文件。

## Optional Split Files

- none

## 当前状态

- 当前进度：T1-T3 已完成，task-scoped review 已发现并修复三项问题；工作区尚有未提交改动。
- 本次补充：`writing-skills` 仅可对有明确来源的实际回避模式增加纪律防御，并写明可观察条件与替代动作；直接界定行为缺口或现有契约的基础规则不受此限，且不恢复压力场景、runner、corpus 或模型行为评测。
- 下一步：提交任务范围改动后，按 Proof Strategy 做最终验证并归档。
