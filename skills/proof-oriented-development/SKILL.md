---
name: proof-oriented-development
description: |-
  证明导向实现 Skill。小步修改代码、运行最小相关验证并交付 Proof Block；进入实现阶段或 bugfix 边界已确认时触发。
  Triggers: 实现功能, 已确认 bugfix, proof-oriented, Proof Block, 证据交付, 最小有效验证, 目标验证, TDD, 测试驱动.
---

# Proof-Oriented Development

以最小增量推进实现，并在交付时给出低成本、可复现、与任务强相关的证明。

**铁律：**
```
没有最小有效证明，就不能声称当前增量完成。
严格 TDD 只在用户明确要求时启用。
```

---

## 入口保护

- 若请求是修复既有错误、测试失败或异常行为，且尚无法确定产生偏离的位置、修复边界或验证路径，先使用 `systematic-debugging`。
- 目标行为、修改边界和验收路径已经明确的功能实现或行为调整，可直接进入本 Skill。
- 只有当 `systematic-debugging` 输出 `FIXABLE`，包含 `causal_explanation`、`evidence_refs`、`fix_boundary`、`target_behavior`、`verification_path`、`execution_authorization=granted` 和可审计的 `execution_authorization_basis`，或用户直接提供同等信息并明确授权当前修复时，才进入本 Skill 做 bugfix。实施前核对 basis 引用的授权来源确实覆盖当前 `fix_boundary`、动作类型和所需专项确认；不匹配、`missing|unknown` 或 basis 缺失时保留 handoff、请求最小授权，不修改文件。
- 本 Skill 可以验证实现是否成立，但不负责在根因未知时猜测修复。
- 用户明确要求 `TDD`、`测试驱动`、`先写失败测试` 或 `Red/Green/Refactor` 时，才启用 strict TDD；其他情况不得自动升级。

### 可行性检查

对输入的计划、任务清单做最小可行性检查。

计划至少需要包含一下三项才可进入实现：

- **目标**：能说清本次要改变的行为、结构或输出。
- **边界**：能判断哪些范围不应顺手扩张；若未显式写出，必须能从任务语义中安全推出。
- **验收**：能判断完成与否；若未给验证命令，但验收可观察，本 Skill 可自行选择最小相关验证。

不满足时不要猜测实现。先用简短问题引导用户补齐 plan，问题只围绕缺失项：

- 缺目标：询问期望行为或最终状态。
- 缺边界：询问哪些范围不能改、哪些兼容性必须保留。
- 缺验收：询问用什么现象、命令、测试、截图或输出判断完成。

若缺口涉及公共 API、数据模型、权限、安全、迁移、并发语义或高影响 UX，返回 `BLOCKED`，说明缺少的决策和继续实现的风险。

---

## 核心流程：证明导向开发闭环

### 1. Scope Slice

选择当前最小可验证增量：

- 只处理一个清晰行为或一个明确修复边界。
- 不把多个独立目标混在一次改动里。
- 若任务范围无法切成可验证增量，先请求澄清或交回规划/调试流程。

### 2. Proof Plan

实现前先明确 Proof Block 需要证明什么：

- 目标约束：本次必须满足什么、禁止触碰什么。
- 验收标准：用户、任务卡、spec 或当前上下文中的可观察完成判据。
- 最小验证方式：与当前任务强相关、成本最低、可复现的命令或观察路径。
- **bugfix 复现与回归测试切入边界**：消费 `verification_path` 的 `original_repro` 和 `minimal_repro`（如有）；修复后两者都重跑，`original_repro` 是真实场景的主要证明。回归测试必须位于能够覆盖缺陷真实发生机制的测试切入边界，保留相关调用链、并发语义或组件交互；未覆盖根因机制的浅层假绿不能作为回归保护。若不存在这样的测试切入边界，记录架构风险并以 `original_repro` 为主要证明。
- **临时产物 disposition**：上游提供或本轮创建 `temporary_artifacts` 时逐项消费/记录位置或标识、敏感性/安全影响、`removed | retained` disposition、保留原因（仅 retained）、责任人和处置验证。字段省略表示上游未报告创建临时产物，不触发额外扫描；显式 `unknown` 必须先闭合。
- **性能 / 稳定性影响**：明确性能验收，或触及 hot path、复杂度、查询、序列化、I/O、并发、缓存、CPU / 内存时，定义同一 workload、环境和口径的 baseline / candidate 与可接受判据；flaky 在同等条件下用风险相称的受控重复或频率比较证明。无合理影响面可记 `not_applicable` 并简述理由。

