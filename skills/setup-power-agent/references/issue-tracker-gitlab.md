# GitLab tracker seed

供 setup 按项目实际情况生成 tracker 配置，不是可直接复制的通用命令保证。填写实际 GitLab host、项目路径、`glab` 版本和项目 tier；核对本机帮助及官方文档后记录可用的读取、列出、创建、评论、更新和关闭操作。GitLab issue 与 merge request 分属不同编号空间；默认只把 issue 当请求，项目明确采用 MR 分诊时才配置其操作。

项目配置可按已核实版本写出可直接使用的操作，例如以下命令的形状；先替换并核对目标项目及当前 `glab --help`：

```sh
glab issue view <number> --comments
glab issue list
glab issue create --title "<title>" --description "<description>"
glab issue note <number> --message "<comment>"
glab issue update <number> --label "<existing-label>"
glab issue close <number>
```

确认当前目录实际解析到所选 GitLab host 和项目，或按 CLI 支持的方式显式指定目标；仅在授权覆盖具体写操作时创建、评论、改标签或关闭。需记录关闭理由时先发表评论再关闭；项目将 MR 纳入请求时，另外写明 MR 的读取、diff 与分诊操作。

父子及阻塞关系优先采用当前实例/tier 和 CLI 实际支持的 native 关系；不可用时在子 issue 描述固定位置分别写 `Part of: #<parent>`、`Blocked by: #<number>, ...`。GitLab 功能随版本与 tier 不同，不把上游列出的 quick action 或 API 当成可用保证。每种关系只用 native 或正文作为可更新真源；调度按该来源查询 blocker 实际状态，不维护双份图。

将现有分诊、ready、wayfinder map 和对象类型映射到项目已有角色；无标签时沿用项目的无标签表示，不默认创建新标签。候选须 open、无未完成 blocker 且没有其他活跃 owner；远端 assignee 非原子锁，冲突时重核协调。只在范围和证据充分后按授权更新状态，子项完成不自动关闭父项。远端创建、评论、认领、标签和关闭都须具体授权。
