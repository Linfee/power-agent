---
type: Playbook
scope:
  - agent-compatibility
---

# 宿主兼容性与安装

Power-Agent 面向 Claude Code、pi、OMP、Codex、Cursor 和 Factory/Droid，以**单个插件或包**分发全部 Skill 与跨任务[最小完整改动默认规则](../skills/codebase-design/references/minimal-complete-change.md)。规则和按需调用的 Skill 作用不同：规则不替代 Skill 的方法，也不保证模型遵守。宿主还需要普通 sub-agent 才能完整使用依赖它的工作方式。

安装前审查插件代码和宿主的权限、信任与配置作用域；插件 hook 和扩展会执行代码。不要把插件安装到一个真实账户、授信或修改其设置当作默认授权。正常安装不需要在业务项目中复制规则或运行项目规则配置器。

以下命令以公开仓库为安装源；需要验证尚未发布的本地修改时，使用完整 checkout，具体开发入口见[开发指南](development.md)。成功的远端安装取得远端版本，可用性取决于宿主版本、认证和信任条件；插件安装不等于规则、Skill 或 hook 已实际加载。

## 安装后的调用范围

手动入口是 `grill-with-docs`、`to-spec`、`to-tickets`、`wayfinder`、`triage`、`improve-codebase-architecture`、`retro`、`handoff`、`knowledge-navigation`、`setup-power-agent`；其余入口允许模型调用。`implement`、`implement-spec` 及其实际依赖保持自动可达。

手动入口同时提供 `SKILL.md` 的 `disable-model-invocation: true` 与 Codex 的 `agents/openai.yaml` 中 `policy.allow_implicit_invocation: false`。Claude、pi、OMP、Cursor、Droid 使用前者，Codex 使用后者；这些是宿主调用策略，不是通用访问控制，也不授予外部副作用权限。内部调用只指向自动能力，不读取手动正文绕过限制。

用户显式入口及命名由宿主决定；各宿主的菜单、发现数量及版本限制须分别确认，不能由元数据推断全部通过。另见 [Cursor Skills](https://cursor.com/docs/skills.md) 与 [Factory Skills](https://docs.factory.ai/harness/skills) 的调用开关说明。

## 安装

### Claude Code

```bash
claude plugin marketplace add https://github.com/Linfee/power-agent
claude plugin install power-agent@power-agent --scope user
# 或使用 --scope project
```

插件 hook 提供默认规则；安装及启用状态和适用生命周期由宿主控制。参见 [Claude Code 插件](https://code.claude.com/docs/en/plugins)与 [hooks](https://code.claude.com/docs/en/hooks)。

### pi

```bash
pi install git:github.com/Linfee/power-agent
# 项目范围安装；--approve 确认信任该项目
pi install git:github.com/Linfee/power-agent --local --approve
```

包声明 Skill 目录与扩展；`pi list --approve` 查看包含项目设置的包。个人安装写用户设置，`--local` 写项目的 pi 设置，项目包仅在宿主信任项目后加载。用 [pi packages](https://pi.dev/docs/latest/packages) 核对当前版本及移除方式；安装配置可筛选资源，不要关闭本包所需的 Skill 或扩展。

### OMP

```bash
omp plugin install github:Linfee/power-agent
omp plugin list
```

OMP 支持包的 `pi` 资源声明；安装写宿主配置，并在新会话初始化扩展。公开仓库的 `github:` 安装已验证；`omp plugin list` 确认插件登记和启用状态。具体行为见 [OMP 插件](https://omp.sh/docs/plugins)和 [扩展加载](https://github.com/can1357/oh-my-pi/blob/main/docs/extension-loading.md)。

### Codex

从公开仓库注册 marketplace 并安装：

```bash
codex plugin marketplace add Linfee/power-agent
codex plugin add power-agent@power-agent
```

安装后启动新会话；桌面应用 Plugins 页面可查看启用状态。官方将生命周期 hook 限于手动安装的桌面插件；非托管 hook 须在 `/hooks` 审核并信任，定义变更后需重新审核。不要未经用户授权授信或绕过信任。Codex IDE 扩展不支持插件；marketplace 注册成功不能证明规则送达。

### Cursor

个人安装入口是 Cursor Marketplace：在 **Customize** 中搜索 Power-Agent 并选择 Install 和用户或项目范围。是否上架以目标版本为准；公开 Git 仓库不能作为个人插件源直接安装。

团队或企业计划可由管理员在 **Dashboard → Plugins & MCPs → Import from Repo** 导入 `https://github.com/Linfee/power-agent`，再在 Customize 安装；导入和访问受计划、管理员权限及组织策略限制。

Cursor 使用插件自己的 `rules/minimal-complete-change.mdc`，而非业务项目的 `.cursor/rules`；该文件作为插件资源安装，与其他宿主共用同一规则源。插件 manifest 还声明 `skills/`。参见 [Cursor 插件格式](https://cursor.com/docs/reference/plugins)。

**版本风险：** Cursor 上游记录过插件中的 `disable-model-invocation: true` Skill 同时从命令菜单消失的问题：2.6.20 获官方确认，3.23.23 仍有报告；未确认目标版本已经修复。见[问题记录](https://github.com/cursor/plugins/issues/527)与[官方论坛](https://forum.cursor.com/t/disable-model-invocation-true-completely-hides-plugin-delivered-skills-from-command-palette/155748)。应以目标版本实测菜单为准，不通过删除调用开关、自动读取手动正文或复制业务项目规则来规避。

### Factory / Droid

```bash
droid plugin marketplace add https://github.com/Linfee/power-agent
droid plugin install power-agent@power-agent --scope user
# 或使用 --scope project
```

`/plugins` 可查看及管理插件。Factory 从插件根目录发现 `skills/` 和 `hooks/hooks.json`，默认规则通过 `SessionStart` hook 提供；官方列出 startup、resume、clear 和 compact 事件，没有文档化的 `SubagentStart`。公开仓库本身包含插件条目，可直接作为 marketplace；不要把单个插件目录当成 marketplace。见 [Factory 插件](https://docs.factory.ai/harness/plugins)及 [hooks](https://docs.factory.ai/harness/hooks#plugin-hooks)。

## 安装条件与限制

命令 hook 需要 Node.js；Claude/Droid 的共享启动 hook 使用 POSIX shell 语法，不声明原生 Windows PowerShell 支持。Factory 会在加载时替换插件根路径；路径含换行且包含独立 heredoc 终止行时存在文本替换风险，应避免这样的安装路径。

规则送达、Skill 发现、普通 sub-agent 及规则继承是分别需要验证的能力；安装或 manifest 存在不等于运行成功。