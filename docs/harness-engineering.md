---
type: Concept
scope:
  - harness-engineering
---

# Harness Engineering 体系设计

基于 OpenAI Harness Engineering 实践构建的 Agent 驱动开发体系。核心理念：**人类掌舵，Agent 执行**——人类的职责是设计意图、构建反馈循环，Agent 负责执行闭环。

**原始参考：** [Harness engineering: leveraging Codex in an agent-first world](https://openai.com/index/harness-engineering/) — Ryan Lopopolo, OpenAI, Feb 11, 2026

**补充参考（Anthropic Engineering）：**

- [Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) — 长任务 harness、initializer/coding agent 分工、progress file、增量提交
- [Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) — 上下文裁剪、structured note-taking、sub-agent 架构
- [Writing effective tools for AI agents — with agents](https://www.anthropic.com/engineering/writing-tools-for-agents) — 工具边界、命名空间、token-efficient 返回、eval 驱动迭代
- [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents) — workflow / agent / orchestrator-workers / evaluator-optimizer 模式选择
- [Code execution with MCP: Building more efficient agents](https://www.anthropic.com/engineering/code-execution-with-mcp) — MCP 工具按需加载、代码执行、上下文效率

---

## 参考文献关键洞察

基于上述 6 篇参考文献提炼的核心原则与启发，按主题组织。

### 上下文工程（Context Engineering）

**上下文是有限资源，边际收益递减。** 随着 token 数量增加，模型准确回忆信息的能力下降（context rot）。有效的上下文工程目标是找到**最小的高信号 token 集合**，最大化期望结果的概率。

- **系统提示的"正确高度"**：避免两个极端——过于刚性的 if-else 硬编码逻辑，和过于模糊的高层指导。最优点是"具体到足以引导行为，灵活到能提供强启发式"。
- **即时上下文检索（Just-in-Time）**：不预加载所有数据，而是维护轻量引用（文件路径、查询、链接），运行时按需加载。Claude Code 的 `glob`/`grep` 就是此模式。
- **渐进式披露（Progressive Disclosure）**：Agent 从小而稳定的入口点开始，逐层发现相关上下文。每次交互产生的上下文指引下一步决策。
- **三种跨窗口持久化策略**：
  - **压缩（Compaction）**：接近窗口上限时，摘要关键信息并开启新窗口。保留架构决策、未解决 bug、实现细节，丢弃冗余工具输出。
  - **结构化笔记（Structured Note-taking）**：Agent 定期将进度写入窗口外的持久化文件（如 progress.txt、TODO 列表），后续窗口拉回使用。
  - **子代理架构**：专用子代理在干净的上下文窗口中处理深度任务，仅返回浓缩摘要（通常 1,000-2,000 tokens），主代理负责综合与分析。

### 长任务 Harness 设计

**跨窗口的增量进展是长任务成功的关键。** Anthropic 提出 initializer agent + coding agent 两阶段方案：

- **Initializer Agent**：首次运行时搭建环境——创建 `init.sh`、progress 文件、功能清单（JSON 格式，带 pass/fail 状态）、初始 git 提交。
- **Coding Agent**：每次会话只做一个功能的增量进展，结束时保持代码"可合并"状态（无重大 bug、有序、有文档）。
- **会话启动仪式**：读 progress 文件 → 读 git log → 读功能清单 → 运行基本健康检查 → 选择最高优先级未完成功能开始工作。
- **功能清单用 JSON 而非 Markdown**：模型不太容易不当修改 JSON 文件。强措辞禁止删除或编辑测试条目。
- **端到端验证**：提供浏览器自动化工具让 Agent 像人类用户一样测试，而非仅依赖单元测试或 curl。

### 工具设计原则

**工具是确定性系统与非确定性 Agent 之间的契约。** Agent 的"可供性"（affordances）与传统软件不同：

- **少而精 > 多而杂**：过多或重叠的工具会分散 Agent 注意力。每个工具应有清晰独立的用途，针对高影响力工作流设计。
- **合并操作**：工具可在底层处理多步操作。例如 `schedule_event` 比 `list_users` + `list_events` + `create_event` 三个工具更有效。
- **命名空间**：按服务和资源前缀分组（如 `asana_projects_search`），帮助 Agent 在大量工具中选择正确的那个。
- **返回有意义上下文**：优先返回 `name`、`file_type` 而非 `uuid`、`mime_type`。将不透明 ID 解析为语义化名称可显著减少幻觉。
- **Token 效率**：实现分页、过滤、截断，带合理默认值。提供 `response_format` 枚举（concise/detailed）让 Agent 控制返回详细程度。
- **可执行的错误信息**：错误响应应包含具体可执行的修复建议，而非不透明的错误码或堆栈跟踪。
- **Eval 驱动迭代**：工具描述值得与系统提示同等的 prompt engineering 投入。用真实场景评估，让 Agent 分析结果并自我改进工具。

### 架构与可读性

**Agent 可读性（Legibility）是首要目标。** Agent 看不到的东西等同于不存在。

- **代码库为 Agent 而非人类优化可读性**：就像为新工程师提升代码可导航性一样，为 Agent 优化仓库结构。
- **"无聊"技术更适合 Agent**：组合性好、API 稳定、训练数据中代表充分的技术更容易被 Agent 建模。某些情况下重新实现子功能比依赖不透明的外部库更划算。
- **强制不变量，而非微管架实现**：例如要求"在边界处解析数据形状"，但不指定使用哪个具体库。Agent 在有严格边界和可预测结构的环境中最有效。
- **机械化执行 > Prompt 啰嗦**：自定义 linter 的错误消息注入修复指令到 Agent 上下文。人类感觉"过于严格"的规则，对 Agent 而言是乘数效应。
- **Worktree 隔离**：每个变更对应独立的 worktree，包含独立的应用实例、日志、指标——任务完成后销毁。

### Agent 模式选择

**从最简单方案开始，仅在有明确收益时增加复杂度。**

- **Workflow vs Agent**：Workflow 是通过预定义代码路径编排 LLM；Agent 是 LLM 动态指导自身流程和工具使用。
- **五种 Workflow 模式**：Prompt Chaining（顺序链）、Routing（路由分发）、Parallelization（并行/投票）、Orchestrator-Workers（编排-执行）、Evaluator-Optimizer（评估-优化循环）。
- **Agent-to-Agent 审查**：随着吞吐量增加，几乎所有审查工作可以由 Agent 之间相互完成，人类不再必须审查每个 PR。
- **吞吐量改变合并哲学**：在高吞吐环境中，修正成本低，等待成本高。最小化阻塞式合并门控，PR 保持短生命周期。

### 熵与技术债治理

**全 Agent 自主性带来的新问题：Agent 复制仓库中已有的模式——包括不良模式。**

- **"黄金原则"机械化**：将质量规则编码到仓库中，定期扫描偏差、更新质量评分、开修复 PR。
- **技术债是高利贷**：每日小额偿还优于积攒后痛苦清算。人类品味只需捕获一次，然后在每行代码上持续执行。
- **Doc Gardening Agent**：后台 Agent 定期扫描过时或不反映实际代码行为的文档，自动开修复 PR。

### MCP 与代码执行

**当工具数量增长，直接工具调用会淹没上下文。** 让 Agent 写代码调用工具而非直接调用：

- **工具定义按需加载**：将 MCP 工具呈现为文件系统上的代码文件，Agent 按需浏览和读取定义，而非预加载全部。实测可减少 98.7% 的 token 消耗。
- **执行环境内过滤**：中间结果在代码执行环境中处理后再返回模型，避免大量原始数据流经上下文。
- **隐私保护**：中间数据默认留在执行环境中，不进入模型上下文。可自动对 PII 做 tokenize/detokenize。
- **状态持久化与技能沉淀**：Agent 将可复用代码保存为函数/技能（Skills），配合 SKILL.md，逐步构建高层能力工具箱。

---

## 设计哲学

### 三个核心原则

**1. 仓库即唯一真相来源（Repo as SSOT）**
所有知识必须版本化、存储在仓库中。Agent 看不到的东西等同于不存在。架构决策写在 Slack 里、口头约定的规范、只存在聊天记录中的"为什么这样设计"——这些信息对 Agent 而言完全不可见。

**2. 目录式上下文（Context as Map, Not Encyclopedia）**
`AGENTS.md` 控制在 ~200 行，是一张**地图**而非百科全书。具体知识下沉到 `docs/` 的结构化文件中。当所有事情都标为重要，就没有什么重要。

**3. 机械化约束优于 Prompt 啰嗦**
核心规范靠 Linter/Test 强制执行，而非在 Prompt 中写 50 条"你应该如何写代码"。Linter 错误信息对 Agent 友好，含直接可执行的修复建议。

---

## 知识库结构

```
docs/
├── architecture.md          # 系统架构：模块划分、层级依赖、数据流
├── development.md           # 开发指南：环境搭建、构建命令、调试
├── workflow.md              # Skill 协调机制详解
├── harness-engineering.md   # 本文档：体系设计与参考
├── skill-and-harness-design.md # Skill 与 Harness 设计原则
├── domain/                  # 领域/模块专题文档
├── references/              # 外部依赖、集成、第三方参考
├── adr/                     # ADR 历史架构决策记录
├── exec-plans/              # 执行计划
│   ├── active/              # 进行中
│   └── completed/           # 已归档
└── specs/                   # 需求规格文档
```

**文档 YAML frontmatter（ADR 除外，普通 docs Concept 必须包含）：**

```yaml
---
type: Concept # 替换为能表达文档用途的非空类型
scope:
  - architecture
status: active # 按生命周期需要添加
---
```

验证运行状态由 `docs/.okf/verification.json` ledger 维护，不写入 Concept。ADR 是历史决策记录，使用 `type: Decision` 和 YAML `status` 表示生命周期。

---

## 体系组件

架构分层、Skill 清单和协调机制见：

- [系统架构](architecture.md) — 模块划分、依赖方向、Gate 机制
- [工作机制与 Skill 协调](workflow.md) — 各 Skill 职责、产出物流转、反模式

## 关键设计决策

所有历史架构决策已独立建档，见 [ADR 目录](adr/)。

核心决策概要：

| 决策                             | ADR                                                         |
| -------------------------------- | ------------------------------------------------------------ |
| Skill 作为执行单元，人类是决策者 | [ADR-0001](adr/0001-skill-as-execution-unit.md)             |
| 实现/修复一次性，Reviewer 同会话连续 | [ADR-0007](adr/0007-reviewer-session-continuity.md)         |
| 产出物作为协调介质               | [ADR-0003](adr/0003-artifacts-as-coordination.md)           |
| AGENTS.md 精简（≤200 行）        | [ADR-0004](adr/0004-lean-agents-md.md)                      |
| Gate 机制重构：规划 Gate + 实现自主 | [ADR-0006](adr/0006-gate-restructuring.md)                  |
