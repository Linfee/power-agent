# power-agent

个人使用的工程 Skill 清单。

从多个开源 Agent Skill 项目中选择、改写和组合，按既定工程习惯沉淀成一套可按需加载的 Skills：实现、诊断、设计、审查、交付、文档。不是通用框架、团队规范或开箱即用产品；默认服务于个人工作流。

## 取舍

- 小任务直接做。只有依赖、恢复或协作确有需要时，才用 spec、tickets 或地图。
- 行为变更先 Red/Green；重构留到 review 阶段，在行为覆盖更完整时进行。
- 诊断先建立能变红、能断言所报症状的反馈环，再提假设。
- 审查默认把需求与工程质量分别交给独立 reviewer；实现路径由 `implement` / `implement-spec` 驱动 review–fix 循环，只有明确要求时才合并两维。
- 自动调用按需触发；标为“手动”的入口只在显式调用时进入。方向、范围、取舍和验收不因自动调用而转移。
- 文档写入项目现有的权威位置；不把会话记录、执行计划或临时结论当长期知识。
- 能自动调用不等于有权提交、推送、发布、删除或改生产；这些仍按具体授权。

## 怎么用

直接描述要完成的结果。自动 Skill 按需触发；手动入口只在显式调用时进入。没有固定阶段链；实现入口驱动 review–fix 循环收敛，纯机械改动可跳过。

常见入口示例，不是固定顺序：

- 明确的小任务或已有 issue → `implement`；需要证明行为时由 `proof-oriented-development` 选择证据。
- 原因不明的问题 → `diagnosing-bugs`；先建立反馈环，再定位根因。
- 目标不清或方案有分歧 → `grilling`；需要领域文档时用 `grill-with-docs`。
- 需要可交付计划 → `to-spec` / `to-tickets`；复杂目标先 `wayfinder`。
- 要比较设计或架构 → `codebase-design` / `improve-codebase-architecture`；需要真实画面或逻辑时用 `prototype`。
- 实现完成 → `code-review`；需要交付说明时用 `pr`。

## Skills

24 个 Skill，14 个允许模型调用，10 个仅手动调用。

### 实现与修复

| Skill | 用途 | 调用 |
|---|---|---|
| [`proof-oriented-development`](skills/proof-oriented-development/SKILL.md) | 用 Red/Green 和匹配证据实现行为变更 | 自动 |
| [`diagnosing-bugs`](skills/diagnosing-bugs/SKILL.md) | 用区分性证据定位根因；先建立会变红的反馈环 | 自动 |
| [`implement`](skills/implement/SKILL.md) | 从明确任务或现有 issue 连续完成实现、验证、驱动默认 review–fix 循环和修复 | 自动 |
| [`implement-spec`](skills/implement-spec/SKILL.md) | 按 tracker 中的任务图调度独立切片、驱动审查并验收组合结果 | 自动 |

### 目标、设计与调查

| Skill | 用途 | 调用 |
|---|---|---|
| [`grilling`](skills/grilling/SKILL.md) | 按问题树逐轮追问，直到共同理解被确认 | 自动 |
| [`grill-with-docs`](skills/grill-with-docs/SKILL.md) | 组合 grilling 与 domain-modeling，用于需要文档和领域语境的讨论 | 手动 |
| [`domain-modeling`](skills/domain-modeling/SKILL.md) | 维护术语、上下文边界和值得记录的 ADR | 自动 |
| [`to-spec`](skills/to-spec/SKILL.md) | 把目标整理成可交付、可验收的 spec | 手动 |
| [`to-tickets`](skills/to-tickets/SKILL.md) | 按垂直结果和真实依赖拆分工作 | 手动 |
| [`triage`](skills/triage/SKILL.md) | 判断请求的范围、重复、信息缺口和可执行性 | 手动 |
| [`wayfinder`](skills/wayfinder/SKILL.md) | 把复杂目标中的决定与可执行工作分开推进 | 手动 |
| [`codebase-design`](skills/codebase-design/SKILL.md) | 判断模块深度、资源责任和接口是否真的降低复杂度 | 自动 |
| [`improve-codebase-architecture`](skills/improve-codebase-architecture/SKILL.md) | 从实际摩擦找值得深化的模块边界，输出候选报告 | 手动 |
| [`research`](skills/research/SKILL.md) | 用匹配版本的一手来源解决技术未知 | 自动 |
| [`prototype`](skills/prototype/SKILL.md) | 用单文件逻辑原型或真实 UI 变体回答设计问题 | 自动 |

### 审查与交付

| Skill | 用途 | 调用 |
|---|---|---|
| [`code-review`](skills/code-review/SKILL.md) | 按需求与工程两维审查变更，给出可定位证据 | 自动 |
| [`pr`](skills/pr/SKILL.md) | 根据真实 diff 和证据起草 PR，发布需要授权 | 自动 |
| [`wizard`](skills/wizard/SKILL.md) | 为需要人工输入或批准的配置生成安全脚本 | 自动 |
| [`handoff`](skills/handoff/SKILL.md) | 把目标、证据和权威状态指针交给下一位 | 手动 |

