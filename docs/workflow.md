<!-- verified: 2026-05-05 -->
<!-- scope: workflow -->

# 工作机制与 Skill 协调

本文档描述 power-agent 的完整工作机制：各 Skill 的职责边界、产出物、以及它们之间如何协调。

---

## 核心设计原则

**Skill 是执行单元，人类是决策者。** 每个 Skill 只做一件事，通过明确的输入/输出协议与其他 Skill 协作。规划阶段（spec 批准）设置强制 Gate 等待人类决策；实现阶段改为轻量启动通知，Agent 自主闭环，worktree 沙盒兜底（DD-006）。

**产出物是协调介质。** Skill 之间的长期状态通过仓库文件传递：spec 文档、exec-plan 文件、代码、docs/ 文档。编排型 Skill 可以在流程中使用下游 Skill，但必须保留明确的输入/输出契约，避免把下游实现细节复制到调用方。

## 状态协议速查

本项目不使用全局单一状态枚举。每个 Skill 保留自己的输出协议，但上下游交接必须显式写清字段与映射。

| Skill / 场景 | 状态值 | 下游消费规则 |
|--------------|--------|--------------|
| `writing-plans` plan review | `APPROVED / ISSUES_FOUND` | `APPROVED` 才能进入执行选项；`ISSUES_FOUND` 按 blocking issues 修正后重新审查 |
| `exec-plan-runner` 实现/修复子代理 | `DONE / DONE_WITH_CONCERNS / BLOCKED / UNKNOWN` | `DONE*` 可继续；`BLOCKED/UNKNOWN` 需要补上下文、拆分、重试或升级 |
| `exec-plan-runner` 内部审查 prompt | `DONE / DONE_WITH_CONCERNS / BLOCKED` | `BLOCKED` 进入 fix loop；连续同类问题无收敛则升级 |
| `requesting-code-review` 全量审查 | `通过 / 通过_含建议 / 阻塞 / 需澄清` | `阻塞` 启动修复并复审；`需澄清` 补充口径后重新审查 |
| `receiving-code-review` 反馈评估 | `DONE / BLOCKED` | `DONE` 表示反馈已完成采纳/驳回判断；`BLOCKED` 等待澄清 |
| `verification-before-completion` | `DONE / PARTIAL / BLOCKED` | 仅 `DONE` 且 `passed=true` 可交给分支收尾；输出 `commit_sha/passed/verified_at/evidence[]` |
| `finishing-a-development-branch` | `READY / BLOCKED / DONE / CANCELLED` | `DONE` 表示分支处置完成；`CANCELLED` 表示用户取消收尾或 destructive 确认失败 |
| `dispatching-parallel-agents` | `DONE / PARTIAL / BLOCKED / FAILED` | 总状态按关键子任务结果归并；非 `DONE` 时必须给出 next_action |

---

## 完整工作流图

```
┌─────────────────────────────────────────────────────────┐
│                    需求阶段                               │
│                                                         │
│   discuss skill                                         │
│   输入：模糊需求                                           │
│   产出：docs/specs/YYYY-MM-DD-<topic>.md                 │
│   gate：spec-reviewer 子代理审查 + 用户批准（强制 Gate）      │
└─────────────────────┬───────────────────────────────────┘
                      │ spec 文档（或用户直接描述功能）
                      ▼
┌─────────────────────────────────────────────────────────┐
│                 规划阶段                                  │
│                                                         │
│   writing-plans skill                                   │
│   输入：spec 文档 或 用户描述                               │
│   产出：docs/exec-plans/active/YYYY-MM-DD-title/         │
│           plan.md + context.md + tasks.md               │
│   gate：tech-plan-reviewer 子代理审查                     │
└─────────────────────┬───────────────────────────────────┘
                      │ exec-plan 三文档
                      ▼
┌─────────────────────────────────────────────────────────┐
│                 实现阶段                                  │
│                                                         │
│   exec-plan-runner skill（状态机自主闭环）                  │
│   ├── BOOTSTRAP：using-git-worktrees 检测/建立隔离工作区      │
│   ├── EXECUTING：依赖驱动批次并行 + conflict_check/review/fix │
│   ├── VERIFYING：verification-before-completion          │
│   └── FINALIZING：finishing-a-development-branch        │
└─────────────────────┬───────────────────────────────────┘

调试路径（独立入口）：
   systematic-debugging skill
       └── [status=FIXABLE] → test-driven-development skill
               └── → verification-before-completion skill
       └── [status=ESCALATE] → discuss 或 writing-plans
```

---

## 各 Skill 详解

### discuss — 需求探索

**触发：** 需求模糊、有多种可行方案、风险较高的架构决策。

**输入：** 用户的文字描述（任意格式）

**核心流程：**
1. 批量澄清问题（按主题分批，不一问一答）
2. 强制呈现 2-3 个方案对比，含权衡和推荐
3. 产出 spec 草稿（使用 `references/spec-template.md`）
4. 启动 `spec-reviewer` 子代理审查（最多 3 轮）
5. 用户确认 → spec 状态标记为 `accepted`

**产出：** `docs/specs/YYYY-MM-DD-<topic>.md`

**交棒给：** `writing-plans`（spec 批准后）

**不做：** 不写任何代码，不创建 exec-plan。spec 未批准前的任何实现动作均被 HARD-GATE 阻止。

---

### writing-plans — 实现计划创建

**触发：** 用户要求创建 exec-plan，discuss 完成后，或 `dev-docs` skill 路由。

**输入：** spec 文档 + 相关代码库上下文

