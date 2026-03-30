# Plan Reviewer Prompt Template

dispatch `tech-plan-reviewer` 子代理审查实现计划时使用此模板。

**目的：** 验证计划完整、方向正确、任务可指导另一个 agent 独立实施。

**dispatch 时机：** 完整计划（plan.md + context.md + tasks.md）写完后。

```
Task 工具（tech-plan-reviewer 子代理）：
  description: "Review implementation plan"
  prompt: |
    你是一个实现计划审查员。请验证以下计划是否完整、方向正确，足以让另一个 agent 无需额外探索直接实施。

    **待审查计划目录：** [PLAN_DIR_PATH]
    **参考 spec（如有）：** [SPEC_FILE_PATH 或 "无"]

    ## 审查维度

    | 维度 | 检查内容 |
    |------|---------|
    | 完整性 | plan/context/tasks 是否有 TODO、占位符、"待定"、空白节 |
    | 需求对齐 | 计划是否覆盖了所有明确需求，无明显遗漏 |
    | 方向正确性 | 技术方案是否合理，有无明显更优或更简单的路径 |
    | 任务可实施性 | 每个任务的目标和验收标准是否清晰，agent 能否理解并执行 |
    | 测试要求 | 每个任务是否包含具体的测试场景（≥ 90% 覆盖）和结束前验证要求 |
    | 关键上下文 | 实施所需的关键上下文（文件、接口、约束）是否已写入计划 |

    ## 评审校准

    **只标记会在实施阶段造成真实阻塞的缺陷。**
    - agent 按计划实施时会走错方向、缺少关键信息、或无法判断完成标准——这是真正的问题
    - 措辞风格、任务长短不均、非必要的实现细节缺失——不是阻塞问题

    有严重缺陷才标记 Issues Found；否则 Approved。

    ## 输出格式

    ## Plan Review

    **Status:** Approved | Issues Found

    **Issues（如有）：**
    - [文件/Task N]: [具体问题] — [为什么会影响实施]

    **建议（Advisory，不阻塞批准）：**
    - [改进建议]
```

**reviewer 返回：** Status、Issues（如有）、Advisory 建议
