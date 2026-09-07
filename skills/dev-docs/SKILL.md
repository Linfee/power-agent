---
name: dev-docs
description: |-
  把稳定系统事实、边界、决策依据或集成参考写入或修订 `docs/` 长期知识时使用；不用于裸“写文档”、README/公告、会话记录或执行计划。
  Triggers: 文档知识沉淀, ADR 记录, dev-docs.
---

# 维护长期开发知识

保存未来工作会复用的系统事实、领域边界、开发方式、精确参考与决策理由。按真实消费需求选内容，沿用已有布局并优先修订现有 Concept；局部显然的实现细节由代码与测试表达。

## 判断写什么

当前事实随实现修订；ADR 保存未来需要、却不能从代码恢复的理由，可逆决定也可能值得记录。已接受决定保留历史；用户已授权重开时，用新 ADR 和双向 supersede 关系表达，不能从当前代码反推决定获批。

术语缺口与同义词漂移可以提示长期知识缺口。用户只说“更新文档”时，先从任务和项目确认变化事实、来源及读者用途；不足以决定权威来源或生命周期时才澄清，不猜写。README、公告、会话记录与执行计划有各自生命周期，不由本 Skill 接管。

## 写入边界

- **敏感资料**：密钥、认证信息、Cookie、个人或客户标识、私有 URL query、原始日志及受限资料不进入正文、示例或 Citations。采用脱敏事实、合成示例和受控来源的稳定名称；无法安全建立来源时保留未确认状态，不用模型记忆补足。
- **元数据**：`docs/` 中除导航 `index.md` 与变更日志 `log.md` 外，Concept 的顶部 YAML frontmatter 是元数据唯一权威，`type` 非空。`timestamp` 仅随语义变化更新；字段、示例与旧格式处理见 [项目 Profile](references/project-docs-profile.md#推荐-frontmatter)。
- **验证登记**：新建或改写不等于验证完成。运行状态只由受控维护工具写入 `docs/.okf/verification.json`，不手工刷新 ledger，也不写回 Concept。
- **路径与来源**：路径即 Concept ID，移动须有概念边界和授权依据并修复入链。内部关系用 Markdown 链接，外部声明在 `# Citations` 保留支撑来源；导航变化才更新 index，长期有意义的变化才进入 log。

## 核对语义与消费结果

读取支撑目标声明的代码、测试、配置、Schema、ADR 和一阶链接，按证据缺口扩大范围。写入后核对关键声明、适用范围、frontmatter、链接与来源；无法核对的部分明确保留，不以结构检查代替语义证明。

用户要求仅凭文档完成任务，或已知读者误解请求流、边界及操作路径时，用不继承当前解释的 fresh sub-agent 消费目标 Concept 与一阶链接。按真实任务选择问题或安全环境中的授权操作，以结果和权威证据验收，不固定题数；失败则修订并重验受影响行为。其他写入不必启动消费测试。

## 按缺口读取

- 字段、type、知识粒度与当前事实/决策/计划的区分：[项目 Profile](references/project-docs-profile.md)；旧文档迁移直接读其 [迁移约定](references/project-docs-profile.md#渐进迁移)。
- Concept 或 Bundle 合规存在疑问：[OKF 规范](references/okf-v0.1.md)。
- 需要结构维护、扫描或验证登记时可使用 `dev-docs-maintain`；缺少最小入口或 Bundle 结构时可使用 `setup-power-agent`。普通语义写入可独立完成，不形成必跑链。
