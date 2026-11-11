---
name: setup-power-agent
description: 初始化项目 Agent 入口、配置所选 issue tracker 或为现有项目知识补齐明确缺口时使用；整体知识导航设计与历史反馈分析不属于此项。
---

# 配置项目 Agent 入口

只补影响当前 Agent 工作的缺口。先识别宿主实际加载链、现有入口、构建与验证命令、知识位置和 tracker；从项目证据确定内容，保留已有编辑。已有 `AGENTS.md` 是权威入口、`CLAUDE.md`/`GEMINI.md` 转引它时，只更新 AGENTS，不向指针文件复制另一套规则。入口只链接实际存在的项目资料及实际安装位置可定位的 Skill，不假设业务仓库有 `skills/`。缺少配置也不阻塞普通实现与审查。

复用已有 glossary/CONTEXT、ADR 和知识导航，不预建空文档。领域与决策缺口见[领域指针](references/domain-docs.md)；具体语义由 `domain-modeling` 负责，采用 Bundle 时写入格式按 `dev-docs` 的 profile。普通 docs 不强制 Bundle 或 ledger；Bundle 中生成的 `docs/agents/*.md` 同样须有非空 `type`，不能原样写入无 frontmatter 的 seed。

## 选择 tracker 并写入项目配置

仅在需要 tracker 配置或用户要求时，优先沿用项目实际选用的 GitHub、GitLab 或本地后端；证据不能确定真实后端时才询问。沿用已有配置位置，无约定时写 `docs/agents/issue-tracker.md`。按实际后端选择本 Skill **安装目录**内唯一对应 seed，替换为项目真实位置、版本与操作约定：

- [GitHub](references/issue-tracker-github.md)
- [GitLab](references/issue-tracker-gitlab.md)
- [本地文件](references/issue-tracker-local.md)

仅在需要时生成 [triage 标签角色](references/triage-labels.md)或[领域资料指针](references/domain-seed.md)，分别写入现有约定位置或 `docs/agents/triage-labels.md`、`docs/agents/domain.md`。映射现有分诊、ready 和对象类型角色；不盲建标签，不假设未配置标签存在。现有约定足够时不生成重复文件。

项目配置应写清后端、目标、读取/创建/更新约定、关系的唯一真源、已有状态及授权边界。命令只在核对本机 CLI 版本、帮助与必要官方契约后写成项目可用操作，源 seed 不保证任意版本可执行；native 关系不可用时按同一 tracker 的固定正文位置记录。远端写入、labels、权限、初始化 git/remote、用户安装目录或敏感配置须有覆盖具体对象和操作的授权；只创建本地入口不推断外部授权。

## 完成

核对真实加载链、新入口和项目指针可达，声明有证据支持；Bundle 产物符合相应元数据。记录实际修改、运行过的检查及无法核实的环境。需要语义写入、扫描维护或整体导航设计时按需使用相应能力，不强制链式执行。
