---
name: pr
description: 草拟、创建或更新 pull request，组织变更摘要、证据与合并风险。
metadata:
  credits:
    skill: show-me
    author: Dex Horthy
    organisation: Humanlayer
    url: "https://github.com/humanlayer/skills/blob/main/plugins/show-me/skills/show-me/SKILL.md"
---

# Pull Request

根据目标分支与实际 diff 准备简洁、便于评审的正文，使用项目领域语言。优先组织为 Summary、Evidence、Merge Danger；不为套模板添加无关内容。

## Summary：选择最小视图

说明目的与关键变化，把视图紧贴它支持的短说明，保留评审理解所需的调用、状态和所有权，不需要同时使用所有形式：

- **算法或规则**用伪代码：

  ```text
  on(save)
    if content unchanged: return cached result
    write content
    invalidate cache
  ```

- **运行顺序**用调用树，例如 `submitForm → createSession → persistPrompt → launchAgent`；需要说明 UI 职责时，用组件树展示 `<SessionPage> → <SessionToolbar> → <RunSkillButton>` 及相关状态；说明文件所有权时用浅文件树。
- **组件交互或数据流**用时序图，例如 User → UI 选择命令，UI → Daemon 发送请求，Daemon → UI 返回结果。图中的顺序与边界必须来自真实变更。
- **现有结构的变化**用适合主题的 diff：组件树展示新增按钮；文件树展示移动后的职责；调用树展示插入的步骤；状态变化可写成：

  ```diff
   on(save)
-    write content
+    if content unchanged: return cached result
+    write content
+    invalidate cache
  ```

大部分内容是新增、截断会掩盖顺序或所有权、或读者需要可复制形状时，可展示完整代码块。不同视图的目的是解释变化，不是装饰。

## Evidence：展示实际观察

给出实际运行或观察的证据、条件与限制。视觉变更在环境允许时可比较真实的前后截图，注明页面、视口、状态和版本；不要用设计稿冒充运行画面。逻辑变更可以列出运行命令、关键输出及其覆盖的行为，例如：

```text
Before: 原问题场景的测试 <实际失败输出或既有失败记录>
After:  相同场景的测试 <实际通过输出>
```

这是证据组织示意，不是声称测试运行过；只有确实观察到对应结果才填入。已有有效失败可复用，不为凑前后对照制造失败；没有前态时说明缺失，附现有相关测试或输出。列出未运行或无法观察的部分，不编造红绿结果、截图或 CI 状态。

## Merge Danger：回退与影响

判断是容易回退的 **two-way door**，还是数据删除、不可逆迁移等难以撤回的 **one-way door**；说明判断依据和恢复手段。再说清 **blast radius**：影响哪些用户、消费者、数据或环境，什么条件下触发，可能的布局偏移、移动端问题或下游兼容性风险。回滚代码不一定撤销已写入的数据；测试通过也不覆盖未验证的迁移与部署风险。

草稿可本地交付；创建或更新 PR、push、commit 等只在任务明确授权具体动作和目标时执行。动作前核对远端、分支、实际包含的提交与工作树内容，防止带入无关改动或秘密；现有有效授权覆盖时无需重复询问。创建 PR 不授权合并、删除分支或清理 worktree；状态或归属不明时保留。署名见 [CREDITS.md](CREDITS.md)。
