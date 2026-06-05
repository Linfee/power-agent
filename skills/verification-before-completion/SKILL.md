---
name: verification-before-completion
description: |-
  完成前验证 Skill。审计 Proof Block 或等价证据并输出 verification_evidence；准备声称编码工作完成前触发。
  Triggers: 验证完成, 完成前验证, 声称通过, verification, Proof Block 审计, verification_evidence.
---

# 完成前验证

在任何“已完成 / 已修复 / 已通过”声明前，先完成证据核验。

---

## verification-before-completion

完成前验证 Skill（completion verifier），负责：

- 审计完成声明是否被 Proof Block 或等价证据块支持。
- 判断证据强度是否匹配任务风险和验收标准。
- 必要时补跑最小额外验证。
- 输出可被编排层和 `finishing-a-development-branch` 消费的 `verification_evidence`。
- 在证据不足时明确阻塞原因与下一步动作。

---

## Objective

### 做什么

- 对“声明”执行证据核验，而不是复述信心判断。
- 审计 Proof Block 是否完整、可复现、与完成声明强相关。
- 判定 Proof Block 或等价证据块的证据强度是否匹配任务风险。
- 必要时补跑最小额外验证，并把结果并入 `evidence[]`。
- 要求证据与本轮改动范围相关，且为新鲜运行结果。
- 输出统一 contract：`status / commit_sha / passed / verified_at / evidence[] / proof_block_audit / blocking_issues / advisories / next_action`。

### 不做什么

- 不实现代码、不修复问题。
- 不替代 `proof-oriented-development` 产出 Proof Block。
- 不替代 `systematic-debugging` 做根因分析。
- 不替代 `writing-plans` 做高风险产品、架构或范围决策。
- 不替代 `requesting-code-review` 的代码质量审查职责。
- 不替代 `finishing-a-development-branch` 做分支处置。
- 不把 `lint → test → build` 写成唯一流程。

---

## Context & Tools

### 最小输入

- 本轮完成声明（宣称“完成了什么”）。
- 本轮改动范围（文件或模块）。
- `proof-oriented-development` 的 Proof Block，或非 POD 入口的等价证据块。
- 任务卡 / review-contract 中的目标约束、验收标准、推荐证明策略、阻塞条件（如存在）。
- 最近验证记录（命令、退出码、时间戳、摘要）。
- 当前 HEAD / 工作树状态。
- 任务类型（代码实现 / 配置变更 / 文档变更 / prompt/Skill 变更 / UI 行为 / bugfix）。

缺失信息按需读取，不预加载大段上下文。

### 参考资料

- 验证路径建议：`references/verification-playbook.md`
- 输出协议示例：`references/output-contract-examples.md`

---

## Constraints & Format

### 核验约束

- 没有证据，`status` 不能是 `DONE`。
- 对 POD 主链路的代码 / Skill / prompt 实现，缺少 Proof Block 时，`status` 不能是 `DONE`。
- 非 POD 入口缺少等价证据块时，`status` 不能是 `DONE`。
- Proof Block 的运行结果为 `FAIL / PARTIAL / NOT_RUN` 时，默认不能 `DONE`；除非本 Skill 补跑验证并明确覆盖缺口。
- Proof Block 的未验证项若影响验收标准，必须 `PARTIAL` 或 `BLOCKED`。
- Proof Block 与完成声明不匹配时，必须 `BLOCKED`。
- 证据过期或与当前 HEAD / 工作树状态不匹配时，必须 `BLOCKED` 或重新验证。
- 只要存在阻塞项，不得给出“可以声称完成”的结论。

### 决策边界：只阻塞，不补定义

本 Skill 可以补跑验证，但不能补定义任务本身，也不向用户追问来补齐计划或根因定义；它应直接回流对应上游 Skill。

- 缺验收标准、范围边界、证明策略或高风险决策：`BLOCKED`，next_action=`return_to_writing-plans`。
- 缺根因证据、验证失败且原因不清：`BLOCKED`，next_action=`return_to_systematic-debugging`。
- 缺 Proof Block 或 Proof Block 与声明不匹配：`BLOCKED`，next_action=`return_to_proof-oriented-development`。
- 证据过期或 HEAD 不匹配，但任务定义清晰：`BLOCKED` 或 `PARTIAL`，next_action=`rerun_minimal_verification`。

