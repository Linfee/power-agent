<!-- verified: 2026-06-05 -->
<!-- scope: workflow -->

# 工作机制与 Skill 协调

本文档描述 power-agent 的完整工作机制：各 Skill 的职责边界、产出物、以及它们之间如何协调。

---

## 核心设计原则

**Skill 是执行单元，人类是决策者。** 每个 Skill 只做一件事，通过明确的输入/输出协议与其他 Skill 协作。规划阶段（需求结论批准）设置强制 Gate 等待人类决策；实现阶段改为轻量启动通知，Agent 自主闭环，worktree 沙盒兜底（DD-006）。

**产出物是协调介质。** 默认链路中，discuss 的已批准需求结论由 writing-plans 折叠进 exec-plan；只有用户或流程明确需要时才额外落盘 spec 文档。Skill 之间的长期状态主要通过 exec-plan 文件、代码、docs 文档传递，避免把上游讨论记录复制成第二套真源。

## 状态协议速查

本项目不使用全局单一状态枚举。每个 Skill 保留自己的输出协议，但上下游交接必须显式写清字段与映射。

| Skill / 场景 | 状态值 | 下游消费规则 |
|--------------|--------|--------------|
| `writing-plans` plan review | `APPROVED / ISSUES_FOUND` | `APPROVED` 才能进入执行选项；`ISSUES_FOUND` 按 blocking issues 修正后重新审查 |
| `plan-impl` 实现/修复子代理 | `DONE / DONE_WITH_CONCERNS / BLOCKED / UNKNOWN` | `DONE*` 可继续；`BLOCKED/UNKNOWN` 需要补上下文、拆分、重试或升级 |
| `plan-impl` 内部审查 prompt | `DONE / DONE_WITH_CONCERNS / BLOCKED` | `BLOCKED` 进入 fix loop；连续同类问题无收敛则升级 |
| `requesting-code-review` 全量审查 | `通过 / 通过_含建议 / 阻塞 / 需澄清` | `通过*` 才进入最终验证；修复审查反馈后必须重新审查，再重新验证 |
| `plan-impl-lightweight` | `DONE / DONE_WITH_CONCERNS / BLOCKED / UNKNOWN` + `path_decision` | `path_decision=lightweight` 且 `DONE*` 可继续；`ask_user/escalate_to_full` 暂停轻量执行并回到用户或完整 runner |
| `receiving-code-review` 反馈评估 | `DONE / BLOCKED` | `DONE` 表示反馈已完成采纳/驳回判断；`BLOCKED` 等待澄清 |
| `verification-before-completion` | `DONE / PARTIAL / BLOCKED` | 仅 `DONE` 且 `passed=true` 可交给分支收尾；输出 `commit_sha/passed/verified_at/evidence[]` |
| `finishing-a-development-branch` | `READY / BLOCKED / DONE / CANCELLED` | `DONE` 表示分支处置完成；`CANCELLED` 表示用户取消收尾或 destructive 确认失败 |

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
│   gate：独立 reviewer 子代理审查 + 用户批准（强制 Gate）        │
└─────────────────────┬───────────────────────────────────┘
                      │ 已批准需求结论（或用户直接描述功能）
                      ▼
┌─────────────────────────────────────────────────────────┐
│                 规划阶段                                  │
│                                                         │
│   writing-plans skill                                   │
│   输入：需求结论 / spec 文档 / 用户描述                       │
│   产出：docs/exec-plans/active/YYYY-MM-DD-title/         │
│           plan.md + review-contract.md                  │
│           （按需拆出 context.md / tasks.md）               │
│   gate：tech-plan-reviewer 子代理审查                     │
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
│   ├── VERIFYING：verification-before-completion          │
│   └── FINALIZING：finishing-a-development-branch        │
└─────────────────────┬───────────────────────────────────┘

调试路径（独立入口）：
   systematic-debugging skill
       └── [status=FIXABLE] → proof-oriented-development skill
               └── Proof Block → verification-before-completion skill
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
8. 用户确认需求结论；只有用户明确要求、合规/流程要求或需要长期产品资产时，才按需落盘 spec/doc。

**产出：** 内联 `Discussion Conclusion` / `需求结论`；按需 `docs/specs/YYYY-MM-DD-<topic>.md`

**交棒给：** `writing-plans`（需求结论批准后）

**不做：** 不写任何代码，不创建 exec-plan，不做接口签名、数据表/字段、库选型、类/函数拆分、文件路径等实现细节；允许讨论影响范围/验收/planning 的上层技术方向。需求结论未批准前的任何实现动作均被 HARD-GATE 阻止。

---

### writing-plans — 实现计划创建

**触发：** 用户要求创建 exec-plan，discuss 需求结论已批准后，或 `dev-docs` skill 路由。

**输入：** 已批准需求结论 / spec 文档 / 用户描述 + 相关代码库上下文

**核心流程：**
1. 读取需求结论、spec 或用户描述，以及直接相关代码/文档。
2. 默认生成 compact exec-plan：`plan.md + review-contract.md`；仅在证据昂贵、上下文过大、任务图复杂或多 Agent 交接需要时拆出 `context.md / tasks.md`。
3. `plan.md` 是执行真源，包含目标、Scope、关键决策、Agent 自主边界、紧凑任务、Proof Strategy、阻塞/升级条件和风险。
4. `review-contract.md` 是人类默认审阅面：人类只审意图、范围、验收、证明策略、Agent 自主边界、阻塞条件和高风险项，不逐行审执行材料。
5. 启动 `tech-plan-reviewer` 子代理审查（最多 3 轮，保留 subagent review loop；不得用同上下文 self-review 替代）。
6. 提供执行选项（推荐 `plan-impl`）。

