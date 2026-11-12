---
type: Architecture
scope:
  - architecture
---

# 系统架构

Power-Agent 是以 Matt 轻量工程能力为主干的整包 Skill。目标、真实证据和授权决定行动；已选执行路径内的自动能力不要求用户逐站启动，也不绑成长流水线。当前决定见 [ADR-0014](adr/0014-current-baseline.md)；此前融合设计保存在[历史归档](archive/2026-11-11-matt-power-agent-fusion.md)，不是当前规范。

## 能力边界

|范围|入口|承重判断|
|---|---|---|
|工程内核|`proof-oriented-development`、`code-review`、`diagnosing-bugs`、`codebase-design`|Red/Green、需求与工程双维审查、因果证据、模块深度与真实责任|
|目标与知识对齐|`grilling`、`grill-with-docs`、`domain-modeling`|问题树逐轮追问、确认共同理解、复用术语真源、记录值得保留的决定|
|任务与调度|`to-spec`、`to-tickets`、`implement`、`implement-spec`、`triage`、`wayfinder`|小任务直接做；必要时创建可验收结果和真实依赖，由单一协调者推进|
|探索与交付|`improve-codebase-architecture`、`research`、`prototype`、`pr`、`wizard`|从证据回答未知、实际运行或展示、草稿与发布分开、必要人工批准|
|协作与环境|`handoff`、`writing-for-agents`、`retro`|携带权威指针、按需可达指令、改进环境而非堆禁令|
|项目知识|`dev-docs`、`knowledge-navigation`、`setup-power-agent`|按既有协议写入与核验知识、真实检索路径、最小初始化|

这六行是能力地图，不是执行层级。完整入口见 [README](../README.md#skills)。

## 整包组合

24 个目录平铺在 `skills/`，其中 15 个允许模型调用；9 个仅手动调用：`grill-with-docs`、`to-spec`、`to-tickets`、`wayfinder`、`triage`、`improve-codebase-architecture`、`retro`、`handoff`、`knowledge-navigation`。`implement`、`implement-spec`、`setup-power-agent` 及其实际依赖保持可达；手动流程只由用户显式启动。`grilling` 保留原版问题树、逐轮 frontier 和用户共同理解确认，确认前不实施。支持文件从实际安装位置解析，不假定业务 cwd 有源码目录。

不承诺单 Skill 独立安装，也不设置品牌 router。主文足以决定何时使用专门知识，references 按当前问题加载；具名调用只指向允许模型调用的能力。手动入口不能成为自动依赖，也不能靠读取其正文绕过限制；元数据是宿主调用策略，不是通用访问控制。已有普通材料可以直接消费，不要求重新通过上游生成。

例如，实现可消费 POD 的测试判断与 review 的审查判断；讨论落盘可消费领域语义及目标项目文档协议。是否需要这些能力由任务决定，不把整包依赖图变成每次必跑的链。

## 跨任务默认与按需 Skill

最小完整改动默认规则的唯一来源是 [`skills/codebase-design/references/minimal-complete-change.md`](../skills/codebase-design/references/minimal-complete-change.md)。它指导所有编码任务优先解决已授权的实际问题，避免无实际消费者的抽象和扩张；完整性、正确性、安全、兼容性和必要验证仍由任务决定。它不是必须执行的固定工作流，也不替代 `codebase-design` 等按需加载的 Skill。

`hooks/defaults.cjs` 从安装位置读取该来源，供原生 hook 和 pi/OMP 扩展使用；Cursor 插件规则由 `scripts/sync-plugin-rules.cjs` 从同一来源生成到 `rules/minimal-complete-change.mdc`，不维护第二份规则正文。Claude Code、pi、OMP、Codex、Cursor、Factory/Droid 使用本仓库的插件或包，无需向业务项目复制规则。各宿主的入口、信任条件和验证边界见[兼容性指南](agent-compatibility.md)；资源声明不等于实际送达或模型遵循。

## 执行状态与知识

有持久任务图时，执行状态以项目选定的 tracker 为唯一真源；没有 tracker 时，普通实现不因此受阻。配置复用已有位置，无约定才用 `docs/agents/issue-tracker.md`；已有 GitHub、GitLab、本地或其他后端按项目实际工作方式配置，不复制第二份状态。仓库文档保存术语、决定和稳定系统事实；计划与交接引用状态源，不取代它。

多票协调者从 tracker 获取任务图，按真实依赖、写所有权和授权推进，并对整体组合验收负责。关系表达、状态写入与恢复方式见[工作方式](workflow.md#任务图与唯一状态源)。

## 宿主与 Sub-agent

支持完整工作方式的宿主需要普通 sub-agent 的任务传入、上下文传递和结果收集能力；独立工作可并行，共享写入需协调。子代理使用新上下文，结果仍由协调者核验和集成。不依赖 team mode，不规定平台并发数字，也不维护无 sub-agent fallback；宿主实际能力不能仅由安装声明推断。

## 证据、授权与机器协议

可自动验证的行为变更默认 Red/Green；复用已知失败，绿色纯重构、UI、文档和机械变更使用匹配证据；重构在 review 阶段进行。review 默认由需求与工程两个独立 reviewer 并行对照。因果诊断先建立能变红的紧反馈环，再提出假设；trace、差分及同口径性能/稳定性观测必须作为可重放的反馈环使用，而不是静态猜测的替代。只有一个实现时先假设 seam 可能不存在：一个 adapter 是假设的 seam，两个 adapter 才说明变化真实存在；独立资源责任或真实消费者边界可以证明单实现 seam。

dirty working tree 可直接验证。声明绑定被测内容、依赖和环境；只有提交、PR、合并等 commit-bound 动作才需绑定提交，目标 CI 门禁仍独立满足。测试通过不扩大授权。模型可连续完成已授权的本地工作；讨论、建议、草稿和生成脚本不授权实施、发布或执行秘密/权限操作。

精确协议只服务真实机器消费者：tracker 关系、文件格式、API 和副作用批准。普通 docs 不自动启用 Knowledge Bundle；已有 Bundle 保留 frontmatter、来源语义和验证策略。OKF 细节只有 `dev-docs` 一份权威 reference。