### Proof Block 兼容与完整性规则

现有 POD Proof Block 格式不由本 Skill 修改。本 Skill 只定义如何审计它。

#### 硬要求字段

POD 主链路的 Proof Block 至少必须能直接或通过任务卡映射出：

- 声明目标 / 目标约束
- 验收标准
- 验证方式（命令、截图、日志、CI、diff 或人工核对路径）
- 运行结果
- 风险或未验证项

#### 可映射字段

以下字段可以来自 Proof Block 本身，也可以来自任务卡 / review-contract / plan，但审计摘要必须说明来源：

- 目标约束
- 验收标准
- 推荐证明策略
- 允许未验证项口径

#### 完整性判定

| 条件 | 完整性 |
|---|---|
| Proof Block 含全部硬要求字段，且关键字段无需外部补齐 | 完整 |
| Proof Block 缺少部分上下文字段，但可从任务卡 / review-contract 明确映射，且运行结果与风险/未验证项存在 | 部分 |
| 缺少验证方式、运行结果、风险/未验证项，或无法映射目标/验收 | 缺失 |

#### 审计结论判定

| 完整性 | 相关性 | 可复现性 | 未验证项影响 | 审计结论 |
|---|---|---|---|---|
| 完整 | 强相关 | 可复现 | 无影响 / 可接受 | accepted |
| 部分 | 强相关 | 可复现 / 部分可复现 | 无影响 / 可接受 | needs_more_verification |
| 完整或部分 | 强相关 | 可复现 | 阻塞 | needs_more_verification 或 rejected（若无法补验） |
| 任意 | 弱相关 / 不匹配 | 任意 | 任意 | rejected |
| 缺失 | 任意 | 任意 | 任意 | rejected |

### 等价证据块兼容规则

非 POD 入口可以没有完整 Proof Block，但只在以下场景接受等价证据块：

- 用户手动要求验证已完成改动，并提供可复查验证记录。
- 纯文档 / 配置 / metadata 改动，已有结构检查、diff、命令输出或人工核对记录。
- CI / 外部系统已提供与完成声明直接相关的验证结果。

以下场景即使不是显式 POD 入口，也必须回到 POD 或上游补契约：

- 代码实现任务缺少目标、验收或验证结果。
- bugfix 缺少复现路径、根因或修复后验证。
- 高风险公共 API / 权限 / 数据 / 迁移变更缺少计划阶段证明策略。
- 完成声明来自实现代理，但没有 Proof Block 或等价证据块。

等价证据块最低字段：

- 声明目标：完成了什么。
- 验证方式：命令、截图、日志、CI、diff 或人工核对路径。
- 运行结果：PASS / FAIL / PARTIAL / NOT_RUN 或等价结论。
- 证据范围：目标模块、变更文件或全仓库。
- 风险 / 未验证项：至少明确“无”或列出缺口。

不满足最低字段时，不能 `DONE`。

### 状态映射矩阵

| Proof Block 审计结论 | 额外验证 | 缺口类型 | VBC 状态 | passed | next_action |
|---|---|---|---|---|---|
| accepted | 不需要或已通过 | 无阻塞 | DONE | true | proceed_to_finishing-a-development-branch |
| accepted | 不需要或已通过 | 未验证项影响验收标准 | PARTIAL 或 BLOCKED | false | rerun_minimal_verification / return_to_writing-plans |
| accepted | 失败 | 失败原因不清 | BLOCKED | false | return_to_systematic-debugging |
| needs_more_verification | 可补且补验通过 | 无阻塞 | DONE | true | proceed_to_finishing-a-development-branch |
| needs_more_verification | 未补 / 补验不足 | 非核心缺口 | PARTIAL | false | rerun_minimal_verification |
| needs_more_verification | 缺验收/证明策略/风险决策 | 计划缺口 | BLOCKED | false | return_to_writing-plans |
| rejected | 任意 | Proof Block 缺失或与声明不匹配 | BLOCKED | false | return_to_proof-oriented-development |
| rejected | 任意 | 证据过期或 HEAD 不匹配 | BLOCKED | false | rerun_minimal_verification |

