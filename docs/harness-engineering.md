---
type: Concept
scope:
  - harness-engineering
---

# Harness Engineering 体系设计

Power-Agent 的 Harness 让环境、知识和验证对 Agent 清晰可用，并以轻量能力支持授权内连续推进，不用固定流程替代判断。当前决定见 [ADR-0014](adr/0014-current-baseline.md)；组件及安装边界见[架构](architecture.md)。

## 参考来源

- [Harness engineering: leveraging Codex in an agent-first world](https://openai.com/index/harness-engineering/) — Ryan Lopopolo, OpenAI, 2026-02-11
- [Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)
- [Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- [Writing effective tools for AI agents — with agents](https://www.anthropic.com/engineering/writing-tools-for-agents)
- [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)
- [Code execution with MCP: Building more efficient agents](https://www.anthropic.com/engineering/code-execution-with-mcp)

这些来源描述可用模式，不构成项目的固定运行剧本。是否保留或调整机制，应结合当前模型、宿主和实际结果判断；没有对照证据时不声称效果提升。

## 环境可读性

Agent 无法读取、查询或执行的工程事实，不能稳定约束结果。重要知识应进入模型实际可达的载体：代码、类型、测试、linter、命令帮助、结构化日志、可查询文档或外部权威系统。

仓库是长期工程真相的 canonical store，不是唯一运行时信息来源。CI、issue、观测系统、宿主 session 和 memory 都可提供权威事实；关键是来源可定位、与当前版本匹配，并能被再次检查。

`AGENTS.md` 是地图而非百科全书。高频、跨任务约束留在入口；专门知识放到清晰路径并按需读取。上下文越大不等于判断越好，高信号和可发现性比预加载更重要。

对于所有编码任务都适用的最小完整改动偏好，Power-Agent 使用一份[默认规则源](../skills/codebase-design/references/minimal-complete-change.md)，由宿主 hook、扩展或 Cursor 插件规则适配。动态读取失败时实现会报告错误，静态生成规则可用同步检查发现缺失或过期；这些机制旨在送达约束，并不证明宿主已加载或模型遵循。安装和宿主限制见[兼容性指南](agent-compatibility.md)。

整包安装、默认发现和实际送达是不同问题：检查元数据和依赖只能证明静态配置；目标宿主中检查请求上下文才能证明该场景送达；只有任务行为证据才能评估实际效果。手动流程不加入自动调用链；事件数量不代表强化效果，是否增加注入点应由真实请求中的缺失、重复或生命周期偏差决定。

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

## Sub-agent 与环境

新上下文子代理可以隔离独立调查、实现、审查或验证，但不自动创造可信度；调用者仍需检查任务解释、证据和最终整合结果。支持条件和资源见[架构](architecture.md#宿主与-sub-agent)，协作与授权见[工作方式](workflow.md#任务图与唯一状态源)。

## 证据优先

模型的流畅解释、自检或流程记录不能证明结果。完成声明需要与实际风险匹配、覆盖当前被测内容和环境的可核对证据；某些历史或不可重跑场景只能提供有限观察，应说明缺口，不能一概声称可复现。

证据不是固定报告格式。一个局部改动可能只需要真实入口的成功输出；一个 bugfix 需要覆盖原失败场景与根因机制，原场景无法安全重跑时，应说明等价观察的依据与未验收条件；性能、安全、数据和 UI 则需要覆盖相应属性的专门观察。Harness 的责任是让这些观察容易获得、容易理解、容易复现。

验证可以针对 dirty working tree。证据复用须核对被测内容、相关依赖和环境；只有提交、PR、合并等操作才需要把证据与 commit identity 对应，目标提交的 CI 门禁仍须满足。授权和外部副作用是独立边界，不能用测试绿色替代对既有授权的核对。

## 长任务与持久产物

跨窗口、跨会话、人类审阅或外部审计可能需要计划、进度、任务图或 manifest。它们是否值得落盘取决于恢复成本和消费者，而不是任务被归入哪个等级。

好的 durable artifact 保存未来行动真正需要的目标、约束、决定、证据与剩余未知。可从 git、CI 或工具重新生成的大体量中间结果留在 scratch 空间；短任务不创建仪式性 handoff、feature list 或 session log。

## 知识可定位性

长期知识、任务状态与执行时证据各有不同生命周期。Agent 应能定位项目现有术语、决定与稳定事实，以及需要时的 tracker、验证来源和环境条件；不要把计划或交接变成另一份可独立更新的任务状态。普通项目沿用自己的文档协议，不强制启用 Bundle。

本仓 `docs/` 已采用 Bundle：Concept 使用非空 `type`，ADR 保留历史及被取代关系。`setup-power-agent` 补最小入口，`dev-docs` 处理知识写入与核验；需要设计或演进导航时，由用户显式调用 `knowledge-navigation`。这些能力不组成固定链；结构检查不能替代对正文事实的核对，未执行的验证不标为已验证。

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