### 3. Implement

按当前增量做最小实现：

- 保持在允许范围内。
- 避免顺手扩张功能、重排结构或修无关问题。
- 涉及测试或 mock 时，遵守 `references/testing-anti-patterns.md`。

### 4. Run Minimal Relevant Verification

自动运行最小相关验证，不固定全量菜单：

| 改动类型 | 最小相关验证 |
|---|---|
| 文档 / Skill / prompt | `rg` 引用检查、结构检查、diff 审查、格式检查 |
| 版本号 / metadata | frontmatter / manifest 检查、相关引用检查 |
| CLI 行为 | 运行具体 CLI 命令，记录退出码和关键输出 |
| API / 函数行为 | 目标单测、最小脚本或现有相关测试 |
| UI 行为 | 浏览器操作、截图、关键 DOM / console 证据 |
| prompt / agent workflow | 示例输入输出、golden diff、结构字段检查 |
| bugfix | 消费 `systematic-debugging` 提供的因果解释、证据引用、修复边界、目标行为和验证路径；`recommended_proof_strategy` 如有则作为建议 |
| 遗留行为 | characterization case 或 golden output |
| 用户明确 TDD | strict TDD：Red → Green → Refactor |

bugfix 按 Proof Plan 重跑 `original_repro`，存在 `minimal_repro` 时也重跑；单次绿色不能证明 flaky 已修复，功能通过也不能替代性能非退化证据。

### 5. Interpret Result

- `PASS`：可交付当前增量，并输出 Proof Block。
- `FAIL`：若原因局部清楚，最多做一轮局部修复并复验；若失败原因不清，转 `systematic-debugging`。
- `PARTIAL`：只能报告部分证明，必须列出未验证项，不得声称完成。
- `NOT_RUN`：必须说明未运行原因和风险，不得声称完成。

### 6. Emit Proof Block

开发结果必须包含 Proof Block，供 reviewer 或用户复查。

### 7. Final Verification Handoff

- 当当前增量已覆盖用户请求，且即将声明“已完成 / 已通过 / 可交付”，或用户要求“确保通过”、端到端验证、合并或 PR 时：默认先调用 `requesting-code-review`；只有用户明确要求跳过时才能跳过，并记录原因。审查通过后必须调用 `verification-before-completion`，再作完成声明。
- 若由 `plan-impl` 编排，返回 Proof Block 和未覆盖项给编排器，不自行重复最终审查或验证；由其按 `REVIEWING -> VERIFYING` 状态机执行。

---

## Proof Block 输出契约

完成当前增量后，用便于阅读的 Markdown 输出

```markdown
## Proof Block

### 目标约束
- <本次只实现什么>
- <明确不做什么 / 禁止范围>

### 验收标准
- <可观察验收点>

### 最小验证命令
- `<command>`：<为什么该命令与本任务强相关且成本最低>

### 运行结果
- 状态：PASS / FAIL / PARTIAL / NOT_RUN
- 关键输出：<测试名、退出码、日志片段、截图路径、CI 链接等>

### 复现、回归与测试切入边界
- <bugfix 的 original / minimal repro 重跑结果（original 为主要证明），以及回归测试所覆盖的真实调用链、并发语义或组件交互；非 bugfix 写 `not_applicable`；若不存在能够覆盖根因机制的测试切入边界，记录架构风险与 original 证明>

### 临时产物处置（仅上游提供或本轮创建时）
- <每项的位置或标识、敏感性/安全影响、removed|retained、保留原因（仅 retained）、责任人和处置验证；无法判断时写 `unknown`>

### 性能 / 稳定性证据
- <同 workload / 环境 / 口径的 baseline / candidate 与判据，或同等条件下的受控重复 / 频率比较；无影响面写 `not_applicable` 及理由>

### 实现摘要
- <改了什么文件 / 行为>

### 附加证据
- <截图 / 日志 / CI / diff / reviewer 可复查路径；无则写“无”>

### 风险说明
- <仍可能出问题的边界；无则写“无已知风险”>

### 未验证项
- <未覆盖的范围及原因；无则写“无”>
```

输出约束：

