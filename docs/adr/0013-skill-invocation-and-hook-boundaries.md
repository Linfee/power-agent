---
type: Decision
status: accepted
verification:
  strategy: historical
supersedes:
  - 0012-matt-led-skill-fusion.md
sources:
  - AGENTS.md
  - skills/writing-for-agents/references/skill-mechanics.md
  - scripts/check-invocation-consistency.sh
  - pi-extension/index.mjs
  - skills/setup-power-agent/references/agent-compatibility.md
---

# ADR-0013: 收敛模型可见入口，按实际缺口增强 hook

**日期：** 2026-11-12

## 背景

Matt 固定来源的插件分发 27 个 Skill，其中 11 个允许模型调用、16 个由用户启动。Power-Agent 原先开放 24 个入口，混合了工程能力和流程选择。整包安装、默认发现、正文加载和外部操作授权是不同边界，不能由安装数量推导模型应看见多少入口。

Ponytail 在 pi/OMP 中只有 `before_agent_start` 注入规则；额外的会话切换、分支和活动事件服务于可变模式与状态栏。Power-Agent 只有固定默认约束，无需复制这些状态机制，也不能将更多事件注册当成更可靠送达的证据。

## 决定

- 继续整包分发 25 个 Skill。`grill-with-docs`、`to-spec`、`to-tickets`、`wayfinder`、`triage`、`improve-codebase-architecture`、`retro`、`handoff` 为 8 个手动入口；其余 17 个允许模型调用。该清单不是固定数量配额，后续变化由实际入口和依赖证明。
- 保留 Matt 的模型可调用工程能力，并保留 Power 的知识能力。`implement`、`implement-spec` 作为自主执行入口保持自动可达，`setup-power-agent` 由它们按需调用，不能直接隐藏这些依赖。
- 手动入口须由用户显式启动；启动后可以组合自动能力，但任何 Skill 都不能自动调用手动入口，也不能读取其正文绕过限制。正文具名入口引用是依赖，普通支持资料和围栏示例不是调度；检查器验证可静态识别的正文依赖，不声称理解所有自然语言。
- 手动入口同时声明 `disable-model-invocation: true` 与 Codex 的 `policy.allow_implicit_invocation: false`。两者的宿主支持、描述可见性和调用语义分别验证，不把元数据当通用访问控制。
- hook 只负责固定约束在宿主生命周期中的送达。维持现有薄适配和幂等合并，不新增模式、分支状态、每工具提醒或 provider payload 改写。固定约束仍只有一个随包来源，不将 Skill 正文全部常驻注入。
- 先观察真实宿主的工具连续调用、恢复、压缩后与新上下文子代理请求；只有发现具体遗漏才补对应注入点。声明配置、手动调用假 handler、模型自评和真实请求送达是不同证据。

本决定替代 [ADR-0012](0012-matt-led-skill-fusion.md) 的默认调用策略，并继续采用其余融合原则：授权内连续推进、按风险选择证明、小任务直接实现、唯一 tracker、新上下文子代理及现有知识协议。旧正文保留作为来源，不恢复旧技能别名或固定流水线。

## 后果与验收

模型常驻发现范围缩小，人工流程仍安装并可显式使用；自动实施与知识依赖保持可达，不引入路由器或隐藏调用机制。人工入口不等于允许发布、删除、访问秘密或改变生产配置。

同步入口、双语 README、调用元数据、现行文档和调用一致性检查。验收分别报告声明一致性、原生 Skill 发现、显式调用、实际规则送达及宿主限制；未取得信任、组织策略拒绝或未运行的宿主不记作成功。不得修改用户真实配置或绕过宿主安全检查。
