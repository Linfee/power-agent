---
type: Playbook
scope:
  - development
---

# 开发指南

## 项目概述

Power-Agent 是以 Markdown Skill、项目知识和确定性脚本构成的 Agent harness pack。它支持 Codex、Claude Code、Cursor、Factory、Droid、Gemini 与具备普通 sub-agent 能力的同类宿主。

## 项目结构

```text
power-agent/
├── skills/                   # 独立能力与知识维护子系统
│   └── <skill-name>/
│       ├── SKILL.md
│       ├── agents/openai.yaml # Codex 调用策略等可选元数据
│       ├── references/       # 低频专门知识或机器协议（按需）
│       └── scripts/          # 确定性操作（按需）
├── docs/                     # 长期工程与知识系统
│   ├── adr/                  # 历史决策
│   ├── exec-plans/           # 仅需要持久计划时使用
│   └── .okf/                 # scanner / verification ledger
├── scripts/                  # 仓库级结构检查
├── AGENTS.md                 # 快速地图
├── CLAUDE.md / GEMINI.md     # 宿主入口
└── *-plugin/                 # 插件清单
```

## 修改 Skill

先确认改动填补了可观察的行为缺口。Skill 应说明什么值得判断、哪些事实改变决策、要保护什么边界、什么证据足以验收；不要把工具顺序、子代理数量、固定章节或状态枚举写成无消费者的流程。

最小 `SKILL.md` 形式：

```markdown
---
name: [skill-name]
description: |-
  [该 Skill 的独特判断能力。]
  Triggers: [实际触发词]
---

# [Skill 标题]

[以领域自然组织的判断指南、边界与验收。]
```

`description` 只服务触发，主体承担判断。新增 reference 前确认其是低频且不可由通用模型稳定恢复的专门知识；可机械执行的检查、转换、扫描或原子写入优先实现为脚本。

除 `setup-power-agent`、`dev-docs`、`dev-docs-maintain` 外，Skill 不应要求另一个具名 Skill 生成输入或接管完成。知识子系统可以按实际缺口互相使用，但同样不形成固定链。

修改后检查受影响的 trigger、仓库索引、references、脚本和文档。按改动选择验证：

- 所有 description 改动：`python3 scripts/check-description-length.py`
- 调用方式、Skill 目录或名称改动：`bash scripts/check-invocation-consistency.sh`（核对速查表、frontmatter 与 Codex `agents/openai.yaml`；手动调用在 Codex 中须为 `policy.allow_implicit_invocation: false`）
- 入口、Markdown 链接/标题或 Skill 脚本指针改动：`python3 scripts/check-skill-references.py`；可传文件或目录限定范围，改检查器时运行 `python3 scripts/test-check-skill-references.py`。
- 共享 Knowledge Bundle reference 改动：`bash scripts/check-shared-references.sh`
- 文档 scanner/ledger 改动：`python3 -m unittest skills/dev-docs-maintain/scripts/test_bundle_status.py`
- 任意脚本：运行直接覆盖其行为的测试或场景

精简或路由变化需要行为对照时，选能暴露已知失败的任务，在相同模型、工具、授权和验收下比较基础 harness、当前版与候选版。保存输入、版本、执行轨迹和结果；以实际行为和安全边界验收，记录实际加载范围，不能把目录匹配或显式读取称为宿主自动触发验证。方法见 [writing-skills 的行为对照](../skills/writing-skills/references/criteria.md#行为对照)，无需为普通文字修改固定运行整套实验。

引用检查器只读核对本地链接、Markdown 锚点和明确的 Skill 脚本指针；远程 URL、示例和模板占位不联网或执行。默认略过归档与 superseded 文档的正文，显式路径可检查历史；内部软链接可用，仓库外目标拒绝读取。支持范围与参数见 [检查器](../scripts/check-skill-references.py) 的 `--help`，结构通过不代表语义正确。

## Sub-agent 协作

宿主提供普通 sub-agent 的任务传入、上下文传递和结果收集。并行取决于依赖与写所有权：独立的工作可以并行，竞争同一文件、接口或状态时指定唯一整合者或串行。不要添加 team mode、固定并发数字或无 sub-agent fallback。

子代理报告是待核验证据。整合者必须检查其是否覆盖任务、是否与当前工作树一致，以及最终行为是否已通过实际验证。

## 文档规范

`docs/` 中除 `index.md`、`log.md` 外的 Concept 应包含非空 `type`：

```yaml
---
type: Concept
scope:
  - src/area/**
status: active # 仅有生命周期语义时添加
---
```

运行时验证状态保存在 `docs/.okf/verification.json`，不迁入 Concept。ADR 使用 `type: Decision` 与 `accepted`、`proposed`、`superseded` 等状态；被替代的 ADR 必须有可解析的 `superseded_by`，新 ADR 用 `supersedes` 反向指向它。

| 类型 | 格式 |
|---|---|
| Skill 主文件 | `SKILL.md` |
| ADR | `NNNN-slug.md` |
| Spec | `YYYY-MM-DD-topic.md` |
| Exec-plan 目录 | `YYYY-MM-DD-title/` |

## 验证与授权

完成声明必须有新鲜、可复现、与改动风险匹配的证据。可在 dirty working tree 验证；只有 commit、PR、merge 等 commit-bound 动作才需要绑定提交。

提交、push、PR、merge、discard、删除、生产或权限修改均须遵守明确授权。测试通过不授权外部副作用，也不替代安全、数据或兼容性边界的专门验证。
