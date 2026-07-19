---
type: Process
scope:
  - workflow
---

# 工作机制与 Skill 协调

本文档描述 power-agent 的完整工作机制：各 Skill 的职责边界、产出物、以及它们之间如何协调。

---

## 核心设计原则

**Skill 是执行单元，人类可按需参与决策。** 每个 Skill 只做一件事，通过明确的输入/输出协议与其他 Skill 协作。规划阶段以独立审查闭合可执行性；实现阶段使用轻量启动通知，Agent 自主闭环，worktree 沙盒兜底（ADR-0006）。

**产出物是协调介质。** 默认链路中，discuss 经独立审查通过的需求结论由 writing-plans 折叠进 exec-plan；只有用户或流程明确需要时才额外落盘 spec 文档。Skill 之间的长期状态主要通过 exec-plan 文件、代码、docs 文档传递，避免把上游讨论记录复制成第二套真源。

## 状态协议速查

本项目不使用全局单一状态枚举。每个 Skill 保留自己的输出协议，但上下游交接必须显式写清字段与映射。

| Skill / 场景 | 状态值 | 下游消费规则 |
|--------------|--------|--------------|
| `writing-plans` plan review | `SELF_REVIEWED / PENDING_INDEPENDENT_REVIEW / APPROVED / ISSUES_FOUND` + Gate Revision | low self-review 后可交棒；medium/high 需 reviewer APPROVED |
| `plan-impl` 实现/修复子代理 | `DONE / DONE_WITH_CONCERNS / BLOCKED / UNKNOWN` | `DONE*` 可继续；`BLOCKED/UNKNOWN` 需要补上下文、拆分、重试或升级 |
| `plan-impl` 单内部 reviewer | `DONE / DONE_WITH_CONCERNS / BLOCKED` + Spec/Quality 双 verdict | `BLOCKED` 进入 fix loop；`DONE_WITH_CONCERNS` 必须闭合 Cannot Verify From Diff；连续同类问题无收敛则升级 |
| `requesting-code-review` 全量审查 | `通过 / 通过_含建议 / 阻塞 / 需澄清` + 主审、主审修复验证、独立终审、终审修复验证、并行审查阶段 | 常规主审收敛后进入工作区检查；增强主审收敛后进入全新 reviewer 独立终审；dirty / 无 HEAD 先提交，clean 且有 HEAD 后进入最终验证 |
| `plan-impl-lightweight` | `DONE / DONE_WITH_CONCERNS / BLOCKED / UNKNOWN` + `path_decision` | `path_decision=lightweight` 且 `DONE*` 可继续；`ask_user/escalate_to_full` 暂停轻量执行并回到用户或完整 runner |
| `receiving-code-review` 反馈评估 | `DONE / BLOCKED` | `DONE` 表示反馈已完成采纳/驳回判断；`BLOCKED` 等待澄清 |
| `verification-before-completion` | `DONE / PARTIAL / BLOCKED` | 仅 `DONE` 且 `passed=true` 可交给分支收尾；输出 `commit_sha/passed/verified_at/evidence[]` |
| `finishing-a-development-branch` | `READY / BLOCKED / DONE / CANCELLED` | dirty / 无 HEAD 时 `READY + mode=uncommitted` 提示提交；clean 且验证通过后进入标准分支处置 |

---

## 完整工作流图

```
┌─────────────────────────────────────────────────────────┐
│                    需求阶段                               │
│                                                         │
│   discuss skill                                         │
│   输入：模糊需求                                           │
│   产出：内联 Discussion Conclusion / 需求结论                │
│        （仅按需落盘 docs/specs/YYYY-MM-DD-<topic>.md）       │
│   审查：独立 reviewer 子代理审查                              │
└─────────────────────┬───────────────────────────────────┘
                      │ 经审查通过的需求结论（或用户直接描述功能）
                      ▼
┌─────────────────────────────────────────────────────────┐
│                 规划阶段                                  │
│                                                         │
│   writing-plans skill                                   │
│   输入：需求结论 / spec 文档 / 用户描述                       │
│   产出：docs/exec-plans/active/YYYY-MM-DD-title/         │
│           plan.md + review-contract.md                  │
│           （按需拆出 context.md / tasks.md）               │
│   gate：low=self-review；medium/high=独立 reviewer             │
└─────────────────────┬───────────────────────────────────┘
                      │ compact exec-plan（人类默认只审 review-contract.md）
                      ▼
┌─────────────────────────────────────────────────────────┐
│                 实现阶段                                  │
│                                                         │
│   plan-impl skill（状态机自主闭环）                  │
│   ├── BOOTSTRAP：using-git-worktrees 检测/建立隔离工作区      │
│   ├── PATH：中小任务可走 plan-impl-lightweight              │
│   ├── EXECUTING：依赖驱动批次并行 + conflict_check/review/fix │
│   ├── REVIEWING：requesting-code-review 全量审查            │
│   ├── WORKTREE GATE：dirty || !has_head → 待提交；clean && has_head → VERIFYING │
│   ├── VERIFYING：verification-before-completion          │
│   └── FINALIZING：finishing-a-development-branch        │
└─────────────────────┬───────────────────────────────────┘

调试路径（独立入口）：
   systematic-debugging skill
       └── [status=FIXABLE && execution_authorization=granted + matching basis] → proof-oriented-development skill
               └── Proof Block → requesting-code-review → 工作区检查 → verification-before-completion skill
       └── [status=ESCALATE] → discuss 或 writing-plans
```

