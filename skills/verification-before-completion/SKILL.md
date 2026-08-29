---
name: verification-before-completion
description: |-
  完成前验证 Skill。审计 Proof Block 或等价证据并输出 verification_evidence；合并/PR、L2、高风险或对外宣称完成前触发。
  Triggers: 完成前验证, 声称通过, verification, Proof Block 审计, verification_evidence.
---

# 完成前验证

在合并/PR、对外宣称完成、L2 或高风险路径上，说出“已完成”之前核对证据。本 Skill 只回答：**完成声明有没有足够的系统外证据**。分层见 `AGENTS.md`。没有系统外证据不得声称完成。

三条原则：

- **没有证据就没有完成。** 证据必须真实运行过、与本轮改动相关、且新鲜（对应当前 HEAD / 工作树）。
- **证据强度与风险相称。** 风险越高，越不能拿一句“测试过了”交差。
- **只裁决，不代劳。** 可以补跑最小验证，但不实现代码、不查根因、不替上游补任务定义。缺什么写进阻塞项，由调用方按 `AGENTS.md` 处理。

## 入口

Git 任务：dirty 或还没有 HEAD 时不做验证，交给 `finishing-a-development-branch` 的未提交提示。只有 clean 且有 HEAD 才继续。

## 输出

下游只消费这些字段：

```markdown
## 完成前验证结果

状态：DONE / PARTIAL / BLOCKED
passed：true / false
commit_sha：<验证时的 HEAD；只能来自真实工具输出>
verified_at：<验证时间>

### 证据
- <命令或路径>：退出码（如适用）、一句话摘要

### 未验证 / 阻塞
- <无则写“无”>
```

- 只有 `DONE + passed=true + 无阻塞` 才能声称完成。
- 交给 `finishing-a-development-branch` 时，`commit_sha / passed / verified_at / 证据` 组成 `verification_evidence`。
- `commit_sha`、退出码、时间只能来自真实工具输出、CI 或用户提供的可复查记录；拿不到就写 `unknown`，且不能据此给 DONE。计划运行但还没跑的命令不是证据。

## 怎么审

短证据、完整 Proof Block、用户提供的可复查记录、diff/结构检查或 CI 都可以。要能回答：完成了什么、怎么验证、结果、覆盖哪里、还有什么没验证。不要只因缺标题退回。

代码实现缺验证结果、bugfix 缺复现、高风险缺证明策略 → `BLOCKED`，写明缺口。

缺口可补时补跑与声明直接相关的最小验证，并入证据后可 DONE。已接受的证据不要重跑。

## 条件性门槛

只在命中时检查：

- **bugfix**：original repro 必须有对应当前代码的新鲜结果；只有 minimal repro 不足以 DONE。
- **临时产物**：有创建记录则逐项确认 `removed | retained`；清单缺失或 `unknown` 不得 DONE。无创建记录写 `not_reported`，不反向扫描。
- **性能 / 稳定性**：有性能验收或合理影响面时，功能通过不能替代同口径对照；flaky 修复单次绿色不算。无影响面写 `not_applicable` 加一句理由。

判定 DONE：至少一条相关且成功的证据，被触发的条件性门槛通过，且无阻塞。`PARTIAL` 只用于有证据但不完整、缺口明确可补；其余 `BLOCKED`。

## References

- `references/output-contract-examples.md`：填法示例。
- `references/verification-playbook.md`：按任务类型选验证路径。
