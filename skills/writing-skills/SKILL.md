---
name: writing-skills
description: |-
  Skill 维护 Skill。创建、修改、审查或优化 Skill 与触发描述；用户要求写 skill、改 skill 或 review skill 时触发。
  Triggers: 创建 skill, 修改 skill, skill 设计, prompt 契约, skill review.
---

# Writing Skills

Skill 是可复用工作流，不是一次性经验记录。修改 Skill 时要像修改代码一样处理：先明确目标行为，再用压力场景验证它是否真的能改变 Agent 行为。

---

## Objective

### 做什么
- 创建或修改 `skills/<name>/SKILL.md`。
- 维护 Skill 与 references、docs、AGENTS.md 之间的触发和交接契约。
- 为关键 Skill 设计压力场景，验证没有 Skill 时的失败模式和有 Skill 后的期望行为。
- 优化 description，使触发条件更准确。

### 不做什么
- 不把项目一次性约定伪装成通用 Skill。
- 不为能用脚本、lint 或 schema 机械化的规则只写 prompt。
- 不在 Skill 中隐藏破坏性命令或平台私有假设。
- 不把长篇背景故事写进 `SKILL.md`。

---

## Skill 设计准则

### 1. 先定义行为

修改前写清楚：
- 触发场景：用户说什么、任务处于什么阶段时应使用。
- 目标行为：Agent 读完 Skill 后应该做出什么不同决策。
- 失败模式：没有这个 Skill 时常见错误是什么。
- 输出契约：下游 Agent 或 Skill 需要消费哪些字段。

### 2. 保持渐进披露

- `SKILL.md` 放入口、边界、流程和输出格式。
- `references/` 放模板、长 prompt、rubric、示例。
- `scripts/` 放可重复、确定性的检查或转换。
- 超过约 300 行的参考内容应拆到 `references/`。

### 3. description 只服务触发

description 要回答“什么时候用”，不要复述完整流程。应包含具体触发词和任务上下文。

较好：
```yaml
description: 在收到代码审查反馈、需要判断采纳/驳回/澄清时使用。
```

较差：
```yaml
description: 本 Skill 会读取反馈、分析代码、输出表格、然后建议下一步。
```

### 4. 契约优先

跨 Skill 交接必须明确：
- 上游输入字段。
- 下游输出字段。
- 状态枚举。
- 缺失字段时如何降级或阻塞。

如果上游模板和下游 prompt 对同一任务卡的要求不同，先修契约，不靠执行时临时解释。

---

## 压力场景

对核心 Skill 修改，至少准备 2-3 个压力场景。每个场景包含：

```markdown
### 场景：[名称]
- 用户输入：[真实用户会怎么说]
- 无 Skill 易错行为：[具体错误]
- 期望行为：[使用 Skill 后应如何处理]
- 验收点：[可观察输出或文件变化]
```

适合压力测试的场景：
- Skill 触发边界容易误判。
- 多个 Skill 可能冲突。
- 子代理任务卡可能缺字段。
- 完成声明可能缺证据。
- destructive / branch cleanup / worktree 操作。

如果当前环境无法运行子代理 eval，仍应把压力场景写入相关文档或 PR 描述，供后续验证。

---

## 修改流程

1. 读取当前 `SKILL.md`、相关 `references/`、调用方 Skill 和 docs。
2. 明确本次要修的行为缺陷，避免顺手重写整套风格。
3. 修改最小必要文件，优先修正契约、触发、输出格式和缺失 reference。
4. 检查交接链路：上游产物是否满足下游输入。
5. 同步 `AGENTS.md`、`docs/architecture.md`、`docs/workflow.md`、`docs/development.md` 中的 Skill 清单和路径。
6. 若修改 Skill 内容，检查 frontmatter、插件 manifest 和相关 docs 是否需要同步更新。

---

## 完成前检查

- [ ] 新/改 Skill 的 description 能准确触发。
- [ ] `SKILL.md` 没有残留 TODO、TBD、占位路径或旧 Skill 名。
- [ ] references 路径真实存在。
- [ ] 上下游契约字段一致。
- [ ] frontmatter / manifest / docs 已按需同步。
- [ ] 至少有 grep、路径检查或压力场景级别的验证证据。

---

## 输出格式

```markdown
## Skill 修改结果

状态：DONE / DONE_WITH_CONCERNS / BLOCKED

### 变更
- <修改了哪些 Skill / reference / docs>

### 证据
- [command/file] <证据>

### 风险
- <剩余风险；无则写“无”>

### 下一步
- <继续验证 / 请求审查 / 完成>
```
