# power-agent

以 [Matt Pocock 的工程 Skills](https://github.com/mattpocock/skills) 为主干，融合 Power-Agent 的 POD、因果诊断、工程判断、项目知识与**授权内连续推进**。目标是少一点流程负担，不是少一点正确性和证据。

## 怎么用

直接描述结果即可：明确的小任务或已有 issue 直接实现；目标不清才讨论；存在任务依赖或恢复需求才使用 spec/tickets。在已选执行路径内，模型按需组合自动能力，不需要用户逐步接力；下表标记的手动 Skill 仅在用户显式调用时进入。

可自动验证的行为变更默认红绿重构。完成实现后继续取得匹配证据、处理适用审查和修复；只请求讨论、建议、草稿时不越界实施或发布。commit、push、PR、merge、秘密/权限与生产变更仍由具体授权控制。

跨任务的[最小完整改动默认规则](skills/codebase-design/references/minimal-complete-change.md)帮助 Agent 解决已授权的问题，避免为假想需求增加抽象；它不牺牲正确性、必要验证或安全边界。它与 25 个 Skill 随同一插件或包交付，由 hook、扩展或 Cursor 插件自带规则加载；这不同于按需调用的 `codebase-design` Skill。

25 个 Skill **整包分发**：17 个允许模型调用、8 个仅手动调用，见下表。`implement`、`implement-spec` 及其依赖保持自动可达；任何 Skill 都不能自动调用手动入口或读取其正文绕过限制。`grilling` 保留原版逐轮问题树与共同理解确认，确认前不实施。不承诺单独安装。宿主必须支持普通 sub-agent；独立工作可以使用新上下文并行，共享写入由唯一协调者处理。执行状态只存选定 tracker，知识和交接不另建进度副本。

## Skills

| Skill | 负责的结果 |
|---|---|
| [`proof-oriented-development`](skills/proof-oriented-development/SKILL.md) | 以红绿重构默认实现行为，并选择覆盖真实风险的证据 |
| [`code-review`](skills/code-review/SKILL.md) | 对照需求与工程质量，找出有证据的交付问题 |
| [`diagnosing-bugs`](skills/diagnosing-bugs/SKILL.md) | 用区分性证据定位根因，而非猜补丁 |
| [`codebase-design`](skills/codebase-design/SKILL.md) | 判断模块深度、资源责任与接口是否降低复杂度 |
| [`grilling`](skills/grilling/SKILL.md) | 按问题树逐轮追问，直到用户确认共同理解 |
| [`grill-with-docs`](skills/grill-with-docs/SKILL.md) | 手动调用；组合原版 grilling 与 domain-modeling |
| [`domain-modeling`](skills/domain-modeling/SKILL.md) | 复用术语真源，维护领域边界与值得记录的决定 |
| [`to-spec`](skills/to-spec/SKILL.md) | 手动调用；将目标整理成可交付、可验收的 spec |
| [`to-tickets`](skills/to-tickets/SKILL.md) | 手动调用；按垂直结果与真实依赖拆分可执行工作 |
| [`implement`](skills/implement/SKILL.md) | 从明确任务或现成 issue 连续完成实现、验证和修复 |
| [`implement-spec`](skills/implement-spec/SKILL.md) | 从唯一 tracker 调度任务图并验收组合结果 |
| [`triage`](skills/triage/SKILL.md) | 手动调用；识别请求的范围、重复、信息缺口与可执行性 |
| [`wayfinder`](skills/wayfinder/SKILL.md) | 手动调用；把复杂目标中的决定与可执行工作分开推进 |
| [`improve-codebase-architecture`](skills/improve-codebase-architecture/SKILL.md) | 手动调用；从实际摩擦找到值得深化的模块边界 |
| [`research`](skills/research/SKILL.md) | 用匹配版本的一手来源解决技术未知 |
| [`prototype`](skills/prototype/SKILL.md) | 用可运行逻辑或真实画面回答设计问题 |
| [`pr`](skills/pr/SKILL.md) | 根据真实 diff 与证据起草 PR，按明确授权发布 |
| [`wizard`](skills/wizard/SKILL.md) | 为确需人工输入或批准的配置生成安全脚本 |
| [`handoff`](skills/handoff/SKILL.md) | 手动调用；携带目标、证据与状态真源指针，不复制进度 |
| [`writing-for-agents`](skills/writing-for-agents/SKILL.md) | 编写能改变 Agent 判断、按需可达的指令与 Skill |
| [`retro`](skills/retro/SKILL.md) | 手动调用；从会话或项目材料改进环境，而非堆叠禁令 |
| [`dev-docs`](skills/dev-docs/SKILL.md) | 按项目协议保存稳定知识，不强制引入 Bundle |
| [`dev-docs-maintain`](skills/dev-docs-maintain/SKILL.md) | 扫描、核对知识并安全登记实际验证 |
| [`knowledge-navigation`](skills/knowledge-navigation/SKILL.md) | 按真实任务建立或改善知识检索路径 |
| [`setup-power-agent`](skills/setup-power-agent/SKILL.md) | 最小补齐 Agent 入口与选定的 tracker/领域指针 |

## 安装

### Claude Code

```bash
claude plugin marketplace add https://github.com/Linfee/power-agent
claude plugin install power-agent@power-agent --scope user
# 或作为项目共享配置
claude plugin install power-agent@power-agent --scope project
```

本地加载使用 `claude --plugin-dir /absolute/path/to/power-agent`。本仓库包含 marketplace catalog 与 `.claude-plugin/plugin.json`；catalog 校验不等于所有宿主的运行验收。

### Droid

```bash
droid plugin marketplace add https://github.com/Linfee/power-agent
droid plugin install power-agent@power-agent --scope user
# 或作为项目共享配置
droid plugin install power-agent@power-agent --scope project
```

### pi、OMP、Codex 与 Cursor

pi 可通过 `pi install git:github.com/Linfee/power-agent` 安装整个包。OMP、Codex 和 Cursor 也使用各自的插件或包入口安装本仓库；具体步骤、版本与信任条件见[宿主兼容性](skills/setup-power-agent/references/agent-compatibility.md)。Cursor 的插件需通过可用的 marketplace 安装，或使用其本地插件开发入口；不能假定本仓库已经上架。

六种宿主的安装均不需要向业务项目复制规则或运行项目配置器。实际规则送达、Skill 发现和子代理能力分别受宿主版本及启用状态影响；manifest 存在不等于运行验证。

## 开发与验证

见 [开发指南](docs/development.md) 与 [Skill 设计指南](docs/skill-and-harness-design.md)。常用入口：

```bash
python3 scripts/check-description-length.py
bash scripts/check-invocation-consistency.sh
python3 scripts/check-skill-references.py
node --test tests/*.test.cjs
node scripts/sync-plugin-rules.cjs --check
python3 -m unittest skills/dev-docs-maintain/scripts/test_bundle_status.py
```

最后一项在知识工具受影响时运行；脚本与行为改动另选直接验证，不把引用可达当作运行成功。

## 设计与来源

当前分工见 [架构](docs/architecture.md)、[工作方式](docs/workflow.md)、[ADR-0013](docs/adr/0013-skill-invocation-and-hook-boundaries.md)。[ADR-0012](docs/adr/0012-matt-led-skill-fusion.md) 与[正式设计](docs/specs/2026-11-11-matt-power-agent-fusion.md)保留融合来源、判断、取舍与验收背景。

- Matt Pocock Skills，MIT，固定来源 `4ae2317ddb22b046e26455e4f9c9b3aaaf62212d`。
- [superpowers](https://github.com/obra/superpowers)，Jesse Vincent，MIT。
- [Ponytail](https://github.com/DietrichGebert/ponytail/tree/96608e078b2d5ea607c5c3b8b5a54d1c1fba6846) v5.3.3，DietrichGebert，MIT；借鉴最小改动与宿主集成，不需要单独安装 Ponytail。
- PR 视觉表达保留 Dex Horthy / HumanLayer `show-me` 的署名与 MIT notice。
- [Harness Engineering](https://openai.com/index/harness-engineering/) 为方法参考，不作为 MIT 软件来源。

许可见 [LICENSE](LICENSE)，第三方完整许可与归属见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。
