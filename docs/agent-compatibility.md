---
type: Playbook
scope:
  - agent-compatibility
---

# 宿主兼容性与安装

Power-Agent 面向 Claude Code、pi、OMP、Codex、Cursor 和 Factory/Droid，以**单个插件或包**分发全部 Skill 与跨任务[最小完整改动默认规则](../skills/codebase-design/references/minimal-complete-change.md)。规则和按需调用的 Skill 作用不同：规则不替代 Skill 的方法，也不保证模型遵守。宿主还需要普通 sub-agent 才能完整使用依赖它的工作方式。

安装前审查插件代码和宿主的权限、信任与配置作用域；插件 hook 和扩展会执行代码。不要把插件安装到一个真实账户、授信或修改其设置当作默认授权。正常安装不需要在业务项目中复制规则或运行项目规则配置器。

以下本地安装路径必须指向包含插件声明、`hooks/` 和 `skills/` 的完整插件源，不能把 Skill 安装目录当成仓库根目录。成功的远端安装取得远端版本；可用性取决于宿主和认证条件，OMP 的私有仓库限制见下文。要使用尚未发布的本地修改，应指定完整 checkout。

## 安装后的调用范围

手动入口是 `grill-with-docs`、`to-spec`、`to-tickets`、`wayfinder`、`triage`、`improve-codebase-architecture`、`retro`、`handoff`、`knowledge-navigation`；其余入口允许模型调用。`implement`、`implement-spec`、`setup-power-agent` 及其实际依赖保持自动可达。

手动入口同时提供 `SKILL.md` 的 `disable-model-invocation: true` 与 Codex 的 `agents/openai.yaml` 中 `policy.allow_implicit_invocation: false`。Claude、pi、OMP、Cursor、Droid 使用前者，Codex 使用后者；这些是宿主调用策略，不是通用访问控制，也不授予外部副作用权限。内部调用只指向自动能力，不读取手动正文绕过限制。