---

## 各 Skill 详解

### discuss — 需求讨论与 PRD 细化

**触发：** 需求模糊、PRD 不完整、功能范围/用户流程/验收标准不清，或存在真实产品/上层技术方向取舍。

**输入：** 用户描述、PRD 草稿、issue、截图或其他需求材料。

**核心流程：**
1. 建立上下文，识别已明确、冲突和缺失的信息。
2. 判断是否需要拆分；复杂需求先收敛到一个最小闭环。
3. 分批澄清目标、范围、用户流程、关键状态、异常路径、验收标准，以及影响范围/验收/planning 的上层技术方向。
4. 按问题判断是否使用 HTML 可视化辅助；视觉/流程/关系/方案对比复杂时一屏一决策。
5. 仅在真实分歧存在时呈现 2-3 个产品方案或上层技术方向对比，先给推荐，再说明取舍。
6. 默认产出内联 `Discussion Conclusion` / `需求结论`，先自查占位符、歧义、范围膨胀，以及是否滑入可直接编码的实现细节。
7. 启动独立 reviewer 子代理审查；blocking issue 修正后重新审查。
8. reviewer 通过后交给 `writing-plans`；只有用户明确要求、合规/流程要求或需要长期产品资产时，才按需落盘 spec/doc。

**产出：** 内联 `Discussion Conclusion` / `需求结论`；按需 `docs/specs/YYYY-MM-DD-<topic>.md`

**交棒给：** `writing-plans`（需求结论经独立审查通过后）

**不做：** 不写任何代码，不创建 exec-plan，不做接口签名、数据表/字段、库选型、类/函数拆分、文件路径等实现细节；允许讨论影响范围/验收/planning 的上层技术方向。结论存在 planning 阻塞缺口时，先修复并重新审查。

---

### writing-plans — 实现计划创建

**触发：** 用户要求创建 exec-plan，discuss 需求结论经独立审查通过后，或 `dev-docs` skill 路由。

**输入：** 经独立审查通过的需求结论 / spec 文档 / 用户描述 + 相关代码库上下文

**核心流程：**
1. 读取需求结论、spec 或用户描述，以及直接相关代码/文档。
2. 默认生成 compact exec-plan：`plan.md + review-contract.md`；仅在证据昂贵、上下文过大、任务图复杂或多 Agent 交接需要时拆出 `context.md / tasks.md`。
3. `plan.md` 是执行真源，包含目标、Scope、关键决策、Agent 自主边界、紧凑任务、Proof Strategy、阻塞/升级条件和风险。
4. `review-contract.md` 是人类默认审阅面：人类只审意图、范围、验收、证明策略、Agent 自主边界、阻塞条件和高风险项，不逐行审执行材料。
5. 所有计划执行 inline self-review，并确定 `plan_risk=low|medium|high`。
6. `low` 直接交棒；`medium/high` 增加一个独立 `tech-plan-reviewer`，通过后直接交棒。
7. 提供执行选项（推荐 `plan-impl`）。

**产出：** `docs/exec-plans/active/YYYY-MM-DD-title/plan.md + review-contract.md`，按需 `context.md / tasks.md`

**交棒给：** `plan-impl`

---

### plan-impl — 执行编排

**触发：** writing-plans 交棒，或用户手动恢复执行。

**状态机：** BOOTSTRAP → READY → EXECUTING → REVIEWING → 工作区检查（dirty / 无 HEAD 先待提交；clean 且有 HEAD 进入 VERIFYING）→ VERIFYING → FINALIZING → DONE（异常：ESCALATED / CANCELLED）