### 知识与元技能

| Skill | 用途 | 调用 |
|---|---|---|
| [`dev-docs`](skills/dev-docs/SKILL.md) | 写入、修订和核验长期开发知识 | 自动 |
| [`knowledge-navigation`](skills/knowledge-navigation/SKILL.md) | 设计或演进仓库知识检索路径 | 手动 |
| [`writing-for-agents`](skills/writing-for-agents/SKILL.md) | 编写能改变 Agent 判断的 Skill、AGENTS.md 和引用材料 | 自动 |
| [`retro`](skills/retro/SKILL.md) | 从会话或项目材料改进 Harness，而不是堆禁令 | 手动 |
| [`setup-power-agent`](skills/setup-power-agent/SKILL.md) | 最小补齐项目 Agent 入口、tracker 和领域指针 | 手动 |

## 安装

整包安装，不承诺单个 Skill 独立运行。宿主步骤、版本与信任条件见 [宿主兼容性](docs/agent-compatibility.md)。

### Claude Code

```bash
claude plugin marketplace add https://github.com/Linfee/power-agent
claude plugin install power-agent@power-agent --scope user
# 或作为项目共享配置
claude plugin install power-agent@power-agent --scope project
```

仓库包含 marketplace catalog 与 `.claude-plugin/plugin.json`；安装后在新会话确认插件、hook 与 Skill 的实际加载状态。catalog 校验不等于所有宿主的运行验收。

### Codex

```bash
codex plugin marketplace add Linfee/power-agent
codex plugin add power-agent@power-agent
```

安装后启动新会话；桌面应用的 Plugins 页面可查看启用状态。非托管 hook 须在 `/hooks` 审核并信任，定义变更后重新审核。IDE 扩展不支持插件；marketplace 注册成功不等于 Skill 或规则已送达。

### OMP

```bash
omp plugin install github:Linfee/power-agent
omp plugin list
```

安装写宿主配置，并在新会话初始化扩展；`omp plugin list` 可确认插件已登记并启用。

### pi

```bash
pi install git:github.com/Linfee/power-agent
# 项目范围安装；--approve 确认信任该项目
pi install git:github.com/Linfee/power-agent --local --approve
```

`pi list --approve` 查看包含项目设置的包。个人范围写宿主设置，`--local` 写项目设置；项目包仅在宿主信任项目后加载。

### Cursor

Cursor 的个人安装入口是 Marketplace：在 **Customize** 中搜索并安装 Power-Agent；是否上架以目标版本为准，公开 Git 仓库本身不能作为个人插件源直接安装。

团队或企业计划可由管理员在 **Dashboard → Plugins & MCPs → Import from Repo** 导入 `https://github.com/Linfee/power-agent`，再在 Customize 安装。插件内 `disable-model-invocation: true` 的 Skill 在部分版本会从命令菜单消失，须按目标版本实测。

### Droid

```bash
droid plugin marketplace add https://github.com/Linfee/power-agent
droid plugin install power-agent@power-agent --scope user
# 或作为项目共享配置
droid plugin install power-agent@power-agent --scope project
```

## 开发与验证

维护方式与清单本身一致：先确认行为缺口，再改 Skill，最后跑结构检查和必要的真实场景。见 [开发指南](docs/development.md) 与 [Skill 设计指南](docs/skill-and-harness-design.md)。

```bash
python3 scripts/check-description-length.py
bash scripts/check-invocation-consistency.sh
python3 scripts/check-skill-references.py
node --test tests/*.test.cjs
node scripts/sync-plugin-rules.cjs --check
```

脚本与行为改动另选直接验证，不把引用可达当作运行成功。

## 状态

个人使用，持续调整；不承诺稳定 API、向后兼容或适合所有团队。Skill 数量、调用方式和正文都可能变化。当前基线见 [ADR-0014](docs/adr/0014-current-baseline.md)；旧 ADR 编号与历史记录由 Git 历史保留，归档正文已移除，不作为现行指令。

## 来源与许可

不是从零设计，主要参考以下开源项目和方法：

- [Matt Pocock Skills](https://github.com/mattpocock/skills)，MIT，固定来源 `4ae2317ddb22b046e26455e4f9c9b3aaaf62212d`。
- [superpowers](https://github.com/obra/superpowers)，Jesse Vincent，MIT。
- [Ponytail](https://github.com/DietrichGebert/ponytail/tree/96608e078b2d5ea607c5c3b8b5a54d1c1fba6846) v5.3.3，DietrichGebert，MIT；借鉴最小改动与宿主集成，不需要单独安装 Ponytail。
- PR 视觉表达保留 Dex Horthy / HumanLayer `show-me` 的署名。
- [Harness Engineering](https://openai.com/index/harness-engineering/) 为方法参考，不作为 MIT 软件来源。

逐 Skill 的来源和取舍已随归档移除，可在 Git 历史中检索；第三方许可见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。许可条款见 [LICENSE](LICENSE)。