**产出：** `docs/exec-plans/active/YYYY-MM-DD-title/plan.md + review-contract.md`，按需 `context.md / tasks.md`

**交棒给：** `plan-impl`

---

### plan-impl — 执行编排

**触发：** writing-plans 交棒，或用户手动恢复执行。

**状态机：** BOOTSTRAP → READY → EXECUTING → REVIEWING → VERIFYING → FINALIZING → DONE（异常：ESCALATED / CANCELLED）

**核心流程：**
1. BOOTSTRAP：读取弹性计划包（必读 `plan.md`，读取 `review-contract.md` 人审边界，按存在情况读取 `context.md / tasks.md`），调用 `using-git-worktrees` 检测/建立隔离工作区
2. READY：确认 `plan.md` 中任务、依赖、Proof、阻塞条件完整；若存在 `tasks.md` 则消费拆分任务图；中等偏小、边界清楚、局部验证充分的任务可转交 `plan-impl-lightweight`
3. EXECUTING：拓扑排序 tasks（来自 `plan.md` 或可选 `tasks.md`），优先检测并使用 team 模式承载 batch、review、fix、verify；缺少 team 工具且不适合轻量路径时回退为按批次并行派发实现子代理，无法并行时改为单个实现子代理推进，并在批次内执行 conflict_check / review / fix loop
4. REVIEWING：调用 `requesting-code-review`（最终验证前默认强制，用户明确跳过除外）；修复审查反馈后必须重新审查
5. VERIFYING：调用 `verification-before-completion` 审计 Proof Block / 等价证据块，必要时补跑最小额外验证，并输出 `verification_evidence`
6. FINALIZING：调用 `finishing-a-development-branch`，按收尾状态归档或保留恢复点

**产出：** 实现代码变更 + Session Log + 归档 exec-plan

**调用链：** `plan-impl-lightweight`（可选轻量分支）→ proof-oriented 实现子代理（输出 Proof Block）→ runner 内部审查 prompt → `requesting-code-review`（最终验证前）→ `verification-before-completion` → `finishing-a-development-branch`

`requesting-code-review` 是最终验证前默认强制的全量审查编排器；仅当用户明确要求跳过时可跳过，并在 Session Log 记录原因。`dev-docs-maintain` 是按需手动文档维护 Skill，不是每次开发执行的固定阶段。

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

**交棒给：** `verification-before-completion`（全量回归与最终完成验证）

---

### systematic-debugging — 根因优先调试

**触发：** bug、测试失败、意外行为。

**铁律：** 证据充分前不输出修复结论。

**核心流程：** 现象隔离 → 假设生成 → 假设验证 → 根因确认 → 修复交接证明策略

**输出结论：** `状态：INVESTIGATING / HYPOTHESIS_VERIFIED / FIXABLE / BLOCKED / ESCALATE`，其中 `FIXABLE` 必须包含 `bug_class`、`fix_boundary`、`recommended_proof_strategy` 和 `verification_path`。

**交棒给：**
- `status=FIXABLE` → `proof-oriented-development`
- `status=ESCALATE` → `discuss` 或 `writing-plans`

---

### requesting-code-review — 全量审查编排

**触发：** 实现完成后、最终验证前默认强制触发；合并/PR 前若尚未完成全量审查，也必须触发，除非用户明确要求跳过并记录原因。

**核心流程：**
1. 评估变更风险等级（低/中 = 单审，高 = 双审并行）
2. 按风险分级派发审查子代理（使用 `references/code-reviewer.md` prompt）
3. 汇总结构化审查结论

**输出：** `状态：通过 / 通过_含建议 / 阻塞 / 需澄清 + 阻塞问题 + 下一步`

**交棒给：** `receiving-code-review` → 修复采纳项 → 重新审查（直到通过或 3 轮上限）→ `verification-before-completion`

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

**触发：** 由 plan-impl（FINALIZING 阶段）或 verification 完成后调用。

**四类选项：**
- Merge：直接合并到目标分支
- PR：创建 Pull Request
- 保留：保留 worktree 供后续使用
- 丢弃：删除 worktree 和分支（高风险，需明确确认）

**输出：** `状态 + 选择 + 验证证据 + 分支状态 + 环境状态 + 工作区状态 + 清理结果 + advisories`

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

**交棒给：** `requesting-code-review`，再由最终验证阶段进入 `verification-before-completion`。

---

### dev-docs — 文档路由器

**disable-model-invocation: true**（直接执行，不召唤新代理）

**支持六种文档类型：** architecture、arch-decision、exec-plan、domain、development、reference

**路由逻辑：** exec-plan 类型 → 委派 `writing-plans`；其余类型 → 直接写入对应 docs/ 路径（含 verified/scope 元信息）

---

### dev-docs-maintain — 文档维护

**disable-model-invocation: true**（直接执行，不召唤新代理）

**触发：** 手动调用，或在重大变更后由用户/代理按需建议调用。

**核心流程：** 扫描 docs/ → 对照实际代码状态 → 识别过期/缺失/失效内容 → 修复

**输出：** 文档健康报告（修复项表格 + 待处理 P2 列表）

---

### setup-power-agent — 项目初始化

**disable-model-invocation: true**（直接执行）

**输出：** AGENTS.md（≤200 行）+ docs/architecture.md + docs/development.md + `CONTEXT.md` / `CONTEXT-MAP.md` 项目记忆骨架 + `docs/arch-decisions/` 目录

**交棒给：** 无固定下游；需要长期文档维护时建议用户手动调用 `dev-docs-maintain`。

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
