---
name: verification-before-completion
description: |-
  完成前验证 Skill。审计 Proof Block 或等价证据并输出 verification_evidence；准备声称编码工作完成前触发。
  Triggers: 完成前验证, 声称通过, verification, Proof Block 审计, verification_evidence.
---

# 完成前验证

在说出“已完成 / 已修复 / 已通过”之前，先核对证据。本 Skill 只回答一个问题：**完成声明有没有足够证据支撑**。

三条原则：

- **没有证据就没有完成。** 证据必须真实运行过、与本轮改动相关、且新鲜（对应当前 HEAD / 工作树）。
- **证据强度与风险相称。** 风险越高，越不能拿一句“测试过了”交差。
- **只裁决，不代劳。** 可以补跑最小验证，但不实现代码、不查根因、不替上游补任务定义——缺什么就退回对应的 Skill。

## 入口前置：工作区检查

Git 任务先看工作区：dirty（含 staged、unstaged、untracked）或还没有 HEAD 时，不做验证，转入 `finishing-a-development-branch` 的 `mode=uncommitted` 提示流程。只有 clean 且有 HEAD 才继续核验。

## 输出契约

下游（编排层、`finishing-a-development-branch`）只消费以下字段，必须出现；其余内容按需要组织，说清楚即可：

```markdown
## 完成前验证结果

状态：DONE / PARTIAL / BLOCKED
passed：true / false
commit_sha：<验证时的 HEAD；只能来自真实工具输出>
verified_at：<验证时间>

### Proof Block 审计
- 结论：accepted / needs_more_verification / rejected
- <一句话说明完整性、相关性、可复现性与关键缺口；被触发的条件性门槛结论也写在这里>

### 证据
- <命令或路径>：来源、退出码（如适用）、时间、覆盖范围、一句话摘要

### 阻塞项
- <阻塞原因> → 需要动作：<required_action>；无则写“无”

### 下一步
- 动作：proceed_to_finishing-a-development-branch / return_to_proof-oriented-development / return_to_systematic-debugging / return_to_writing-plans / rerun_minimal_verification
```

消费规则：

- 只有 `DONE + passed=true + 无阻塞项` 才能声称完成；`PARTIAL / BLOCKED` 按 `下一步` 回流。
- 交给 `finishing-a-development-branch` 时，`commit_sha / passed / verified_at / 证据` 组成 `verification_evidence`。
- `commit_sha`、退出码、时间只能来自真实工具输出、CI 或用户提供的可复查记录；拿不到就写 `unknown`，且不能据此给 DONE。计划运行但还没跑的命令不是证据。

填写示例见 `references/output-contract-examples.md`；按任务类型选择验证路径的建议见 `references/verification-playbook.md`；行为边界的验证场景见 `references/stress-scenarios.md`。

## 怎么审 Proof Block

POD 链路审 Proof Block；非 POD 入口可接受等价证据块（用户提供的可复查验证记录、文档/配置改动的结构检查或 diff、CI 结果）。等价证据块至少要能回答：完成了什么、怎么验证的、结果如何、覆盖哪里、还有什么没验证。以下情况不接受降级，退回上游补契约：代码实现缺验证结果；bugfix 缺复现路径或根因；高风险变更缺计划阶段证明策略。

审计看四件事：

1. **完整**：能读出目标约束、验收标准、验证方式、运行结果、风险/未验证项。个别字段可从任务卡 / review-contract 映射，但要在摘要里说明来源。
2. **相关**：验证的内容和完成声明是同一件事，证据范围覆盖改动范围。
3. **可复现**：别人能按记录重跑；截图、日志、CI、diff 有可复查路径。
4. **未验证项**：影响验收标准的就是阻塞。

结论分三档：四项都过关是 `accepted`；有可补缺口是 `needs_more_verification`；关键项缺失、与声明对不上或不可复现是 `rejected`。

缺口可补时，补跑与完成声明直接相关的最小验证，结果并入证据后可 DONE；Proof Block 已被接受时，不要重复实现阶段跑过的验证。

## 条件性门槛

只在命中时检查，没命中不要为了凑字段去补做：

- **bugfix**：original repro 是主要证明，必须有对应当前代码的新鲜结果；只有 minimal repro 永远不足以 DONE。缺少理想测试切入点不单独阻塞一个边界清楚的修复，但要在风险中写明 seam 缺口与受影响边界，且 original repro 必须通过。
- **临时产物**：上游或本轮创建过 `temporary_artifacts` 的，逐项确认位置、敏感性、`removed | retained` 和处置验证；有创建记录但清单缺失或标 `unknown` 时不得 DONE。没有已知创建记录就写 `not_reported`，不需要反向扫描去证明“没创建过”。
- **性能 / 稳定性**：有性能验收，或改动存在合理性能影响面时，功能通过不能替代同 workload、环境、口径下的 baseline / candidate 对照；flaky 修复要有风险相称的受控重复观测或失败率对照，单次绿色不算数。没有合理影响面时写 `not_applicable` 并给一句理由，不预设固定次数、阈值或工具菜单。

## 缺什么退回哪

- 缺验收、范围、证明策略或高风险决策 → BLOCKED，`return_to_writing-plans`
- 验证失败但原因不清、缺根因证据 → BLOCKED，`return_to_systematic-debugging`
- 缺 Proof Block，或 Proof Block 与完成声明对不上 → BLOCKED，`return_to_proof-oriented-development`
- 证据过期、HEAD 不匹配，但任务定义清楚 → `rerun_minimal_verification`（或直接补跑后并入证据）

判定 DONE 的底线：至少一条相关且成功的证据，Proof Block 审计为 accepted（或缺口已由补验覆盖），所有被触发的条件性门槛通过，且无阻塞项。`PARTIAL` 只用于有证据但不完整、非致命缺口明确可补的情形；其余一律 BLOCKED。
