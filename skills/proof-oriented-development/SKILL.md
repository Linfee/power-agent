---
name: proof-oriented-development
description: |-
  证明导向实现 Skill。小步修改代码、运行最小相关验证并交付 Proof Block；进入实现阶段或 bugfix 边界已确认时触发。
  Triggers: 实现功能, 中小开发任务, 局部开发验证, 已确认 bugfix, proof-oriented, Proof Block, 证据交付, 最小有效验证, TDD, 测试驱动.
---

# Proof-Oriented Development

以最小增量推进实现，交付时给出低成本、可复现、与任务强相关的证明。

**铁律：没有最小有效证明，就不能声称当前增量完成。strict TDD 只在用户明确要求（`TDD`、`测试驱动`、`先写失败测试`、`Red/Green/Refactor`）时启用，其他情况不自动升级。**

## 入口

- 目标行为、修改边界、验收路径都清楚的功能实现或行为调整 → 直接用本 Skill。
- 修 bug 但根因、修复边界或验证路径还不清楚 → 先去 `systematic-debugging`。
- 从 `systematic-debugging` 接手 bugfix 的前提：拿到 `FIXABLE` 交接，且 `execution_authorization=granted`、basis 覆盖当前 `fix_boundary` 和动作类型。授权缺失、对不上或 basis 不可审计时，保留交接并请求最小授权，不动文件。

开始前做最小可行性检查：**目标**（要改变什么）、**边界**（什么不能顺手改）、**验收**（凭什么判断完成）三样要齐。缺哪样问哪样，问题只围绕缺失项。缺口涉及公共 API、数据模型、权限、安全、迁移、并发语义或高影响 UX 时，返回 BLOCKED，说明缺什么决策。

影响面超出局部时（跨模块依赖、多阶段迁移、安全/权限/数据一致性风险、预期多轮审查），不由本 Skill 直接实现：有完整计划交给 `implement`，没有计划先 `writing-plans`。

## 工作方式

一次只做一个可验证的增量，不把多个独立目标混在一次改动里。每个增量走这个循环：

1. **先想清楚要证明什么**：目标约束、验收标准、成本最低的验证方式。bugfix 还要确认 original repro（真实场景的主要证明）和 minimal repro（如有）；有性能验收或合理影响面时，先定好同口径的 baseline / candidate 判据；上游报告或本轮会创建临时产物的，先想好怎么逐项处置。
2. **实现**：保持在允许范围内，不顺手扩张功能、重排结构或修无关问题。涉及测试或 mock 时，遵守 `references/testing-guide.md` 与 `references/testing-anti-patterns.md`。

   选型按 ordered ladder 依次尝试，在第一条满足当前契约、消费者、风险边界与 Proof 的层级停止，不跳到更重的层级：
   1. 不新增：复用仓库已有实现/函数/API/模块；
   2. stdlib / 平台原生能力；
   3. 已有依赖的能力；
   4. 满足当前契约的最小直接实现。

   进入会新增长期所有权的方案前，须由当前需求、真实消费者或代码/运行边界举证，并说明更早层级为何不充分。长期所有权仅指五类：新依赖、跨模块边界、外部配置面、持久/跨请求共享状态、具有 init/cleanup/concurrency 语义的生命周期；局部变量、派生状态和普通内部 helper 不进入此判断。ladder 永远不能削减 correctness、security、data 完整性、错误语义、契约或 Proof，也不能拒绝由真实外部约束、消费者或生命周期购买的必要 SDK、adapter、配置、状态或 cleanup。seam / adapter 深度与模块边界的裁决归 `codebase-design`，本 Skill 不接管。
3. **跑最小相关验证**：选与改动强相关、成本最低、可复现的方式，不固定菜单。文档类改动用引用/结构检查和 diff 审查；代码改动跑目标测试或最小脚本；UI 改动留浏览器操作和截图证据；bugfix 必须重跑 original repro（有 minimal 也重跑）。
4. **如实解读**：PASS 才能交付；FAIL 且原因局部清楚，最多就地修一轮再验；原因不清转 `systematic-debugging`；PARTIAL / NOT_RUN 写明没验证什么和原因，不得包装成完成。
5. **输出 Proof Block**。

两条硬约束：功能通过不能替代性能非退化证据；单次绿色不能证明 flaky 已修复。

## Proof Block 契约

固定小节如下（下游审计和 reviewer 以此为依据）：

```markdown
## Proof Block

### 目标约束
- <本次只实现什么；明确不做什么 / 禁止范围>

### 验收标准
- <可观察的完成判据>

### 最小验证命令
- `<command>`：<为什么它与本任务强相关且成本最低>

### 运行结果
- 状态：PASS / FAIL / PARTIAL / NOT_RUN
- 关键输出：<测试名、退出码、日志片段、截图路径、CI 链接等>

### 实现摘要
- <改了什么文件 / 行为>

### 风险说明
- <仍可能出问题的边界；无则写“无已知风险”>

### 未验证项
- <未覆盖的范围及原因；无则写“无”>
```

以下条件性小节只在命中时追加：

- **复现、回归与测试切入边界**（bugfix 必填）：original / minimal repro 的重跑结果，original 是主要证明。回归测试要落在能覆盖根因机制的切入边界上，保留相关调用链、并发语义或组件交互；覆盖不到根因机制的浅层假绿不算回归保护。不存在这种切入点时，记录架构风险并以 original repro 为主要证明。
- **临时产物处置**（上游报告或本轮创建过 `temporary_artifacts` 时必填）：逐项给出位置或标识、敏感性/安全影响、`removed | retained`、保留原因（仅 retained）、责任人和处置验证；无法判断写 `unknown`。
- **性能 / 稳定性证据**（有性能验收或合理影响面时必填）：同 workload / 环境 / 口径的 baseline / candidate 对照，或风险相称的受控重复 / 频率比较；无影响面写 `not_applicable` 加理由。

写作要求：默认简短，每项 1-3 条；大输出引用命令、文件路径或 CI 链接，不贴全文；证据必须给出可复查路径或稳定复现方式；额外的截图、日志、diff 证据附在运行结果后面。

## 什么时候停下来 BLOCKED

执行中不做高风险决策，发现以下情况就停下来返回 BLOCKED，在风险说明 / 未验证项中写清缺什么决策，交回计划制定者或用户：

- 计划缺少关键决策：数据模型 / Schema 变更未明确，对外 API 语义破坏或删除未明确。
- 高风险边界不清：鉴权、权限、隐私数据处理，并发一致性或事务边界。
- 继续实现需要超出任务卡允许的范围、验收标准或证明策略。

BLOCKED 时保持 handoff 完整：已确认的事实、已尝试的动作和缺失项都写进 Proof Block，方便上游接手。

## 交接

- 独立使用本 Skill、准备声明整体完成时：默认先调用 `code-review`（用户明确跳过时记录原因），再按工作区检查语义（dirty 或无 HEAD 先提交）进入待提交提示或最终验证。
- 由 `implement` 编排时：把 Proof Block 和未覆盖项交给编排器，不自行重复最终审查或验证。
- 全量回归与最终完成验证归 `verification-before-completion`；分支收尾归 `finishing-a-development-branch`。

---

## References

- `references/testing-guide.md`：好测试、接缝与 mock 的位置；strict TDD 限定规则。
- `references/testing-anti-patterns.md`：测试与 mock 的反模式约束。
