---
name: requesting-code-review
description: 完成任务、实现主要功能或合并前使用，构建审查上下文并启动代码审查子代理。Triggers: '代码审查', 'code review', '请求审查', '合并前审查'.
---

# 请求代码审查

启动代码审查子代理，捕获问题。审查子代理获得精确构建的上下文——不是会话历史，而是刚好需要的信息。

**核心原则：** 尽早审查，经常审查。

---

## 何时请求

**必须：**
- exec-plan-runner 每个 batch 完成后
- 完成主要功能后
- 合并到 main 前

**可选：**
- 卡住时（新鲜视角）
- 重构前（基线检查）
- 修复复杂 bug 后

---

## 流程

### 1. 获取 Git SHA

```bash
BASE_SHA=$(git rev-parse HEAD~N)  # N = 本次任务的 commit 数
HEAD_SHA=$(git rev-parse HEAD)
# 或对比主分支
BASE_SHA=$(git rev-parse origin/main)
```

### 2. 构建审查上下文

为审查子代理准备：
- **实现内容**：刚构建了什么
- **规格/需求**：它应该做什么（引用 exec-plan 任务描述）
- **BASE_SHA / HEAD_SHA**：变更范围
- **关键文件**：涉及的主要文件

### 3. 启动审查子代理

```
Task 工具：
  description: "Code review: [task name]"
  prompt: |
    你是代码审查员。使用 receiving-code-review skill 评估以下变更。

    ## 实现内容
    [具体描述构建了什么]

    ## 规格要求
    [任务的验收标准，来自 exec-plan]

    ## 代码变更
    Base: [BASE_SHA]
    Head: [HEAD_SHA]
    主要文件：[文件列表]

    运行以下命令获取 diff：
    git diff [BASE_SHA]..[HEAD_SHA]

    ## 报告格式
    **规格符合性：** ✅ 通过 | ❌ [问题描述]
    **代码质量：** ✅ 通过 | ⚠️ [建议] | ❌ [问题]
    **Issues（阻塞）：** [具体问题 + 为何影响实现]
    **建议（Advisory）：** [非阻塞改进建议]
```

### 4. 根据反馈行动

| 严重级别 | 处理 |
|---------|------|
| 规格不符 | 立即修复（启动新修复子代理） |
| 代码质量问题 | 继续前修复 |
| Advisory 建议 | 记录，视情况处理 |
| 审查者有误 | 用技术推理推回（见 receiving-code-review） |

---

## 危险信号

- 因为"很简单"跳过审查
- 忽略规格不符问题
- 带未修复的阻塞问题继续下一任务
