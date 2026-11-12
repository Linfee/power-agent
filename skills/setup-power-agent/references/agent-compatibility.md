---
type: Playbook
scope:
  - agent-compatibility
---

# 宿主兼容性与安装

Power-Agent 面向 Claude Code、pi、OMP、Codex、Cursor 和 Factory/Droid，按**一个插件或包**分发全部 25 个 Skill 与跨任务[最小完整改动默认规则](../../codebase-design/references/minimal-complete-change.md)。规则和按需调用的 Skill 作用不同：规则不替代 Skill 的方法，也不保证模型遵守。宿主还需要普通 sub-agent 才能完整使用依赖它的工作方式。

安装前审查插件代码和宿主的权限、信任与配置作用域；插件 hook 和扩展会执行代码。不要把插件安装到一个真实账户、授信或修改其设置当作默认授权。正常安装不需要在业务项目中复制规则或运行项目规则配置器。

本指南随 Skill 整包分发。以下本地安装路径必须指向包含插件声明、`hooks/` 和 `skills/` 的完整插件源，不能把 Skill 安装目录当成仓库根目录。Git 安装取得远端版本；要使用尚未发布的本地修改，应指定完整 checkout。

## 安装后的调用范围

全部 25 个 Skill 仍随同一插件或包安装；17 个允许模型调用，8 个仅用户显式调用：`grill-with-docs`、`to-spec`、`to-tickets`、`wayfinder`、`triage`、`improve-codebase-architecture`、`retro`、`handoff`。`implement`、`implement-spec`、`setup-power-agent` 及其实际依赖保持自动可达，不要求逐步人工接力。

手动入口同时提供 `SKILL.md` 的 `disable-model-invocation: true` 与 Codex 的 `agents/openai.yaml` 中 `policy.allow_implicit_invocation: false`。Claude、pi、OMP、Cursor、Droid 使用前者，Codex 使用后者；这些是宿主调用策略，不是通用访问控制，也不授予外部副作用权限。内部调用只指向自动能力，不读取手动正文绕过限制。

