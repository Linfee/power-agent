# power-agent

Power-Agent 是面向前沿编码模型的 **Judgment + Verification + Domain Knowledge** pack。它融合 [superpowers](https://github.com/obra/superpowers) 的 Skill 思路与 [OpenAI Harness Engineering](https://openai.com/index/harness-engineering/) 的环境设计方法，但不把开发工作预绑为标准流水线。

## 核心理念

强模型不需要更多仪式，需要更清楚的承重判断：用户要得到什么、哪些事实会改变方案、哪些边界不能破坏，以及什么系统外证据足以验收。

Power-Agent 的 Skill 因此遵循：

- **判断可迁移，结果可验证**：过程可以不同，完成声明必须匹配新鲜证据。
- **独立能力优先**：普通 Skill 不要求另一个具名 Skill 先产生输入或后续接管。
- **工具与步骤由现场决定**：模型根据依赖、风险和写所有权选择工具、顺序、sub-agent 与并行度。
- **机械化优先**：schema、脚本、测试与 hook 处理确定性规则；Prompt 保留领域判断。
- **授权边界不弱化**：外部副作用、破坏性操作、权限、生产和敏感数据仍需要明确授权。

完整设计见 [ADR-0010](docs/adr/0010-judgment-oriented-skills.md)、[架构](docs/architecture.md) 与 [工作方式](docs/workflow.md)。

## Skills

| Skill | 独立解决的判断 |
|---|---|
| `discuss` | 需求、取舍和验收是否已经清楚 |
| `writing-plans` | 如何交付用户需要的计划，锁定必要依赖与验收 |
| `codebase-design` | 模块边界、接口、seam 和 adapter 是否真实降低复杂度 |
| `implement` | 如何组织 sub-agent 完成独立工作与集成 |
| `proof-oriented-development` | 实现中如何选择验收证据、控制风险或执行 TDD |
| `systematic-debugging` | 什么解释最符合观察，根因和修复边界在哪里 |
| `code-review` | 哪些问题会妨碍安全、正确交付 |
| `finish-development` | 证据是否足以完成，以及如何安全处置分支 |
| `writing-skills` | Skill 是否教会了可迁移判断 |
| `harness-engineering-review` | Harness 哪些机制承重，哪些可以删除 |
| `knowledge-navigation` | 如何结合项目观察、启发式讨论及历史反馈建立或优化知识导航（手动调用） |
| `setup-power-agent` | 如何补齐最小 Agent 入口与明确知识缺口 |
| `dev-docs` | 哪些稳定知识应写入项目文档 |
| `dev-docs-maintain` | 文档知识是否健康、新鲜且可验证 |

除 `setup-power-agent`、`dev-docs`、`dev-docs-maintain` 组成的知识维护子系统外，Skill 不存在强制命名依赖。知识子系统可在初始化、语义写入与机械维护之间按实际缺口协作，但也不形成固定链。

### 建立与优化知识导航

显式调用 [`knowledge-navigation`](skills/knowledge-navigation/SKILL.md)，可以从项目观察与启发式讨论开始初始化，也可以分析指定范围的对话历史和用户反馈，优化已有入口、索引、知识边界与来源关系。例如：

- “使用 knowledge-navigation，为当前仓库建立 Agent 知识导航。先观察项目，再和我讨论主要任务、权威知识位置和维护成本，随后完成初始化。”
- “使用 knowledge-navigation，结合本项目过去两周的可访问会话和这些反馈，找出重复阅读、知识过期或入口误导的原因，讨论必要取舍后修复。”

它复用仓库已有布局，按需读取参考材料，并明确历史覆盖与验证限度；不自动创建后台维护任务。与最小初始化、语义写入和健康扫描的边界见 [ADR-0011](docs/adr/0011-knowledge-navigation-lifecycle.md)。

## Sub-agent 支持

Power-Agent 假设宿主支持普通 sub-agent：能传入任务与上下文、并行处理独立工作并返回结果。它不使用 team mode、不规定并发数字，也不提供无 sub-agent fallback。

并行依据真实依赖与写所有权：独立调查可并行，共享接口和共享文件先明确契约或由单一整合者处理。子代理结果是待核验证据，不自动构成完成声明。

## 验证与分支处置

完成声明需要与当前结果匹配的新鲜系统外证据。验证可以在 dirty working tree 上运行；只有提交、PR、合并等 commit-bound 行为才需将证据绑定到具体提交。

`finish-development` 在用户要求时判断完成并协助安全处理 commit、PR、merge、保留或 discard。任何外部副作用或破坏性动作均在执行点遵守明确授权。

## 安装

### Droid

```bash
droid plugin marketplace add https://github.com/Linfee/power-agent
droid plugin install power-agent@power-agent --scope user
# 或通过 git 与项目共享
droid plugin install power-agent@power-agent --scope project
```

也可以在 `/plugins` 的 Browse 标签页安装。

### Claude Code

```bash
claude plugin marketplace add https://github.com/Linfee/power-agent
claude plugin install power-agent@power-agent --scope user
# 或通过 git 与项目共享
claude plugin install power-agent@power-agent --scope project
```

也可通过 `.claude-plugin/plugin.json` 从本地路径加载。

### Cursor、Factory 与 Gemini

- Cursor：使用 `.cursor-plugin/plugin.json`，或复制 `skills/` 内容。
- Factory：使用 `.factory-plugin/plugin.json`，或复制 `skills/` 内容。
- Gemini：使用 `gemini-extension.json`；它通过 `GEMINI.md` 加载 `AGENTS.md`。

## 开发与验证

修改 Skill 时先看 [Skill 与 Harness 设计指南](docs/skill-and-harness-design.md)，并以实际改动选择验证：

```bash
python3 scripts/check-description-length.py
bash scripts/check-invocation-consistency.sh
python3 scripts/check-skill-references.py
bash scripts/check-shared-references.sh
python3 -m unittest skills/dev-docs-maintain/scripts/test_bundle_status.py
```

最后两项仅在受影响时运行。更多维护约定见 [开发指南](docs/development.md)。

## 来源

- [superpowers](https://github.com/obra/superpowers) — Jesse Vincent (obra), MIT License
- [Harness Engineering](https://openai.com/index/harness-engineering/) — Ryan Lopopolo, OpenAI
