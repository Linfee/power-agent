---
type: Architecture
scope:
  - architecture
---

# 系统架构

Power-Agent 是以 Matt 轻量工程能力为主干的整包 Skill。目标、真实证据和授权决定行动；不要求用户逐站启动，也不把所有能力绑成长流水线。当前决定见 [ADR-0012](adr/0012-matt-led-skill-fusion.md)，逐项来源与取舍见[融合设计](specs/2026-11-11-matt-power-agent-fusion.md)。

## 能力边界

|范围|入口|承重判断|
|---|---|---|
|工程内核|`proof-oriented-development`、`code-review`、`diagnosing-bugs`、`codebase-design`|红绿重构、需求与工程双维审查、因果证据、模块深度与真实责任|
|目标与知识对齐|`grilling`、`grill-with-docs`、`domain-modeling`|问题树逐轮追问、确认共同理解、复用术语真源、记录值得保留的决定|
|任务与调度|`to-spec`、`to-tickets`、`implement`、`implement-spec`、`triage`、`wayfinder`|小任务直接做；必要时创建可验收结果和真实依赖，由单一协调者推进|
|探索与交付|`improve-codebase-architecture`、`research`、`prototype`、`pr`、`wizard`|从证据回答未知、实际运行或展示、草稿与发布分开、必要人工批准|
|协作与环境|`handoff`、`writing-for-agents`、`retro`|携带权威指针、按需可达指令、改进环境而非堆禁令|
|项目知识|`dev-docs`、`dev-docs-maintain`、`knowledge-navigation`、`setup-power-agent`|按既有协议写知识、扫描与安全登记、真实检索路径、最小初始化|

这六行是能力地图，不是执行层级。完整入口见 [README](../README.md#skills)。

## 整包组合

25 个目录平铺在 `skills/`；`grill-with-docs` 保留 Matt 原版手动调用，其余允许模型调用。`grilling` 保留原版问题树、逐轮 frontier 和用户共同理解确认，确认前不实施。主文可具名调用同包能力，将每种承重判断保留在一个权威位置；支持文件从实际安装位置解析，不假定业务 cwd 有源码目录。

不承诺单 Skill 独立安装，也不设置品牌 router。主文足以决定何时使用专门知识；references 只按当前问题加载。具名调用是模型内部协作，不是向用户交回“下一步请调用另一个 Skill”。已有普通材料可以直接消费，不要求重新通过某个上游生成。

例如，实现可消费 POD 的测试判断与 review 的审查判断；讨论落盘可消费领域语义及目标项目文档协议。是否需要这些能力由任务决定，不把整包依赖图变成每次必跑的链。

## 执行状态与知识

执行状态只在项目已选定的 tracker。配置复用现有位置，无约定才用 `docs/agents/issue-tracker.md`；GitHub、GitLab、本地三选一。spec 表达整体目标，tickets 在有调度消费者时表达工作切片，现有完整 issue 无需再包装。

native 关系/状态受实际平台版本与 tier 支持时优先使用；不支持时用约定正文，一个属性不双写。本地条目最小区分 `Kind`、`State`、`Blocked by`、`Owner`，仅外来请求另有可选 `Triage`。单协调者拥有状态写入，assignee 或重读标记不是原子锁。

仓库文档保存术语、决定、稳定系统事实和拒绝理由。计划与 handoff 保存意图、证据和状态源指针，不复制进度；恢复先重读当前 tracker。子项完成不能直接关闭父 spec/map，整体组合验收仍由协调者负责。

## Sub-agent 与集成

宿主必须提供普通 sub-agent 的任务传入、上下文传递、结果收集和并行执行。子代理使用新上下文；独立工作按依赖并行，共享文件或接口由唯一整合者写入或串行处理。结果是待核验证据，不自动构成完成声明。

不使用 team mode、不规定并发数字、不提供无 sub-agent fallback。默认可以在工作树按不重叠写范围协作，不为并行暗中创建分支、worktree、commit、merge、PR 或清理目录。

## 证据、授权与机器协议

可自动验证的行为变更默认红绿重构；复用已知失败，绿色纯重构、UI、文档和机械变更使用匹配证据。review 同时对照需求和工程质量；因果诊断接受 trace、差分及同口径性能/稳定性观测，不要求先造 runnable red command。模块边界由不变量、复杂度或真实资源责任证明，不按 adapter 数裁决。

dirty working tree 可直接验证。声明绑定被测内容、依赖和环境；只有提交、PR、合并等 commit-bound 动作才需绑定提交，目标 CI 门禁仍独立满足。测试通过不扩大授权。模型可连续完成已授权的本地工作；讨论、建议、草稿和生成脚本不授权实施、发布或执行秘密/权限操作。

精确协议只服务真实机器消费者：tracker 关系、scanner、ledger、文件格式、API 和副作用批准。普通 docs 不自动启用 Knowledge Bundle；已有 Bundle 保留 frontmatter、来源语义、freshness 策略及安全原子登记。OKF 细节只有 `dev-docs` 一份权威 reference。
