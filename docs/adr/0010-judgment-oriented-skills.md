---
type: Decision
status: accepted
supersedes: 0009-lean-default-orchestration.md
---

# ADR-0010: 判断导向的独立 Skill

**状态：** accepted（supersedes [ADR-0009](0009-lean-default-orchestration.md)）  
**日期：** 2026-08-30  
**影响文件：** `AGENTS.md`, `skills/`, `docs/architecture.md`, `docs/workflow.md`, `docs/harness-engineering.md`, `docs/skill-and-harness-design.md`

## 背景

Power-Agent 先后用完整工作流与 L0/L1/L2 分层降低编码 Agent 的不确定性。最近一个月的会话说明，固定阶段、状态枚举、交接模板和具名 Skill 链会让强模型花力气复现流程，而不是根据现场证据解决问题。L0/L1/L2 只部署了一天，没有足够运行证据；本决定来自用户明确的产品方向，而不是把旧会话事后归入新分层。

## 决定

Power-Agent 的 Skill 改为判断导向：教模型识别问题中承重的目标、事实、约束和验收证据，由模型自主决定工具、步骤、顺序、子代理和表达方式。Skill 的可靠性来自结果与真实证据，不来自过程一致或模板完整。

Skill 可以自由组织内容，不采用统一章节模板。精确 schema、步骤和顺序只在脚本、外部协议、安全边界或真实机器消费者要求时存在；能够机械化的重复动作优先实现为脚本。

除 `setup-power-agent`、`dev-docs`、`dev-docs-maintain` 组成的知识维护子系统外，一个 Skill 的正常完成路径不得依赖另一个具名 Skill。Skill 可以消费任意已有材料或使用普通 sub-agent，但必须能独立完成自己的用户目标。

Power-Agent 只支持具备普通 sub-agent 能力的宿主。不提供无 sub-agent fallback，不使用 team mode，不规定子代理并发上限。是否并行由任务依赖和写所有权决定，平台资源限制由宿主承担。

`verification-before-completion` 与 `finishing-a-development-branch` 合并为 `finish-development`。它判断当前工作是否有足够新鲜证据支撑完成，并在用户要求时安全处理提交、PR、合并、保留或丢弃；dirty working tree 可以直接验证，只有 commit-bound 行为才要求证据绑定提交。

## 仍然成立的约束

- 用户目标与授权边界不能由模型自行扩大。
- 完成声明必须有与实际结果匹配的新鲜系统外证据，未验证面如实说明。
- 安全、权限、数据、生产和不可逆操作的真实边界不能因减少流程而削弱。
- 复杂度必须由当前目标、消费者、运行边界或风险证明；ADR-0008 的 ordered ladder 不再是固定执行顺序。
- 计划、审查、调试、实现和完成判断仍是可用能力，但不构成强制链路或固定层级。

## 与既有 ADR 的关系

- supersedes ADR-0009：删除 L0/L1/L2 运行时分层，以“达到目标所需的最轻判断与证据”取代层级路由。
- 限定 ADR-0006：不再设置规划 Gate 或固定审查循环；人类继续持有意图、授权和不可逆决策。
- 限定 ADR-0008：保留“复杂度需要当前证据”的判断，删除 ordered ladder、消费者矩阵和多处投影的运行时义务。
- 延续 ADR-0003 的 durable artifact 能力，但不要求 Skill 通过固定产物交接。
- 延续 ADR-0007 的职责隔离原则，但 reviewer 生命周期与修复轮数由当前任务判断，不成为固定流程。

## 后果

- `AGENTS.md`、架构与工作流文档描述能力和判断原则，不再规定标准流水线。
- Skill 删除固定状态、模板、Gate、轮数、具名路由和无 sub-agent 兼容路径。
- references 只保留特殊判断知识或机器协议；确定性动作保留脚本。
- Skill 可以组合，但组合是模型根据任务作出的选择，不是仓库预先绑定的链路。
- 知识维护三个 Skill 可以按实际缺口互相调用，但不形成每次必跑的串行流程。
