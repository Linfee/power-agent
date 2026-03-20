# 可视化伴侣指南

在设计讨论过程中，通过浏览器展示线框图、架构图和方案对比。

> **路径说明：** 以下脚本路径为 `skills/discuss/scripts/`，相对于插件安装目录。
> 安装为个人 skill 后路径为 `~/.factory/skills/discuss/scripts/`。

## 使用时机

**按问题判断，而非按 session 判断。** 判断标准：**用户看到比读到更容易理解吗？**

**使用浏览器** 当内容本身是可视化的：

- **UI 线框图** — 布局、导航结构、组件设计
- **架构图** — 系统组件、数据流、关系图
- **并排可视化对比** — 对比两种布局、两种配色、两种设计方向
- **设计细节** — 问题关于外观、间距、视觉层次时
- **空间关系** — 状态机、流程图、实体关系图

**使用终端** 当内容是文本或表格：

- **需求和范围问题** — "X 是什么意思？"、"哪些功能在范围内？"
- **概念性 A/B/C 选择** — 在文字描述的方案间选择
- **权衡列表** — 优缺点、对比表
- **技术决策** — API 设计、数据建模、架构方案选择
- **澄清性问题** — 答案是文字而非视觉偏好的任何情况

关于 UI 话题的问题不等于可视化问题。"你想要什么类型的向导？"是概念问题——用终端。"这两种向导布局哪个更合适？"是可视化问题——用浏览器。

## 工作原理

服务器监视一个目录中的 HTML 文件，将最新的文件提供给浏览器。你写 HTML 内容，用户在浏览器中看到并可以点击选择方案。选择结果记录到 `.events` 文件，你在下一轮对话中读取。

**内容片段 vs 完整文档：** 如果 HTML 文件以 `<!DOCTYPE` 或 `<html` 开头，服务器原样提供（只注入辅助脚本）。否则，服务器自动将你的内容包装在框架模板中——添加页眉、CSS 主题、选择指示器和所有交互基础设施。**默认写内容片段。** 只有在需要完全控制页面时才写完整文档。

## 启动 Session

```bash
# 带持久化地启动服务器（线框图保存到项目）
skills/discuss/scripts/start-server.sh --project-dir /path/to/project

# 返回: {"type":"server-started","port":52341,"url":"http://localhost:52341",
#        "screen_dir":"/path/to/project/.superpowers/brainstorm/12345-1706000000"}
```

保存响应中的 `screen_dir`。告诉用户打开 URL。

**查找连接信息：** 服务器将启动 JSON 写入 `$SCREEN_DIR/.server-info`。如果你在后台启动了服务器且没有捕获 stdout，读取该文件获取 URL 和端口。使用 `--project-dir` 时，在 `<project>/.superpowers/brainstorm/` 中查找 session 目录。

**注意：** 传入项目根目录作为 `--project-dir`，使线框图持久化到 `.superpowers/brainstorm/` 并在服务器重启后仍然可用。不传则文件放到 `/tmp` 会被清理。提醒用户将 `.superpowers/` 添加到 `.gitignore`（如果尚未添加）。

**按平台启动服务器：**

**Droid（macOS / Linux）：**
```bash
# 默认模式可用——脚本本身会在后台运行服务器
skills/discuss/scripts/start-server.sh --project-dir /path/to/project
```

**Droid（Windows）：**
```bash
# Windows 自动检测并使用前台模式，这会阻塞工具调用。
# 使用 fireAndForget: true 使服务器在对话轮次间保持运行。
skills/discuss/scripts/start-server.sh --project-dir /path/to/project
```
通过 Execute 工具调用时，设置 `fireAndForget: true`。然后在下一轮对话中读取 `$SCREEN_DIR/.server-info` 获取 URL 和端口。

**其他环境：** 服务器必须在对话轮次间持续在后台运行。如果你的环境会回收分离的进程，使用 `--foreground` 并通过平台的后台执行机制启动命令。

如果 URL 无法从浏览器访问（远程/容器化环境常见），绑定非回环地址：

```bash
skills/discuss/scripts/start-server.sh \
  --project-dir /path/to/project \
  --host 0.0.0.0 \
  --url-host localhost
```

用 `--url-host` 控制返回的 URL JSON 中显示的主机名。

## 循环

1. **确认服务器运行**，然后**写 HTML** 到 `screen_dir` 中的新文件：
   - 每次写入前，检查 `$SCREEN_DIR/.server-info` 是否存在。如果不存在（或 `.server-stopped` 存在），服务器已关闭——在继续之前用 `start-server.sh` 重启。服务器在无活动 30 分钟后自动退出。
   - 使用语义化文件名：`platform.html`、`visual-style.html`、`layout.html`
   - **不要复用文件名** — 每个屏幕使用新文件
   - 使用 Create 工具——**不要用 cat/heredoc**（会在终端输出噪音）
   - 服务器自动提供最新文件

2. **告诉用户预期看到什么，然后结束本轮：**
   - 每一步都提醒 URL（不只是第一次）
   - 简短描述屏幕上的内容（如"显示首页的 3 种布局方案"）
   - 引导用户在终端回复："看一下，如果想选择某个方案可以点击。"

3. **下一轮**——用户在终端回复后：
   - 如果 `$SCREEN_DIR/.events` 存在就读取——其中包含用户的浏览器交互（点击、选择），每行一个 JSON 对象
   - 结合用户的终端文字获取完整图像
   - 终端消息是主要反馈；`.events` 提供结构化的交互数据

4. **迭代或推进** — 如果反馈改变了当前屏幕，写新文件（如 `layout-v2.html`）。只有当前步骤确认后才进入下一个问题。

