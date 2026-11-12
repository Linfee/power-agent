---
type: Concept
scope:
  - harness-engineering
---

# Harness Engineering 体系设计

Power-Agent 的 Harness 让环境、知识和验证对 Agent 清晰可用，并以 Matt 的轻量能力组织支持授权内连续推进，不用固定流程替代判断。当前调用与 hook 边界见 [ADR-0013](adr/0013-skill-invocation-and-hook-boundaries.md)，其余融合和状态原则沿用 [ADR-0012](adr/0012-matt-led-skill-fusion.md)。

## 参考来源

- [Harness engineering: leveraging Codex in an agent-first world](https://openai.com/index/harness-engineering/) — Ryan Lopopolo, OpenAI, 2026-02-11
- [Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)
- [Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- [Writing effective tools for AI agents — with agents](https://www.anthropic.com/engineering/writing-tools-for-agents)
- [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)
- [Code execution with MCP: Building more efficient agents](https://www.anthropic.com/engineering/code-execution-with-mcp)

这些来源描述了可用模式，不构成项目的固定运行剧本。Power-Agent 根据前沿模型与宿主能力持续做 ablation，只保留当前仍能提高结果可靠性的机制。

## 环境可读性

Agent 无法读取、查询或执行的工程事实，不能稳定约束结果。重要知识应进入模型实际可达的载体：代码、类型、测试、linter、命令帮助、结构化日志、可查询文档或外部权威系统。

仓库是长期工程真相的 canonical store，不是唯一运行时信息来源。CI、issue、观测系统、宿主 session 和 memory 都可提供权威事实；关键是来源可定位、与当前版本匹配，并能被再次检查。

`AGENTS.md` 是地图而非百科全书。高频、跨任务约束留在入口；专门知识放到清晰路径并按需读取。上下文越大不等于判断越好，高信号和可发现性比预加载更重要。

对于所有编码任务都适用的最小完整改动偏好，Power-Agent 使用一份[默认规则源](../skills/codebase-design/references/minimal-complete-change.md)，再由插件 hook、扩展或 Cursor 插件自带规则适配到宿主；动态注入时缺少规则源应可见报错，不应伪装成已启用，静态生成规则则通过同步检查发现缺失或过期。按需 Skill 提供更完整的方法，不能用常驻规则替代，也不要求每个任务都调用设计 Skill。安装入口和能力限制见[宿主兼容性](agent-compatibility.md)。

整包安装与默认发现分开：工程能力和自动执行依赖保持模型可达，人工流程不加入自动调用链。hook 只保障固定约束送达；事件数量不代表强化效果，Ponytail 的 OMP 会话切换和分支事件主要恢复模式，本包不复制没有消费者的状态机制。是否增加注入点由真实请求中的缺失、重复或生命周期偏差决定。

## 约束与自由度

Harness 应明确必须保护的边界，例如授权、兼容性、数据完整性、外部协议和验收入口；不应规定模型可以根据现场证据自行选择的工具、顺序或表达形式。

可迁移的 Skill 会说明：

- 什么结果对用户真正有用；
- 哪些事实会改变方案；
- 哪些约束不能为了速度牺牲；
- 什么证据足以支持结论；
- 哪些实现选择留给当前模型。

这些是设计审查维度，不是统一 Prompt 模板。Skill 应允许不同的正确路径，不要求输出固定章节来证明遵循。

## 机械化边界

重复、确定、机器可裁决的工作不应长期留在 Prompt：

- 文件格式、机器状态和 API 使用 schema；
- 代码不变量使用类型、lint、测试或 hook；
- 原子更新、扫描、同步和计算使用脚本；
- 工具错误返回可执行上下文，而不是只给错误码；
- 大结果支持过滤、分页和摘要，避免无关数据占满上下文。

精确步骤只在外部世界确实要求顺序时保留，例如授权确认、破坏性动作、事务性写入或机器协议。其他地方优先陈述判断原则。

## Sub-agent 作为基础能力

Power-Agent 面向支持普通 sub-agent 的宿主。主代理可以把独立调查、实现、审查或验证交给干净上下文中的子代理，再整合局部结果。

是否使用一个或多个子代理由任务依赖决定，不由固定层级决定：独立工作并行，共享写边界协调，后续依赖前序证据时串行。仓库不引入 team mode、平台专属 group API 或数字并发上限，也不维护无 sub-agent fallback。

子代理不会自动创造可信度。调用者仍需检查任务解释、证据来源、改动边界和最终整合结果。

## 证据优先

模型的流畅解释、自检或流程记录不能证明结果。完成声明需要新鲜、可复现、与实际风险匹配的系统外证据。

证据不是固定报告格式。一个局部改动可能只需要真实入口的成功输出；一个 bugfix 需要覆盖原失败场景与根因机制，原场景无法安全重跑时，应说明等价观察的依据与未验收条件；性能、安全、数据和 UI 则需要覆盖相应属性的专门观察。Harness 的责任是让这些观察容易获得、容易理解、容易复现。

验证可以针对 dirty working tree。证据复用须核对被测内容、相关依赖和环境；只有提交、PR、合并等操作才需要把证据与 commit identity 对应，目标提交的 CI 门禁仍须满足。授权和外部副作用是独立边界，不能用测试绿色替代对既有授权的核对。

## 长任务与持久产物

跨窗口、跨会话、人类审阅或外部审计可能需要计划、进度、任务图或 manifest。它们是否值得落盘取决于恢复成本和消费者，而不是任务被归入哪个等级。

好的 durable artifact 保存未来行动真正需要的目标、约束、决定、证据与剩余未知。可从 git、CI 或工具重新生成的大体量中间结果留在 scratch 空间；短任务不创建仪式性 handoff、feature list 或 session log。

## 知识系统

```text
docs/
├── architecture.md
├── development.md
├── workflow.md
├── harness-engineering.md
├── skill-and-harness-design.md
├── domain/
├── references/
├── adr/
├── exec-plans/
└── specs/
```

`setup-power-agent` 与 `dev-docs` 分别拥有初始化和知识写入/核验；按各自触发条件独立判断，不形成固定交接链。frontmatter 和来源语义在采用 Bundle 时保持准确；没有实际核验时不标为已验证。

需要设计或演进知识导航时，由用户显式调用 `knowledge-navigation`：从任务反推知识单元，区分导航、前置依赖与来源引用，通过项目观察、必要讨论及指定历史反馈选择改动。结构检查、任务走查和真实消费是不同证据，不用目录数量证明效果。它遵循目标仓库协议，不形成固定链；当前边界见 [架构](architecture.md)，历史理由见 [ADR-0011](adr/0011-knowledge-navigation-lifecycle.md)。

## 熵与 ablation

Agent 会复制仓库中的模式，包括坏模式。高价值不变量应通过工具和自动检查持续执行；文档 freshness、重复实现和技术债需要可观察入口。

同时，Harness 本身也会积累熵。模型和宿主升级后先问：

- 哪些步骤模型现在能稳定自行判断；
- 哪些模板没有真实消费者；
- 哪些状态只在描述流程而未保护结果；
- 哪些检查可改成确定性工具；
- 删除机制后，失败率或风险是否真的上升。

只有能改善真实结果的机制才留下。当前架构与 Skill 边界见 [architecture.md](architecture.md)，协作方式见 [workflow.md](workflow.md)。

## 宿主送达验证记录

以下为 2026-11-12 在隔离环境（独立 HOME/XDG 配置、合成凭据和 loopback 提供方）中的观察，属于维护证据，不是安装指南或兼容性承诺。它不证明真实模型的遵从、任务质量或抑制过度设计的效果，也不证明自然选择子代理；其他版本和未列明生命周期不推断通过。

| 宿主 | 已有观察或未验证范围 |
|---|---|
| Claude Code | 2.1.322 在隔离 HOME 中原生安装并发现 25 个 Skill；生命周期专项覆盖连续 Read、实际新上下文子代理、恢复、手动压缩及同进程压缩后继续执行。27 个相关请求各含一份规则；未强制自动压缩，未单独断言调用开关修改后的自动列表数量。 |
| pi | 1.5.2 隔离持久安装后保留 25 个 Skill 命令，向模型通告 17 个；`/skill:to-spec` 可显式展开。10 轮重复工具交互的 20 次 Read 均成功，30 个请求各含一份规则；手动压缩后继续执行也为一份。此前恢复已验证；本次原生工具集没有 sub-agent，未模拟该能力。移除后列表为空。 |
| OMP | 18.18.9 隔离持久安装后向模型通告 17 个 Skill，`/skill:to-spec` 可显式展开；实际 Read 连续调用、子代理、手动压缩后继续执行的编码请求各含一份规则。此前恢复已验证；自动压缩未强制。原生卸载后列表为空。 |
| Codex | 0.167.2 曾安装并启用插件，但请求未含规则；未授予 hook 信任，原因未定位，不能判为通过。完整 Skill 发现及子代理未验证。 |
| Cursor | 插件规则和 Skill 的真实 IDE 加载未验证；手动 Skill 的菜单可达性另有版本风险，不能判为全部可用。 |
| Factory / Droid | 1.8.0 的加载器代码支持共享 hook 格式，但实际 marketplace 添加被账户插件策略拒绝；未使用真实凭据或绕过策略，插件 hook、Skill 及子代理送达仍未验证。 |

规则送达、Skill 发现、普通 sub-agent 及规则继承分别验证；安装或 manifest 存在不等于运行成功。恢复、压缩后与更新按适用入口覆盖；协议测试、配置存在或模型自述不能替代送达证据。

Claude 的 `plugin validate --strict` 仍因警告退出 1：已有根目录 `CLAUDE.md` 上下文提示、共享 heredoc 的静态路径引用警告，以及图标和系统文件提示。路径在引用式 heredoc 中作为数据传递，特殊字符命令用例和真实 Claude 加载已通过；这不等于严格校验通过，也不代表公共目录发布已验收。
