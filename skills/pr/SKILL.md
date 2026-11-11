---
name: pr
description: 草拟、创建或更新 pull request，组织变更摘要、真实证据和合并风险；是否发布取决于具体授权。
metadata:
  credits:
    skill: show-me
    author: Dex Horthy
    organisation: Humanlayer
    url: "https://github.com/humanlayer/skills/blob/main/plugins/show-me/skills/show-me/SKILL.md"
---

# Pull Request

根据目标分支与实际 diff 准备简洁、便于评审的正文，使用项目领域语言。优先组织为 Summary、Evidence、Merge Danger；不为套模板添加无关内容。

- **Summary**：说明目的与关键变化。按需要选择最小、贴近说明的表达：算法伪代码、调用树、组件/状态树、文件树、交互或数据流图、针对结构的 diff；大部分为新增或省略上下文会掩盖顺序和所有权时可展示完整代码块。无需同时使用多种图示。
- **Evidence**：列出实际运行或观察的证据及条件。适用时用真实前后对照；视觉变更可附实际截图，逻辑变更可引用对应测试或输出。复用仍适用的证据，说明未验证项，不编造红绿结果、截图或 CI 状态。
- **Merge Danger**：说明影响范围、消费者及运行条件，是否易于回滚，数据迁移或不可逆操作的后果，以及需要的恢复手段；不要以测试通过掩盖未验证风险。

草稿可本地交付；创建或更新 PR、push、commit 等只在任务明确授权具体动作和目标时执行。动作前核对远端、分支、实际包含的提交与工作树内容，防止带入无关改动或秘密；现有有效授权覆盖时无需重复询问。创建 PR 不授权合并、删除分支或清理 worktree；状态或归属不明时保留。署名见 [CREDITS.md](CREDITS.md)。
