---
type: Execution Plan
scope:
  - skills/plan-impl
  - skills/writing-plans
  - docs/workflow
status: completed
---

# 采用 review artifacts 与风险分层计划审查

## Goal / Done Means

- 目标：让 `plan-impl` 通过轻量 scratch artifacts 交接任务、实现报告和 review package，并用单个内部 reviewer 同时给出规格与质量 verdict；让 `writing-plans` 按风险选择 self-review、独立 reviewer 与人类 Gate。
- Done Means：协议、脚本、reviewer prompt 和主链路文档一致；review package 能覆盖指定路径下相对基线的 staged、unstaged 与 untracked 变更；旧双 reviewer prompt 不再被主链路调用。
- 不做事项：不删除旧 prompt，不改变最终全分支 `requesting-code-review`，不恢复默认 strict TDD，不允许实现子代理 commit，不建立通用 eval harness。

## Scope

### In Scope

- `skills/plan-impl/` 的 scratch artifact 协议、workspace/review-package 脚本、单 reviewer 双 verdict prompt 与编排说明。
- `skills/writing-plans/` 的计划风险分级、自查清单和 Gate 选择。
- `AGENTS.md`、`docs/architecture.md`、`docs/workflow.md` 的直接同步。

### Out of Scope

- `discuss` 的需求结论审查 Gate。
- 最终全分支审查的风险分级和输出协议。
- commit、push、发布和现有未提交改动清理。

## Key Decisions

- 决策：scratch artifacts 使用仓库内自忽略的 `.power-agent/review-runs/<run-id>/`。
  - 原因：subagent 可按路径读取，避免把大段任务、报告和 diff 常驻 controller 上下文；工作树级目录也兼容 worktree。
  - 执行含义：它不是 durable source of truth，`git clean -fdx` 后应从 exec-plan Session Log 和 Git 状态恢复。
- 决策：review package 以显式 `BASE` 和可选 path scope 生成，包含 status、stat、tracked diff 和 untracked 文件 diff。
  - 原因：Power-Agent 禁止实现子代理 commit，不能照搬 Superpowers 的 per-task commit range。
  - 执行含义：并行任务优先生成 batch-level package；只有边界可归属时才生成 task-level package。
- 决策：内部 task/batch reviewer 一次读取 package，分别给出 `Spec Compliance` 与 `Code Quality` verdict。
  - 原因：避免两个 reviewer 重复读取 diff，同时保留两个独立判断维度。
- 决策：计划审查按风险分级。
  - 原因：低风险计划的额外 subagent review 成本可能高于增益；高风险方向不能只靠 reviewer 裁决。
  - 执行含义：低风险 self-review；中风险 self-review + 独立 reviewer；高风险再要求人类显式批准 review contract。

## Agent 自主边界

- 可自由决策：脚本参数命名、artifact 文件名、文档措辞和最小测试夹具。
- 不可自行决策：删除旧 prompts、改变 Git 所有权、把 scratch 变成版本化真源、跳过最终全量审查。
- 必须保持的不变量：不覆盖用户已有改动；artifact 不进入提交；reviewer 只读；所有 blocking finding 有证据；高风险计划由人类最终决定。
- 触发升级条件：需要修改现有授权边界、无法在不纳入无关 dirty changes 的情况下生成 review package，或脚本需引入第三方依赖。

## Plan Risk

- 风险等级：medium
- 命中理由：跨 `plan-impl`、`writing-plans` 与主链路文档修改编排契约，但不触及外部 API、数据、权限、发布或不可逆操作，可通过保留的 legacy prompts 回滚。
- 审查路径：self-review + independent reviewer
- 审查状态：APPROVED
- 独立审查依据：只读 reviewer 对 `review-e4c3d59-worktree.diff` 完整复审，结论 `DONE`，Critical/Important/Minor 均为空；首轮 4 个 Important 已修复并复审闭合。
- 人类批准依据：not_required；用户已明确批准三个实现方向，但本计划不属于 high 风险强制 Gate。

## Tasks

- T1 建立 artifact protocol 与无依赖脚本；完成信号是临时 Git 仓库验证 tracked/untracked/path scope 均正确。
- T2 合并内部 reviewer；完成信号是 `plan-impl` 只引用单 reviewer，prompt 输出两个 verdict 和不可验证项。
- T3 实现计划风险分层；完成信号是低/中/高三档入口、Gate 和输出契约一致。
- T4 同步主链路文档并做结构、引用和 shell 验证。

## Proof Strategy

- 主证明：在临时 Git 仓库运行 workspace/review-package 脚本，断言 package 包含 staged、unstaged、untracked 变更且 path scope 排除无关文件。
- 次证明：`bash -n`、`rg` 检查主链路只引用新 reviewer 和风险分层字段、`git diff --check`。
- 非证明：只阅读 Markdown 或只检查文件存在。
- 已知未验证面：不运行真实多模型 reviewer 成本/质量 A/B；本次采用由用户明确批准。
- 失败解释：脚本失败回到 T1；引用不一致回到对应 Skill；风险 Gate 无法判定则回到 T3。

## Blockers / Escalation

- 阻塞条件：需要删除用户已有文件、改变 commit 策略或扩大到 `discuss` / 最终审查协议。
- 升级对象：用户。
- 升级时携带材料：冲突文件、现有规则、拟议变更和最小替代方案。

## Risks / Rollback

- 风险：dirty worktree 中 package 误纳入无关改动。
  - 失败信号：指定 scope 外文件出现在 package。
  - 缓解方式：支持显式 path scope，并在协议中要求 shared dirty tree 必须指定 scope。
  - 回滚方式：停止引用新脚本和 prompt，保留旧 prompts 可恢复。
- 风险：单 reviewer 把两个 verdict 合并成含糊结论。
  - 失败信号：输出缺少任一 verdict 或不可验证项。
  - 缓解方式：固定输出 slot 和状态映射。
  - 回滚方式：主链路重新指向现有双 prompts。

## 当前状态

- 当前进度：已完成并归档
- 下一步：按需运行真实多模型压力场景，评估单 reviewer 双 verdict 的成本与稳定性。

## Session Log

### 2026-07-11 17:34 实现与复审完成

- **已完成**：T1 scratch artifact/review-package；T2 单 reviewer 双 verdict；T3 风险分层；T4 主链路同步与验证。
- **遇到的问题**：首轮 reviewer 发现 package 自递归、失败 verdict 无 finding、run-id 覆盖和 pathspec magic 共 4 个 Important；全部修复并补回归测试。
- **已验证假设**：base + literal path scope 可覆盖 staged、unstaged、untracked 变更而不纳入 scope 外 dirty 文件；单 reviewer 输出可保持两个独立 verdict。
- **Review Artifacts**：`.power-agent/review-runs/20260711-173238-28018/review-e4c3d59-worktree.diff`；scratch，可重建。
- **环境状态**：review-package tests PASS；bash syntax PASS；git diff --check PASS；独立复审 DONE。
- **下一步**：已完成最终验证并归档；真实模型压力场景保留为后续 eval。