### 输出格式（必须遵循）

完成核验后，用便于阅读的 Markdown 小节输出结果，不使用 YAML：

```markdown
## 完成前验证结果

状态：DONE / PARTIAL / BLOCKED
commit_sha：<验证时 HEAD commit sha，供下游分支收尾 skill 消费>
passed：true / false
verified_at：<timestamp>

### Proof Block 审计
- 是否提供：是 / 否 / 等价证据
- 完整性：完整 / 部分 / 缺失
- 相关性：强相关 / 弱相关 / 不匹配
- 可复现性：可复现 / 部分可复现 / 不可复现
- 未验证项影响：无影响 / 可接受 / 阻塞
- 结论：accepted / needs_more_verification / rejected

### 证据
- [proof_block_audit / test / check / build / manual / ci / screenshot / log / other] <command_or_path>
  - source：proof_block / equivalent_evidence / vbc_extra_verification / user_provided / ci / manual_review
  - exit code：<integer 或 not_applicable>
  - 时间：<timestamp>
  - 范围：变更文件 / 目标模块 / 全仓库 / 外部系统 / 完成声明范围
  - 摘要：<summary>

### 阻塞项
- [无证据 / 证据过期 / 检查失败 / 范围不匹配 / Proof Block 不足 / 计划缺口 / 根因未明] <message>
  - 需要动作：<required_action>

### 非阻塞建议
- <建议内容；无则写“无”>

### 下一步
- 负责人：代理 / 用户
- 动作：proceed_to_finishing-a-development-branch / return_to_proof-oriented-development / return_to_systematic-debugging / return_to_writing-plans / rerun_minimal_verification
```

### evidence[] 字段语义

`### 证据` 中的每条证据必须可映射为：

```text
kind: proof_block_audit | test | check | build | manual | ci | screenshot | log | other
source: proof_block | equivalent_evidence | vbc_extra_verification | user_provided | ci | manual_review
command_or_path: <command / file / URL / screenshot path / log path / proof_block:<section-or-anchor>>
exit_code: <integer / not_applicable>
time: <timestamp>
scope: <变更文件 / 目标模块 / 全仓库 / 外部系统 / 完成声明范围>
summary: <summary>
```

#### `kind=proof_block_audit` 字段约定

- `source`: `proof_block` 或 `equivalent_evidence`
- `command_or_path`: `proof_block:<section-or-anchor>`；若无稳定锚点，写 `proof_block:inline`
- `exit_code`: `not_applicable`
- `time`: VBC 审计时间
- `scope`: 本次完成声明覆盖范围
- `summary`: 必须包含 `accepted|needs_more_verification|rejected` 和关键缺口摘要

示例：

```text
kind: proof_block_audit
source: proof_block
command_or_path: proof_block:inline
exit_code: not_applicable
time: 2026-06-03T15:01:23Z
scope: skills/verification-before-completion
summary: accepted；Proof Block 完整、验证命令与声明强相关，未验证项为无
```

### 判定规则

- `status=DONE`：至少一条相关且成功的证据，Proof Block 审计为 `accepted` 或缺口已由额外验证覆盖，且 `blocking_issues=[]`。
- `status=PARTIAL`：有证据但不完整，或存在非致命缺口。
- `status=BLOCKED`：无证据、证据失败、Proof Block 被 rejected、证据与声明不匹配、计划缺口、根因未明、证据过期或 HEAD 不匹配。

### 编排层消费规则

- 仅当 `status=DONE` 且 `passed=true` 且 `blocking_issues=[]` 时，允许声称完成。
- 当 `status=PARTIAL|BLOCKED` 时，必须按 `next_action` 继续执行。
- 交给 `finishing-a-development-branch` 时，使用 `commit_sha`、`passed`、`verified_at` 和 `evidence[]` 组成 `verification_evidence`；不要从展示文案中推断字段名。
