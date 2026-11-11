# power-agent

以 [Matt Pocock 的工程 Skills](https://github.com/mattpocock/skills) 为主干，融合 Power-Agent 的 POD、因果诊断、工程判断、项目知识与**授权内连续推进**。目标是少一点流程负担，不是少一点正确性和证据。

## 怎么用

直接描述结果即可：明确的小任务或已有 issue 直接实现；目标不清才讨论；存在任务依赖或恢复需求才使用 spec/tickets。模型按需组合能力，不需要用户每一步手工接力。

可自动验证的行为变更默认红绿重构。完成实现后继续取得匹配证据、处理适用审查和修复；只请求讨论、建议、草稿时不越界实施或发布。commit、push、PR、merge、秘密/权限与生产变更仍由具体授权控制。

25 个 Skill **整包分发、均可模型调用**，内部允许具名依赖，不承诺单独安装。宿主必须支持普通 sub-agent；独立工作可以使用新上下文并行，共享写入由唯一协调者处理。执行状态只存选定 tracker，知识和交接不另建进度副本。

## Skills

| Skill | 负责的结果 |
|---|---|
| [`proof-oriented-development`](skills/proof-oriented-development/SKILL.md) | 以红绿重构默认实现行为，并选择覆盖真实风险的证据 |
| [`code-review`](skills/code-review/SKILL.md) | 对照需求与工程质量，找出有证据的交付问题 |
| [`diagnosing-bugs`](skills/diagnosing-bugs/SKILL.md) | 用区分性证据定位根因，而非猜补丁 |
| [`codebase-design`](skills/codebase-design/SKILL.md) | 判断模块深度、资源责任与接口是否降低复杂度 |
| [`grilling`](skills/grilling/SKILL.md) | 查清事实，只询问会改变方案的取舍 |
| [`grill-with-docs`](skills/grill-with-docs/SKILL.md) | 将已确认的讨论结论保存到正确知识位置 |
| [`domain-modeling`](skills/domain-modeling/SKILL.md) | 复用术语真源，维护领域边界与值得记录的决定 |
| [`to-spec`](skills/to-spec/SKILL.md) | 将目标整理成可交付、可验收的 spec |
| [`to-tickets`](skills/to-tickets/SKILL.md) | 按垂直结果与真实依赖拆分可执行工作 |
| [`implement`](skills/implement/SKILL.md) | 从明确任务或现成 issue 连续完成实现、验证和修复 |
| [`implement-spec`](skills/implement-spec/SKILL.md) | 从唯一 tracker 调度任务图并验收组合结果 |
| [`triage`](skills/triage/SKILL.md) | 识别请求的范围、重复、信息缺口与可执行性 |
| [`wayfinder`](skills/wayfinder/SKILL.md) | 把复杂目标中的决定与可执行工作分开推进 |
| [`improve-codebase-architecture`](skills/improve-codebase-architecture/SKILL.md) | 从实际摩擦找到值得深化的模块边界 |
| [`research`](skills/research/SKILL.md) | 用匹配版本的一手来源解决技术未知 |
| [`prototype`](skills/prototype/SKILL.md) | 用可运行逻辑或真实画面回答设计问题 |
| [`pr`](skills/pr/SKILL.md) | 根据真实 diff 与证据起草 PR，按明确授权发布 |
| [`wizard`](skills/wizard/SKILL.md) | 为确需人工输入或批准的配置生成安全脚本 |
| [`handoff`](skills/handoff/SKILL.md) | 携带目标、证据与状态真源指针，不复制进度 |
| [`writing-for-agents`](skills/writing-for-agents/SKILL.md) | 编写能改变 Agent 判断、按需可达的指令与 Skill |
| [`retro`](skills/retro/SKILL.md) | 从会话或项目材料改进环境，而非堆叠禁令 |
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

### 其他宿主

Cursor、Factory 分别提供 `.cursor-plugin/plugin.json`、`.factory-plugin/plugin.json`。也可把整个 `skills/` 内容放入宿主支持的技能加载位置，保持各目录相邻，不能只复制一个入口。具体加载方式和 sub-agent 能力以目标宿主为准。

`gemini-extension.json` 仅通过 `GEMINI.md` 引用项目入口；它本身不证明 25 个 Skill 已安装或具名调用可用。需单独配置整包发现并验证宿主能力。

## 开发与验证

见 [开发指南](docs/development.md) 与 [Skill 设计指南](docs/skill-and-harness-design.md)。常用入口：

```bash
python3 scripts/check-description-length.py
bash scripts/check-invocation-consistency.sh
python3 scripts/check-skill-references.py
python3 -m unittest skills/dev-docs-maintain/scripts/test_bundle_status.py
```

最后一项在知识工具受影响时运行；脚本与行为改动另选直接验证，不把引用可达当作运行成功。

## 设计与来源

当前分工见 [架构](docs/architecture.md)、[工作方式](docs/workflow.md)、[ADR-0012](docs/adr/0012-matt-led-skill-fusion.md)。[正式设计](docs/specs/2026-11-11-matt-power-agent-fusion.md)列出每项来源、保留判断、融合/删除与验收。

- Matt Pocock Skills，MIT，固定来源 `4ae2317ddb22b046e26455e4f9c9b3aaaf62212d`。
- [superpowers](https://github.com/obra/superpowers)，Jesse Vincent，MIT。
- PR 视觉表达保留 Dex Horthy / HumanLayer `show-me` 的署名与 MIT notice。
- [Harness Engineering](https://openai.com/index/harness-engineering/) 为方法参考，不作为 MIT 软件来源。

许可见 [LICENSE](LICENSE)，第三方完整许可与归属见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。
