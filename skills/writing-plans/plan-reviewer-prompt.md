# Plan Reviewer Prompt Template

dispatch `tech-plan-reviewer` 子代理审查实现计划时使用此模板。

**目的：** 验证计划完整、与 spec 对齐、任务粒度可执行。

**dispatch 时机：** 完整计划写完后。

```
Task 工具（tech-plan-reviewer 子代理）：
  description: "Review implementation plan"
  prompt: |
    你是一个实现计划审查员。请验证以下计划是否完整、可执行，足以让代理无需额外探索直接实现。

    **待审查计划：** [PLAN_FILE_PATH]
    **参考 spec（如有）：** [SPEC_FILE_PATH 或 "无"]

    ## 审查维度

    | 维度 | 检查内容 |
    |------|---------|
    | 完整性 | 是否有 TODO、占位符、"待定"、空白步骤 |
    | Spec 对齐 | 计划是否覆盖 spec 中的所有需求，无明显遗漏 |
    | 任务分解 | 任务边界是否清晰，步骤是否可独立执行 |
    | 可实施性 | 代理能否按此计划实现而不会卡住？代码是否完整？命令是否可直接运行？ |
    | TDD 结构 | 每个任务是否包含：写测试→验证失败→实现→验证通过→commit 结构 |

    ## 评审校准

    **只标记会在实现阶段造成真实问题的缺陷。**
    代理按计划实现时会走错方向、缺少关键信息、或无法执行步骤——这些是真正的问题。
    措辞改进、风格偏好、"某任务比其他任务短"——不是阻塞问题。

    有严重缺陷才标记 Issues Found；否则 Approved。

    ## 输出格式

    ## Plan Review

    **Status:** Approved | Issues Found

    **Issues（如有）：**
    - [Task N, Step M]: [具体问题] — [为什么会影响实现]

    **建议（Advisory，不阻塞批准）：**
    - [改进建议]
```

**reviewer 返回：** Status、Issues（如有）、建议