5. **返回终端时卸载** — 当下一步不需要浏览器时（如澄清性问题、权衡讨论），推送等待屏幕以清除过期内容：

   ```html
   <!-- 文件名: waiting.html（或 waiting-2.html 等） -->
   <div style="display:flex;align-items:center;justify-content:center;min-height:60vh">
     <p class="subtitle">在终端继续...</p>
   </div>
   ```

   这防止用户盯着已经解决的选项看，而对话已经继续推进。下一个可视化问题出现时，正常推送新内容文件。

6. 重复直到完成。

## 编写内容片段

只写放在页面内部的内容。服务器自动将其包装在框架模板中（页眉、主题 CSS、选择指示器和所有交互基础设施）。

**最小示例：**

```html
<h2>哪种布局更好？</h2>
<p class="subtitle">考虑可读性和视觉层次</p>

<div class="options">
  <div class="option" data-choice="a" onclick="toggleSelect(this)">
    <div class="letter">A</div>
    <div class="content">
      <h3>单列</h3>
      <p>清晰、专注的阅读体验</p>
    </div>
  </div>
  <div class="option" data-choice="b" onclick="toggleSelect(this)">
    <div class="letter">B</div>
    <div class="content">
      <h3>双列</h3>
      <p>侧边导航 + 主内容区</p>
    </div>
  </div>
</div>
```

就这些。不需要 `<html>`、CSS 或 `<script>` 标签。服务器全部提供。

## 可用 CSS 类

框架模板为你的内容提供以下 CSS 类：

### 选项（A/B/C 选择）

```html
<div class="options">
  <div class="option" data-choice="a" onclick="toggleSelect(this)">
    <div class="letter">A</div>
    <div class="content">
      <h3>标题</h3>
      <p>描述</p>
    </div>
  </div>
</div>
```

**多选：** 在容器上添加 `data-multiselect`，允许用户选择多个选项。每次点击切换选中状态，指示栏显示数量。

```html
<div class="options" data-multiselect>
  <!-- 相同的 option 标记——用户可以选择/取消选择多个 -->
</div>
```

### 卡片（可视化设计）

```html
<div class="cards">
  <div class="card" data-choice="design1" onclick="toggleSelect(this)">
    <div class="card-image"><!-- 线框图内容 --></div>
    <div class="card-body">
      <h3>名称</h3>
      <p>描述</p>
    </div>
  </div>
</div>
```

### 线框图容器

```html
<div class="mockup">
  <div class="mockup-header">预览：仪表盘布局</div>
  <div class="mockup-body"><!-- 你的线框图 HTML --></div>
</div>
```

### 并排视图

```html
<div class="split">
  <div class="mockup"><!-- 左侧 --></div>
  <div class="mockup"><!-- 右侧 --></div>
</div>
```

### 优缺点

```html
<div class="pros-cons">
  <div class="pros"><h4>优点</h4><ul><li>优势</li></ul></div>
  <div class="cons"><h4>缺点</h4><ul><li>劣势</li></ul></div>
</div>
```

### 模拟元素（线框图构建块）

```html
<div class="mock-nav">Logo | 首页 | 关于 | 联系</div>
<div style="display: flex;">
  <div class="mock-sidebar">导航</div>
  <div class="mock-content">主内容区</div>
</div>
<button class="mock-button">操作按钮</button>
<input class="mock-input" placeholder="输入框">
<div class="placeholder">占位区域</div>
```

### 排版和章节

- `h2` — 页面标题
- `h3` — 小节标题
- `.subtitle` — 标题下方的次要文本
- `.section` — 有底部间距的内容块
- `.label` — 小型大写标签文本

## 浏览器事件格式

用户在浏览器中点击选项时，交互记录到 `$SCREEN_DIR/.events`（每行一个 JSON 对象）。推送新屏幕时文件自动清空。

```jsonl
{"type":"click","choice":"a","text":"选项 A - 简单布局","timestamp":1706000101}
{"type":"click","choice":"c","text":"选项 C - 复杂网格","timestamp":1706000108}
{"type":"click","choice":"b","text":"选项 B - 混合方案","timestamp":1706000115}
```

完整的事件流显示用户的探索路径——他们可能点击多个选项再确定。最后一个 `choice` 事件通常是最终选择，但点击模式可以揭示犹豫或值得追问的偏好。

如果 `.events` 不存在，用户没有与浏览器交互——只使用他们的终端文字。

## 设计建议

- **按问题调整保真度** — 布局问题用线框图，细节问题用高保真
- **每页都说明问题** — "哪种布局更专业？"而不只是"选一个"
- **迭代后再推进** — 如果反馈改变了当前屏幕，先写新版本
- **每屏最多 2-4 个选项**
- **需要时使用真实内容** — 摄影作品集用真实图片（如 Unsplash）。占位内容会掩盖设计问题。
- **保持线框图简洁** — 聚焦布局和结构，不追求像素完美

## 文件命名

- 使用语义化名称：`platform.html`、`visual-style.html`、`layout.html`
- 不要复用文件名——每个屏幕必须是新文件
- 迭代版本追加后缀：`layout-v2.html`、`layout-v3.html`
- 服务器按修改时间提供最新文件

## 清理

```bash
skills/discuss/scripts/stop-server.sh $SCREEN_DIR
```

使用 `--project-dir` 的 session，线框图文件持久化在 `.superpowers/brainstorm/` 供后续参考。只有 `/tmp` session 会在停止时删除。

## 参考

- 框架模板（CSS 参考）：`skills/discuss/scripts/frame-template.html`
- 辅助脚本（客户端）：`skills/discuss/scripts/helper.js`
