---
type: Decision
status: superseded
verification:
  strategy: historical
superseded_by: ../0014-current-baseline.md
---

# ADR-0008: 复杂性准入——ordered ladder 与证据购买的长期所有权

> 历史记录：已由 [ADR-0014](../0014-current-baseline.md) 归并取代。下文的决定、状态说明与旧 Skill 名称保留当时含义，不作为当前指令。

**状态：** accepted
**日期：** 2026-08-04
**影响文件：** `skills/proof-oriented-development/SKILL.md`, `skills/writing-plans/SKILL.md`, `skills/writing-plans/references/plan-reviewer-prompt.md`, `docs/architecture.md`

## 背景

计划与实现此前未定义实现选型顺序：已有能力、stdlib/平台原生、已有依赖与最小直接实现之间的选择依赖隐性判断，长期所有权（新依赖、跨模块边界等）也缺少证据准入。r4 对照实验显示既有行为在固定场景下已稳定避免五类过度构建，但用户仍在 `feat/complexity-admission` 分支授权以显式政策固定“当前证据购买长期所有权”与 ordered ladder，即吸收 Ponytail 的方法论而不引入其产品机制。

## 共享语义原子

1. **ordered ladder**：不新增，复用仓库已有实现/函数/API/模块 → stdlib/平台原生 → 已有依赖 → 满足当前契约的最小直接实现。在第一条满足当前契约、消费者、风险边界与 Proof 的层级停止；契约、消费者与 Proof 高于层级本身。
2. **长期所有权**：仅指新依赖、跨模块边界、外部配置面、持久/跨请求共享状态，以及具有 init/cleanup/concurrency 语义的生命周期；局部变量、派生状态和普通内部 helper 不进入 Gate。

## 长期所有权证据来源

每项长期所有权必须由当前需求、真实消费者或代码/运行边界举证，并说明更早层级为何不充分。Key Decisions / Evidence Cache 中具体、无保留且未冲突的已确认需求、提供方约束或仓库事实本身就是当前证据；只有事实缺失、标为 unknown/unconfirmed 或与其它证据冲突时才需要补充来源指针。已确认的提供方约束（如必须使用官方 SDK）本身足以排除不满足契约的 stdlib、已有依赖或手写直接实现。证据购买的是所有权类别本身：运行边界已直接要求外部配置、共享状态或生命周期时，不必提前指定私有实现机制或库；计划另行引入的新依赖或跨模块边界仍须具体举证。证据不绑定必须存在的 plan/brief；缺证据时计划不得交棒。

## 消费者矩阵

| 消费者 | 投影 |
|--------|------|
| `proof-oriented-development` | 内联完整 ordered ladder、停止条件、证据来源与不可削减边界（每条实现路径都需要，按渐进披露不得下沉到 reference） |
| `writing-plans` self-review | 条件性长期所有权证据检查；low 路径由 self-review 覆盖 |
| plan reviewer | 用现有 `missing_evidence / blocking_issues / advisories` 表达准入判定，不改 schema |

## 非目标

- 不引入 Ponytail 产品机制：无独立 Skill、mode、hook、命令族、debt/audit/gain 或常驻评测。
- 不新增 shared reference、检查脚本、frontmatter 字段、Gate、状态枚举或输出字段；三个消费者各自内联阶段特有投影。
- 不建立第二套 seam/adapter/模块深度裁决入口：`codebase-design` 保持独占，`engineering-calibration` 与 `verification-before-completion` 职责不变。
- task reviewer、final reviewer 与 workflow 保持不变；不以 LOC、token 或 diff 尺寸作为成功判据。
- 本 ADR 仅是维护决策真源，不是运行时规则入口：Skill 独立安装时运行时不保证 `docs/adr/` 可达，各消费者规则必须自包含。

## 后果

- 计划与实现显式选择第一条满足当前契约的最小充分方案，过度构建有可引用的判定依据。
- 相同语义在三处投影，漂移风险由本 ADR 登记消费者与两个共享语义原子缓解；同一变更必须同步全部投影。
- 一次性探针只作 non-regression 闸，不构成跨模型普遍有效性的证明。
- 维护决策（含本 ADR 的修订）只更新文档与消费者文件，不引入任何运行时机制。
