---
type: Spec
status: accepted
---

# Matt 主干的 Power-Agent 融合设计

## 状态与适用范围

方向与实施已获用户确认；本文是 25 个目标 Skill 的融合契约。S05/S06 已按用户后续要求恢复 Matt 固定版本原文与调用元数据，不再使用初次融合的简化讨论行为。用户进一步要求按 Matt 原版的篇幅设计，迁入内容以原版方法和 references 的完整度为底稿，不再以缩短为目标。当前实现与验证按[迁移计划](../exec-plans/active/2026-11-11-matt-power-agent-fusion/plan.md)推进，完成证据以实际验收记录为准，不以设计描述代替运行结果。

目标不是并排安装两套规则，而是：**以 Matt 的轻量工程能力为主干，用 Power-Agent 的少量判断、证明和自动推进能力补足。** 不以旧 ADR 限制新设计；被改变的旧决定在实施切换时通过新 ADR 明确取代，不提前宣称已废止。

## 1. 已确认的产品决定

1. Matt 是默认来源，以固定原版正文及 references 为内容底稿，保留方法、理由、反例、示例和模板。Power-Agent 的内容只有在改变行动、判断、授权边界或验收时保留，并在确认的差异处局部融合，不拼接两份重复正文。
2. 用户确认目标和必要取舍后，Agent 在授权范围内连续完成实现、验证、适用审查与修复，不把每个 Skill 的结束变成人工启动下一步的关卡。进入 `grilling` 时保留原版用户共同理解确认，确认前不实施。
3. 保留 `proof-oriented-development`（下文简称 POD），吸收 Matt 的 TDD 知识，不再提供一份平行的 `tdd`。可自动化验证的行为变更默认 Red/Green/Refactor；UI、文档和机械变更采用匹配结果的证据。
4. 沿用 Matt 的主要分工与命名。`systematic-debugging` 改为 `diagnosing-bugs`；讨论、计划、收尾、Skill 写作和环境评估的旧入口分别融合，不留兼容别名。
5. 采用 tracker 中的 spec、tickets 和依赖关系。tracker 保存执行状态；仓库文档保存术语、决定和仍然成立的知识，不双写进度。
6. 小而明确的任务直接进入 POD。只有跨会话、任务依赖或并行协作需要时才展开 spec/tickets；已有 issue 可以直接实现，不必为了形式再建 ticket。
7. 保留知识写入、维护和导航能力；OKF 字段、账本、扫描器按真实消费者裁剪，不整体照搬，也不整体删掉。
8. 默认分发整套能力，允许具名 Skill 调用；`grill-with-docs` 按 Matt 原版手动调用，其余入口允许模型调用。不再承诺每个 Skill 单独安装也完整运行。宿主仍需支持普通 sub-agent，不引入 team mode、无 sub-agent fallback 或固定并发上限。
9. 审查保留“需求符合性”和“工程正确性与质量”两维。维度不等于固定两个 reviewer；独立性和投入由影响、复杂度及不确定性决定。
10. 诊断优先建立反馈，但没有可运行的红色命令不妨碍提出、检验假设。日志、trace、成功/失败差分可以提供区分性证据；读代码不能单独证明失败运行的根因。
11. 自动推进不扩大授权。commit、push、PR、合并、issue 修改、敏感配置和破坏性动作，均核对已有授权是否覆盖具体对象与操作；覆盖时不重复询问，未覆盖时只暂停相关动作。
12. 引入工程能力与必需的通用原语，不全盘引入 Matt 的生产力、个人、实验或废弃技能。

## 2. 来源与核对边界

本设计针对以下已观察的版本，不跟随上游浮动分支自动改变：

