# Power-Agent — Agent 指南

Power-Agent 是面向前沿模型的判断、验证与项目知识包。它不为模型规定标准开发流水线，而是帮助模型理解一类任务中真正承重的目标、约束、证据和验收。

## 核心原则

- **判断可迁移，结果可验证。** Skill 教模型如何判断，不要求复现固定过程。
- **目标先于形式。** 根据用户需要的可观察结果选择行动；模板、状态和产出物只有真实消费者需要时才存在。
- **过程由模型决定。** 在用户要求和既有契约内，按证据、依赖与风险选择工具、顺序、子代理和表达方式；必要的安全与兼容顺序不能省略。
- **独立优先。** 除知识维护子系统外，一个 Skill 的正常完成路径不依赖另一个具名 Skill。
- **证据外置。** 完成声明必须有与当前结果匹配的新鲜系统外证据；未验证面如实说明。
- **复杂度需要理由。** 新依赖、边界、配置、共享状态和生命周期必须由当前目标、消费者、运行边界或风险证明，不按固定阶梯机械选型。
- **机械化胜过提示。** 确定、重复、机器可裁决的工作用脚本、测试或 schema；Prompt 只保留模型需要理解的判断。

## 支持边界

- 宿主必须支持普通 sub-agent：能传入任务和上下文、并行运行独立工作并返回结果。
- 不提供无 sub-agent fallback，不使用 team mode，不规定子代理并发上限。
- 并行度由真实依赖和写所有权决定；平台配额由宿主管理。
- 外部副作用、破坏性操作、权限、数据和生产边界仍遵守明确授权。

## 知识库导航

| 主题 | 位置 | 说明 |
|---|---|---|
| 系统架构 | [docs/architecture.md](docs/architecture.md) | Skill 边界、独立性与知识子系统 |
| 开发指南 | [docs/development.md](docs/development.md) | 环境、文件命名与验证入口 |
| 工作方式 | [docs/workflow.md](docs/workflow.md) | 判断导向协作与反模式 |
| Harness 体系 | [docs/harness-engineering.md](docs/harness-engineering.md) | 环境、证据和知识设计 |
| Skill 设计 | [docs/skill-and-harness-design.md](docs/skill-and-harness-design.md) | 判断导向 Skill 的维护原则 |
| ADR | [docs/adr/](docs/adr/) | 历史架构决策；当前默认见 [ADR-0010](docs/adr/0010-judgment-oriented-skills.md) |
| 执行计划 | [docs/exec-plans/](docs/exec-plans/) | 仅在计划需要跨会话或供人审时使用 |

项目术语优先沿用 `CONTEXT.md`；与既有 ADR 冲突时显式指出，不静默覆盖。`CONTEXT.md` 或 ADR 缺失时根据当前证据继续，不为形式预建文件。

## Skill 速查

| Skill | 帮助模型判断什么 |
|---|---|
| `discuss` | 问题是否真正明确，哪些取舍需要决定 |
| `writing-plans` | 按用户规划需求锁定目标、必要依赖与验收，判断持久化方式 |
| `codebase-design` | 模块是否消除了复杂度，接口和 seam 是否有真实消费者 |
| `implement` | 如何利用 sub-agent 完成独立工作并处理集成 |
| `proof-oriented-development` | 实现中如何选择验收证据、控制风险或执行 TDD |
| `systematic-debugging` | 哪个解释最符合证据，根因与修复边界在哪里 |
| `code-review` | 哪些问题会妨碍改动安全、正确地交付 |
| `finish-development` | 当前工作是否足以完成，以及如何安全处置分支 |
| `dev-docs` | 哪些知识值得长期保存，如何准确表达 |
| `dev-docs-maintain` | 既有知识是否健康、新鲜并可验证 |
| `knowledge-navigation` | 如何结合项目观察、用户讨论和历史反馈建立或优化知识导航（手动调用） |
| `setup-power-agent` | 如何补齐最小 Agent 入口与明确知识缺口（手动调用） |
| `writing-skills` | Skill 是否真正教会了可迁移判断 |
| `harness-engineering-review` | 当前 Harness 哪些机制承重、哪些可以删除（手动调用） |

## Skill 独立性

普通 Skill 可以读取用户提供的计划、代码、证据或文档，也可以按需使用 sub-agent，但不得要求这些材料由某个具名 Skill 产生。完成自己的用户目标后即可停止，不输出只为下一 Skill 服务的固定 schema。

`setup-power-agent`、`dev-docs`、`dev-docs-maintain` 是唯一允许具名协作的子系统：初始化、语义写入、扫描和验证登记围绕同一个知识 Bundle，可以按实际缺口互相使用，但不形成每次必跑的固定链。

`knowledge-navigation` 独立负责导航体系的设计与演进：观察项目、开展启发式讨论、按历史与反馈选择并实现结构改进；它不扩大上述具名依赖例外。最小入口补缺口仍可使用 `setup-power-agent`，单篇知识写入或纯扫描仍按相应目标选择能力。

## 文档约定

`docs/` 中除 `index.md`、`log.md` 外的 Concept 使用带非空 `type` 的 YAML frontmatter。`scope`、`sources`、`status` 和验证策略只在有实际语义时声明；运行时验证状态由 `docs/.okf/verification.json` 维护。ADR 使用 `type: Decision`，过期决定通过新 ADR 和双向 `supersedes` / `superseded_by` 关系保留历史。

命名：

- Skill 主文件：`SKILL.md`
- ADR：`NNNN-slug.md`
- Spec：`YYYY-MM-DD-topic.md`
- 跨会话执行计划：`YYYY-MM-DD-title/`

## 开发与验证

- 修改 Skill 前先确认它填补的行为缺口；删除后默认模型仍会正确处理的文字。
- 不为统一外观强加章节、模板、状态枚举或报告格式。
- reference 只保存按需的专门知识或机器协议；确定性动作优先脚本化。
- 修改入口、链接、标题或脚本指针后，运行 `python3 scripts/check-skill-references.py`；支持传路径只检查受影响内容，协议边界见脚本 `--help`。
- description 只服务触发，尽可能短且保持可区分；110 token 是上限而非目标。修改后运行 `scripts/check-description-length.py` 和 `scripts/check-invocation-consistency.sh`。手动调用登记还须与 frontmatter 及 Codex `agents/openai.yaml` 的 `policy.allow_implicit_invocation: false` 一致。
- 重大架构、Skill 名称或长期知识变化同步更新现有文档和 ADR；普通局部实现不增加仪式文档。
- 没有运行与实际改动匹配的验证，不得声称完成。

## 上游追踪

| 项目 | 来源 |
|---|---|
| superpowers | github.com/obra/superpowers |
| Harness Engineering | openai.com/index/harness-engineering |
