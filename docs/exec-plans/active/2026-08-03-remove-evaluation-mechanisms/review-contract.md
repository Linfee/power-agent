---
type: Review Contract
scope:
  - evals/**
  - skills/**
  - scripts/**
  - docs/**
  - .gitignore
---

# 移除 Skill 评测机制 — Review Contract
## Current applicability

本文档是旧计划的审阅快照，不定义当前运行时 Gate、固定审阅路径或 Skill 依赖。恢复相关工作前，依 [ADR-0010](../../../adr/0010-judgment-oriented-skills.md) 重新判断当前范围和证据。


## Intent

- 按用户明确要求，彻底移除 Power-Agent 用来评估自身 Skill 路由、行为和工作流遵循的 eval 基础设施；不把目标项目的普通验证、Proof、review 或 docs scanner 误删为 eval。

## Scope

### In Scope
- 删除 `evals/`、routing-eval 方法和作为 Skill 自我评测 corpus 的压力场景 reference；从 `.gitignore` 移除 eval 专属规则，并在删除前迁出仍承担运行时契约的规则。
- 移除 live Skill、架构/开发/工作流文档和 active `codebase-design-skill` plan 中对这些机制的依赖；保留 invocation/shared-reference consistency scripts。

### Out of Scope
- 普通项目测试、Proof Block、代码审查、最终验证、docs scanner。
- 已归档计划和外部评测调研笔记中的历史记录。

## Acceptance

- [ ] 不存在 `evals/`、路由评测 reference 或作为 Skill 自我评测 corpus 的压力场景 reference；`.gitignore` 不保留 eval 专属规则。
- [ ] 所有仍在维护的 Skill 与 live 文档不再要求或链接到已删除的 Skill eval 资产，同时普通 consistency scripts 仍可用且不引用删除资产。
- [ ] active `codebase-design-skill` plan/review contract 已 material amendment，且不再将评测或其脚本作为范围、验收或证明。
- [ ] 普通验证、Proof、review、docs scanner 与必要运行时契约仍保留且没有失效引用。

## Agent 自主边界

- 可自由决策：删除 eval 专属资产，并作最小文本改写清除直接 consumer。
- 不可自行决策：删除普通验证体系、改写 archived execution plan 历史或修改外部仓库。
- 必须保持的不变量：剩余 live 链接有效；active plan/review contract 的 Gate 元数据一致；没有可执行或强制性的本仓 Skill eval 机制。

## Proof

- 主证明：基于删除/consumer manifest 定点搜索 live `skills/`、`docs/`、`scripts/` 与根配置，确认不再存在已删除路径、路由评测或压力场景要求；同时确认被保留的一致性脚本不引用删除资产。
- 次证明：确认删除路径不存在；复读 active plan/review contract 的范围、Proof 和 Gate 字段，并核对受影响的剩余 Markdown 引用可解析。
- 非证明：仅格式化、仅宽泛关键字搜索、或运行已删除的评测。
- 已知未验证面：不再对本仓 Skill 做模型行为评测；这是用户明确要求移除的能力。

## Blockers / Escalation

遇到以下情况必须停止并请求确认：

- 某路径经证据表明是普通项目验证或生产行为所必需，而非 Skill eval 专属资产。

## Risks

- 风险：删除过宽会移除目标项目验证或使在途 codebase-design plan 的现有 Gate 失真。
  - 决策状态：已由用户确认删除 eval；普通验证和 archived 历史受范围保护。
  - 缓解方式：删除前映射所有 direct consumers，并以 material amendment 同步在途 plan。
  - 执行期阻塞条件：无法区分候选文件的 eval 与普通验证职责。

## Plan Review Gate

- Gate Revision：r3
- Plan Risk：medium
- Review Path：self-review + independent reviewer
- Plan Review Status：APPROVED
- Independent Review：approved
- Independent Review Basis：gate_revision=r3; kind=independent-review; record=Plan Review History › Gate Revision r3

## Plan Review History

### Gate Revision r1

- Gate Revision：r1
- Independent Review：issues_found
- Independent Review Basis：gate_revision=r1; kind=independent-review; record=Plan Review History › Gate Revision r1
- Findings：`check-invocation-consistency.sh` 与 `check-shared-references.sh` 是普通结构检查，必须保留；`.gitignore` 的 eval 专属规则必须纳入删除和主证明。

### Gate Revision r2

- Gate Revision：r2
- Independent Review：issues_found
- Independent Review Basis：gate_revision=r2; kind=independent-review; record=Plan Review History › Gate Revision r2
- Findings：`.gitignore` 是 root-level eval consumer，必须加入计划与 review contract 的正式 scope。

### Gate Revision r3

- Gate Revision：r3
- Independent Review：approved
- Independent Review Basis：gate_revision=r3; kind=independent-review; record=Plan Review History › Gate Revision r3
- Finding：approved；r2 root-scope finding 已修复，无新增阻塞问题。

## Review Focus

- 核对“完全删除 eval”与“保留普通验证及一致性检查”边界是否清晰、删除范围是否完整，以及 active codebase-design plan 的 material amendment 是否纳入验收。