**核心流程：**
1. 读取 spec 和相关代码文件
2. 拆解为三文档 exec-plan（plan.md / context.md / tasks.md）
3. 每个任务包含：目标行为、主要文件/模块、可读取上下文、禁止触碰范围、验收标准、测试场景、实施提示、验证命令、阻塞条件和依赖关系
4. 启动 `tech-plan-reviewer` 子代理审查（最多 3 轮，保留 subagent review loop）
5. 提供执行选项（推荐 `exec-plan-runner`）

**产出：** `docs/exec-plans/active/YYYY-MM-DD-title/plan.md + context.md + tasks.md`

**交棒给：** `exec-plan-runner`

---

### exec-plan-runner — 执行编排

**触发：** writing-plans 交棒，或用户手动恢复执行。

**状态机：** BOOTSTRAP → READY → EXECUTING → VERIFYING → FINALIZING → DONE（异常：ESCALATED / CANCELLED）

**核心流程：**
1. BOOTSTRAP：读取三文档，调用 `using-git-worktrees` 检测/建立隔离工作区
2. READY：确认依赖图、batch 划分和任务卡字段完整
3. EXECUTING：拓扑排序 tasks，默认先按批次并行派发实现子代理；无法并行时改为单个实现子代理推进，并在批次内执行 conflict_check / review / fix loop
4. VERIFYING：全量调用 `verification-before-completion`
5. FINALIZING：调用 `requesting-code-review`（合并/PR 前默认强制，用户明确跳过除外）与 `finishing-a-development-branch`，按收尾状态归档或保留恢复点

**产出：** 实现代码变更 + Session Log + 归档 exec-plan

**调用链：** TDD 子代理 → runner 内部审查 prompt → `verification-before-completion` → `requesting-code-review`（合并/PR 前）→ `finishing-a-development-branch`

`requesting-code-review` 是合并/PR 前默认强制的全量审查编排器；仅当用户明确要求跳过时可跳过，并在 Session Log 记录原因。`dev-docs-maintain` 是按需手动文档维护 Skill，不是每次开发执行的固定阶段。

---

### test-driven-development — 增量 TDD 实现

**触发：** 由 exec-plan-runner 派发任务卡，或用户直接触发。

**铁律：** 没有跑通的目标测试就没有声称完成。

**核心流程：** 选择最小行为变更 → 补目标测试或验证 → 最小实现 → 增量验证 → 必要时重构

**产出：** 实现代码 + 可运行通过的目标测试

**交棒给：** `verification-before-completion`（全量回归验证）

---

### systematic-debugging — 根因优先调试

**触发：** bug、测试失败、意外行为。

**铁律：** 证据充分前不输出修复结论。

**核心流程：** 现象隔离 → 假设生成 → 假设验证 → 根因确认

**输出结论：** `状态：INVESTIGATING / HYPOTHESIS_VERIFIED / FIXABLE / BLOCKED / ESCALATE`

**交棒给：**
- `status=FIXABLE` → `test-driven-development`
- `status=ESCALATE` → `discuss` 或 `writing-plans`

---

### requesting-code-review — 全量审查编排

**触发：** 实现完成后按风险或用户要求触发；合并/PR 前默认强制触发，除非用户明确要求跳过并记录原因。

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

**触发：** 任何"声称完成"之前。

**铁律：** 没有本轮可验证证据（命令/退出码/时间戳/摘要）不得声称完成。

**输出：** `状态：DONE / PARTIAL / BLOCKED + commit_sha + passed + verified_at + evidence + blocking_issues`

**交棒给：** `finishing-a-development-branch`（仅 `状态：DONE` 且 `passed=true` 后）

---

### finishing-a-development-branch — 分支处置

**触发：** 由 exec-plan-runner（FINALIZING 阶段）或 verification 完成后调用。

**四类选项：**
- Merge：直接合并到目标分支
- PR：创建 Pull Request
- 保留：保留 worktree 供后续使用
- 丢弃：删除 worktree 和分支（高风险，需明确确认）

**输出：** `状态 + 选择 + 验证证据 + 分支状态 + 环境状态 + 工作区状态 + 清理结果 + advisories`

---

### dispatching-parallel-agents — 并行调度

**约束：** 单批次最大并行度 3，仅当任务彼此独立（无共享改动面、无顺序依赖）时才并行。

**输出：** 各子代理结构化结果汇总（status: DONE/PARTIAL/BLOCKED/FAILED）

**参考文件：** `task-card-template.md`、`result-contract.md`、`conflict-resolution-rubric.md`

---

### using-git-worktrees — 隔离工作区

**触发：** exec-plan-runner BOOTSTRAP、高风险改动、用户要求隔离执行。

**核心流程：** 检测当前是否已在 linked worktree → 优先使用宿主原生 worktree 能力 → 无原生能力时回退 `git worktree` → 运行最小基线检查。

**输出契约：** 向后续收尾流程传递 `path`、`is_linked_worktree`、`is_detached_head`、`worktree_source`、`managed_by`、`cleanup_allowed`。

**不做：** 不创建嵌套 worktree，不清理来源不明或宿主管理的 worktree。

---

### writing-skills — Skill 创建与维护

**触发：** 新增、修改、审查或优化 Skill。

**核心流程：** 定义目标行为与失败模式 → 修改最小必要 Skill/refs/docs → 检查上下游契约 → 准备压力场景 → 同步版本。

**交棒给：** `verification-before-completion` 或 `requesting-code-review`。

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

### init-harness-engineering — 项目初始化

**disable-model-invocation: true**（直接执行）

**输出：** AGENTS.md（≤200 行）+ docs/architecture.md + docs/development.md

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
| 无测试声称通过 | TDD 铁律：没有跑通的目标测试 = 没有完成 |