用户显式入口及命名由宿主决定；本轮已验证 pi/OMP 的 `/skill:to-spec` 可展开，pi 保留全部 25 个 Skill 命令。其他宿主的菜单、发现数量及版本限制须分别确认，不能由元数据推断全部通过。另见 [Cursor Skills](https://cursor.com/docs/skills.md) 与 [Factory Skills](https://docs.factory.ai/harness/skills) 的调用开关说明。

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
omp plugin install /absolute/path/to/power-agent
# 或从 Git 安装
omp plugin install 'github:Linfee/power-agent'
omp plugin list
```

本地安装链接到用户插件目录；安装后重新启动会话以初始化扩展。OMP 支持包的 `pi` 资源声明；可用 `omp --extension /absolute/path/to/power-agent` 仅在一次会话中加载本地包。安装会写宿主配置，具体行为见 [OMP 插件](https://omp.sh/docs/plugins)和 [扩展加载](https://github.com/can1357/oh-my-pi/blob/main/docs/extension-loading.md)。

### Codex

先从本地 checkout 注册 marketplace：

```bash
codex plugin marketplace add /absolute/path/to/power-agent
```

本仓库的 marketplace catalog 已由 0.167.2 实际解析；该 CLI 不提供 `plugin install` 子命令。然后按[本地插件安装说明](https://developers.openai.com/plugins/build/plugins#install-a-local-plugin-manually)，在 Codex 桌面应用 Plugins 中安装并启用插件，再启动新会话。官方将生命周期 hook 限于手动安装的桌面插件；非托管 hook 须在 `/hooks` 审核并信任，定义变更后需重新审核。不要未经用户授权授信或绕过信任。Codex IDE 扩展不支持插件；marketplace 注册成功不能证明规则送达。

### Cursor

在可用 marketplace 的 **Customize** 页面找到 Power-Agent，选择 Install 和用户或项目范围。团队 marketplace 及从仓库导入受计划和管理员权限限制；本仓库不假定已在公共 marketplace 上架。开发时可按 [Cursor 插件说明](https://cursor.com/docs/plugins#test-plugins-locally)将整个插件放入 `~/.cursor/plugins/local/power-agent`，重启或 Reload Window，再在 Customize 检查；本地导入可能被组织策略禁止，指向该目录以外的符号链接不会加载。

Cursor 使用插件自己的 `rules/minimal-complete-change.mdc`，而非业务项目的 `.cursor/rules`；该文件作为插件资源安装，与其他宿主共用同一规则源。插件 manifest 还声明 `skills/`。参见 [Cursor 插件格式](https://cursor.com/docs/reference/plugins)。

**版本风险：** Cursor 上游记录过插件中的 `disable-model-invocation: true` Skill 同时从命令菜单消失的问题：2.6.20 获官方确认，3.23.23 仍有报告；未确认目标版本已经修复。见[问题记录](https://github.com/cursor/plugins/issues/527)与[官方论坛](https://forum.cursor.com/t/disable-model-invocation-true-completely-hides-plugin-delivered-skills-from-command-palette/155748)。应以目标版本实测菜单为准，不通过删除调用开关、自动读取手动正文或复制业务项目规则来规避。

### Factory / Droid

```bash
droid plugin marketplace add https://github.com/Linfee/power-agent
droid plugin install power-agent@power-agent --scope user
# 或使用 --scope project
```

`/plugins` 可查看及管理插件。Factory 从插件根目录发现 `skills/` 和 `hooks/hooks.json`，默认规则通过 `SessionStart` hook 提供；官方列出 startup、resume、clear 和 compact 事件，没有文档化的 `SubagentStart`。添加本地源时须提供包含插件条目的 marketplace，而不是直接把插件目录当成 marketplace。见 [Factory 插件](https://docs.factory.ai/harness/plugins)及 [hooks](https://docs.factory.ai/harness/hooks#plugin-hooks)。

## 机制与证据边界

`hooks/defaults.cjs` 从安装位置读取唯一规则源；Claude、Codex、Droid 使用各自宿主 hook，pi 和 OMP 使用扩展，Cursor 使用插件自带生成规则。规则送达、Skill 发现、普通 sub-agent 及规则继承是分别需要验证的能力；安装或 manifest 存在不等于运行成功。命令 hook 需要 Node.js；Claude/Droid 的共享启动 hook 使用 POSIX shell 语法，不声明原生 Windows PowerShell 支持。Factory 会在加载时替换插件根路径；路径含换行且包含独立 heredoc 终止行时存在文本替换风险，应避免这样的安装路径。

当前默认规则没有可切换模式，不增加 Ponytail 的模式恢复、状态栏或额外会话事件，也不在每次工具调用前重复注入。编码主代理与子代理的实际请求分别验证；无工具的初始化、任务辅助和压缩请求单独记录，不能把所有 HTTP 请求都当成同一种编码上下文。只有发现对应生命周期的真实送达缺口，才增加注入点。

| 宿主 | 已有观察或未验证范围 |
|---|---|
| Claude Code | 2.1.322 在隔离 HOME 中原生安装并发现 25 个 Skill；生命周期专项覆盖连续 Read、实际新上下文子代理、恢复、手动压缩及同进程压缩后继续执行。27 个相关请求各含一份规则；未强制自动压缩，未单独断言本次调用开关修改后的自动列表数量。 |
| pi | 1.5.2 隔离持久安装后保留 25 个 Skill 命令，向模型通告 17 个；`/skill:to-spec` 可显式展开。10 轮重复工具交互的 20 次 Read 均成功，30 个请求各含一份规则；手动压缩后继续执行也为一份。此前恢复已验证；本次原生工具集没有 sub-agent，未模拟该能力。移除后列表为空。 |
| OMP | 18.18.9 隔离持久安装后向模型通告 17 个 Skill，`/skill:to-spec` 可显式展开；实际 Read 连续调用、子代理、手动压缩后继续执行的编码请求各含一份规则。此前恢复已验证；自动压缩未强制。原生卸载后列表为空。 |
| Codex | 0.167.2 曾安装并启用插件，但请求未含规则；未授予 hook 信任，原因未定位，不能判为通过。完整 Skill 发现及子代理未验证。 |
| Cursor | 插件规则和 Skill 的真实 IDE 加载未验证；手动 Skill 的菜单可达性另有上述版本风险，不能判为全部可用。 |
| Factory / Droid | 1.8.0 的加载器代码支持共享 hook 格式，但实际 marketplace 添加被账户插件策略拒绝；未使用真实凭据或绕过策略，插件 hook、Skill 及子代理送达仍未验证。 |

上述请求观察来自独立 HOME/XDG 配置、合成凭据和 loopback 提供方，不证明真实模型的遵从、任务质量或抑制过度设计的效果，也不证明自然选择子代理；其他版本和未列明生命周期不推断通过。宿主支持、调用元数据与运行证据分开，适用版本和信任条件变化时应重新确认。

Claude 的 `plugin validate --strict` 仍因警告退出 1：已有根目录 `CLAUDE.md` 上下文提示、共享 heredoc 的静态路径引用警告，以及图标和系统文件提示。路径在引用式 heredoc 中作为数据传递，特殊字符命令用例和真实 Claude 加载已通过；这不等于严格校验通过，也不代表公共目录发布已验收。

## 验证

在获授权的临时项目、独立 HOME 及宿主/XDG 配置中安装或加载插件；先审查代码，不触碰真实设置、凭据或信任。启动新会话，分别确认自动 Skill 列表、手动入口的显式可达性、默认规则是否进入实际编码请求且只有一份，以及子代理和继承是否可用；同时确认其他系统指令未被覆盖。按宿主适用事件检查连续工具调用、恢复或压缩后继续执行，单独记录辅助请求、版本和未覆盖范围。协议测试、配置存在或模型自述不能替代送达证据。