**核心流程：**
1. BOOTSTRAP：读取弹性计划包（必读 `plan.md` frontmatter 中的 `runner` 恢复状态，读取 `review-contract.md` 人审边界，按存在情况读取 `context.md / tasks.md`），调用 `using-git-worktrees` 检测/建立隔离工作区；不读取 HTML runner 注释
2. READY：确认 `plan.md` 中任务、依赖、Proof、阻塞条件完整，并比对两份材料同名的 Gate Revision、风险、状态与 revision-bound basis；medium/high 的 pending、缺失、冲突或 basis 不匹配一律停止在 READY。若存在 `tasks.md` 则消费拆分任务图；中等偏小、边界清楚、局部验证充分的任务可转交 `plan-impl-lightweight`
3. EXECUTING：拓扑排序 tasks（来自 `plan.md` 或可选 `tasks.md`），优先检测并使用 team 模式承载 batch、review、fix、verify；缺少 team 工具且不适合轻量路径时回退为按批次并行派发实现子代理，无法并行时改为单个实现子代理推进；task brief、实现 report 和 review package 经 `.power-agent/review-runs/` scratch artifacts 交接，并在批次内执行 conflict_check / 单 reviewer 双 verdict / fix loop；修复后优先由原 reviewer 验证，不能继续时使用替代 reviewer
4. REVIEWING：调用 `requesting-code-review`（最终验证前默认强制，用户明确跳过除外）；常规审查由单主审收敛，增强审查在主审收敛后增加全新 reviewer 独立终审
5. WORKTREE GATE：dirty 或仓库尚无 HEAD 时调用 `finishing-a-development-branch` 展示待提交提示；提交后重新执行 gate。只有 clean 且 `has_head=true` 时进入 VERIFYING
6. VERIFYING：调用 `verification-before-completion` 审计 Proof Block / 等价证据块，必要时补跑最小额外验证，并输出 `verification_evidence`
7. FINALIZING：调用 `finishing-a-development-branch`，按收尾状态归档或保留恢复点

**产出：** 实现代码变更 + Session Log + 归档 exec-plan

**调用链：** `plan-impl-lightweight`（可选轻量分支）→ proof-oriented 实现子代理（Proof Block 写入 report artifact）→ runner 单 reviewer 双 verdict → `requesting-code-review`（最终验证前）→ 工作区检查（dirty / 无 HEAD 先提交）→ `verification-before-completion` → `finishing-a-development-branch`

`requesting-code-review` 是最终验证前默认强制的全量审查编排器；仅当用户明确要求跳过时可跳过，并在 Session Log 记录原因。`dev-docs-maintain` 是在 docs 健康检查、漂移修复或 verification ledger 登记需要时按需触发的普通 Skill，不是每次开发执行的固定阶段。

---

### plan-impl-lightweight — 轻量执行路径

**触发：** 中等偏小任务，边界清楚、风险较低、局部验证足以证明完成。

**核心流程：** `scope_check -> execute -> targeted_verify -> review -> fix_once(最多一次)`。

**输出：** `状态：DONE / DONE_WITH_CONCERNS / BLOCKED / UNKNOWN` + `path_decision: lightweight / escalate_to_full / ask_user`。

**交棒规则：** `path_decision=lightweight` 且 `DONE*` 可继续；`ask_user` 暂停等待澄清；`escalate_to_full` 回到 `plan-impl` 完整路径或先创建 exec-plan。

**不做：** 不做 team/多代理编排，不处理恢复点或多 batch 复杂依赖，不承担分支收尾。


---

### proof-oriented-development — 证明导向实现

**触发：** 由 plan-impl 派发任务卡，或用户直接触发实现功能、编写代码、证据交付、最小有效验证；只有用户明确要求 TDD / 测试驱动 / 先写失败测试时才启用 strict TDD。

**铁律：** 没有低成本、可复现、与任务强相关的 Proof Block，就不能声称当前增量完成。

**核心流程：** Scope Slice → Proof Plan → Implement → Run Minimal Relevant Verification → Interpret Result → Emit Proof Block

**产出：** 实现代码 + Proof Block（目标约束、验收标准、最小验证命令、运行结果、实现摘要、附加证据、风险说明、未验证项）

**交棒给：** `requesting-code-review`；审查通过后进入工作区检查，dirty 或仓库尚无 HEAD 时先进入待提交提示，clean 且有 HEAD 后进入 `verification-before-completion`（全量回归与最终完成验证）

---