- 默认简短，每项 1-3 条。
- 日志只贴关键片段；大输出引用命令、文件路径或 CI 链接。
- `FAIL / PARTIAL / NOT_RUN` 不得包装成完成。
- 若 proof 来自截图、日志、CI、文件 diff 或生成物，必须给出可复查路径或稳定复现方式。
- 不得用单次绿色声明 flaky 已修复，也不得用功能通过替代性能非退化证据。

---

## 执行期决策边界

本 Skill 不负责在实现阶段发起高风险产品、架构或范围决策；这些决策必须在进入实现前被识别，并写入计划、任务卡或阻塞条件。

执行期只消费以下已确定输入：

- bugfix 的已验证因果解释与证据引用（非 bugfix 不要求）
- 修复或实现边界
- 目标行为与验收标准
- 验证路径；`recommended_proof_strategy` 如有则作为建议
- 人工已确认的高风险决策和阻塞条件

若实现过程中发现以下情况，停止并返回 `BLOCKED`，不得在执行期补做人工决策后继续扩大实现：

1. **计划缺少关键决策**
   - 数据模型 / Schema 变更未明确
   - 对外 API 语义破坏或删除未明确
2. **高风险边界不清**
   - 鉴权、权限、隐私数据处理逻辑边界不清
   - 并发一致性或事务边界不清
3. **高影响范围与验收不明确**
   - 跨多个模块联动修改，且目标边界或验收标准不清晰
   - 需要改变任务卡允许范围、验收标准或证明策略

返回 `BLOCKED` 时，在 Proof Block 的“风险说明 / 未验证项”中写明缺失决策，并交回计划制定者或用户处理。

---

## 职责边界

本 Skill 负责：

- 小步实现当前增量。
- 自动运行最小相关验证。
- 输出可复现 Proof Block。
- 根据 `systematic-debugging` 的 `FIXABLE + execution_authorization=granted + matching execution_authorization_basis` 交接修复已确认根因且获授权的 bug。

本 Skill 不负责：

- 根因未知时猜测修复。
- 全量测试套件回归判定。
- 发布前系统级验收。
- 分支收尾、PR、合并或 worktree 清理。

全量回归与最终完成验证交由 `verification-before-completion`。

---

## 完成验收清单（本 Skill）

在标记当前增量完成前：

- [ ] 当前增量已被切成单一可验证范围。
- [ ] 已明确目标约束和验收标准。
- [ ] systematic-debugging bugfix 的 `execution_authorization=granted`，且 basis 已匹配当前 fix boundary、动作类型和所需专项确认；其它入口不适用。
- [ ] 已运行最小相关验证，或明确说明 `PARTIAL / NOT_RUN` 原因。
- [ ] Proof Block 包含运行结果、风险说明和未验证项。
- [ ] bugfix 已重跑 `original_repro`，存在时亦重跑 `minimal_repro`；回归保护位于能够覆盖根因机制的测试切入边界，或已记录不存在该边界的架构风险。
- [ ] 若上游提供或本轮创建了 `temporary_artifacts`，已逐项记录统一字段并闭合 `unknown`。
- [ ] 已评估性能 / 稳定性影响；适用时有同口径 baseline / candidate 或风险相称的频率证据，不适用时已说明理由。
- [ ] 未将 strict TDD 用于用户未明确要求的场景。
- [ ] 若发现计划缺少高风险决策，已返回 `BLOCKED`，没有在执行期自行扩大范围。

---

## 示例：文档 / Skill 改动

```markdown
## Proof Block

### 目标约束
- 只更新当前 Skill 的触发与输出契约。
- 不修改执行脚本或无关 Skill。

### 验收标准
- 新 Skill 名和交接字段在主链路文档中一致。
- 旧默认实现路径不再引用旧 Skill。

### 最小验证命令
- `rg -n "proof-oriented-development|Proof Block" skills docs AGENTS.md`：检查主链路引用一致性。

### 运行结果
- 状态：PASS
- 关键输出：旧名只出现在允许保留的历史说明或已知未同步项中。

### 实现摘要
- 重写 Skill 契约并同步主链路引用。

### 附加证据
- diff 可审查路径：`skills/proof-oriented-development/SKILL.md`

### 风险说明
- 运行时已加载的 Skill 列表可能需要重新加载后才显示新名。

### 未验证项
- 未运行完整 agent eval。
```

## 示例：用户明确要求 strict TDD

```text
用户输入包含“用 TDD 实现”或“先写失败测试”。
```

此时可使用 Red → Green → Refactor，但仍必须在最后输出 Proof Block，说明失败测试、通过测试和未验证项。