|标记|来源|核对基线|
|---|---|---|
|M|[mattpocock/skills](https://github.com/mattpocock/skills/tree/4ae2317ddb22b046e26455e4f9c9b3aaaf62212d)|`4ae2317ddb22b046e26455e4f9c9b3aaaf62212d`；只把 tracked 内容视为此次上游基线|
|P|本仓库 Power-Agent|`538bef929e23204acc73f0c739ad449f9002d3ba`；设计开始时工作树干净|

下文 `M engineering/<name>` 指 M 的 `skills/engineering/<name>/`，`M productivity/<name>` 指 `skills/productivity/<name>/`，`P <name>` 指 P 的 `skills/<name>/`。源文件均为对应目录的 `SKILL.md`，有专门来源时另列文件名。路径写成代码，避免未来删掉旧入口后把历史来源变成断链。

Matt 本地存在未跟踪扩展，例如 `writing-great-skills`、`resolving-merge-conflicts`、`skills-zh`、`docs-zh`、`skills/personal` 与部分 deprecated/in-progress 内容。它们**不属于上述上游基线，也不因本地可见就纳入迁移**。本文不把这些内容判断成上游缺陷。

## 3. 目标形态

### 3.1 25 个入口，按职责理解而非按顺序执行

|职责|目标 Skill|
|---|---|
|判断与工程内核|`grilling`、`domain-modeling`、`codebase-design`、`proof-oriented-development`、`code-review`、`diagnosing-bugs`|
|目标、任务与执行|`to-spec`、`to-tickets`、`implement`、`implement-spec`、`triage`、`wayfinder`|
|探索、评估与交付|`grill-with-docs`、`research`、`prototype`、`improve-codebase-architecture`、`pr`、`wizard`|
|协作与环境|`handoff`、`writing-for-agents`、`retro`、`setup-power-agent`|
|项目知识|`dev-docs`、`dev-docs-maintain`、`knowledge-navigation`|

这是能力分组，不是新增运行时层级，也不是必须依次通过的阶段。入口数从当前 14 个增至 25 个，**不意味着每个任务加载 25 份正文**。轻量化要看正常路径需要多少阅读、重复规则、人工接力与状态副本，不能只看文件数量；新增 description 的发现成本也必须在实际任务中检查。

### 3.2 默认自动推进

- **目标清楚、范围小**：POD 完成实现和对应证明；需要时调用设计、诊断、审查。无需先建 spec、ticket 或完成报告文件。
- **影响结果的取舍未定**：`grilling` 按 Matt 原版的问题树和 frontier 分轮访谈，事实由新上下文子代理查证；问题树收敛且用户确认共同理解后，才可继续已授权行动。需要边讨论边记录领域知识时，由用户选择 `grill-with-docs`。
- **目标已知但需持久协作**：`to-spec` 表达目标；`to-tickets` 仅在拆分有收益时建立可交付切片与依赖；`implement` 执行单个目标，`implement-spec` 协调整张任务图。
- **目标尚在探索**：`wayfinder` 维护低分辨率地图和当前待解问题，可调用研究、原型或讨论；信息足够后转入交付，不强制每个决定占一个会话。
- **完成**：交付当前请求需要的结果及证据。若发布已获授权，可继续 `pr` 等动作；否则说明完成的本地结果和未执行的发布动作，不把缺少发布授权误报成实现未完成。

没有固定的 `grilling → to-spec → to-tickets → implement → review → pr` 必跑链，也不要求用户记住这串命令。常见路由放在 description、README 与 setup 生成的项目指针中；不引入 `ask-matt` 或新的品牌路由 Skill。

### 3.3 具名调用与加载方式

除 `grill-with-docs` 按原版保留手动调用外，其余目标 Skill 允许模型根据任务调用。`grill-with-docs` 的 frontmatter 保留 `disable-model-invocation: true`，Codex metadata 保留 `policy.allow_implicit_invocation: false`。发现性、调用开关和副作用权限是三件事：能自动调用 `pr`，不代表可以自动发布。

共享工程判断只保留一个权威来源：POD 负责行为证明，`codebase-design` 负责模块与接口判断，`code-review` 负责审查判断，`domain-modeling` 负责术语和决定的语义。调用方给出触发条件和上下文，不复制整份规则。宿主无名为 Skill 的工具时，可以按安装后的可靠指针读取正文；这不是无 sub-agent fallback。

sub-agent 使用新的上下文，不把父会话全文当任务 brief。交付目标、范围、写所有权、必要事实和验收；需要保持原始讨论理由时给原始来源指针，不把无依据的摘要当事实。并行取决于真正独立的工作和写所有权，不规定固定 reviewer 数或设计候选数。

### 3.4 原版内容深度与删改判据

用户选择的是 Matt 的轻量组织与稳定方法，不是将原版改写为更短的原则摘要。22 个有 Matt 对应来源的入口以固定原版为底稿；S05/S06 已恢复原文，其余 20 个按当前融合差异适配。三个 Power 独有知识入口不以 Matt 篇幅为配额。

- **默认保留方法。** 原版的操作步骤、判断理由、反例、示例、模板及支持文件应有去处；不能仅以“现代模型默认会做”为由删掉，也不能把整段实操压成几个性质词。
- **只改明确差异。** 名称、调用方式、自动推进、POD、工程边界、tracker/知识协议和副作用授权按已确认决定局部改写；恢复内容不等于恢复所有旧政策。
- **reference 保持完整。** 专门分支可移入 reference，但保留实际操作粒度，并给出明确读取时机。移动不是删除的替代说法，也不要求每个任务加载全部材料。
- **不设等长指标。** 原版篇幅用于警惕信息损失，不要求相同行数、字数或字节。中文表述、消除重复和宿主中立改写可以改变长度；有用的 Power 增益也不因较长而删除。
- **覆盖可追踪。** 逐项核对源方法和示例在当前阅读路径的位置，删除或替换必须能对应当前目标的真实冲突；结构可达性、内容覆盖和实际模型行为分别记录，不互相冒充。


## 4. 状态、知识、证据与授权

### 4.1 spec、ticket 与 issue

- **Issue 是 tracker 的容器，spec 与 ticket 是承担的职责，不必是不同产品对象。** 一个 issue 已有清楚目标、验收与范围，直接 `implement`；只有需要拆分与调度时才创建子 ticket。
- spec 保存当前目标、约束、明确不做什么、验收及必要决定；不要求固定数量的 user stories 或长模板。
- ticket 是可独立验收的垂直交付单元，带 spec 来源、局部验收与真正的 blocker。机械迁移可以按实际依赖拆分，不为“垂直切片”拆出不可用中间态。
- tracker 的状态、认领和 blocker 是执行事实。会话待办、交接文件、工作目录里的下载副本只是当前运行视图，不成为第二套可独立更新的状态。
- 项目已配置 GitHub、GitLab 或本地 tracker 时沿用配置；不另起一套 `.scratch` 默认状态。远程创建、评论、标记、认领和关闭均属于需要任务授权覆盖的写操作。
- 并行调度只有在当前依赖和所有权允许时推进。远程 assignee 不被假定为原子锁；遇到竞争认领要重新核对，不新增分布式锁服务掩盖 tracker 限制。

### 4.2 交付证据

POD 持有“目标行为与证明匹配”的判断：自动化行为变更默认先观察相关红色，再实现、绿色、必要重构。现有失败已经覆盖缺陷时复用，不为演示 TDD 改坏正确代码；已有行为测试能覆盖的纯重构以保持绿色为约束。不能机械自动化的目标用真实 UI、文档结构/事实核对或合适的差分证明，不伪造红色阶段。

验证从消费者可观察行为进入；切入边界必须覆盖实际故障机制。测试中的调用次数、顺序、落库结果是否合理，取决于它们是否属于契约，不一概禁止。真实组件与替身按覆盖、稳定性、成本选择；不为测试强造公共接口，也不能 mock 掉待验证的协作。

证据必须对应当前结果和适用条件；仍适用的有效证据可以复用，变化影响其结论时补验。功能绿色不证明性能与 flaky 修复；同口径 workload、频率和运行条件按实际风险保留。结构检查不能证明 Skill 会正确行动。

### 4.3 审查与完成

审查的需求维度防止做错/漏做目标；工程维度检查正确性、安全、资源、兼容、验证和设计负担。小改动可由一个 reviewer 看两维，高影响或高不确定性改动用独立审查；明确要求多角度审查时才按该请求组织。审查范围包含相关 staged、unstaged、untracked 内容，不要求先 commit 才能审。

意见以触发条件、定位、影响和所需行为改变成立，不以原则名称、风格偏好或猜测成立。采纳反馈须核实；反馈要求的重写超出修复需要时不顺带扩张。修复增量仍需验证与复核，但不因一处局部修复重新运行整套无关审查。

`finish-development` 的完成证据、未提交改动保护、worktree 所有权与发布授权进入执行/PR 的动作边界，不再保留一个额外终点 Skill。授权检查集中在动作发生处，不复制成每个 Skill 都要用户重新确认的流程。

### 4.4 知识不承担任务状态

`domain-modeling` 负责术语与决定的语义判断；`dev-docs` 负责落到现有知识结构；`dev-docs-maintain` 负责结构、漂移与验证事实；`knowledge-navigation` 负责体系结构及反馈驱动的演进；`setup-power-agent` 负责首次接入和缺口指针。

这里的归属是知识与格式的单一权威，不要求每次写文档都再开一位 Agent 或完整运行一个 Skill。当前执行者已掌握适用规则时直接完成；只有实际缺少知识时按需读取，避免把职责分工重新变成人工/模型接力流程。

沿用已有 glossary/CONTEXT，不同时创建两套术语真源。没有既有约定时采用 Matt 的 `GLOSSARY.md`，多上下文确有需要才引入地图；已有 `CONTEXT.md` 根据内容而不是文件名迁移。ADR 只记录有未来消费者的理由和约束，不复制 Matt“必须同时难逆、反直觉、存在取舍”的三项硬门槛，也不让每次讨论生成 ADR。

研究结论、原型代码、会话 handoff 与任务轨迹不自动升级为长期事实。保留用于决定的来源和范围；持久知识需要核对当前适用性。旧执行计划和 ADR 保留历史，不在新默认中继续消费过时指令。

### 4.5 知识协议的保留与裁剪

本节把“按消费者判断”落实为具体方案，而不是把取舍全部留到实施时：

|对象|目标决定|消费者与理由|
|---|---|---|
|普通项目文档|继续服从项目现有协议；不因安装 Power-Agent 就要求整体转成 Bundle|单篇写作与导航不需要完整维护系统|
|采用 Power Bundle 的项目|保留 `docs/`、导航 index、Concept 的非空 `type`；未知类型/字段不因不在模板里而被删|扫描器和知识维护确实使用这些边界；不把可选字段升成门槛|
|根 index|普通 Markdown 有效；只有声明策略时才需要相应 YAML；声明了但损坏的 YAML 仍报错|完整 OKF 参考本来允许 plain index，当前扫描器却强制 frontmatter；修正这个不一致，不重写用户 index|
|完整 OKF reference|只保留 P dev-docs 下的一份，作为按需格式背景；实际工具子集由项目 profile 与 maintenance policy 明说|删掉第二份 443 行副本与只比较这两份的脚本；不把完整规范变成普通任务必读材料|
|来源追踪|新声明使用明确的 `sources`；保持扫描器现有路径形 `scope` 行为，概念 scope 不当文件来源|保持既有记录意义，不借融合偷偷修改 source fingerprint 的输入|
|freshness 策略与 ledger|可选启用；保留现有策略集合及 ledger schema `1.0`，不做用户数据迁移|已有扫描器是实际消费者，缺少专门测试不等于可无代价删除其公开字段；本轮不顺带删除 `generated` 或重设策略|
|验证状态|`scan` 只读、不要求创建 ledger；`record` 只在完成真实核验且需要登记时使用|没有账本表示未登记，不表示任务必然失败；创建账本不是每次写 docs 的步骤|
|账本安全|保留 canonical containment、symlink/别名拒绝、Bundle 单写者锁、原子替换、受控 evidence、完整性与损坏拒写|这些是当前工具与测试保护的数据/安全行为，不是流程负担|
|附加字段|`title`、`description`、`tags`、`timestamp`、`owners` 等按真实表达需要使用；不再推荐无消费者的字段填充|字段存在或更新时间不能证明语义已验证；`okf_version` 当前未被扫描器验证，不能拿它宣称兼容或验证通过|
|ADR|语义取舍由 domain-modeling 判断；采用 Bundle 时由 dev-docs 使用 profile 写入 `type: Decision`、historical 策略与有效生命周期关系|不能把 Matt 无 frontmatter 的裸模板直接写进采用 Bundle 的 `docs/`；非 Bundle 项目遵守自己的协议|

保留 `bundle_status.py` 和其 37 个现有测试所保护的真实行为，局部修正 plain-index 接受规则，不重写整个工具。调整受影响的契约测试；损坏 ledger 不覆盖、锁互斥、路径逃逸防护、证据不泄密、来源缺失不伪绿等保护不得因精简而丢失。未知字段、孤立旧记录和既有知识文件不自动清除。

setup 不再维护第二套 glossary/CONTEXT、ADR 格式：词汇格式归 domain-modeling，Bundle 元数据归 dev-docs，机械状态归 maintain。知识导航的四份 reference 均有独立消费场景，保留按需加载，不为缩文件数强行合并。

### 4.6 tracker 配置与可执行的最小协议

配置由 setup 按已有约定建立；无约定时使用 `docs/agents/issue-tracker.md`，按需附上 `triage-labels.md` 和 `domain.md`。若项目采用 Bundle，生成的这些文档也须有相应非空 `type`，不能原样复制无元数据的 seed。项目入口指向实际文件；`CLAUDE.md`/`GEMINI.md` 已是 AGENTS 指针时，不向指针文件另塞一份规则。

- **唯一后端**：GitHub、GitLab 或本地文件任选实际已配置的一种。优先使用支持的 native parent/blocking 关系；CLI 版本或 GitLab tier 不支持时，在同一 tracker 的固定正文位置记录关系。每条关系只有一个可更新真源，不同时维护“native 与正文各自都可改”的图。
- **能力与标签**：源模板列出的 `gh`/`glab` 命令不保证本机版本支持。使用前核对实际版本/帮助与官方契约。分诊类别、ready 状态、wayfinder 对象类型都映射项目现有角色；不无条件创建 Matt 五个标签后假设其余标签已经存在。缺少非必要 label 可按已配置的无标签表示推进，需要新增 label 的写动作另核对授权。
- **本地状态冲突**：不沿用把 `ready-for-agent`、`claimed`、`resolved` 混在同一个 `Status` 的协议。本地文件以 `Kind` 区分 spec/implementation/map/decision，`State` 表达 `open/active/done`，`Blocked by` 保存稳定 ID，`Owner` 关联当前协调者；仅外来请求按需另有 `Triage`。这是实际调度消费者需要的最小文件协议，不是全 Skill 的统一状态机。远程后端已有 native 状态时不再复制这些字段。
- **本地认领**：一个任务图由一个协调者写认领和完成状态，子代理只返回结果。多会话若无现成可靠的原子认领机制，就串行协调同一图；“写一个唯一标记再重读”不能证明互斥，不新增通用锁服务。
- **完成回写**：代码、证明和组合验收与该条目当前范围相符后，才更新获授权的状态。子项完成不自动关闭父 spec/map；存在未解目标、过时证据或别人的活跃所有权时不能冒领完成。

分诊中的历史拒绝理由属于可复用知识，不是第二份任务状态。先读取项目既有 SCOPE、ADR 与 tracker 决定；只有确有重复请求消费者时才按现有位置保存短理由，不默认新建一套 `.out-of-scope/` 知识库。

## 5. 逐 Skill 融合契约

本节的“删除”是已批准的实施范围：删除旧实现或不迁入来源资产。每个入口列出来源、值得保留的判断、融合方式、删除项与可观察验收。验收看实际任务与产物，不把正文是否出现某个词当行为证明。

### S01 `proof-oriented-development`

- **来源**：P POD 及 `references/testing-guide.md`、`testing-anti-patterns.md`；M engineering/tdd 及 `tests.md`、`mocking.md`。
- **保留判断**：目标行为先行；证明覆盖真实契约与故障机制；测试的独立期望；隔离不能替代真实协作；证据随变化补验；复杂度须有消费者或边界理由。
- **融合方式**：POD 保持身份，Matt 的行为测试、垂直反馈和 Red/Green 与 Power 的 Green 后重构合成一份 Red/Green/Refactor 知识。保留可执行反馈方法、横向切片的反例与理由，完整测试/替身知识及实例归可达 reference。执行 Skill 调用 POD，不再重复 TDD 规则。
- **删除项**：独立 `tdd`；P 的“仅用户明确要求才 strict TDD”默认；M 的逐 seam 人工确认、每轮恰好一个测试、把所有重构推迟到 review、对内部观测/替身的一刀切禁令；重复的测试知识副本。
- **验收方式**：完成一个新增行为和一个已有失败的修复，分别观察合理的 Red/Green/Refactor 与失败复用；实现与契约未变的重构不使行为测试失效。再做文档/UI任务，采用匹配证据而非制造红色测试；用户只授权本地修改时不 commit。

### S02 `code-review`

- **来源**：M engineering/code-review；P code-review 与三个 references；P implement 的 review package 工具提供可选输入。
- **保留判断**：需求与工程两维；需求和实际运行证据优先于实现自述；diff 范围内、项目可覆盖、只作启发而非硬违规的 Fowler smell 基线；安全、性能、生命周期、兼容与复杂度；影响和实现不确定性分开；不因只有一个实现就否定有效边界；反馈先核验后修。
- **融合方式**：以 Matt 的两维视角组织，Power 补足工程判断和脏工作树范围。人数由风险决定；审查者获得明确范围并独立判断。Review Assets 的敏感性、freshness、路径与 symlink 限制只在实际提供 manifest 时加载。
- **删除项**：无条件固定两位 reviewer、固定报告字数、只能看三点提交 diff、没有 spec 就强迫补 spec、为审查强迫先 commit；不把 diff 外的全仓 smell 当自动违规。重复 reviewer 准则保留单一权威，不删除原版已经限定范围与适用性的 smell 方法。
- **验收方式**：在同时存在 staged、unstaged 与新文件的变更中，识别一项需求遗漏和一项真实工程问题，不漏掉新文件，也不把被工具覆盖的风格问题当 blocker；一个合理的单实现生命周期边界不被误判为过度设计。小改动不强制双人，高风险改动有独立证据。

### S03 `diagnosing-bugs`

- **来源**：M engineering/diagnosing-bugs 与其 scripts 子目录的 `hitl-loop.template.sh`；P systematic-debugging 及反馈、因果、边界、防抖/等待、性能与 flaky references。
- **保留判断**：先使症状可观察；触发、第一处偏离、传播和用户症状相连；预测与探针区分主要解释；最小化服务信息价值；缓解和永久修复分开；原场景是验收锚点。
- **融合方式**：使用 Matt 的名称与实操反馈优先路线，Power 的证据资格控制根因声明。可运行命令、trace、差分和必要 HITL 均是观察边界；由信息价值选择探针，不固定假设或实验数量。修复交给 POD，诊断负责保留因果和原场景信息。
- **删除项**：旧名称与别名；“得到红色命令前不能提出假设”、穷尽最小化、固定假设数/复现频率门槛；`find-polluter.sh` 不迁入（实际线性、绑定 npm、吞掉失败）；等待示例中依赖不存在项目类型的独立 `.ts` 文件不迁入，保留条件等待知识。
- **验收方式**：一个只能取得脱敏 trace 的案例仍能推进并区分解释，证据不足时不声称根因；一个并发/污染案例使用保留机制的观察而非浅层单测；性能/flaky 结论使用同口径比较而非单次绿色。需要人工触发时仅等待真实缺口，不把整个调查停在命令格式上。

### S04 `codebase-design`

- **来源**：M engineering/codebase-design、`DEEPENING.md`、`DESIGN-IT-TWICE.md`；P codebase-design 与两个 references。
- **保留判断**：深模块、接口负担、locality、leverage；接口包括不变量、顺序、错误和资源责任；边界应隐藏真实复杂度；公开抽象由消费者/运行边界证明；候选比较要能改变决定。
- **融合方式**：Matt 提供简洁词汇和模块加深方法，Power 修正边界证据。依赖类型用于选择验证，不自动推出 ports/adapters。测试替身不是新增公开多态接口的独立充分理由。
- **删除项**：“两个 adapter 才是真 seam”的数量规则；远程依赖必建 port；固定 3+ 激进候选；合并模块后无差别删除仍保护公共行为的测试；以接口/实现行数比代替复杂度判断。
- **验收方式**：一个第三方 I/O 适配边界被保留，一个只为 mock 添加的公开 wrapper 被拒绝；单消费者但集中资源所有权的接口被正确保留。替代方案比较不改变消费者约束，不为凑数量提出不可行设计。

### S05 `grilling`

- **来源**：M productivity/grilling；恢复固定版本的 `SKILL.md` 与 `agents/openai.yaml` 原文，不继续融合 P discuss 的最少提问与自动结束规则。
- **保留判断**：以完整 design tree 表达决定依赖；每轮询问整个已就绪 frontier，编号并给推荐，“yes”接受推荐；新上下文子代理查事实，用户作决定；调查只阻塞其下游问题。
- **融合方式**：原样保留 Matt 的访谈目标、轮次、问题示例和完成条件。所有分支已访问、无静默假设后，仍须用户确认共同理解，确认前不行动。
- **删除项**：初次融合的“仅解决当前最少选择”、限定单一问题的补丁和确认前自动继续原任务；不恢复旧 `discuss` 入口或专用 server。
- **验收方式**：原文及调用元数据与固定 M 一致；实际访谈按前置条件分轮、每问给推荐，事实由工具调查，不提前问依赖答案的分支；用户确认共同理解前不实施。

### S06 `grill-with-docs`

- **来源**：M engineering/grill-with-docs；恢复固定版本的 `SKILL.md` 与 `agents/openai.yaml` 原文。
- **保留判断**：以薄组合入口同时消费 `grilling` 与 `domain-modeling`，在访谈中澄清并记录词汇与决定。
- **融合方式**：正文原样保留对两个 Skill 的具名调用；恢复 `disable-model-invocation: true` 与 `policy.allow_implicit_invocation: false`，由用户显式选择。领域语义和目标项目文档协议仍由现有被调用能力负责，不复制到包装入口。
- **删除项**：初次融合的自动调用、额外包装规则和自主转入实施的说明；不新增品牌 router 或旧入口别名。
- **验收方式**：原文与调用元数据和固定 M 一致，索引正确标记手动调用；显式使用后实际消费两个能力，在获授权位置保存已确认领域知识，而不实施业务代码。

### S07 `domain-modeling`

- **来源**：M engineering/domain-modeling、`GLOSSARY-FORMAT.md`、`ADR-FORMAT.md`；P setup 的领域/ADR 指南与 dev-docs 的语义边界。M 本地未跟踪的 `CONTEXT-FORMAT.md` 不纳入。
- **保留判断**：同一概念选择一致语言；同名跨上下文冲突显式处理；用真实场景和代码核对定义；词汇表写领域概念，不灌通用编程词汇。
- **融合方式**：Matt 的 glossary 是无既有约定时的轻默认；已有 CONTEXT 或领域文档优先复用。ADR 采用短理由，是否记录按未来消费者判断；需要修订历史决定时显式 supersession，由 dev-docs 落盘。
- **删除项**：按文件名机械转换全部 CONTEXT、glossary 与 CONTEXT 双写、每个词建独立文档、ADR 三条件必须全满足的硬门槛、强制长模板。
- **验收方式**：在已有 CONTEXT 的仓库消除一个真实概念歧义，不新建平行 glossary；在两个真实业务上下文中保留有意义的不同定义；一项可逆但重要的运维理由可被记录，不因可逆而丢失。

### S08 `to-spec`

- **来源**：M engineering/to-spec 及 spec 模板/参考；P writing-plans 的目标、范围、必要决定与证据要求。
- **保留判断**：复用已经确认的信息；把目标、非目标、必要约束与可观察验收说清；不给实现者留下关键产品/权限决定；允许实现细节自主选择。
- **融合方式**：spec 是 tracker 中可执行的目标说明。没有 tracker 写授权时先产出可审阅内容，不擅自发布；已有 issue 足够时直接使用，不补一份同义 spec。原型可以作为决定依据，但不能隐藏仍需验收的行为。
- **删除项**：固定 user story 数量与冗长章节、所有文件指针一律禁止、重访已确认需求、把生成 spec 等同发布许可；本地 exec-plan 与远端 spec 双主。
- **验收方式**：只根据已确认讨论生成可独立消费的目标；新会话能区分目标、验收与自由实现空间。只授权“整理方案”时无 tracker 写入；已有完整 issue 不产生重复对象。

### S09 `to-tickets`

- **来源**：M engineering/to-tickets 及 ticket 模板；P writing-plans 的依赖、独立验收与范围判断。
- **保留判断**：优先能交付的垂直切片；blocker 是真实依赖；任务可独立消费并保留父 spec 指针；集成不能留到“各自都绿”之后才发现缺失。
- **融合方式**：在一个 tracker 中保存验收、关系与进度。已获拆分/创建授权且决定已锁定时自动推进；只把改变范围或承诺的选择交给用户。票据数量由交付单元决定。
- **删除项**：每张票或每轮都必须重新批准、为小任务拆票、把研究问题误当实现 ticket、发布后继续维护可独立改状态的本地副本、无依据自动关闭父 issue。
- **验收方式**：把含两条独立实现支路和一个集成依赖的 spec 拆成可验收任务，真实关系写入选定 tracker；一个简单 issue 保持原对象直接执行；外部创建未授权时只交付草案，不创建真实票据。

### S10 `implement`

- **来源**：M engineering/implement；P implement、finish-development 的本地完成与授权判断；目标 POD、code-review。
- **保留判断**：接受任务、issue、spec 或 ticket；补齐不改变目标的实现细节；写所有权清楚；slice 完成与整体完成分开；复核脏工作树；未授权动作不外溢。
- **融合方式**：作为单个目标的自动执行入口：消化已有材料，按需调用 POD、诊断、设计和审查，修复本次问题，更新实际获授权的 tracker 状态。review-package/workspace 保留为需要可携带审查输入时的可选工具。
- **删除项**：执行者只照抄计划不得判断；任务已清楚仍强制建计划；无条件末尾 commit/全量测试/发布；固定等待人推进下一 Skill；把 Skill 安装目录误当目标仓库。
- **验收方式**：对一个现成 issue 完成本地实现、相关证明、适用审查和修复，不等待逐步指令、不额外建票；从另一个安装目录运行可选审查工具时仍指向正确目标仓库，空格路径有效，目标切换失败不回落旧目录。

### S11 `implement-spec`

- **来源**：M engineering/implement-spec；P implement 的 brief、写所有权、集成和证据复用。
- **保留判断**：按任务图的 ready frontier 调度；独立切片并行；相互冲突的写入串行或隔离；协调者承担集成与全目标验收；每个子任务用新上下文。
- **融合方式**：tracker 是任务图真源，协调者保留当前运行内的调度视图。Git worktree/分支只是获授权且适合当前仓库时的隔离手段；不能擅自 commit/merge 时使用不相交写所有权和串行集成，不假装完成了 Git 集成。共享契约先明确，语义冲突返回目标判断。
- **删除项**：无条件建 integration branch、每票 commit/merge、自动草稿 PR/ready/关闭、固定并发上限、任务局部成功等同 spec 完成、把探索摘要当已验证事实。
- **验收方式**：运行有并行支路和共享集成点的任务图，依赖未满足不调度，冲突不并写，最终检查组合行为而非只汇总子代理声明；在仅授权本地代码的场景没有分支、commit、merge 或远端副作用，仍能完成安全可达的实现。

### S12 `triage`

- **来源**：M engineering/triage 与 canonical labels、tracker 配置；P 的事实、授权与范围边界。
- **保留判断**：处理外来、尚未分诊的请求；核对项目范围、重复项、维护者决定与真正的信息缺口；已进入执行图的 ticket 不重复分诊。
- **融合方式**：分类/状态服从项目现有约定。先读再建议；只有授权覆盖相应 tracker 目标时才应用 labels、评论或关闭。AI 披露沿用项目政策，不通过伪装维护者发言取得权限。
- **删除项**：无条件把 Matt 项目的固定标签和状态施加到所有仓库、自动公开评论、把所有 issue 都视作缺少 spec、无差别重分诊 agent 自建票。
- **验收方式**：对范围外、重复、信息不足和已可执行请求给出有证据的不同处理；read-only 请求没有远端写入；已确认实施 ticket 不被误降级或重复建票。

### S13 `wayfinder`

- **来源**：M engineering/wayfinder 及地图/decision ticket 模板；P discuss、writing-plans 的不确定性与自动推进判断。
- **保留判断**：不确定目标先维护低分辨率地图；把“当前需要知道什么”与“如何实现”分开；研究可独立运行，偏好和产品取舍由人决定。
- **融合方式**：用 tracker 连接地图和当前决策。能从证据回答的决策由 Agent 研究并回写获授权的真源；需要人决定的才暂停相应分支。信息足够后进入 spec 或直接实现。
- **删除项**：一个决定固定占一个 session、AFK 研究必建分支并 push、Agent 代替 HITL 作产品决定、地图/decision ticket/实现 ticket 混用、未经授权认领或发布。
- **验收方式**：一个含技术未知与产品偏好的探索，技术支路自主取证，偏好支路真正等待用户；能继续的独立工作不停摆；不把未知直接转成伪确定实现任务，也不擅自 push 研究成果。

### S14 `improve-codebase-architecture`

- **来源**：M engineering/improve-codebase-architecture 与 `HTML-REPORT.md`；P codebase-design 的边界、删除测试与实际负担判断。
- **保留判断**：从实际修改摩擦和调用关系寻找高杠杆改进；既有设计也是候选；能具体解释删除什么复杂度、调用者承担什么，不凭“更优雅”立项。
- **融合方式**：作为代码库级的发现/取舍入口，具体接口知识调用 codebase-design。可用图说明前后变化；明确是“找机会”还是“实施已授权改进”，不自动把建议变成重构。
- **删除项**：所有报告必须生成 HTML、依赖在线 CDN 才可读、固定术语替换一切正常表达、固定候选数、用抽象数量或热度单独证明价值；未授权实施。
- **验收方式**：对一个真实痛点给出可定位的复杂度来源、保留约束和较简单方案；证据不足的热点不被硬改。只要求建议时交付建议，不改代码；必要图形在断网时仍可理解。

### S15 `research`

- **来源**：M engineering/research；P 的证据资格、来源与持久知识边界。
- **保留判断**：优先官方文档、源码、规范和第一方 API；主张可追到拥有该事实的来源；委派采用新上下文，结论与未确认项分开。
- **融合方式**：可独立委派阅读，结果按实际消费者保存在已有位置或直接交付；确需长期保存时由 dev-docs 处理语义和适用范围。并行只在有独立工作可继续时使用，不为一个简短事实查询强开后台。
- **删除项**：任何研究都必须 sub-agent、必须入库、研究自动等于当前系统事实、未经授权的分支/push/PR；二手摘要替代可得的一手来源。
- **验收方式**：对一个版本相关 API 问题给出与该版本匹配的一手依据和可复查结论，冲突来源明确；一次性答案不制造无人消费的笔记，不发布私人研究材料。

### S16 `prototype`

- **来源**：M engineering/prototype、`LOGIC.md`、`UI.md`；P discuss 的按问题选择视觉辅助与临时产物安全。
- **保留判断**：原型回答具体不确定性；状态机/逻辑与 UI 方案分开验证；清楚标记可丢弃、可运行、可观察，不把演示当生产实现。
- **融合方式**：吸收视觉讨论能力，复用宿主已有展示/反馈方式；确需本地服务才启动受控临时服务。决定依赖原型代码时保留准确版本和指针，是否用 Git 由授权和实际保存需要决定。
- **删除项**：默认 throwaway branch、无条件 push/PR、旧 discuss 的专用 frame/event 协议与五个配套 server/helper 文件、为原型套生产工程结构、原型绿色冒充生产验收。
- **验收方式**：分别用一个逻辑原型和一个 UI 对比解决明确问题；观察实际状态/画面，能说清证据只支持哪项决定；无额外 Git 动作，临时服务停止，需保留的依据没有随清理丢失。

### S17 `pr`

- **来源**：M engineering/pr；P finish-development、implement 和 code-review 的证据、工作树与动作授权判断。
- **保留判断**：Summary、实际 Evidence、Merge Danger 帮助评审；视觉/运行证据真实且最小充分；风险说明覆盖影响面与恢复，不以“测试通过”掩盖未验证条件。
- **融合方式**：处理已获授权的 PR 准备/创建/更新与完成信息；正文可先本地草拟。重新核对目标远端、分支、包含的改动与敏感材料；发布授权不推导为 merge/删分支授权。
- **删除项**：没有视觉影响仍硬附图、固定长模板、默认 push/开 PR/合并、因用户说“完成”就清理不明 worktree；重新跑仍适用的无关全套检查。
- **验收方式**：用已有真实验证生成与实际 diff 相符的正文，明确未验证项；只要求草稿时无远端写入；明确授权创建特定 PR 时完成该动作但不自动合并，也不带入无关改动或敏感信息。

### S18 `wizard`

- **来源**：M engineering/wizard 及 `template.sh`；P 的凭证、不可逆动作与人工缺口判断。
- **保留判断**：只把确需人操作的缺口变成简短引导；Agent 能做且已获授权的步骤自行完成；敏感输入不回显、不进日志；脚本执行状态可核对。
- **融合方式**：沿用可选生成式引导脚本，界面/命令须来自当前官方资料或实际表面；每个有副作用的阶段对应现有授权，不因用户允许运行 wizard 就默认接受条款或发放权限。
- **删除项**：把可自动操作的全部工作推给人、猜测第三方界面、无需求地固化进度目录、自动写真实 .env/上传 secret、一次确认覆盖不明外部动作。
- **验收方式**：一条含普通本地步骤、秘密输入和权限授予的流程，自动完成可达本地工作，秘密不出现在输出，权限步骤在准确目标处等待批准；脚本通过语法/适用静态检查，并在沙盒演练非敏感分支，不声称这证明真实服务授权成功。

### S19 `handoff`

- **来源**：M productivity/handoff；P writing-plans/implement 的恢复所需事实与证据判断。
- **保留判断**：可移植交接保留目标、已锁定决定及理由、真实进度来源、当前产物、授权、未解问题和下一可执行动作；摘要不是原始证据。
- **融合方式**：用于真正跨会话/人/仓库/宿主的携带；指向 tracker 和准确来源，不另造进度账本。需要完整讨论理由时保留原始材料指针，不固定 session 长度或 token 门槛。
- **删除项**：每阶段必写 handoff、未经核对的“已完成”、把一份交接文件永久当执行状态、引入 ask-matt 的固定 phase-boundary 决策树。
- **验收方式**：让新上下文只消费交接和所指来源，能继续正确任务并知道不能执行哪些发布动作；tracker 更新后不会因旧 handoff 回退真实状态；不把临时假设升级成决定。

### S20 `writing-for-agents`

- **来源**：M productivity/writing-for-agents 与 `SKILL-MECHANICS.md`；P writing-skills 与 `references/criteria.md`。
- **保留判断**：指针的触发和读取时机；渐进披露；上下文与认知负担；目标/完成条件可检查；删除不改变行动的文字；确定工作机械化；行为比较不能用复述规则代替。
- **融合方式**：通用写作与 Skill 分支共用入口。Skill 分支写清行为缺口、真实依赖、发现性和按需 reference；支持具名调用，不再为独立安装复制整份知识。批评默认行为时用当前模型/宿主上的证据，不写未经验证的心理学结论。
- **删除项**：`writing-skills` 旧入口；可预测固定过程优先于结果的默认、独立安装硬保证、重复机械格式说明、对特定 leading word 的未经验证因果承诺、每次文字修订必跑评测平台。
- **验收方式**：改写一份有实际行为缺口的 Skill，保留有用方法、示例、安全和完成边界，合适场景能发现并实际消费 reference；一个自然请求可正确路由，不靠显式点名答案。不要求产物更短；结构校验、内容覆盖与行为观察分开报告。

### S21 `retro`

- **来源**：M engineering/retro；P harness-engineering-review；目标 writing-for-agents 和知识维护能力。
- **保留判断**：从实际摩擦改进环境；机械错误优先交给检查；导航、工具、反馈循环与没有消费者的机制可审；发现必须有可观察依据。
- **融合方式**：保留两条入口意图：复盘一次运行，或主动审视当前项目 Harness。没有会话日志也可基于指定环境审视；需要改规则时调用 writing-for-agents，需要改知识结构时调用知识能力。
- **删除项**：`harness-engineering-review` 旧入口及 metadata；固定评分/维度/长报告、必须有 session log 才能评估环境、每个失误都追加 prompt 禁令、复盘默认附带未授权实施。
- **验收方式**：一个重复机械错误被建议放入可运行检查而非加口号；对没有会话日志但有明确环境材料的请求仍能给证据化判断；只要评估时不修改配置。

### S22 `dev-docs`

- **来源**：P dev-docs 与 `project-docs-profile.md`、OKF 规范中确有消费者的部分；与目标 domain-modeling 协作。
- **保留判断**：事实/假设/决定/任务状态分开；文档有目标读者和使用时机；来源支持当前结论；新文档不能覆盖旧有效决定；写入沿用现有结构。
- **融合方式**：作为语义写入能力，不强制每次实现落 docs。普通文档可直接写；已采用 Bundle 的项目继续使用其最小结构和维护能力。术语/ADR 的判断交给 domain-modeling，避免两份策略。
- **删除项**：没有消费者的字段和强制模板、把写入时间当验证通过、把研究/执行进度自动收入长期知识、为单篇文档先建完整 Bundle。
- **验收方式**：更新一条因代码改变而过期的知识，正确区分当前事实与历史理由，保留必要来源；纯文本指南不凭空生成验证账本；语义未核实的内容不标 fresh。

### S23 `dev-docs-maintain`

- **来源**：P dev-docs-maintain、`bundle_status.py` 与 `test_bundle_status.py`、维护/CLI references。
- **保留判断**：结构可机械判定，语义验证要真实证据；漂移、不新鲜、未知和有效验证分开；读取/写入账本受路径、scope、来源及时间约束；修复不能伪造验证。
- **融合方式**：维护已有知识体系，可按实际请求做结构扫描、语义核验或缺口修复，不要求三者每次全跑。Bundle 工具仅服务采用该协议的项目，未采用者沿用其原有检查。
- **删除项**：所有 docs 都必须启用 OKF、无人消费的每次全扫/报告、mtime 或代码 diff 自动推出语义 fresh、双份 OKF 规范；不删除仍承载有效验证事实的账本。
- **验收方式**：分别处理坏链接/非法结构、代码事实漂移、缺少验证和真实新验证四种情况；旧或 scope 不匹配的证据不能刷新状态；没有维护授权时不修改账本，真实数据不会被静默清空。

### S24 `knowledge-navigation`

- **来源**：P knowledge-navigation 与四个 references；M 的轻量指针和 glossary 思路作为表达方式，而非第二套导航系统。
- **保留判断**：入口根据真实任务与使用者组织；观察项目、讨论关键歧义、结合获授权的历史/反馈；检索线索不是事实；设计改进需要在真实路径验证。
- **融合方式**：保留独立的导航设计与演进能力；可以调用已具名能力完成讨论、语义写入或机械验证。与 setup 的区别是“重新设计导航”，与 maintain 的区别是“重选结构和信息路径”。
- **删除项**：因为旧独立性 ADR 而复制其他 Skill 规则、为统一目录外观迁移所有知识、自动扫描私人历史、创建无当前读者的地图与入口。
- **验收方式**：根据一个真实检索失败改进入口，让新上下文通过实际导航找到正确知识；不读取未指定历史，不把过时讨论覆盖当前事实；简单坏链接留给维护，不升级为体系改造。

### S25 `setup-power-agent`

- **来源**：P setup-power-agent 及模板；M engineering/setup-matt-pocock-skills 的 tracker、协作与项目知识指针。
- **保留判断**：只补影响当前 Agent 工作的缺口；先识别宿主、现有说明、验证命令和 tracker；配置与事实由项目证据决定；不预建完整知识树。
- **融合方式**：统一品牌入口，生成简短、可消费的项目规则与目标 Skill 指针；tracker 配置只声明实际后端、状态/关系和操作约定。按需调用 domain-modeling/dev-docs/maintain，不再拥有第二份词汇、ADR 和验证政策。
- **删除项**：`setup-matt-pocock-skills` 品牌入口、ask-matt 指针、固定 Matt 标签/人名/安装目录、全套生产力技能要求、无需求的知识模板填充、自动修改远端 labels/权限。
- **验收方式**：在已有项目和最小新项目分别初始化，前者不覆盖现有规则，后者只产生可用最小入口；另一个安装路径下所有指针仍可解析；tracker 写入和敏感配置在实际授权边界停下，不以初始化授权推断生产授权。

## 6. 不迁入与旧入口退出

### 6.1 Power-Agent 当前 14 个入口的去向

|当前入口|目标去向|切换处理|
|---|---|---|
|`proof-oriented-development`|S01|保留名称，升级行为默认及测试知识|
|`code-review`|S02|保留名称，按两维重组并保留工程判断|
|`systematic-debugging`|S03 `diagnosing-bugs`|迁移全部调用者后删除旧目录，不设别名|
|`codebase-design`|S04|保留名称，以 Matt 主干融合 Power 边界判断|
|`discuss`|S05/S06，视觉能力进入 S16|删除旧入口与专用 server 资产|
|`writing-plans`|S08/S09/S13；跨会话携带进入 S19|删除旧入口，不另留本地执行状态系统|
|`implement`|S10/S11|保留单目标入口，增加整图协调入口|
|`finish-development`|S10/S11 的完成判断、S17 的发布动作|删除独立终点；保护未提交改动和授权语义不删除|
|`writing-skills`|S20 的 Skill 分支|删除旧入口并迁移校验脚本的旧名称提示|
|`harness-engineering-review`|S21 的环境评估分支|删除旧入口及 manual-only metadata|
|`dev-docs`|S22|保留能力，裁剪无消费者的强制协议|
|`dev-docs-maintain`|S23|保留能力，Bundle 自动化按协议适用|
|`knowledge-navigation`|S24|保留入口，允许具名协作，边界不扩为默认每次运行|
|`setup-power-agent`|S25|保留名称，吸收 Matt setup|

### 6.2 Matt promoted 工程 20 个入口的去向

|M engineering 入口|处理|
|---|---|
|`ask-matt`|不引入；路由知识重写到 description/README/setup，不保留 phase-boundary 固定树|
|`grill-with-docs`|S06|
|`triage`|S12|
|`improve-codebase-architecture`|S14|
|`setup-matt-pocock-skills`|S25，品牌和项目特定设置改写|
|`to-spec`|S08|
|`to-tickets`|S09|
|`implement`|S10|
|`implement-spec`|S11|
|`wayfinder`|S13|
|`retro`|S21|
|`prototype`|S16|
|`diagnosing-bugs`|S03|
|`research`|S15|
|`tdd`|S01，不并行分发 tdd|
|`domain-modeling`|S07|
|`codebase-design`|S04|
|`code-review`|S02|
|`pr`|S17|
|`wizard`|S18|

### 6.3 Matt productivity 7 个入口的去向

|入口|处理|
|---|---|
|`grilling`|引入为 S05，工程链必需原语|
|`handoff`|引入为 S19，真正需要携带上下文时使用|
|`writing-for-agents`|引入为 S20，替代旧 writing-skills 并服务 retro/setup|
|`grill-me`|不引入，薄人工包装与直接 grilling 重复|
|`teach`|不引入，不是本次工程自动化的必要依赖|
|`to-questionnaire`|不引入为独立 Skill；仅在宿主已有结构化提问能力时使用该能力|
|`wait-what`|不引入，不是本次工程链必要依赖|

misc、in-progress、deprecated、personal 以及本地未跟踪扩展都不在默认融合范围。以后引入须有新的用户目标或消费者，不借本轮顺带扩张。

## 7. 交付与切换约束

1. 本文是目标设计；当前 AGENTS、README、架构文档和 accepted ADR 在实施切换前仍描述旧版本。实施时一次完成现行契约更新，不能让两套相反指令同时作为默认。
2. 新入口及其正文、references、脚本、metadata、目录指针、校验规则与文档必须共同切换。保留历史中的旧名称不等于保留运行时 alias。
3. 已安装副本或 symlink 不在本轮或默认仓库编辑权限内；本地卸载旧名字/更新用户目录须有相应范围授权，不覆盖用户自建同名 Skill。
4. 单 Skill 独立安装不再是质量承诺。整包安装必须包含可达依赖，安装目录与业务仓库分别解析；不能把 `./skills/...` 假定为业务仓库文件。
5. 结构、脚本真实行为与 Agent 行为分别验收。改文案、链接通过或模型会复述目标，都不能单独宣布融合完成。
6. 迁移通过后，正常小任务不需要人逐 Skill 接力；大任务能从同一个 tracker 恢复并完成集成；授权边界、根因证据和完成证据不能因自动化而减弱。

## 8. 支撑资产的明确去向

### 8.1 Power 现有支撑资产

以下来源路径均相对 `skills/`；14 份主文件的去向见 §6.1。本表覆盖其余 42 个 tracked 文件。这里描述未来文件操作，不改变本轮“不修改 Skill”的边界。

|当前资产|目标处置与消费路径|
|---|---|
|`proof-oriented-development/references/testing-guide.md`|保留路径，合并 M tests/mocking 的有效知识，改为默认 Red/Green/Refactor，仍按测试边界问题加载|
|`proof-oriented-development/references/testing-anti-patterns.md`|保留路径，去掉旧 opt-in-only 默认与重复规则，保留伪证据/耦合/期望值判断|
|`code-review/references/code-reviewer.md`|保留路径，收缩为独立审查 brief 与可选 Review Assets 协议；工程准则不再另复制一套|
|`code-review/references/risk-classification.md`|保留，只有选择审查投入时加载，不按文件名/标签自动定级|
|`code-review/references/response-examples.md`|保留有区分价值的反馈案例，按需加载，不作为强制回复模板|
|`codebase-design/references/dependency-boundaries.md`|保留路径，融合 M DEEPENING 的分类，删除 adapter 数量与强制 ports 的判断|
|`codebase-design/references/design-it-twice.md`|保留路径，融合 M 的比较角度，不保留固定 3+ 候选和固定并发|
|`systematic-debugging/references/building-feedback-loops.md`|迁到 diagnosing-bugs 同名 reference，作为反馈构造的唯一详细来源|
|`systematic-debugging/references/root-cause-tracing.md`|迁到 diagnosing-bugs 同名 reference，保留因果资格与原场景锚点|
|`systematic-debugging/references/defense-in-depth.md`|迁到 diagnosing-bugs 同名 reference，只在缓解/防护所有权问题时加载|
|`systematic-debugging/references/performance-and-flakiness.md`|迁到 diagnosing-bugs 同名 reference，保留同口径性能/频率判断|
|`systematic-debugging/references/condition-based-waiting.md`|迁到 diagnosing-bugs 同名 reference，保留等待真实条件、超时/取消及实际结果断言|
|`systematic-debugging/references/condition-based-waiting-example.ts`|不迁入；依赖特定项目类型的可改写示例不作为通用可运行资产，所需知识留在 Markdown|
|`systematic-debugging/references/find-polluter.sh`|不迁入；不把绑定 npm、吞失败的线性循环包装为通用二分工具|
|`implement/scripts/review-package`|保留可选 CLI，继续覆盖完整目标工作树；不默认生成无人消费的 package|
|`implement/scripts/review-workspace`|保留 review-package 的私有输出/所有权安全依赖|
|`implement/scripts/test-review-package.sh`|保留实际 CLI/路径/工作树安全回归；若正文示例改变，不重钉无关文本，继续证明正确目标与拒绝危险输出|
|`discuss/references/visual-companion.md`|使用条件与有效视觉反馈判断进入 prototype；专用会话/事件/样式协议删除|
|`discuss/scripts/server.cjs`|删除，不再作为默认配套服务|
|`discuss/scripts/start-server.sh`|删除，原型按实际宿主/项目选择展示方式|
|`discuss/scripts/stop-server.sh`|随专用服务删除；临时服务仍按实际创建者负责停止|
|`discuss/scripts/frame-template.html`|删除，不保留固定讨论 UI 框架|
|`discuss/scripts/helper.js`|删除，不保留专用浏览器 event 协议|
|`writing-skills/references/criteria.md`|迁到 writing-for-agents 的 `references/criteria.md`，改掉单 Skill 独立安装前提，保留真实行为对照判据|
|`harness-engineering-review/agents/openai.yaml`|随退役入口删除；该文件只有禁用自动调用 policy，无须复制到 retro|
|`setup-power-agent/agents/openai.yaml`|删除只承载 `allow_implicit_invocation: false` 的旧 policy 文件，使保留入口可自动调用|
|`setup-power-agent/references/domain-docs.md`|保留为短路由与缺口判断，格式归属转给 domain-modeling/dev-docs，不复制模板|
|`setup-power-agent/references/adr-format.md`|去重后删除；决策价值进入 domain-modeling，Bundle 元数据进入 dev-docs profile|
|`setup-power-agent/references/context-template.md`|删除；唯一词汇模板在 domain-modeling，既有用户 CONTEXT 不动|
|`setup-power-agent/references/context-map-template.md`|删除；唯一多上下文词汇规则在 domain-modeling，已有地图不动|
|`knowledge-navigation/agents/openai.yaml`|删除只承载禁用自动调用的旧 policy 文件；触发边界由目标 description 保持狭窄|
|`knowledge-navigation/references/design-principles.md`|保留，导航成本/权威/维护判断有独立消费者|
|`knowledge-navigation/references/discovery-and-dialogue.md`|保留，初始化观察/讨论按需消费，不复制完整 grilling|
|`knowledge-navigation/references/history-and-feedback.md`|保留，历史覆盖/偏好/因果证据与私人历史边界|
|`knowledge-navigation/references/validation.md`|保留，结构、走查、隔离消费和对照结论分开|
|`dev-docs/references/project-docs-profile.md`|保留并收缩为项目选用的 Bundle 子集、语义颗粒度及 ADR 写入；机器状态规则指向维护 policy，不再规定 exec-plan 回写链|
|`dev-docs/references/okf-v0.1.md`|保留为唯一完整按需参考，不再为独立安装复制|
|`dev-docs-maintain/references/maintenance-policy.md`|保留为扫描器/ledger 语义的唯一详细说明，明确 opt-in 与 plain-index，不扩大字段门槛|
|`dev-docs-maintain/references/cli-operations.md`|保留，使用真实 CLI 和拒绝条件；从实际安装目录定位脚本|
|`dev-docs-maintain/references/okf-v0.1.md`|删除重复副本，消费者改指向 dev-docs 的唯一版本|
|`dev-docs-maintain/scripts/bundle_status.py`|保留，局部修正 plain-index；不顺带改 ledger schema、策略集合或数据含义|
|`dev-docs-maintain/scripts/test_bundle_status.py`|保留实际 37 项测试保护，更新 plain-index 契约并补其有效/非法 YAML 边界；数据安全用例保留|

### 8.2 Matt 支撑内容

|来源|目标处置|
|---|---|
|engineering/tdd 的 `tests.md`、`mocking.md`|完整融合进 POD 的既有测试 references，保留行为/内部形状对照、替身边界、独立期望和接口实例，不另复制第三套 TDD 文档|
|engineering/codebase-design 的 `DEEPENING.md`、`DESIGN-IT-TWICE.md`|融合进 codebase-design 既有两个 reference；采用 §S04 修正后的判断|
|engineering/domain-modeling 的 `GLOSSARY-FORMAT.md`|迁入 `domain-modeling/references/glossary-format.md`；包含单/多上下文规则，读取既有 CONTEXT|
|engineering/domain-modeling 的 `ADR-FORMAT.md`|迁入 `domain-modeling/references/adr-format.md`，保留理由、内容模板与具体示例；Bundle 格式调用 dev-docs，不保留相反的 status 模板或机械三条件门槛|
|productivity/writing-for-agents 的 `SKILL-MECHANICS.md`|迁入其 references，改为整包/具名调用政策；保留发现性与调用方式的必要区分，不引入 router|
|`engineering/diagnosing-bugs/scripts/hitl-loop.template.sh`|作为需要人工触发反馈时的可选模板迁入；不设为诊断入口前提，核对输入/输出、秘密、超时与临时运行处置|
|engineering/prototype 的 `UI.md`、`LOGIC.md`|完整迁入 prototype references，保留 URL 稳定变体切换/键盘焦点/生产门禁、可移植模型、真实状态、自由探索及逐步走查；去掉固定 variant 数、强制分支/commit 与特定框架假设|
|engineering/improve-codebase-architecture 的 `HTML-REPORT.md`|迁为可选图示参考，保留候选展示、图示选择和比较方法及实例，不保留必须 HTML/CDN/固定措辞的输出协议|
|engineering/pr 的 `CREDITS.md` 与 frontmatter credits|保留，不能因精简丢失 HumanLayer/show-me 来源；Matt 原始 pr 是正文能力，目标的授权发布编排来自 Power 收尾能力|
|engineering/wizard 的 `template.sh`|迁到目标 `wizard/scripts/template.sh`，更新消费者指针；保持可选、沙盒可验与秘密不回显，生成不等于获准执行|
|engineering/triage 的 `AGENT-BRIEF.md`|迁为按需 brief reference，保留方法、模板及 bug/功能/PR 示例；不与 spec/ticket 另写相反要求，不以短为目标|
|engineering/triage 的 `OUT-OF-SCOPE.md`|迁为按需历史拒绝理由模式；复用已有知识位置，不默认创建第二知识库或记录普通已实现请求|
|engineering/setup-matt-pocock-skills 的 `issue-tracker-github.md`、`issue-tracker-gitlab.md`、`issue-tracker-local.md`|迁为 setup 的三种可选 seed；只生成项目实际选用的一种，按 §4.6 修正命令、权限、关系与本地状态|
|engineering/setup-matt-pocock-skills 的 `triage-labels.md`、`domain.md`|迁为按需 seed；配置真实角色/词汇位置，适配 Bundle metadata，避免品牌和固定标签泄漏|
|to-spec、to-tickets、wayfinder 正文中的内联模板|随对应主文件完整适配，不伪造独立源文件；保留目标、验收、范围、依赖、决定及示例，删除固定长度/数量和人工关卡的硬要求而非模板内容|
|选定 M Skill 的 `agents/openai.yaml`|保留有用的界面信息并改成目标名称；除 S05/S06 原文恢复外，按 §3.3 的整包调用政策适配，不照搬所有源 Skill 的调用方式|

### 8.3 仓库维护与分发资产

- 保留 description、invocation、reference 校验器及其有实际契约的回归；改掉旧 Skill 名称提示。校验器只负责确定性约束，不替模型做所有工程判断。
- 删除仓库 scripts 目录的 `check-shared-references.sh` 及当前消费者，因为它唯一比较的 OKF 副本将删除；这不是“删除所有引用校验”。
- 保持 flat 整包分发，同步现有三个 plugin manifest 与 Gemini 的真实能力说明。既有 marketplace 命令缺少 catalog 的问题在实施时补齐，不以文件存在推断宿主安装成功。
- 迁入时补实际 MIT notices，保留 Matt、superpowers、HumanLayer/show-me 的相应归属；文章与著作引用不冒充软件许可。原创权属不从作者字段猜测；发布材料由维护者核准。
- 旧 active exec-plan 若包含已失效的当前指令，只在真实状态核对后标明被新 tracker/本次决定取代，并保留历史；不全仓替换历史中的 Skill 名称，也不为满足历史链接重新创建旧入口。
