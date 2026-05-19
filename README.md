# power-agent

> **早期实验项目。** 这是一个个人实验，试图将 [superpowers](https://github.com/obra/superpowers) 的 Skill 体系与 OpenAI [Harness Engineering](https://openai.com/index/harness-engineering/) 的方法论整合为一套连贯的 AI 编码 Agent 工作流。目前处于非常早期阶段，许多 Harness Engineering 的核心主张（尤其是基础设施层：自定义 Linter、Application legibility、自动化 Doc gardening）尚未实现，见[下方路线图](#harness-engineering-实践现状与路线图)。

---

融合两套互补方法论的 AI 编码 Agent 工作流系统：

- **[superpowers](https://github.com/obra/superpowers)**（当前追踪版本 **v5.1.0**）— 面向 AI Agent 的完整软件开发 Skill 体系
- **[Harness Engineering](https://openai.com/index/harness-engineering/)**（Ryan Lopopolo, OpenAI, 2026 年 2 月）— OpenAI 关于在工程工作流中运用 AI Agent 的方法论

两者结合，形成一套完整、有主张的工作流：结构化设计探索 → TDD 驱动的执行计划 → 默认先并行委派 → 不能并行时单代理推进 → 系统化调试 → 文档维护。

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
| `discuss` | 编码前的设计探索——含 2-3 方案对比、Spec 子代理审查循环和用户批准 Gate |
| `writing-plans` | 将 spec/设计转化为 TDD 结构的 exec-plan，产出可执行任务卡 |
| `exec-plan-runner` | 自主执行或恢复 exec-plan，含默认并行委派、单代理回退、依赖批次、冲突检测、审查修复收敛、验证与收尾 |
| `dev-docs` | 文档路由器——exec-plan 委派给 `writing-plans`，其他文档类型直接处理 |
| `dev-docs-maintain` | 文档维护（Doc Gardening）——按需扫描并修复过期、缺失或失效文档 |
| `init-harness-engineering` | 从零为项目建立 Harness Engineering 知识体系 |
| `using-git-worktrees` | 执行大任务前检测/创建隔离 worktree，优先使用宿主原生能力 |
| `writing-skills` | 创建、修改、审查和压力测试 Skill |
| `systematic-debugging` | 四阶段根因优先调试（先找根本原因，再动手修复） |
| `test-driven-development` | 务实增量测试闭环，含反模式参考 |
| `requesting-code-review` | 通过子代理编排代码审查，输出结构化发现 |
| `receiving-code-review` | 技术性评估审查反馈（非表演性同意） |
| `verification-before-completion` | 证据优先验证——没有新鲜证据不得声称完成 |
| `dispatching-parallel-agents` | 将独立任务调度为并行子代理 |
| `harness-engineering-review` | 对照 Harness Engineering 最佳实践审查项目 Agent 工作流 |
| `finishing-a-development-branch` | 实现完成后的分支收尾（merge/PR/保留/丢弃） |

### 完整工作流

```
discuss skill          ← 设计探索 → spec 文档
    ↓（spec 批准后）
writing-plans skill    ← 创建 TDD 结构 exec-plan
    ↓
exec-plan-runner skill ← BOOTSTRAP(using-git-worktrees) → TDD 子代理并行实现
                     └── 内部审查 → 验证 → 分支收尾

Bug / 测试失败 → systematic-debugging skill
                     └── → test-driven-development + verification-before-completion
```

`requesting-code-review` 在合并/PR 前默认强制执行，除非用户明确要求跳过并记录原因。
`dev-docs-maintain` 是按需或用户要求调用的文档维护 Skill，不是每次开发执行的固定主流程。

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

---

## 版本追踪

本项目持续追踪上游变更：

| 上游项目 | 当前追踪版本 | 来源 |
|----------|------------|------|
| superpowers | v5.1.0 | https://github.com/obra/superpowers |
| Harness Engineering | 2026 年 2 月 | https://openai.com/index/harness-engineering/ |

当 superpowers 发布新版本时，查阅 RELEASE-NOTES 并将相关改进移植到本项目。

---

## Harness Engineering 实践现状与路线图

以下逐条对照 [Harness Engineering 博客](https://openai.com/index/harness-engineering/)（Ryan Lopopolo, OpenAI, 2026 年 2 月）的核心主张，评估本项目的当前实践状态。

图例：✅ 已实践 · ⚠️ 部分实践 · ❌ 尚未实现（路线图）

---

### ✅ 1. AGENTS.md 是目录，不是百科全书

> "We tried the 'one big AGENTS.md' approach. It failed in predictable ways... When everything is 'important,' nothing is... So instead of treating AGENTS.md as the encyclopedia, we treat it as **the table of contents**. A short AGENTS.md (roughly 100 lines) is injected into context and serves primarily as a map, with pointers to deeper sources of truth elsewhere."
> — §We made repository knowledge the system of record

**本项目状态：** `init-harness-engineering` skill 在初始化项目时生成精简的 AGENTS.md（~200行），作为 Agent 指南和知识库导航。`docs/` 下的分层结构承载具体知识。

---

### ✅ 2. docs/ 是版本化的知识系统

> "The repository's knowledge base lives in a structured docs/ directory treated as the system of record... Design documentation is catalogued and indexed, including verification status and a set of core beliefs that define agent-first operating principles."
> — §We made repository knowledge the system of record

**本项目状态：** `dev-docs` skill 将文档分为 architecture / arch-decision / domain / development / reference 五类，各有固定路径和 `<!-- verified: YYYY-MM-DD -->` 元信息。`dev-docs-maintain` skill 负责检查新鲜度和导航指针有效性。

---

### ✅ 3. Exec-plan 是一等公民

> "Plans are treated as first-class artifacts. Ephemeral lightweight plans are used for small changes, while complex work is captured in execution plans with progress and decision logs that are checked into the repository. Active plans, completed plans, and known technical debt are all versioned and co-located."
> — §We made repository knowledge the system of record

**本项目状态：** `writing-plans` skill 产出 exec-plan 到 `docs/exec-plans/active/`，`exec-plan-runner` 执行完成后归档到 `completed/`。博客还提到 tech-debt-tracker，本项目尚未实现（见路线图 #13）。

---

### ✅ 4. Progressive disclosure：从小入口被引导

> "This enables **progressive disclosure**: agents start with a small, stable entry point and are taught where to look next, rather than being overwhelmed up front."
> — §We made repository knowledge the system of record

**本项目状态：** AGENTS.md 只包含知识库导航指针，具体知识分散在 `docs/` 各文件中。Agent 按需加载，不被一次性灌入所有上下文。

---

### ✅ 5. TDD 驱动实现

> "we require Codex to parse data shapes at the boundary, but are not prescriptive on how that happens... Agents are most effective in environments with strict boundaries and predictable structure."
> — §Enforcing architecture and taste

博客未直接命名 TDD，但全文强调每个变更必须有测试覆盖，且 exec-plan 结构中测试与实现不可分离。

**本项目状态：** `test-driven-development` skill 要求增量测试闭环，`exec-plan-runner` 的实现子代理被要求使用该 skill，`testing-anti-patterns.md` 列出了 5 类常见违规模式。

---

### ✅ 6. 系统化调试，根因优先

博客在描述开发循环时反复强调 agent 的自我验证能力和修复质量，并指出当 agent 遇到失败时，人类的任务不是"试更努力"，而是识别缺失了什么能力并补充到仓库中。

**本项目状态：** `systematic-debugging` skill 提供四阶段根因优先调试框架，明确禁止在没有根本原因分析的情况下动手修复，并包含 `root-cause-tracing.md`、`defense-in-depth.md` 等支撑文件。

---

### ⚠️ 7. Doc gardening 是自动化的后台 agent 任务

> "A recurring 'doc-gardening' agent scans for stale or obsolete documentation that does not reflect the real code behavior and opens fix-up pull requests."
> — §We made repository knowledge the system of record

**本项目状态：** `dev-docs-maintain` skill 覆盖了 doc gardening 的逻辑（新鲜度检查、内容对照代码验证、P0/P1/P2 修复优先级），但它是**按需手动触发的 skill**，不属于每次开发执行的固定阶段。博客描述的是在 CI 中定时自动运行、自动开 PR 的后台任务，两者的可靠性和覆盖度有根本差异。

---

### ⚠️ 8. Agent-to-agent review，人工逐渐变为可选

> "Humans may review pull requests, but aren't required to. Over time, we've pushed almost all review effort towards being handled agent-to-agent."
> — §Redefining the role of the engineer

**本项目状态：** `requesting-code-review` skill 通过 subagent 执行结构化代码审查，`exec-plan-runner` 在每个 batch 后自动启动两阶段审查（规格符合性 + 代码质量）。审查结果仍将人工决策作为 gate，未给出随时间减少人工介入的路径。

---

### ⚠️ 9. 区分轻量临时计划和正式 exec-plan

> "Ephemeral lightweight plans are used for small changes, while complex work is captured in execution plans."
> — §We made repository knowledge the system of record

**本项目状态：** `writing-plans` skill 区分了单文件（小任务）和目录结构（大需求）两种输出格式。但没有明确的"临时计划"概念和对应的轻量格式，可能对中等复杂度的变更造成过重的开销。

---

### ❌ 10. 自定义 Linter，error message 注入 agent 修复指令

> "we enforce these rules with custom linters and structural tests... Because the lints are custom, **we write the error messages to inject remediation instructions into agent context**."
> — §Enforcing architecture and taste

这是博客"机械约束优于冗长 Prompt"原则的真正落地。不是让 agent 记住规则，而是让违规行为在 CI 中立刻报错，且错误信息本身就告诉 agent 怎么修。

**本项目状态：** `docs/harness-engineering.md` 写了"机械化约束优于 Prompt 啰嗦"的原则，`harness-engineering-review` skill 的审查维度中包含"约束机制化"。但项目本身没有提供任何 linter 配置模板、错误信息设计指南或 CI 集成方式。这是当前最大的结构性缺口。

**路线图：** 提供一套 linter 模板（ESLint / Ruff / custom）和 agent 友好错误信息的设计规范，作为 `init-harness-engineering` 输出的一部分。

---

### ❌ 11. 分层领域架构，依赖方向由 linter 机械执行

> "Each business domain is divided into a fixed set of layers, with strictly validated dependency directions and a limited set of permissible edges. These constraints are enforced mechanically via custom linters (Codex-generated, of course!) and structural tests."
> — §Enforcing architecture and taste

博客展示的层级是 Types → Config → Repo → Service → Runtime → UI，跨领域的横切关注点（auth、telemetry 等）只通过单一显式接口 Providers 进入。

**本项目状态：** 项目没有提供任何关于如何设计和机械执行分层架构的指导。这需要与第 10 条（自定义 linter）协同实现。

**路线图：** 在 `init-harness-engineering` skill 中加入分层架构的脚手架建议，以及对应的 linter 规则模板。

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

**路线图：** 在 `init-harness-engineering` 输出中加入 `docs/quality.md` 模板，由 `dev-docs-maintain` 在每次维护时更新。

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

**路线图：** 在 `dev-docs` 和 `init-harness-engineering` 中加入 llms.txt 格式的引导，说明如何为核心依赖创建 agent 可消费的本地参考文档。

---

### ❌ 17. PR 是主要工作单元，agent 全程参与 PR 生命周期

> "Humans interact with the system almost entirely through prompts: an engineer describes a task, runs the agent, and allows it to open a pull request. To drive a PR to completion, we instruct Codex to review its own changes locally, request additional specific agent reviews both locally and in the cloud, respond to any human or agent given feedback, and iterate in a loop until all agent reviewers are satisfied."
> — §Redefining the role of the engineer

博客描述的完整循环是：agent 开 PR → agent 响应 review 评论 → agent 修复 CI 失败 → agent 判断可以 merge 时自动合并。人类只是在需要判断时介入。

**本项目状态：** `exec-plan-runner` 执行完成后即结束，没有覆盖 PR 开启、review 响应、CI 修复、merge 这些后续环节。`requesting-code-review` 和 `receiving-code-review` 处理的是 review 内容本身，不是 PR 生命周期管理。

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

- **superpowers** by [Jesse Vincent (obra)](https://github.com/obra/superpowers) — MIT License。当前追踪 **v5.1.0**。以下 Skill 派生或受其启发：`discuss`（来自 `brainstorming`）、`writing-plans`、`exec-plan-runner`（融合了 `subagent-driven-development`）、`test-driven-development`、`requesting-code-review`、`receiving-code-review`、`verification-before-completion`、`dispatching-parallel-agents`、`systematic-debugging`、`using-git-worktrees`、`writing-skills`。

- **Harness Engineering** — [Ryan Lopopolo，OpenAI，2026 年 2 月 11 日](https://openai.com/index/harness-engineering/)。`harness-engineering-review`、`init-harness-engineering`、`dev-docs`、`dev-docs-maintain` Skill 以及"仓库即唯一真相来源"的整体设计哲学源于该方法论。
