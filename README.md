# power-agent

> **早期实验项目。** 这是一个个人实验，试图将 [superpowers](https://github.com/obra/superpowers) 的 Skill 体系与 OpenAI [Harness Engineering](https://openai.com/index/harness-engineering/) 的方法论整合为一套连贯的 AI 编码 Agent 工作流。目前处于非常早期阶段，许多 Harness Engineering 的核心主张（尤其是基础设施层：自定义 Linter、Application legibility、自动化 Doc gardening）尚未实现，见[下方路线图](#harness-engineering-实践现状与路线图)。

---

融合两套互补方法论的 AI 编码 Agent 工作流系统：

- **[superpowers](https://github.com/obra/superpowers)** — 面向 AI Agent 的完整软件开发 Skill 体系
- **[Harness Engineering](https://openai.com/index/harness-engineering/)**（Ryan Lopopolo, OpenAI, 2026 年 2 月）— OpenAI 关于在工程工作流中运用 AI Agent 的方法论

两者结合，形成一套完整、有主张的工作流：结构化设计探索 → 证明导向执行计划 → 紧凑 exec-plan 包 → Agent 自主实现闭环 → 系统化调试 → 文档维护。

---

## 核心理念

**人类掌舵，Agent 执行。** 人类负责设计意图、构建反馈循环；Agent 负责执行闭环。所有决策必须在仓库中版本化——Agent 看不到的内容等同于不存在。

来自 Harness Engineering 的三个核心原则：

1. **仓库是唯一真相来源（Repo as SSOT）** — 所有知识必须版本化。Agent 看不到的东西不存在。
2. **上下文是地图而非百科全书** — `AGENTS.md` 是导航索引（约 200 行），而非 Wiki。
3. **机械化约束优于冗长 Prompt** — Linter/Test 规则胜过大篇幅的指令说明。

---

## Skills 一览

| Skill | 用途 |
|-------|------|
| `discuss` | 通用讨论——任何需要想清楚再行动的问题，行动前的讨论、澄清与对齐，审查强度与决策权重相称 |
| `writing-plans` | 将会修改软件资产的讨论结论 / spec / 用户描述转化为开发 compact exec-plan，并按风险选择 self-review 或独立 reviewer |
| `codebase-design` | 为具体模块收窄接口、评估模块深度，并判断 seam / adapter 与可观察测试表面是否必要 |
| `implement` | 执行或恢复任何开发计划（exec-plan、手写计划、任务清单或 spec）；优先 team 模式，通过 scratch artifacts 交接并使用单 reviewer 双 verdict 内审，再完成全量审查、验证与收尾 |
| `dev-docs` | 长期开发知识回写——把稳定系统事实、边界、决策依据或集成参考写入/修订 `docs/`；软件资产变更的开发计划委派给 `writing-plans` |
| `dev-docs-maintain` | Docs Bundle 维护——按需检查健康状态、修复结构或知识漂移，并登记已完成验证 |
| `setup-power-agent` | 从零为项目建立 Harness Engineering 知识体系 |
| `writing-skills` | 创建、修改、审查和压力测试 Skill |
| `systematic-debugging` | 探索式根因调查：以因果证据、安全边界及风险相称的性能/稳定性证据约束修复交接 |
| `proof-oriented-development` | 证明导向开发闭环：小步实现、最小相关验证、交付 Proof Block |
| `code-review` | 通过子代理编排代码审查并评估审查反馈，输出结构化发现 |
| `verification-before-completion` | 证据优先验证——没有新鲜证据不得声称完成 |
| `harness-engineering-review` | 对照 Harness Engineering 最佳实践审查项目 Agent 工作流 |
| `finishing-a-development-branch` | dirty / 无 HEAD 待提交提示；clean 验证后的分支收尾（merge/PR/保留/丢弃） |

### 完整工作流

```
开发工作流（仅处理修改代码、测试、配置、自动化、Skill/prompt 或开发工作流的软件资产变更）：

discuss skill          ← 通用讨论：任何需要想清楚再行动的问题 → 内联讨论结论（按需落盘 spec）
    ↓（独立审查通过后；边界清楚的工作可跳过 writing-plans 直接交 implement）
writing-plans skill    ← 为跨模块 / 多批次 / 高风险工作创建 compact exec-plan，并按 low/medium/high 选择 self-review 或独立 reviewer
    ↓
implement skill ← 准备（git worktree 按需隔离 + exec-plan Gate）→ 轻量启动通知
                     └── 优先 team 模式；缺失 team 工具时回退 proof-oriented 实现子代理并行/单代理推进 → scratch artifacts + 单 reviewer 双 verdict → 全量审查 → 工作区检查（dirty / 无 HEAD 先提交）→ 验证 → 分支收尾

Bug / 测试失败 → systematic-debugging skill
                     └── → proof-oriented-development → 全量审查 → 工作区检查 → verification-before-completion

```

非开发的路由不进入 exec-plan：根因未知的异常先用 `systematic-debugging`；长期项目知识用 `dev-docs` / `dev-docs-maintain`；面向读者的实质文档用 `doc-coauthoring`（范围或验收未定时先 `discuss`）；研究、运营和普通清单使用宿主原生任务清单或直接推进。重叠时以当前主要交付物为准：诊断优先于实施，软件资产变更优先于附带文档，长期项目知识优先于通用文档共创。

`code-review` 在最终验证前默认强制执行；合并/PR 前不得跳过未通过的审查结果，除非用户明确要求跳过并记录原因。
`dev-docs-maintain` 是在 docs 健康检查、漂移修复或 verification ledger 登记需要时按需触发的普通 Skill，不是每次开发执行的固定主流程。

详细的 Skill 协调机制见 [docs/workflow.md](docs/workflow.md)。

---

## 安装

### 作为 Droid 插件（推荐）

```bash
# 将此仓库添加为 marketplace
droid plugin marketplace add https://github.com/Linfee/power-agent

# 安装插件（user 作用域——跨项目可用）
droid plugin install power-agent@power-agent --scope user

# 或 project 作用域——通过 git 与团队共享
droid plugin install power-agent@power-agent --scope project
```

也可通过交互界面：`/plugins` → Browse 标签页。

### 作为 Claude Code 插件

```bash
# 将此仓库添加为 marketplace
claude plugin marketplace add https://github.com/Linfee/power-agent

# 安装插件（user 作用域——跨项目可用）
claude plugin install power-agent@power-agent --scope user

# 或 project 作用域——通过 git 与团队共享
claude plugin install power-agent@power-agent --scope project
```

也可手动安装：将项目目录复制到本地后，通过 Claude Code 插件管理器从本地路径加载（`.claude-plugin/plugin.json` 格式与 Droid 互通）。

### 作为 Cursor 插件

使用 `.cursor-plugin/plugin.json`，通过 Cursor 插件管理器安装，或手动将 `skills/` 目录内容复制到项目中。

### 作为 Factory 插件

使用 `.factory-plugin/plugin.json`，通过 Factory 插件管理器安装，或手动将 `skills/` 目录内容复制到项目中。

### 作为 Gemini 扩展

使用 `gemini-extension.json`；该清单指向 `GEMINI.md`，再由 `GEMINI.md` 加载 `AGENTS.md`。

---


## Harness Engineering 实践现状与路线图

以下逐条对照 [Harness Engineering 博客](https://openai.com/index/harness-engineering/)（Ryan Lopopolo, OpenAI, 2026 年 2 月）的核心主张，评估本项目的当前实践状态。

图例：✅ 已实践 · ⚠️ 部分实践 · ❌ 尚未实现（路线图）

---

### ✅ 1. AGENTS.md 是目录，不是百科全书

> "We tried the 'one big AGENTS.md' approach. It failed in predictable ways... When everything is 'important,' nothing is... So instead of treating AGENTS.md as the encyclopedia, we treat it as **the table of contents**. A short AGENTS.md (roughly 100 lines) is injected into context and serves primarily as a map, with pointers to deeper sources of truth elsewhere."
> — §We made repository knowledge the system of record

**本项目状态：** `setup-power-agent` skill 在初始化项目时生成精简的 AGENTS.md（~200行），作为 Agent 指南和知识库导航。`docs/` 下的分层结构承载具体知识；同时初始化 `CONTEXT.md` / `CONTEXT-MAP.md` 与 `docs/adr/` 这组项目记忆骨架，供后续 Agent 读取领域语言与历史架构决策。

---

### ✅ 2. docs/ 是版本化的知识系统

> "The repository's knowledge base lives in a structured docs/ directory treated as the system of record... Design documentation is catalogued and indexed, including verification status and a set of core beliefs that define agent-first operating principles."
> — §We made repository knowledge the system of record

**本项目状态：** `dev-docs` skill 将文档分为 architecture / adr / exec-plan / domain / development / reference 六类，其中 exec-plan 立即委派给 `writing-plans`；`docs/` Knowledge Bundle 内的 Concept 使用具有非空 `type` 的 YAML frontmatter，验证运行状态由 `docs/.okf/verification.json` ledger 表示。ADR 作为历史决策记录使用 `type: Decision` 与 YAML lifecycle status。`dev-docs-maintain` skill 负责检查普通文档新鲜度和导航指针有效性。

---

### ✅ 3. Exec-plan 是一等公民

> "Plans are treated as first-class artifacts. Ephemeral lightweight plans are used for small changes, while complex work is captured in execution plans with progress and decision logs that are checked into the repository. Active plans, completed plans, and known technical debt are all versioned and co-located."
> — §We made repository knowledge the system of record

**本项目状态：** `writing-plans` skill 产出 exec-plan 到 `docs/exec-plans/active/`，`implement` 执行完成后归档到 `completed/`。博客还提到 tech-debt-tracker，本项目尚未实现（见路线图 #13）。

---

### ✅ 4. Progressive disclosure：从小入口被引导

> "This enables **progressive disclosure**: agents start with a small, stable entry point and are taught where to look next, rather than being overwhelmed up front."
> — §We made repository knowledge the system of record

**本项目状态：** AGENTS.md 只包含知识库导航指针，具体知识分散在 `docs/` 各文件中。Agent 按需加载，不被一次性灌入所有上下文。

---

### ✅ 5. Proof-oriented 证明导向实现

> "we require Codex to parse data shapes at the boundary, but are not prescriptive on how that happens... Agents are most effective in environments with strict boundaries and predictable structure."
> — §Enforcing architecture and taste

博客强调每个变更必须有可验证证据，并且计划结构中验收、验证与实现不可分离。

**本项目状态：** `proof-oriented-development` skill 要求小步实现、自动运行最小相关验证，并交付 Proof Block；`writing-plans` 在计划阶段定义证明策略、Proof Block 期望证据和执行期阻塞条件；`testing-anti-patterns.md` 约束测试和 proof 反模式。

---

### ✅ 6. 系统化调试，根因优先

博客在描述开发循环时反复强调 agent 的自我验证能力和修复质量，并指出当 agent 遇到失败时，人类的任务不是"试更努力"，而是识别缺失了什么能力并补充到仓库中。

**本项目状态：** `systematic-debugging` skill 允许前沿模型自主选择高信息增益的调查路径，以 feedback loop 质量、区分性证据、因果闭合和 original/minimal repro 约束根因声明；性能或稳定性存在合理影响面时，POD 与 VBC 要求同口径 baseline/candidate 或重复观测，功能绿色不能替代非退化证明。`root-cause-tracing.md`、`performance-and-flakiness.md`、`defense-in-depth.md` 等 references 按需加载。

---

### ⚠️ 7. Doc gardening 是自动化的后台 agent 任务

> "A recurring 'doc-gardening' agent scans for stale or obsolete documentation that does not reflect the real code behavior and opens fix-up pull requests."
> — §We made repository knowledge the system of record

**本项目状态：** `dev-docs-maintain` skill 覆盖了 doc gardening 的逻辑（新鲜度检查、内容对照代码验证、P0/P1/P2 修复优先级），并可在文档变更、来源变化或用户请求时按需触发；它不属于每次开发执行的固定阶段。博客描述的是在 CI 中定时自动运行、自动开 PR 的后台任务，两者的可靠性和覆盖度有根本差异。

---

### ⚠️ 8. Agent-to-agent review，人工逐渐变为可选

> "Humans may review pull requests, but aren't required to. Over time, we've pushed almost all review effort towards being handled agent-to-agent."
> — §Redefining the role of the engineer

**本项目状态：** `code-review` skill 通过 subagent 执行结构化代码审查，`implement` 在实现阶段以内审循环保障质量，`review-contract.md` 提供按需审阅面；人工决策可按需参与，分支丢弃等破坏性操作仍遵守明确授权边界。

---

### ⚠️ 9. 区分轻量临时计划和正式 exec-plan

> "Ephemeral lightweight plans are used for small changes, while complex work is captured in execution plans."
> — §We made repository knowledge the system of record

**本项目状态：** `writing-plans` 已有轻重分层：默认产出 compact exec-plan（`plan.md + review-contract.md`），仅在上下文过大、任务图复杂或多 Agent 交接需要时拆出 `context.md / tasks.md`。但仍没有一套完全临时、无需落盘的轻量计划格式。

---

### ❌ 10. 自定义 Linter，error message 注入 agent 修复指令

> "we enforce these rules with custom linters and structural tests... Because the lints are custom, **we write the error messages to inject remediation instructions into agent context**."
> — §Enforcing architecture and taste

这是博客"机械约束优于冗长 Prompt"原则的真正落地。不是让 agent 记住规则，而是让违规行为在 CI 中立刻报错，且错误信息本身就告诉 agent 怎么修。

**本项目状态：** `docs/harness-engineering.md` 写了"机械化约束优于 Prompt 啰嗦"的原则，`harness-engineering-review` skill 的审查维度中包含"约束机制化"。但项目本身没有提供任何 linter 配置模板、错误信息设计指南或 CI 集成方式。这是当前最大的结构性缺口。

**路线图：** 提供一套 linter 模板（ESLint / Ruff / custom）和 agent 友好错误信息的设计规范，作为 `setup-power-agent` 输出的一部分。

---

### ❌ 11. 分层领域架构，依赖方向由 linter 机械执行

> "Each business domain is divided into a fixed set of layers, with strictly validated dependency directions and a limited set of permissible edges. These constraints are enforced mechanically via custom linters (Codex-generated, of course!) and structural tests."
> — §Enforcing architecture and taste

博客展示的层级是 Types → Config → Repo → Service → Runtime → UI，跨领域的横切关注点（auth、telemetry 等）只通过单一显式接口 Providers 进入。

**本项目状态：** 项目没有提供任何关于如何设计和机械执行分层架构的指导。这需要与第 10 条（自定义 linter）协同实现。

**路线图：** 在 `setup-power-agent` skill 中加入分层架构的脚手架建议，以及对应的 linter 规则模板。

---

### ❌ 12. Application legibility：app 运行时对 agent 可见

> "we made the app bootable per git worktree, so Codex could launch and drive one instance per change... we wired the Chrome DevTools Protocol into the agent runtime and created skills for working with DOM snapshots, screenshots, and navigation. This enabled Codex to reproduce bugs, validate fixes, and reason about UI behavior directly."
> — §Increasing application legibility

> "Codex works on a fully isolated version of that app—including its logs and metrics, which get torn down once that task is complete. Agents can query logs with LogQL and metrics with PromQL."
> — §Increasing application legibility

博客在这一节描述的是：agent 能自己启动应用、驱动 UI、查询日志和指标，从而形成完整的"实现 → 启动 → 观察 → 修复"闭环，无需人工转述报错信息。

**本项目状态：** `verification-before-completion` skill 要求 agent 运行验证命令，但没有覆盖"如何让 app 对 agent 可见"的基础设施层：per-worktree 隔离启动、结构化日志接入、本地 observability stack 配置、UI 驱动能力。这是博客花篇幅最多的部分，也是本项目最显著的空白。

**路线图：** 提供 application legibility 配置指南，涵盖 worktree 启动脚本模板、结构化日志规范、本地 observability 接入方式。

---

### ❌ 13. Golden principles + 自动化持续清理

> "Initially, humans addressed this manually. Our team used to spend every Friday (20% of the week) cleaning up 'AI slop.' Unsurprisingly, that didn't scale. Instead, we started encoding what we call 'golden principles' directly into the repository and built a recurring cleanup process... Human taste is captured once, then enforced continuously on every line of code."
> — §Entropy and garbage collection

Golden principles 是团队对代码风格的具体约定（如"优先使用共享 utility 包而非手写 helper"），编码为可检查的规则后由后台 agent 每日扫描并开 PR 修复。

**本项目状态：** 项目没有 golden principles 文档，没有自动化的 cleanup agent，没有质量评级机制。`dev-docs-maintain` 仅覆盖文档层的维护，不覆盖代码层的模式漂移。

**路线图：** 增加 `golden-principles.md` 模板和对应的自动化扫描 skill，与 doc gardening 形成代码层 + 文档层的双重持续维护机制。

---

### ❌ 14. Quality scoring 文档追踪各领域质量评级

> "A quality document grades each product domain and architectural layer, tracking gaps over time."
> — §We made repository knowledge the system of record

博客提到 `QUALITY_SCORE.md` 是知识库的常规组成部分，记录各领域的质量现状和历史变化，供 agent 在做决策时参考。

**本项目状态：** 无对应机制。`harness-engineering-review` skill 可以生成审查报告，但没有持久化的质量追踪文档。

**路线图：** 在 `setup-power-agent` 输出中加入 `docs/quality.md` 模板，由 `dev-docs-maintain` 在每次维护时更新。

---

### ❌ 15. Tech debt tracker 版本化，与 exec-plans 并列

> "Active plans, completed plans, and known technical debt are all versioned and co-located."
> — §We made repository knowledge the system of record

博客将 tech-debt-tracker 与 exec-plans 放在同一目录下，作为可被 agent 读取和更新的结构化文件。

**本项目状态：** `docs/exec-plans/` 只有 active / completed 两个分区，没有 tech-debt 追踪机制。

**路线图：** 在 `docs/exec-plans/` 下增加 `tech-debt.md`，作为 `writing-plans` 和 `dev-docs-maintain` 的标准输出之一。

---

### ❌ 16. References 目录存放 llms.txt 格式的外部库文档

> "references/ — design-system-reference-llms.txt, nixpacks-llms.txt, uv-llms.txt..."
> — §We made repository knowledge the system of record（知识库目录结构）

博客把外部依赖的文档以 llms.txt 格式存放在仓库中，让 agent 能直接查阅而无需访问外网。

**本项目状态：** `dev-docs` skill 有 reference 文档类型，但没有 llms.txt 格式规范，也没有引导如何为项目依赖创建 reference 文件。

**路线图：** 在 `dev-docs` 和 `setup-power-agent` 中加入 llms.txt 格式的引导，说明如何为核心依赖创建 agent 可消费的本地参考文档。

---

### ❌ 17. PR 是主要工作单元，agent 全程参与 PR 生命周期

> "Humans interact with the system almost entirely through prompts: an engineer describes a task, runs the agent, and allows it to open a pull request. To drive a PR to completion, we instruct Codex to review its own changes locally, request additional specific agent reviews both locally and in the cloud, respond to any human or agent given feedback, and iterate in a loop until all agent reviewers are satisfied."
> — §Redefining the role of the engineer

博客描述的完整循环是：agent 开 PR → agent 响应 review 评论 → agent 修复 CI 失败 → agent 判断可以 merge 时自动合并。人类只是在需要判断时介入。

**本项目状态：** `implement` 执行完成后即结束，没有覆盖 PR 开启、review 响应、CI 修复、merge 这些后续环节。`code-review` 处理的是 review 内容与反馈评估，不是 PR 生命周期管理。

**路线图：** 增加 `pr-lifecycle` skill，覆盖从"实现完成"到"PR 合并"的完整流程：开 PR、响应 review 评论、处理 CI 失败、确认 merge。

---

### ❌ 18. 最小阻塞 merge gate，test flake 用重跑处理

> "The repository operates with minimal blocking merge gates. Pull requests are short-lived. Test flakes are often addressed with follow-up runs rather than blocking progress indefinitely. In a system where agent throughput far exceeds human attention, corrections are cheap, and waiting is expensive."
> — §Throughput changes the merge philosophy

博客指出在高吞吐量 agent 环境下，传统的严格 merge gate 反而成为瓶颈，快速修复比等待 block 更有效率。

**本项目状态：** 项目没有覆盖 merge 策略。`verification-before-completion` 强调验证，但没有区分"验证通过才能声称完成"和"merge gate 策略"这两个不同层次的问题。

**路线图：** 在 `docs/harness-engineering.md` 中增加关于 merge 策略的指导，作为项目级决策供团队参考。

---

## 致谢与灵感来源

本项目基于以下工作构建：

- **superpowers** by [Jesse Vincent (obra)](https://github.com/obra/superpowers) — MIT License。以下 Skill 派生或受其启发：`discuss`（来自 `brainstorming`）、`writing-plans`、`implement`（融合了 `subagent-driven-development`）、`proof-oriented-development`（由原测试驱动实现思路演进为证明导向实现）、`code-review`、`verification-before-completion`、`systematic-debugging`、`writing-skills`。

- **Harness Engineering** — [Ryan Lopopolo，OpenAI，2026 年 2 月 11 日](https://openai.com/index/harness-engineering/)。`harness-engineering-review`、`setup-power-agent`、`dev-docs`、`dev-docs-maintain` Skill 以及"仓库即唯一真相来源"的整体设计哲学源于该方法论。
