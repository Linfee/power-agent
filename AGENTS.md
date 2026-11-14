# Power-Agent — Agent 指南

Power-Agent 以 Matt Pocock 的轻量工程能力为主干，融合 Power 的证明、因果诊断、工程判断、项目知识和授权内自动推进。现行决定统一见 [ADR-0014](docs/adr/0014-current-baseline.md)，不再串读旧 ADR 推导当前规则。

## 核心原则

- **目标先于流程。** 用户确认目标和必要取舍后，在已选执行路径内连续实现、验证、适用审查和修复，不等用户逐个启动自动能力；手动流程须由用户显式调用。进入 `grilling` 时保留原版的共同理解确认，确认前不实施。
- **小任务直接做。** 明确的现成 issue 可直接实现。spec、tickets 和地图只在依赖、恢复或协作需要时存在。
- **轻内核，真实证据。** 可自动验证的行为变更默认 Red/Green；已有失败可以复用，纯重构、UI、文档和机械变更选择匹配证据，不制造无意义的红灯。重构在 review 阶段进行。
- **复杂度需要理由。** 新依赖、公开接口、共享状态、配置和生命周期由当前消费者或真实运行边界证明，不按固定阶梯裁决。只有一个实现时先假设 seam 可能不存在；一个 adapter 是假设的 seam，两个 adapter 才说明变化真实存在；独立资源所有权、不变量或真实消费者边界仍可证明单实现 seam。
- **整包组合，单一判断来源。** 24 个 Skill 整包分发，14 个允许模型调用、10 个仅手动调用，见下表。工程内核、自动执行入口及其依赖保持可达；手动入口不作为自动依赖，也不以读取其正文绕过限制。可以具名组合自动能力，不预绑固定长链，不承诺单 Skill 独立安装。
- **状态与知识分开。** 执行状态只在选定 tracker；仓库保存仍成立的知识。交接和计划只引用状态源，不另记进度。
- **机械化胜过提示。** 确定、重复、机器可裁决的工作交给脚本、测试或 schema。
- **自治不扩张授权。** 讨论、建议、草稿不等于实施或发布；外部副作用、破坏性操作、秘密、权限和生产边界按具体已有授权处理。

## 支持边界

宿主须支持普通 sub-agent：任务与上下文传入、独立执行及结果收集。子代理使用新上下文；并行由真实依赖和写所有权决定，共享文件和状态有唯一协调者。不使用 team mode，不维护无 sub-agent fallback，不规定平台并发数字。

跨任务的最小完整改动默认规则见 [`minimal-complete-change.md`](skills/codebase-design/references/minimal-complete-change.md)，与 24 个 Skill 一起由插件或包提供；它不同于按任务调用的设计 Skill。[宿主兼容性](docs/agent-compatibility.md)说明六种宿主的安装方式、加载条件及证据边界。

## 知识库导航

|主题|位置|
|---|---|
|架构与能力边界|[docs/architecture.md](docs/architecture.md)|
|开发与验证入口|[docs/development.md](docs/development.md)|
|宿主安装与能力范围|[安装指南](docs/agent-compatibility.md)|
|自动推进与授权|[docs/workflow.md](docs/workflow.md)|
|环境与证据|[docs/harness-engineering.md](docs/harness-engineering.md)|
|Skill 维护|[docs/skill-and-harness-design.md](docs/skill-and-harness-design.md)|
|当前决定与理由|[ADR-0014](docs/adr/0014-current-baseline.md)|
|历史决定与融合来源|[ADR 导航](docs/adr/index.md)（归档正文已移除）|

项目术语优先沿用已有 CONTEXT 或 glossary；没有真实内容不预建文件。tracker 配置复用项目现有约定，缺省位置为 `docs/agents/issue-tracker.md`；只配置需要的后端，不同时维护本地和远程副本。

## Skill 速查

|Skill|帮助模型判断什么|
|---|---|
|`proof-oriented-development`|以 Red/Green 默认实现行为，并选择覆盖真实风险的证据|
|`code-review`|对照需求与工程质量，找出有证据的交付问题|
|`diagnosing-bugs`|用区分性证据定位根因，而非猜补丁|
|`codebase-design`|判断模块深度、资源责任与接口是否降低复杂度|
|`grilling`|按问题树逐轮追问，直到用户确认共同理解|
|`grill-with-docs`|手动调用；组合原版 grilling 与 domain-modeling|
|`domain-modeling`|复用术语真源，维护领域边界与值得记录的决定|
|`to-spec`|手动调用；将目标整理成可交付、可验收的 spec|
|`to-tickets`|手动调用；按垂直结果与真实依赖拆分可执行工作|
|`implement`|从明确任务或现成 issue 连续完成实现、验证、驱动 review–fix 循环和修复|
|`implement-spec`|从唯一 tracker 调度任务图、驱动切片审查并验收组合结果|
|`triage`|手动调用；识别请求的范围、重复、信息缺口与可执行性|
|`wayfinder`|手动调用；把复杂目标中的决定与可执行工作分开推进|
|`improve-codebase-architecture`|手动调用；从实际摩擦找到值得深化的模块边界|
|`research`|用匹配版本的一手来源解决技术未知|
|`prototype`|用可运行逻辑或真实画面回答设计问题|
|`pr`|根据真实 diff 与证据起草 PR，按明确授权发布|
|`wizard`|为确需人工输入或批准的配置生成安全脚本|
|`handoff`|手动调用；携带目标、证据与状态真源指针，不复制进度|
|`writing-for-agents`|编写能改变 Agent 判断、按需可达的指令与 Skill|
|`retro`|手动调用；从会话或项目材料改进环境，而非堆叠禁令|
|`dev-docs`|按项目协议写入、修订和核验稳定知识，不强制引入 Bundle|
|`knowledge-navigation`|手动调用；按真实任务建立或改善知识检索路径|
|`setup-power-agent`|手动调用；最小补齐 Agent 入口与选定的 tracker/领域指针|

## 知识协议

普通文档不强制成为 Knowledge Bundle。本仓库已使用 Bundle：`docs/` 中除 `index.md`、`log.md` 外的 Concept 有非空 `type`；ADR 为 `type: Decision`，被取代时保留历史和双向 `supersedes` / `superseded_by`。当前指南与归档分开，旧计划、评估和决定不作为活动状态或现行规范。`scope`、`sources`、验证策略按真实含义声明；验证以实际核验为准，不把未检查事实记成已验证。

命名沿用 `SKILL.md`、`NNNN-slug.md`、`YYYY-MM-DD-topic.md`；持久计划只在恢复或人审需要时使用。

## 开发与验证

修改 Skill 前说明实际行为缺口。迁入内容以固定 Matt 原文及 references 为底稿，保留方法、理由、反例、示例和模板，只在已确认融合差异处局部改写；轻量指按需加载、少重复与少人工接力，不以正文或 reference 更短为目标。默认行为的无效复述可以删除，但不能仅以“模型应该懂”为由把具体方法压成原则。工具入口相对安装位置解析，不能假定业务 cwd 含有 `skills/`。

- description 改动：`python3 scripts/check-description-length.py`。
- 调用方式、名称或目录改动：`bash scripts/check-invocation-consistency.sh`。
- 入口、链接、标题或脚本指针改动：`python3 scripts/check-skill-references.py`；可传受影响路径。
- 工具行为改动：运行直接覆盖该行为及风险边界的检查，详见开发指南。

重大分工和协议变化同步现行文档、分发与来源署名。结构通过不证明行为正确；完成声明只报告实际运行的验证和未覆盖面。
