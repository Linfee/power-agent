---
name: harness-engineering-review
description: Use when auditing a project's agent workflow, AGENTS.md structure, or development practices against OpenAI's Harness Engineering best practices. Triggers when user mentions "agent best practices", "AGENTS.md review", "workflow audit", "harness engineering", "知识库结构", "agent工作流审查", "最佳实践检查".
---

# Harness Engineering Review

基于 OpenAI 团队的 Harness Engineering 实践经验，审查项目和工作流中不符合最佳实践的部分，并给出调整方案。

**原文参考：** [Harness engineering: leveraging Codex in an agent-first world](https://openai.com/index/harness-engineering/) — Ryan Lopopolo, OpenAI, Feb 11, 2026

## 核心原则

**人类掌舵，Agent 执行。** 人类的角色是设计环境、明确意图、构建反馈循环，而非直接写代码。

## 审查维度

执行审查时，依次检查以下六个维度，为每个维度打分（优/需改进/缺失），并列出具体问题和建议。

---

### 1. AGENTS.md 结构（Context Management）

**目标：** AGENTS.md 应是简短的"目录"（~100行），而非百科全书。

检查项：
- [ ] AGENTS.md 是否超过 150 行？（超过则需拆分）
- [ ] 是否将具体规则、架构细节、历史决策堆砌在同一文件？
- [ ] 是否存在 `docs/` 或类似结构化知识库，承接具体细节？
- [ ] 是否有指向更深层文档的明确指针？

**反模式识别：**
- 一个包含所有内容的巨型 AGENTS.md → 上下文拥挤、重点丢失、极易腐化
- 每条规则都标为"重要" → 当所有事情都重要，就没有什么重要

**建议方案：** 将 AGENTS.md 重构为目录结构，具体规则下沉到：
```
docs/
├── architecture.md      # 系统架构与模块依赖
├── frontend.md          # 前端规范
├── security.md          # 安全规范
├── design-decisions/    # 重要决策记录
└── exec-plans/          # 执行计划
    ├── active/
    └── completed/
```

---

### 2. Agent 可见性（Agent Legibility）

**目标：** Agent 看不到的东西等同于不存在。所有上下文必须版本化、存储在仓库中。

检查项：
- [ ] 重要决策是否记录在 Slack/邮件/人脑中而非仓库文件？
- [ ] 项目背景、架构理由是否有 markdown 文档化？
- [ ] 错误日志、应用状态是否可被工具直接捕获？
- [ ] 是否有 `memories.md` 或等效机制沉淀知识？

**反模式识别：**
- 口头协议的架构决策
- 只存在于聊天记录中的"为什么这样设计"

**建议方案：** 每次重大决策后，立即将结论写入对应文档并提交到仓库。把"新同事入职能否只靠仓库理解全局"作为检验标准。

---

### 3. 约束机制化（Enforced Architecture & Taste）

**目标：** 用 Linter/Test 强制执行规范，而非靠 Prompt 啰嗦。

检查项：
- [ ] 核心规范是否只写在 Prompt/AGENTS.md 中？（低效）
- [ ] 是否有 Linter 规则、结构化测试来机械化执行约束？
- [ ] Linter 报错信息是否对 Agent 友好（含修复建议）？
- [ ] 是否定义了模块依赖方向并机械化验证？

**反模式识别：**
- 在 AGENTS.md 中写 50 条"你应该怎样写代码"的规则
- 没有测试覆盖的"黄金原则"

**建议方案：**
- 将高频规范转化为自定义 Linter 规则
- Linter 错误信息直接告知修复方式（Agent 能直接执行）
- 建立层级依赖规则（如 Types → Config → Service → UI）并测试

---

### 4. 反馈循环质量（Feedback Loop）

**目标：** Agent 应能自己运行应用、捕获错误、验证修复，形成闭环。

检查项：
- [ ] 是否有工具让 Agent 运行并观察应用状态（日志/UI/测试结果）？
- [ ] 复杂任务是否有执行计划（exec-plans）追踪进度？
- [ ] PR 是否有 Agent 自审步骤（code review）后再提交人工审核？
- [ ] 是否支持 git worktree 级别的隔离测试环境？

**建议方案：** 在工作流中固化：
1. Agent 提交前必须跑 lint + test
2. 委派 `code-reviewer` 子代理进行代码审查
3. 复杂特性使用 exec-plans 追踪

---

### 5. 知识维护（Documentation Gardening）

**目标：** 文档必须与代码同步，防止腐化。

检查项：
- [ ] 是否存在只描述"计划"而非"现状"的过期文档？
- [ ] 是否有机制定期扫描和更新文档（harness-doc-gardening）？
- [ ] 决策文档是否有"验证状态"标记？
- [ ] 已完成的执行计划是否归档？

**建议方案：** 定期运行 `knowledge-architect` 代理，根据代码现状更新文档；在文档顶部注明最后验证时间。

---

### 6. 技术债管理（Garbage Collection）

**目标：** 连续小增量偿还技术债，而非等待大爆发。

检查项：
- [ ] 是否有 AI 生成的重复代码/不一致模式（AI slop）？
- [ ] 是否有"黄金原则"列表（golden principles）来防止模式漂移？
- [ ] 是否定期运行代码清理任务？

**黄金原则示例（可定制）：**
- 优先使用共享工具包，而非手写同类 helper
- 所有边界数据必须验证/解析，不允许 YOLO 读取
- 不超过 X 行的文件大小限制

---

## 审查报告格式

完成审查后，输出以下格式：

```
## Harness Engineering 审查报告

### 总体评分
| 维度 | 状态 | 优先级 |
|------|------|--------|
| AGENTS.md 结构 | ✅优 / ⚠️需改进 / ❌缺失 | 高/中/低 |
| Agent 可见性 | ... | ... |
| 约束机制化 | ... | ... |
| 反馈循环质量 | ... | ... |
| 知识维护 | ... | ... |
| 技术债管理 | ... | ... |

### 高优先级问题
1. [问题描述] → [具体调整方案]

### 中优先级问题
...

### 建议的下一步行动（按优先级）
1. 立即可做（<1天）：...
2. 本周内（1-5天）：...
3. 持续习惯：...
```

## 使用方式

用户提供以下任意内容，即可开始审查：
- AGENTS.md 文件路径或内容
- 项目目录结构（`ls` 或 `tree` 输出）
- 描述当前工作流

若用户未提供，主动询问以下信息：
1. AGENTS.md 当前内容
2. 项目是否有 `docs/` 或知识库目录
3. 当前代码审查和 lint 流程
