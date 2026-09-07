# Discuss Visual Companion Guide

本指南用于 `discuss` 在需求讨论和 PRD 细化中启用本地 HTML 可视化辅助。脚本复用自 superpowers `brainstorming` companion，并按本项目命名落地；会话文件默认写入 `/tmp`，不假设项目内存在持久目录。

## 何时使用

按当前问题判断，而不是按整个 session 判断：**如果用户通过“看见”比通过“阅读”更容易理解或决策，就使用 HTML。**

适合使用 HTML：
- UI wireframe：页面布局、导航结构、信息层级、组件位置关系。
- 流程图：用户旅程、表单/wizard 步骤、状态切换、异常路径。
- 关系图：权限矩阵、对象关系、角色视图、范围边界。
- 方案对比：side-by-side 布局、流程、范围方案，或影响范围/验收的上层技术方向。

不适合使用 HTML：
- 术语定义、范围文字确认、成功指标、优先级策略。
- 接口签名、数据表/字段、库选型、代码结构、文件路径等实现细节。
- 纯文本/表格就能清楚表达的问题。

一个问题涉及 UI，并不意味着必须使用 HTML：
- “这个页面要解决什么问题？”是概念问题，用文字。
- “这三种布局哪种更符合预期？”是视觉问题，用 HTML。

## 启动会话

从本次实际加载的 `SKILL.md` 所在目录解析脚本路径，将其绝对目录记为 `DISCUSS_SKILL_DIR`；不假设调用 cwd 或目标项目包含 `skills/discuss/`。

```bash
"$DISCUSS_SKILL_DIR/scripts/start-server.sh"
```

返回示例：

```json
{
  "type": "server-started",
  "port": 52341,
  "url": "http://localhost:52341",
  "screen_dir": "/tmp/discuss-<session>/content",
  "state_dir": "/tmp/discuss-<session>/state"
}
```

保存 `screen_dir`、`state_dir` 及其共同父目录 `session_dir`。使用宿主可用的浏览器入口展示 `url`，或给用户可打开的链接。

启动脚本从自身目录加载资源，会话文件保存在 `/tmp/discuss-<session>/`，停止服务时会被清理；`--project-dir` 仅是兼容参数，不会改变会话目录。目标项目由任务上下文独立确定，讨论内容如需持久化再按主 Skill 的条件写入该项目。

服务只绑定 `127.0.0.1`。不要把 visual companion 暴露到非 loopback 网络；远程或容器环境应通过宿主提供的端口转发访问本机 loopback URL。

## 视图与反馈

`state_dir/server-info` 保存启动信息；`server-stopped` 表示服务已停止。状态不明时核实进程或 URL 是否仍可用，不能仅凭旧文件认定正在运行。服务空闲 30 分钟会自动退出。

写入新 HTML 到 `screen_dir` 时使用新文件名，如 `scope-options.html`、`layout-v2.html`，以便区分当前画面与旧反馈。默认写 HTML 片段，服务会注入 frame、样式和交互脚本。向用户说明当前链接和主题，并使用当前宿主可用的反馈入口；无需为了本指南切换到终端。

按需读取 `state_dir/events` 中的点击/选择事件，并结合当前画面与用户陈述判断。用户明确陈述优先于辅助点击；仍存在会影响决策的歧义时才澄清。

结论默认在对话中表达。只有用户明确要求、流程要求或需要长期维护时才落盘，沿用主 Skill 的持久化条件与目标项目已有位置，不固定生成 spec。回到纯文字讨论或更换议题时，推送等待页或明确旧画面已不再适用，避免过期视觉误导。

## 内容片段示例

```html
<h2>这个需求先做哪个最小闭环？</h2>
<p class="subtitle">请选择最能快速验证用户价值的一项</p>

<div class="options">
  <div class="option" data-choice="a" onclick="toggleSelect(this)">
    <div class="letter">A</div>
    <div class="content">
      <h3>只做核心路径</h3>
      <p>覆盖主流程，异常和配置能力延后。</p>
    </div>
  </div>
  <div class="option" data-choice="b" onclick="toggleSelect(this)">
    <div class="letter">B</div>
    <div class="content">
      <h3>核心路径 + 异常状态</h3>
      <p>同时明确空状态、失败状态和边界提示。</p>
    </div>
  </div>
</div>
```

## 可用 CSS 结构

### 选项

```html
<div class="options">
  <div class="option" data-choice="a" onclick="toggleSelect(this)">
    <div class="letter">A</div>
    <div class="content">
      <h3>标题</h3>
      <p>说明</p>
    </div>
  </div>
</div>
```

多选：在 `.options` 上添加 `data-multiselect`。

### 卡片

```html
<div class="cards">
  <div class="card" data-choice="design1" onclick="toggleSelect(this)">
    <div class="card-image"><!-- mockup --></div>
    <div class="card-body">
      <h3>方案名</h3>
      <p>说明</p>
    </div>
  </div>
</div>
```

### Mockup

```html
<div class="mockup">
  <div class="mockup-header">Preview: 用户流程</div>
  <div class="mockup-body"><!-- mockup content --></div>
</div>
```

### Split View

```html
<div class="split">
  <div class="mockup"><!-- 左侧方案 --></div>
  <div class="mockup"><!-- 右侧方案 --></div>
</div>
```

### Pros / Cons

```html
<div class="pros-cons">
  <div class="pros"><h4>Pros</h4><ul><li>优点</li></ul></div>
  <div class="cons"><h4>Cons</h4><ul><li>代价</li></ul></div>
</div>
```

## 浏览器事件格式

用户点击带 `data-choice` 的元素时，事件写入 `state_dir/events`，一行一个 JSON：

```jsonl
{"type":"click","choice":"a","text":"Option A - Core path","timestamp":1706000101}
```

若 `state_dir/events` 不存在，说明当前没有可读取的浏览器事件；继续使用宿主可用的对话或结构化反馈，不据此推断用户是否看过画面。

## 停止服务

```bash
"$DISCUSS_SKILL_DIR/scripts/stop-server.sh" "$SESSION_DIR"
```
`SESSION_DIR` 使用本次启动返回的 `screen_dir` / `state_dir` 的共同父目录。脚本停止该会话，并清理匹配 `/tmp/discuss-*` 的会话目录。

## 文件索引

以下路径均相对本 Skill 目录，执行时使用从实际加载位置解析的绝对路径：

- 启动：`scripts/start-server.sh`
- 停止：`scripts/stop-server.sh`
- 服务：`scripts/server.cjs`
- Frame 样式：`scripts/frame-template.html`
- 客户端事件：`scripts/helper.js`