### systematic-debugging — 探索式根因调查

**触发：** bug、测试失败、性能退化、flaky 或意外行为。

模型默认沿“确认信号 → 建立并收紧 loop → 复现/按需最小化 → 竞争解释 → 单个区分性探针 → 因果闭合”推进，也可依据证据偏离；不得越过系统、安全、授权和项目红线。反馈循环需对应精确症状并记录实际观察、重复性和局限，本地不可运行时可使用安全的 trace/log/artifact observation boundary。

`FIXABLE` 的 canonical handoff 必填：`causal_explanation`、`evidence_refs`、`fix_boundary`、`target_behavior`、`verification_path`、`execution_authorization`、`execution_authorization_basis`。授权状态为 `granted | missing | unknown`，basis 记录授权来源、覆盖动作/边界及专项确认，只表达是否允许实施，不改变诊断完成度；仅 `granted` 且 basis 匹配当前动作时可进入 POD。`verification_path` 在 minimal/original 不同时保留映射并要求修后双重复验；实际创建过临时产物时 `temporary_artifacts` 必填并记录 removed/retained disposition。`bug_class` 和 `recommended_proof_strategy` 仅为可选信息。

性能验收或存在合理性能/稳定性影响面时，POD 与 VBC 必须消费风险相称、同口径的 baseline/candidate 或重复观测证据；无影响面可记录 `not_applicable`，不机械要求 benchmark。

**路由：** `FIXABLE + granted + matching basis` → `proof-oriented-development`；`FIXABLE + missing|unknown|basis mismatch` → 保留 handoff 并请求最小授权；`ESCALATE` → `discuss` 或 `writing-plans`；其它状态继续调查或解除阻塞。只有继续调查本身需要越权动作时才因授权进入 `BLOCKED`。

---

### requesting-code-review — 全量审查编排

**触发：** 实现完成后、最终验证前默认强制触发；合并/PR 前若尚未完成全量审查，也必须触发，除非用户明确要求跳过并记录原因。

**核心流程：**
1. 评估变更重要性等级（低/中默认常规，高默认增强）
2. 收集标准审查输入；只有当前 review session 提供显式 `review-assets.md` 时才传辅助资产，同时传权威 review run root、可比较的 review basis 和允许的 sensitivity。无 manifest 不扫描 `.power-agent`
3. 派一名主审 reviewer 对完整目标做多维审查，并独立评估实现风险；低/中重要性的初始主审或主审修复验证若 `实现风险=高`，当前 verdict 立即升级为增强审查
4. 阻塞 finding 修复后优先由提出问题的 reviewer 验证；运行时不能继续时，使用携带原 finding、原证据、修复说明、修复增量和新验证证据的替代 reviewer
5. 有效强度仍为常规时在主审收敛后通过；增强审查在主审阶段收敛后派全新 reviewer 对最终范围做独立终审
6. 只有用户或上游契约明确要求时启用并行双审；修复后不机械重新启动两个完整 reviewer

Review assets 只读权威当前 run root 内 manifest 命名且通过 containment、target+paths/finding scope、freshness、source 与 sensitivity 校验的普通文件；无效条目只形成 evidence gap，不触发目录扩展。代码/Git diff、当前需求和匹配当前 basis 的新验证证据优先于 report 与其它 assets。

**输出：** `状态 + 审查阶段 + 重要性等级 + 实现风险 + 审查强度 + 阻塞问题 + 下一步`

**交棒给：** `receiving-code-review` → 修复采纳项 → 原 reviewer 优先验证 / 替代 reviewer 降级 → 增强审查独立终审 → 工作区检查 → `verification-before-completion`

---

### receiving-code-review — 审查反馈评估

**触发：** 收到代码审查反馈时。

**铁律：** 基于代码事实做技术判断，非情绪化接受或拒绝。

**输出：** 逐条决策（采纳/部分采纳/驳回/需澄清）+ 阻塞项 + 下一步

**参考：** `references/response-examples.md`

---

### verification-before-completion — 完成前验证

**触发：** 任何"声称完成"之前，尤其是 `proof-oriented-development` 交付 Proof Block 后。

**铁律：** 没有通过审计的 Proof Block / 等价证据块，或没有本轮可验证证据（命令/退出码/时间戳/摘要），不得声称完成。

**核心流程：** 审计 Proof Block / 等价证据块 → 判断证据强度 → 必要时补跑最小额外验证 → 输出 `verification_evidence`

