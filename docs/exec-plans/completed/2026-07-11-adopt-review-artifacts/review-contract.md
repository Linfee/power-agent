---
type: Review Contract
scope:
  - human-review-contract
status: completed
---

# Review Contract

## Intent

- 降低内部审查的重复上下文和重复读取成本，同时保持规格符合性与代码质量两个独立 verdict。

## Scope

### In Scope

- scratch artifacts、review-package、单 reviewer 双 verdict、计划风险分层。

### Out of Scope

- 删除旧 prompts、改变 commit 所有权、改变最终全分支审查、建立完整 eval harness。

## Acceptance

- [ ] review package 能正确表达指定 scope 的 tracked 与 untracked 变更。
- [ ] 内部 reviewer 明确只读，一次读取 package，输出规格与质量两个 verdict，并显式列出无法从 diff 验证的要求。
- [ ] 低风险计划 self-review；中风险增加独立 reviewer；高风险再等待人类显式批准。
- [ ] 主链路文档和 Skill 引用一致，旧 prompts 保留但不再被调用。

## Agent 自主边界

- 可自由决策：最小协议和脚本实现细节。
- 不可自行决策：扩大流程范围、删除旧文件、提交或发布。
- 必须保持的不变量：不覆盖用户改动；不让 scratch artifact 成为 durable source of truth。

## Proof

- 主证明：临时 Git 仓库中的端到端脚本断言。
- 次证明：shell 语法、引用一致性、diff whitespace 检查。
- 非证明：单纯文件存在检查。
- 已知未验证面：真实多模型成本与缺陷捕获率。

## Blockers / Escalation

- 只有需要改变授权、Git 或最终审查边界时停止请求确认。

## Risks

- 风险：dirty worktree 产生范围污染。
  - 决策状态：已由显式 path scope 缓解。
  - 缓解方式：共享 dirty tree 必须指定审查路径。
  - 执行期阻塞条件：无法隔离目标变更。

## Plan Review Gate

- Plan Risk：medium
- Review Path：self-review + independent reviewer
- Plan Review Status：APPROVED
- Independent Review：approved；只读 reviewer 最终复审无 Critical/Important/Minor finding
- Human Approval：not_required

## Approval Bar

- 用户已在当前会话明确批准三个方向，可直接实现；范围实质变化时重新确认。
