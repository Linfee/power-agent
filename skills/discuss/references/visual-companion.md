<!-- verified: 2026-06-05 -->
<!-- scope: discuss, html-visual-companion -->

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

```bash
skills/discuss/scripts/start-server.sh
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

保存 `screen_dir` 和 `state_dir`。告诉用户打开 `url`。

会话文件默认保存在 `/tmp/discuss-<session>/`，停止服务时会被清理；不要依赖仓库内持久目录。

服务只绑定 `127.0.0.1`。不要把 visual companion 暴露到非 loopback 网络；远程或容器环境应通过宿主提供的端口转发访问本机 loopback URL。

## 讨论闭环

1. 检查服务状态：
   - `$STATE_DIR/server-info` 存在表示服务正在运行。
   - `$STATE_DIR/server-stopped` 存在表示服务已停止，需要重启。
   - 服务空闲 30 分钟会自动退出。
2. 写入新 HTML 到 `screen_dir`：
   - 每屏用新文件名，不复用旧文件名。
   - 使用语义化文件名，如 `scope-options.html`、`layout-v1.html`、`flow-v2.html`。
   - 默认写 HTML 片段，不写完整文档；服务会自动注入 frame、样式和交互脚本。
3. 告诉用户：
   - 当前 URL。
   - 屏幕展示的主题。
   - 请在浏览器查看/点击，并回到终端反馈。
4. 下一轮读取 `$STATE_DIR/events`：
   - HTML 点击/选择事件是辅助证据。
   - 用户终端文字反馈是主反馈。
   - 若两者冲突，以终端文字为准，并主动确认。
5. 将确认结果沉淀进 spec：
   - 用户流程。
   - 方案取舍。
   - 验收标准。
   - Open Questions。
6. 回到纯文字讨论时，推送等待页或明确说明当前不再看旧画面，避免过期视觉误导。

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

用户点击带 `data-choice` 的元素时，事件写入 `$STATE_DIR/events`，一行一个 JSON：

```jsonl
{"type":"click","choice":"a","text":"Option A - Core path","timestamp":1706000101}
```

若 `$STATE_DIR/events` 不存在，表示用户未在浏览器中交互，只使用终端反馈。

## 停止服务

```bash
skills/discuss/scripts/stop-server.sh <session_dir>
```
如果 session 在 `/tmp` 下，停止服务会删除临时文件。

## 文件索引

- 启动：`skills/discuss/scripts/start-server.sh`
- 停止：`skills/discuss/scripts/stop-server.sh`
- 服务：`skills/discuss/scripts/server.cjs`
- Frame 样式：`skills/discuss/scripts/frame-template.html`
- 客户端事件：`skills/discuss/scripts/helper.js`
