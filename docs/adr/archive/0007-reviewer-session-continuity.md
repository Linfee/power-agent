---
type: Decision
status: superseded
verification:
  strategy: historical
superseded_by: ../0014-current-baseline.md
supersedes: 0002-disposable-subagents.md
---

# ADR-0007: Reviewer 会话连续性与子代理生命周期

> 历史记录：已由 [ADR-0014](../0014-current-baseline.md) 归并取代。下文的决定、状态说明与旧 Skill 名称保留当时含义，不作为当前指令。

**状态：** accepted（supersedes ADR-0002）
**日期：** 2026-07-19
**影响文件：** `AGENTS.md`, `skills/plan-impl/`, `skills/requesting-code-review/`, `skills/receiving-code-review/`, `docs/architecture.md`, `docs/development.md`, `docs/workflow.md`

## 背景

ADR-0002 将所有子代理定义为一次性，并禁止主代理与同一子代理多轮交互。该规则为实现和修复工作提供了干净上下文，但也使 reviewer 在自己提出 finding 后无法直接验证修复，导致每轮都由新 reviewer 重新读取完整范围。高重要性变更采用并行双审时，这一成本会在修复循环中成倍增加。

代码审查的修复验证与跨任务复用不同：reviewer 需要保持原 finding 的判断上下文，验证问题是否关闭，同时仍必须基于当前代码和新证据产生新的 verdict。不同运行时对 reviewer 连续会话的支持并不一致，因此工作流还需要平台无关的降级路径。

## 约束

- 实现和修复子代理需要干净上下文，不能在多轮中累积错误假设。
- reviewer 不得跨实现目标复用，也不得同时承担实现或修复职责。
- 修复验证必须产生新 verdict，不能沿用旧结论。
- 高重要性或高实现风险仍需要一个未参与主审的独立视角。
- Skill 不能依赖特定 agent 名称、消息接口或平台私有生命周期能力。

## 决定

采用按职责区分的子代理生命周期：

1. **实现与修复子代理保持一次性。** 每轮修复使用新的子代理和完整问题上下文。
2. **跨实现目标的子代理调用保持一次性。** reviewer 不能从一个目标迁移到另一个目标继续工作。
3. **同一 review session 内允许 reviewer 连续验证自己的 findings。** 修复后优先由提出 finding 的 reviewer 检查原问题、修复增量和受影响路径，并产生新 verdict。
4. **运行时不支持继续 reviewer 时使用新 reviewer 降级。** 替代 reviewer 必须获得原 finding、原证据、修复说明、修复增量和新验证证据。
5. **增强审查采用顺序独立终审。** 高重要性或高实现风险在主审收敛后，由此前未参与该目标审查的新 reviewer 对最终范围做独立全量终审。
6. **显式并行双审不机械重复。** 只有用户或上游契约明确要求时并行派发；修复后只路由给提出 finding 的 reviewer，不能继续时使用替代 reviewer。

## 后果

- 常规修复循环避免新 reviewer 重复读取全部上下文，降低审查延迟和成本。
- 同一 reviewer 的确认偏差由增强审查的全新独立终审缓解。
- 不支持连续 reviewer 的运行时仍可通过完整修复上下文获得等价的替代复审路径。
- 编排器需要记录 finding owner、修复增量和新验证证据，并区分主审、修复验证、独立终审和显式并行审查阶段。
- ADR-0002 保留为历史记录，但其“所有子代理均禁止多轮交互”的决定不再生效。
