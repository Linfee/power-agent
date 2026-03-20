# power-agent

融合两套互补方法论的 AI 编码 Agent 工作流系统：

- **[superpowers](https://github.com/obra/superpowers)**（当前追踪版本 **v5.0.5**）— 面向 AI Agent 的完整软件开发 Skill 体系
- **[Harness Engineering](https://openai.com/index/harness-engineering/)**（Ryan Lopopolo, OpenAI, 2026 年 2 月）— OpenAI 关于在工程工作流中运用 AI Agent 的方法论

两者结合，形成一套完整、有主张的工作流：结构化设计探索 → TDD 驱动的执行计划 → 子代理并行实现 → 系统化调试 → 文档维护。

---

## 核心理念

**人类掌舵，Agent 执行。** 人类负责设计意图、构建反馈循环；Agent 负责执行闭环。所有决策必须在仓库中版本化——Agent 看不到的内容等同于不存在。

来自 Harness Engineering 的三个核心原则：

1. **仓库是唯一真相来源（Repo as SSOT）** — 所有知识必须版本化。Agent 看不到的东西不存在。
2. **上下文是地图而非百科全书** — `AGENTS.md` 是导航索引（约 150 行），而非 Wiki。
3. **机械化约束优于冗长 Prompt** — Linter/Test 规则胜过大篇幅的指令说明。

---

## Skills 一览

| Skill | 用途 |
|-------|------|
| `feature-dev` | 八阶段引导式功能开发（薄编排层，串联其他所有 Skill） |
| `discuss` | 编码前的设计探索——含 2-3 方案对比和 Spec 审查循环，产出经批准的 spec 文档 |
| `writing-plans` | 将 spec/设计转化为 TDD 结构的 exec-plan，含完整代码片段 |
| `exec-plan-runner` | 通过一次性子代理并行批次执行 exec-plan，含两阶段代码审查 |
| `dev-docs` | 文档路由器——exec-plan 委派给 `writing-plans`，其他文档类型直接处理 |
| `dev-docs-maintain` | 文档维护（Doc Gardening）——扫描并修复重大功能完成后的过期文档 |
| `init-harness-engineering` | 从零为项目建立 Harness Engineering 知识体系 |
| `systematic-debugging` | 四阶段根因优先调试（先找根本原因，再动手修复） |
| `test-driven-development` | RED-GREEN-REFACTOR 执行强制，含反模式参考 |
| `requesting-code-review` | 通过子代理编排代码审查，输出结构化发现 |
| `receiving-code-review` | 技术性评估审查反馈（非表演性同意） |
| `verification-before-completion` | 证据优先验证——没有新鲜证据不得声称完成 |
| `dispatching-parallel-agents` | 将独立任务调度为并行子代理 |
| `harness-engineering-review` | 对照 Harness Engineering 最佳实践审查项目 Agent 工作流 |

### 完整工作流

```
discuss skill          ← 可选：设计探索 → spec 文档
    ↓（spec 批准后）
feature-dev skill
    ├── 阶段 1-3：上下文建立 + 代码库探索 + 澄清（人工确认）
    ├── 阶段 4：架构设计（人工选方案）
    ├── 阶段 5：writing-plans skill → exec-plan
    ├── 阶段 6：exec-plan-runner skill（TDD 子代理，并行）
    ├── 阶段 7：requesting-code-review skill
    └── 阶段 8：dev-docs-maintain skill

Bug / 测试失败 → systematic-debugging skill
                     └── → test-driven-development + verification-before-completion
```

详细的 Skill 协调机制见 [docs/workflow.md](docs/workflow.md)。

---

## 安装

### 作为 Droid 插件（推荐）

```bash
# 将此仓库添加为 marketplace
droid plugin marketplace add https://github.com/your-org/power-agent

# 安装插件（user 作用域——跨项目可用）
droid plugin install power-agent@power-agent --scope user

# 或 project 作用域——通过 git 与团队共享
droid plugin install power-agent@power-agent --scope project
```

也可通过交互界面：`/plugins` → Browse 标签页。

### 作为 Claude Code 插件

```bash
# 将此仓库添加为 marketplace
claude plugin marketplace add https://github.com/your-org/power-agent

# 安装插件（user 作用域——跨项目可用）
claude plugin install power-agent@power-agent --scope user

# 或 project 作用域——通过 git 与团队共享
claude plugin install power-agent@power-agent --scope project
```

也可手动安装：将项目目录复制到本地后，通过 Claude Code 插件管理器从本地路径加载（`.claude-plugin/plugin.json` 格式与 Droid 互通）。

### 作为 Cursor 插件

使用 `.cursor-plugin/plugin.json`，通过 Cursor 插件管理器安装，或手动将 `skills/` 目录内容复制到项目中。

### 手动安装（独立使用）

将 `skills/` 目录复制到 `~/.factory/skills/`（个人全局）或项目的 `.factory/skills/`（项目级）：

```bash
cp -r skills/* ~/.factory/skills/
```

---

## 版本追踪

本项目持续追踪上游变更：

| 上游项目 | 当前追踪版本 | 来源 |
|----------|------------|------|
| superpowers | v5.0.5 | https://github.com/obra/superpowers |
| Harness Engineering | 2026 年 2 月 | https://openai.com/index/harness-engineering/ |

当 superpowers 发布新版本时，查阅 CHANGELOG 并将相关改进移植到本项目。

---

## 致谢与灵感来源

本项目基于以下工作构建：

- **superpowers** by [Jesse Vincent (obra)](https://github.com/obra/superpowers) — MIT License。当前追踪 **v5.0.5**。以下 Skill 派生自 superpowers：`discuss`（来自 `brainstorming`）、`writing-plans`、`exec-plan-runner`（融合了 `subagent-driven-development`）、`test-driven-development`、`requesting-code-review`、`receiving-code-review`、`verification-before-completion`、`dispatching-parallel-agents`、`systematic-debugging`。

- **Harness Engineering** — [Ryan Lopopolo，OpenAI，2026 年 2 月 11 日](https://openai.com/index/harness-engineering/)。`harness-engineering-review`、`init-harness-engineering`、`dev-docs`、`dev-docs-maintain` Skill 以及"仓库即唯一真相来源"的整体设计哲学源于该方法论。
