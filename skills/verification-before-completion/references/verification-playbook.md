<!-- verified: 2026-05-05 -->
<!-- scope: verification-before-completion, verification-playbook -->

# Verification Playbook

本文件提供验证路径建议，不是强制命令菜单。

## 验证顺序

1. 审计 Proof Block 或等价证据块。
2. 比较完成声明、任务范围、验收标准和证据范围。
3. 判断证据强度是否匹配任务风险。
4. 缺口可补时补跑最小额外验证。
5. 缺口不可补时返回 `PARTIAL` 或 `BLOCKED`。
6. 缺的是任务定义、验收、证明策略、风险决策或根因时，不补定义，直接交回对应上游。

## Proof Block 审计

### 完整性检查

- 是否包含目标约束或声明目标。
- 是否包含验收标准或能从任务卡 / review-contract 映射。
- 是否包含验证方式：命令、截图、日志、CI、diff 或人工核对路径。
- 是否包含运行结果。
- 是否包含风险说明或未验证项。

### 相关性检查

- 验证命令是否直接覆盖完成声明。
- 证据范围是否覆盖改动范围。
- 未验证项是否影响验收标准。
- Proof Block 是否与任务卡 / plan / review-contract 冲突。

### 可复现性检查

- 命令能否重新运行。
- 截图、日志、CI、diff 是否有可复查路径。
- 时间戳是否新鲜。
- `commit_sha` 是否与当前 HEAD 匹配。

## 等价证据块

非 POD 入口可以使用等价证据块，但至少包含：

- 声明目标。
- 验证方式。
- 运行结果。
- 证据范围。
- 风险 / 未验证项。

以下场景不得降级为等价证据块：

- 代码实现任务缺少目标、验收或验证结果。
- bugfix 缺少复现路径、根因或修复后验证。
- 高风险公共 API / 权限 / 数据 / 迁移变更缺少计划阶段证明策略。
- 完成声明来自实现代理，但没有 Proof Block 或等价证据块。

## 任务类型与建议路径

| 任务类型 | Proof Block 足够条件 | 常见补充验证 |
|---|---|---|
| 文档 / Skill / prompt | 引用检查、结构检查、diff 证据 | `rg`、格式检查、模板字段检查 |
| 代码实现 | 目标行为测试或最小脚本 PASS | 受影响模块测试、lint/typecheck |
| UI 行为 | 截图 / 浏览器操作覆盖验收 | 控制台日志、DOM 检查 |
| bugfix | 同一复现路径修复后通过 | regression / characterization case |
| 配置变更 | 配置加载和关键路径可用 | dry-run、启动检查 |
| 高风险变更 | 任务卡指定验证 + 风险对应证据 | 局部回归、CI、审查 |

## 证据记录最小字段

- commit_sha
- verified_at
- kind
- source
- command_or_path
- exit_code
- scope
- summary

`kind=proof_block_audit` 时：

- `source`：`proof_block` 或 `equivalent_evidence`
- `command_or_path`：`proof_block:<section-or-anchor>`，无稳定锚点时写 `proof_block:inline`
- `exit_code`：`not_applicable`
- `scope`：本次完成声明覆盖范围
- `summary`：包含 `accepted|needs_more_verification|rejected` 与关键缺口

## 选择原则

- 先选择“能直接证明声明”的验证路径。
- 最小充分验证优先，避免无关全量运行。
- Proof Block 可接受时，不重复实现阶段验证。
- Proof Block 有可补缺口时，只补与完成声明直接相关的验证。
- 证据过期、HEAD 不匹配或工作树状态变化时，重新运行最小验证。
- 若无法验证，必须明确阻塞原因与下一步动作。