用户显式入口及命名由宿主决定；各宿主的菜单、发现数量及版本限制须分别确认，不能由元数据推断全部通过。另见 [Cursor Skills](https://cursor.com/docs/skills.md) 与 [Factory Skills](https://docs.factory.ai/harness/skills) 的调用开关说明。

## 安装

### Claude Code

```bash
claude plugin marketplace add https://github.com/Linfee/power-agent
claude plugin install power-agent@power-agent --scope user
# 或使用 --scope project
```

临时加载本地 checkout：`claude --plugin-dir /absolute/path/to/power-agent`。插件 hook 提供默认规则；安装及启用状态和适用生命周期由宿主控制。参见 [Claude Code 插件](https://code.claude.com/docs/en/plugins)与 [hooks](https://code.claude.com/docs/en/hooks)。

### pi

```bash
pi install git:github.com/Linfee/power-agent
# 或安装本地 checkout
pi install /absolute/path/to/power-agent
# 项目范围安装（须经宿主项目可信确认）
pi install --local /absolute/path/to/power-agent
```

包声明 Skill 目录与扩展；`pi list` 查看已配置包。个人安装写用户设置，`--local` 写项目的 pi 设置，项目包仅在宿主信任项目后加载。用 [pi packages](https://pi.dev/docs/latest/packages) 核对当前版本及移除方式；安装配置可筛选资源，不要关闭本包所需的 Skill 或扩展。

### OMP

```bash
# 开发安装：本地目录以链接加载，不是独立副本
omp plugin install /absolute/path/to/power-agent
omp plugin list
```

OMP 支持包的 `pi` 资源声明；本地安装链接到用户插件目录，会受 checkout 变动影响，不能当独立快照。安装后启动新会话以初始化扩展；`omp --extension /absolute/path/to/power-agent` 仅在一次会话中加载本地包。安装会写宿主配置，具体行为见 [OMP 插件](https://omp.sh/docs/plugins)和 [扩展加载](https://github.com/can1357/oh-my-pi/blob/main/docs/extension-loading.md)。

**私有 GitHub 与副本安装：** 在 OMP 18.18.9 / Bun 1.4.0 的已观察环境中，本仓原生 `github:` 安装请求 GitHub tarball API 并返回 404；设置 `GITHUB_TOKEN` 或 `GH_TOKEN` 仍未通过，不能把现有 Git/`gh` 登录推断为 Bun 已获得权限。不得为绕过安装失败而擅自公开仓库或登记 SSH key，也不能把 token 写进 URL 和配置。

**独立副本（手动快照）：** 在已授权、已有 `gh` 登录的环境中，已执行的路径是用 `gh api` 下载 GitHub 指定提交的 tarball，在临时目录解包并运行 `npm pack`，将产物保存在 OMP 插件目录的 `sources/`，再在该插件目录以 `bun add file:./sources/<产物文件名>.tgz` 安装。此路径产生独立副本，不是指向工作仓库的链接；直接把 `.tgz` 交给该版本的 `omp plugin install` 会被当目录处理，不能替代这一步。

这是操作记录，不是跨版本通用安装脚本；插件目录及登记、启用状态须按当前宿主配置确认，并在新会话验证加载。它是指定提交的快照，不是原生 GitHub 依赖，更新须显式重新下载、打包和安装，不能声称 `omp plugin upgrade` 会跟踪 `main`。后续版本及其他认证方式须另行验证；没有对应授权不修改凭据、组织策略或账户配置。

### Codex

先从本地 checkout 注册 marketplace：

```bash
codex plugin marketplace add /absolute/path/to/power-agent
```

Codex CLI 不提供 `plugin install` 子命令。按[本地插件安装说明](https://developers.openai.com/plugins/build/plugins#install-a-local-plugin-manually)，在 Codex 桌面应用 Plugins 中安装并启用插件，再启动新会话。官方将生命周期 hook 限于手动安装的桌面插件；非托管 hook 须在 `/hooks` 审核并信任，定义变更后需重新审核。不要未经用户授权授信或绕过信任。Codex IDE 扩展不支持插件；marketplace 注册成功不能证明规则送达。

### Cursor

在可用 marketplace 的 **Customize** 页面找到 Power-Agent，选择 Install 和用户或项目范围。团队 marketplace 及从仓库导入受计划和管理员权限限制。本地测试时可按 [Cursor 插件说明](https://cursor.com/docs/plugins#test-plugins-locally)将整个插件放入 `~/.cursor/plugins/local/power-agent`，重启或 Reload Window，再在 Customize 检查；本地导入可能被组织策略禁止，指向该目录以外的符号链接不会加载。

Cursor 使用插件自己的 `rules/minimal-complete-change.mdc`，而非业务项目的 `.cursor/rules`；该文件作为插件资源安装，与其他宿主共用同一规则源。插件 manifest 还声明 `skills/`。参见 [Cursor 插件格式](https://cursor.com/docs/reference/plugins)。

**版本风险：** Cursor 上游记录过插件中的 `disable-model-invocation: true` Skill 同时从命令菜单消失的问题：2.6.20 获官方确认，3.23.23 仍有报告；未确认目标版本已经修复。见[问题记录](https://github.com/cursor/plugins/issues/527)与[官方论坛](https://forum.cursor.com/t/disable-model-invocation-true-completely-hides-plugin-delivered-skills-from-command-palette/155748)。应以目标版本实测菜单为准，不通过删除调用开关、自动读取手动正文或复制业务项目规则来规避。

### Factory / Droid

```bash
droid plugin marketplace add https://github.com/Linfee/power-agent
droid plugin install power-agent@power-agent --scope user
# 或使用 --scope project
```

`/plugins` 可查看及管理插件。Factory 从插件根目录发现 `skills/` 和 `hooks/hooks.json`，默认规则通过 `SessionStart` hook 提供；官方列出 startup、resume、clear 和 compact 事件，没有文档化的 `SubagentStart`。添加本地源时须提供包含插件条目的 marketplace，而不是直接把插件目录当成 marketplace。见 [Factory 插件](https://docs.factory.ai/harness/plugins)及 [hooks](https://docs.factory.ai/harness/hooks#plugin-hooks)。

## 安装条件与限制

命令 hook 需要 Node.js；Claude/Droid 的共享启动 hook 使用 POSIX shell 语法，不声明原生 Windows PowerShell 支持。Factory 会在加载时替换插件根路径；路径含换行且包含独立 heredoc 终止行时存在文本替换风险，应避免这样的安装路径。

规则送达、Skill 发现、普通 sub-agent 及规则继承是分别需要验证的能力；安装或 manifest 存在不等于运行成功。