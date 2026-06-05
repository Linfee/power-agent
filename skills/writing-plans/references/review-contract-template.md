<!-- verified: YYYY-MM-DD -->
<!-- scope: human-review-contract -->

# Review Contract

> 人类默认只审本文档。默认持久化计划包为 `plan.md + review-contract.md`；`review-contract.md` 是必需文件，不能用 `plan.md` 中的长章节替代。

## Intent

- [任务目标、业务意义和关键约束的压缩总结]

## Scope

### In Scope
- [本次明确包含]

### Out of Scope
- [本次明确不包含]

## Acceptance

- [ ] [可验证、可判定的完成条件 1]
- [ ] [可验证、可判定的完成条件 2]

## Agent 自主边界

- 可自由决策：[执行 Agent 可以自己决定什么]
- 不可自行决策：[哪些范围、协议、关键 UX、权限、发布/迁移或风险等级不能擅自改变]
- 必须保持的不变量：[执行期间必须始终成立的契约]

## Proof

- 主证明：[最能证明目标达成的验证方式]
- 次证明：[补充验证；若无写 none]
- 非证明：[不能单独作为完成证明的检查；若无写 none]
- 已知未验证面：[允许不覆盖的范围及原因；若无写 none]

## Blockers / Escalation

遇到以下情况必须停止并请求确认：

- [会改变范围、验收标准、风险等级、关键用户体验或 Agent 自主边界的决策点]

## Risks

- 风险：[潜在越权、破坏性操作、兼容性风险或安全风险；若无写 none]
  - 决策状态：[已由用户确认 / 可由仓库证据闭合 / 需要人工确认 / 不适用]
  - 缓解方式：[如何避免、限制或验证]
  - 执行期阻塞条件：[遇到哪些情况必须 BLOCKED，而不是自行继续]

## Approval Bar

- 人类只需判断：Intent、范围边界、Acceptance、Agent 自主边界、Proof、阻塞条件和风险是否足够。
- 若其中任一项不可判定，应先修订 review surface，而不是要求人类通读全部执行材料。