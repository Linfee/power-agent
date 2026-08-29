# 调查交接（按需）

**加载时机：** 创建过临时探针、授权含糊、要升级架构，或调用方需要可校验字段时。日常调查用主 Skill 的最小交接即可。

## 状态

| 状态 | 何时 | 下一步 |
|---|---|---|
| `INVESTIGATING` | 还不够区分 | 继续调查 |
| `HYPOTHESIS_VERIFIED` | 因果已支持，交接未闭合 | 补边界与复验路径 |
| `FIXABLE` | 因果闭合且交接完整 | 按授权交给 POD |
| `BLOCKED` | 外部/安全/授权挡住调查 | 写清解除条件 |
| `ESCALATE` | 局部边界不够，需要设计决策 | `discuss` |

`ESCALATE` 由证据触发，不用失败次数。缓解不能标成根因修复。

## `FIXABLE` 字段

必填：`status`、`evidence_refs`、`causal_explanation`、`fix_boundary`、`target_behavior`、`verification_path`（original repro；有 minimal 也要，二者不替代）、`execution_authorization`（`granted | missing | unknown`）及其依据（来源、覆盖的动作与边界、生产/破坏性等专项确认）。

`granted` 只在当前用户请求或已授权任务卡明确覆盖本次 `fix_boundary` 和动作类型时成立。

创建过临时产物时，逐项记录位置、敏感性、`removed | retained`、保留原因和处置验证。
