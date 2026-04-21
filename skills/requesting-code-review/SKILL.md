---
name: requesting-code-review
description: |-
  实现完成后使用，作为收尾阶段的全量代码审查编排器：基于风险分级派发审查子代理，结构化汇总结论并给出下一步动作。
  Triggers: 代码审查, code review, 请求审查, 合并前审查, 全量审查.
version: 1.2.0
---

# 请求代码审查

在实现阶段完成后，组织一次面向整个变更范围的审查。

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
- 在收尾阶段发起全量审查（功能级别，不是 batch 级别）
- 用统一输出 contract 生成可消费结果
- 对阻塞问题给出明确下一步动作

### 不做什么
- 不替代 `exec-plan-runner` 的 batch 内部审查循环
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
- `低风险` / `中风险`：单审
- `高风险`：双审（2 个独立审查子代理并行）

### 冲突归并
双审结果按 `references/conflict-resolution.md` 归并，取更严格结论并保留证据。

### 输出 contract（必须遵循）
```yaml
status: DONE | DONE_WITH_ADVISORIES | BLOCKED | NEEDS_CLARIFICATION
risk_level: 低风险 | 中风险 | 高风险
evidence:
  - source: string
    locator: string
    summary: string
blocking_issues:
  - severity: 严重 | 重要
    issue: string
    impact: string
    required_fix: string
advisories:
  - suggestion: string
next_action: 继续流程 | 启动修复子代理 | 重新审查 | 升级处理
```

### 行动规则
- `blocking_issues` 非空：`next_action` 只能是 `启动修复子代理` 或 `重新审查`
- 修复后必须重新审查，不能沿用旧结论
- 连续修复-复审 2 轮仍 `BLOCKED` 且无收敛：`next_action=升级处理`

---

## 何时触发

**必须：**
- 一个实现目标完成后，需要做全量审查
- 合并到主分支前

**可选：**
- 复杂重构完成后
- 复杂 bug 修复后
- 需要独立视角做质量把关时

---

## 工作流定位

- 上游：`exec-plan-runner`（已完成 batch 内审查）
- 本 Skill：做收尾阶段全量审查编排
- 下游：`receiving-code-review`（评估与采纳反馈）→ `verification-before-completion` → `dev-docs-maintain`
