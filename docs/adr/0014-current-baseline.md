---
type: Decision
status: accepted
verification:
  strategy: historical
supersedes:
  - archive/0001-skill-as-execution-unit.md
  - archive/0002-disposable-subagents.md
  - archive/0003-artifacts-as-coordination.md
  - archive/0004-lean-agents-md.md
  - archive/0005-gate-mechanism.md
  - archive/0006-gate-restructuring.md
  - archive/0007-reviewer-session-continuity.md
  - archive/0008-complexity-admission.md
  - archive/0009-lean-default-orchestration.md
  - archive/0010-judgment-oriented-skills.md
  - archive/0011-knowledge-navigation-lifecycle.md
  - archive/0012-matt-led-skill-fusion.md
  - archive/0013-skill-invocation-and-hook-boundaries.md
sources:
  - package.json
  - skills/implement/SKILL.md
  - skills/implement-spec/SKILL.md
  - skills/proof-oriented-development/SKILL.md
  - skills/code-review/SKILL.md
  - skills/knowledge-navigation/SKILL.md
  - skills/dev-docs/references/project-docs-profile.md
  - skills/writing-for-agents/references/skill-mechanics.md
  - skills/codebase-design/references/minimal-complete-change.md
  - hooks/defaults.cjs
  - pi-extension/index.mjs
  - scripts/check-invocation-consistency.sh
---

# ADR-0014: 当前工程能力、调用与分发基线

**日期：** 2026-11-12

**基准：** Power-Agent 0.2.0。按用户要求合并 ADR-0001 至 0013 中仍有效的决定，以当前 Skill、代码和调用元数据为准；不借文档整理改变产品行为。

## 为什么合并

旧 ADR 中仍标为 accepted 的固定 Gate、旧 Skill 链和独立安装要求，已被后续记录部分限定或替代。读者必须串读多份历史才能恢复当前契约，容易把已经退出的义务重新带入。现将当前决定集中在本记录，原文及原有取代链保存在 [ADR 归档](archive/)。日常事实和操作分别见[架构](../architecture.md)、[工作方式](../workflow.md)、[开发指南](../development.md)，不再拼接旧 ADR 作为现行指令。

2026-11-12 后续技能重构将入口收敛为 24 个，`dev-docs-maintain` 合并入 `dev-docs`，`knowledge-navigation` 改为手动；本记录第 1、2、3 节已同步当前边界。

## 1. 能力可组合，入口有边界

以 Matt 固定版本的工程方法为主干，融合 Power 的证明、因果诊断、工程判断和项目知识。24 个 Skill 整包分发，不承诺单 Skill 独立安装，不引入品牌路由器或固定长链；相关迁入内容保留方法、理由、反例、示例和模板，轻量不等于正文越短越好。

15 个入口允许模型调用，9 个仅用户显式启动：`grill-with-docs`、`to-spec`、`to-tickets`、`wayfinder`、`triage`、`improve-codebase-architecture`、`retro`、`handoff`、`knowledge-navigation`。Matt 的自动能力位置（`tdd` 一对一融合为 POD）与 `dev-docs`、`setup-power-agent`、`implement`、`implement-spec` 保持自动可达。数量来自当前用途与依赖，不是配额或收益实验的结论。

需要用户选择工作方向、且没有内部自动调用依赖的入口才收为手动；零入边本身不表示所有能力都必须手动。整包内部具名调用只指向自动能力，不能读取手动正文绕过限制。手动入口同时声明 `disable-model-invocation: true` 与 Codex 的 `policy.allow_implicit_invocation: false`；宿主的实际发现、菜单可达性和调用语义仍须分别确认，元数据不是访问控制。

## 2. 授权内自主推进，证据与风险匹配

明确小任务或完整 issue 直接做，只有依赖、恢复或协作确有需要时才维护 spec、tickets 或地图。目标和必要取舍明确后，在已选路径内完成授权的实现、验证、适用审查和修复，不为能力切换增加人工接力。进入 `grilling` 仍按原版问题树逐轮追问并取得共同理解确认，确认前不实施。

可自动验证的行为默认 Red/Green；重构留到 review 阶段，在行为覆盖更完整时进行。已有失败可复用，纯重构、UI、文档和机械变更选匹配证据，不制造红灯。审查默认把需求符合性与工程质量分别交给独立 reviewer 并行；用户明确要求合并时才由同一 reviewer 覆盖，仍分维报告。不固定修复轮数。完成声明说明实际检查与未验证面，不将结构成功、模型复述或子票完成当成整体通过。

最小完整改动约束有一个[随包来源](../../skills/codebase-design/references/minimal-complete-change.md)：先核对目标、调用链与可复用能力，选择能完整满足约束的简单方案；不以行数、单一实现或固定阶梯否定真实的资源责任、不变量和 I/O 边界。不得借精简省略需求、安全、必要验证或数据保护。

普通 sub-agent 从新上下文开始，按真实依赖与写所有权并行，共享文件和状态有单一协调者，集成者负责组合验收。不使用 team mode，不规定平台并发数字，不维护无 sub-agent fallback；不把 worktree 当作权限沙盒，也不强制每轮更换 reviewer。

讨论、建议和草稿不等于实施许可；本地实现不自动授权 tracker 写入、Git 操作、发布、删除、秘密、权限或生产变更。按具体对象和动作核对已有授权，必要的人工决定不能因自治而省略。

## 3. 状态与知识各有权威位置

需要持久调度时，执行状态只在项目选定的 tracker；计划、交接和运行中的调度视图引用它，不维护第二份可独立更新的状态。普通实现和审查不因缺少 tracker 阻塞，也不要求每个阶段都落盘。

仓库保存可复用的系统知识和决定。`setup-power-agent` 补最小入口，`dev-docs` 负责稳定知识的写入与核验，`knowledge-navigation` 由用户显式启动设计或演进检索路径；这些能力按实际缺口组合，不形成固定链。

普通项目沿用自身文档协议，不强制建立 Bundle。本仓库继续采用 Bundle：Concept 有有效 `type`，ADR 使用历史策略及双向取代关系；验证以实际核验为准，不从文件年龄、结构通过或本文的 accepted 状态推导已验证。历史设计、计划与评估只证明当时范围，不继续充当当前规范或活动状态。

## 4. 固定规则薄适配，不复制动态产品机制

支持 Claude Code、pi、OMP、Codex、Cursor、Factory/Droid 的插件或包入口，不向业务项目复制规则或提供项目规则配置器。`hooks/defaults.cjs` 读取唯一规则源；Claude、Codex、Droid 使用原生 hook，pi/OMP 使用扩展，Cursor 使用生成的插件规则。安装、启用、信任和实际送达是不同边界，具体限制见[安装指南](../agent-compatibility.md)。

只有固定约束，没有可切换模式。保留幂等合并与用户已有文本，不复制 Ponytail 的模式恢复、状态栏、额外会话状态或每工具提醒，不改写 provider payload。先观察工具连续调用、恢复、压缩后与新上下文子代理的真实请求，发现具体送达缺口才补注入点；辅助请求单独判断。

本记录不宣布所有宿主均已通过，也不证明减少过度设计或普遍提高任务质量。真实宿主验证使用隔离配置；改用户实际安装、授予信任或修改组织策略仍须对应授权。当前验证入口见[开发指南](../development.md#选择检查)，历史实验保留其版本、失败与未覆盖面。
