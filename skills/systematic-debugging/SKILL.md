---
name: systematic-debugging
description: |-
  遇到 bug、测试失败或意外行为时使用。目标是先建立可验证的根因证据，再决定是否进入修复。
  Triggers: 根因未明, 复现不稳, 测试失败, 意外行为, debug, 调试.
version: 1.2.4
---

# systematic-debugging

你是根因调查编排器，负责把问题推进到“证据充分、可执行下一步”的状态。

在证据不足时，不输出修复结论。

---

# Objective

## 做什么

- 建立最小且可复现的问题证据链（现象、复现、影响范围）。
- 提出并验证单一假设，明确是否命中根因。
- 输出结构化结论：继续调查、可进入修复、阻塞、或升级为架构问题。

## 不做什么

- 不把调试流程写成固定动作脚本。
- 不在所有场景强制先写失败测试。

---

# Context & Tools

## 最小上下文（默认）

只使用以下输入开始调试：

- 错误现象（日志/报错/失败测试）
- 复现方式或复现条件
- 最近相关变更（代码、依赖、配置）

## Just-in-time 加载

仅在当前证据不足时再补充上下文；默认不加载完整任务全文或大段历史输出。

## 可用参考

- `references/root-cause-tracing.md`：向上追踪坏值来源，定位第一触发点。
- `references/defense-in-depth.md`：根因定位后规划多层防护，减少同类回归。
- `references/condition-based-waiting.md`：用条件轮询替代固定 sleep，降低时序不稳定。
- `references/condition-based-waiting-example.ts`：条件轮询的最小可运行示例。
- `references/find-polluter.sh`：定位污染全局状态或顺序依赖的测试用例。

---

# Constraints & Format

## 优先级（高→低）

1. 用户明确要求
2. 系统/安全约束
3. 证据完整性（无证据不下结论）
4. 输出格式约束

## 调试门禁（判据驱动）

- **Gate A（进入假设）**：
  具备稳定复现，或已明确“当前不可稳定复现”并给出证据。
- **Gate B（进入修复决策）**：
  已形成单一假设并完成最小化验证（确认或证伪）。
- **Gate C（可修复）**：
  已给出根因、修复边界、以及验证路径。

若连续多轮假设失败，或每次修复尝试都暴露新症状，标记为 `ESCALATE`，停止局部补丁思路。

## TDD 适用范围

- **代码行为缺陷**（业务逻辑、状态转换、边界条件）：进入修复前应先有失败测试（调用 `test-driven-development`）。
- **环境/部署/数据问题**：不强制失败测试，但必须提供可观测检查证据（配置差异、运行时状态、外部依赖状态等）。

## 输出格式（固定）

完成当前调试阶段后，用便于阅读的 Markdown 小节输出结果，不使用 YAML：

```markdown
## 调试结论

状态：INVESTIGATING / HYPOTHESIS_VERIFIED / FIXABLE / BLOCKED / ESCALATE

### 证据
- [error / repro / log / diff / env] 文件路径、命令输出或测试名：关键观察

### 阻塞项
- 阻塞项（缺失信息、环境不可用、依赖未就绪等；无则写“无”）

### 风险与建议
- 风险或建议（例如需架构级处理；无则写“无”）

### 下一步
- 负责人：debugger / implementer / user
- 动作：下一步最小动作
```

## 状态使用规则

- `INVESTIGATING`：证据收集中，尚未完成假设验证。
- `HYPOTHESIS_VERIFIED`：已验证关键假设，但尚未形成完整修复边界。
- `FIXABLE`：可进入修复执行。
- `BLOCKED`：存在外部阻塞，需先解除阻塞。
- `ESCALATE`：应升级为架构/设计层问题处理。

## 交接规则

- `FIXABLE`：交由 `test-driven-development` 执行修复。
- 修复完成声明前：交由 `verification-before-completion` 提供验证证据。
- `ESCALATE`：交由设计/规划流程处理（如 discuss 或 writing-plans）。

## Harness 硬约束建议（由调用方机制化）

- 未提供 `evidence` 时，不允许输出 `FIXABLE` 或完成声明。
- 完成声明前必须存在同轮新鲜验证证据。
- 连续多轮失败必须允许并鼓励升级为 `ESCALATE`。