**输出：** `状态：DONE / PARTIAL / BLOCKED + commit_sha + passed + verified_at + evidence[] + Proof Block 审计 + blocking_issues + next_action`

**交棒给：** `finishing-a-development-branch`（仅 `状态：DONE` 且 `passed=true` 后）

---

### finishing-a-development-branch — 分支处置

**触发：** 由 plan-impl 在 dirty 工作区或仓库尚无 HEAD 的待提交前置阶段，或 verification 完成后调用。

**待提交前置路径：** 工作区 dirty 或仓库尚无 HEAD 时先展示友好的未提交提示，不运行完成前验证；提交后重新检查，只有 clean 且 `has_head=true` 时才进入 verification 绑定新 HEAD，随后进入标准分支处置。

**四类选项：**
- Merge：直接合并到目标分支
- PR：创建 Pull Request
- 保留：保留 worktree 供后续使用
- 丢弃：删除 worktree 和分支（破坏性操作，需明确确认）

**输出：** `状态 + 模式 + 选择 + 验证证据 + 分支状态 + 环境状态 + 工作区状态（含 has_head）+ 清理结果 + advisories`

---

### using-git-worktrees — 隔离工作区

**触发：** plan-impl BOOTSTRAP、高风险改动、用户要求隔离执行。

**核心流程：** 检测当前是否已在 linked worktree → 优先使用宿主原生 worktree 能力 → 无原生能力时回退 `git worktree` → 运行最小基线检查。

**输出契约：** 向后续收尾流程传递 `path`、`is_linked_worktree`、`is_detached_head`、`worktree_source`、`managed_by`、`cleanup_allowed`。

**不做：** 不创建嵌套 worktree，不清理来源不明或宿主管理的 worktree。

---

### writing-skills — Skill 创建与维护

**触发：** 新增、修改、审查或优化 Skill。

**核心流程：** 定义目标行为与失败模式 → 修改最小必要 Skill/refs/docs → 检查上下游契约 → 准备压力场景。

**交棒给：** `requesting-code-review`，再经工作区检查进入最终验证阶段。

---

### dev-docs — 长期知识维护

**触发：** 需要把实现后稳定系统事实回写到 `docs/`，或维护架构、领域、开发流程、集成参考与有依据的 ADR 时。

**路由逻辑：** exec-plan 直接交给 `writing-plans`；普通 `docs/` Concept 使用具有非空 `type` 的 YAML frontmatter；ADR 使用 `type: Decision` 与 YAML `status`。验证运行状态仅由 `docs/.okf/verification.json` ledger 表示。

---

### dev-docs-maintain — 文档维护

**定位：** 按需触发的普通 Skill；不属于每次实现、审查或收尾的固定步骤。

**触发：** `docs/` 健康检查、知识库体检、OKF Bundle 检查、文档漂移修复或 verification ledger 登记。

**核心流程：** 扫描 docs/ → 对照实际代码状态 → 识别过期、缺失或失效内容 → 修复，并只在已完成验证时更新 verification ledger。

**输出：** 稳定 Markdown：状态、范围、变更/修复、证据、剩余问题/风险、下一步。

---

### setup-power-agent — 项目初始化

**disable-model-invocation: true**（直接执行）

**输出：** AGENTS.md（≤200 行）+ docs/architecture.md + docs/development.md + `CONTEXT.md` / `CONTEXT-MAP.md` 项目记忆骨架 + `docs/adr/` 目录

**交棒给：** 无固定下游；需要长期文档维护时按需触发 `dev-docs-maintain`。

---

### harness-engineering-review — 工作流审查

**disable-model-invocation: true**（直接执行，不召唤新代理）

**七个审查维度：**
1. AGENTS.md 结构与质量
2. Agent 可见性（知识库导航）
3. 约束机制化程度
4. 反馈循环完整性
5. 知识库维护实践
6. 技术债管理
7. 代码模式一致性

**输出：** P0/P1/P2 分级报告 + blocking_issues + advisories

---

## 反模式

| 反模式 | 说明 |
|--------|------|
| 无证据声称完成 | 没有运行命令/退出码/时间戳，不得说"完成了" |
| 猜测根因 | 没有假设验证证据前不能输出"根因是 X" |
| 重用子代理 | 子代理是一次性的，不得跨任务复用 |
| 跨层反向依赖 | 下层 Skill 不得调用上层 Skill |
| 超限并行 | 并行度超过 3 必须分批 |
| 无 Proof Block 声称完成 | proof-oriented-development 铁律：没有低成本、可复现、与任务强相关的最小有效证明 = 没有完成 |
