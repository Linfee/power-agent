---
name: requesting-code-review
description: |-
  代码审查请求 Skill。编排全量代码审查并输出结构化发现；编码完成后、合并或 PR 前触发。
  Triggers: 代码审查, code review, 请求审查, 审查当前实现, 多角度 review, 双重审查, double review, 合并前审查, 全量审查.
---

# 请求代码审查

在实现阶段完成后，组织一次面向整个变更范围的审查；进入合并或 PR 前默认必须执行。

本 Skill 是审查编排器，不是审查员本体。

---

## requesting-code-review

代码审查编排器，负责：
- 收集最小审查上下文
- 对变更进行风险分级
- 根据风险派发单审或双审
- 合并审查结论并输出结构化结果

---

## Objective

### 做什么
- 在功能完成后或合并/PR 前发起全量审查（功能级别，不是 batch 级别）
- 用统一且人类可读的输出格式生成可消费结果
- 对阻塞问题给出明确下一步动作

### 不做什么
- 不替代 `plan-impl` 的 batch 内部审查循环
- 不承担最终验证职责（由 `verification-before-completion` 负责）
- 不承担文档维护职责（由 `dev-docs-maintain` 负责）
- 不在主 Skill 内嵌长 prompt 模板与命令菜单

---

## Context & Tools

### 最小输入
- `BASE_SHA` / `HEAD_SHA`
- 需求或规格摘要（验收口径）
- 关键变更文件列表
- 变更摘要（实现了什么）

缺失信息按需读取，不预加载冗长上下文。

### 基线选择优先级
1. `git merge-base HEAD origin/main`
2. `origin/main`
3. `HEAD~N`（仅当前两者不可用时）

### 模板与规则引用
- 审查模板：`references/code-reviewer.md`
- 风险分级：`references/risk-classification.md`
- 冲突归并：`references/conflict-resolution.md`
- 输出协议：`references/output-contract.md`

---

## Constraints & Format

### 风险驱动派发
- 默认启动一个审查子代理，除非用户指定多个
- 默认使用平台可用的 reviewer 子代理；没有专用 reviewer 时，使用通用子代理并粘贴 `references/code-reviewer.md`。
- 不依赖 named `code-reviewer` agent，避免跨平台不可用或 persona 漂移。

### 冲突归并
双审结果按 `references/conflict-resolution.md` 归并，取更严格结论并保留证据。

### 输出格式（必须遵循）

完成审查编排后，用便于阅读的 Markdown 小节输出结果，不使用 YAML：

```markdown
## 代码审查结果

状态：通过 / 通过_含建议 / 阻塞 / 需澄清
风险等级：低风险 / 中风险 / 高风险

### 证据
- <source>（<locator>）：<summary>

### 阻塞问题
- [严重 / 重要] <issue>
  - 影响：<impact>
  - 必须修复：<required_fix>

### 非阻塞建议
- [轻微] <suggestion>

### 下一步
- 继续流程 / 启动修复子代理 / 重新审查 / 升级处理
```

### 行动规则
- `阻塞问题` 非空：`下一步` 只能是 `启动修复子代理`、`重新审查` 或达到轮次上限后的 `升级处理`
- 修复后必须重新审查，不能沿用旧结论
- 连续修复-复审 3 轮仍 `阻塞` 且无收敛：`下一步=升级处理`
- 当 `状态=阻塞` 且 `下一步=启动修复子代理` 时，必须先交给 `receiving-code-review` 评估反馈
- 若 `receiving-code-review` 输出 `状态=DONE`，不得中途询问用户；必须实施所有 `决策=采纳|部分采纳` 的阻塞项、运行相关验证，然后重新发起本 Skill 审查
- 只有当 `receiving-code-review` 输出 `状态=BLOCKED`、连续 3 轮仍阻塞且无收敛，或修复涉及破坏性/越权操作时，才能升级询问用户

---

## 何时触发

**必须：**
- 合并到主分支或创建 PR 前默认执行全量审查；只有用户明确要求跳过时才能跳过，并记录跳过原因
- 一个实现目标完成且准备进入分支处置或交付时

**按风险触发：**
- 复杂重构完成后
- 复杂 bug 修复后
- 需要独立视角做质量把关时

---

## 工作流定位

- 上游：`plan-impl`（已完成 batch 内审查）
- 本 Skill：做收尾阶段全量审查编排
- 下游：`receiving-code-review`（评估与采纳反馈）→ 修复采纳项 → 重新审查，直到通过或达到 3 轮上限 → `verification-before-completion`
- `dev-docs-maintain` 是在 docs 健康检查、漂移修复或 verification ledger 登记需要时按需触发的普通 Skill，不是每次代码审查后的固定步骤。
