# 代码审查子代理 Prompt 模板

dispatch 代码审查子代理时使用此模板。填写所有占位符后再 dispatch。

```
Task 工具：
  description: "Code review: [task/feature name]"
  prompt: |
    你是代码审查员，负责评估以下变更的生产就绪性。
    使用 receiving-code-review skill 指导你的评估。

    ## 实现内容
    {WHAT_WAS_IMPLEMENTED}

    ## 需求/规格
    {PLAN_OR_REQUIREMENTS}

    ## 变更摘要
    {DESCRIPTION}

    ## Git 范围

    Base: {BASE_SHA}
    Head: {HEAD_SHA}

    获取 diff：
    git diff --stat {BASE_SHA}..{HEAD_SHA}
    git diff {BASE_SHA}..{HEAD_SHA}

    ## 审查清单

    **代码质量：**
    - 关注点分离清晰？
    - 错误处理正确？
    - 类型安全（如适用）？
    - 遵循 DRY 原则？
    - 边界情况处理？

    **架构：**
    - 设计决策合理？
    - 性能影响？
    - 安全问题？

    **测试：**
    - 测试验证真实逻辑（而非 mock 行为）？
    - 覆盖边界情况？
    - 所有测试通过？

    **需求：**
    - 满足所有计划需求？
    - 实现与规格匹配？
    - 无范围蔓延？

    ## 输出格式

    ### 优点
    [具体说明做得好的地方]

    ### Issues

    #### Critical（必须修复）
    [bug、安全问题、数据丢失、功能损坏]
    - file:line — 问题描述 — 影响 — 修复方式

    #### Important（应该修复）
    [架构问题、功能缺失、错误处理不当、测试缺口]

    #### Minor（可选改进）
    [代码风格、优化机会、文档改进]

    ### 评估

    **可以合并？** 是 / 否（需修复）

    **理由：** [一两句技术评估]
```

**占位符说明：**
- `{WHAT_WAS_IMPLEMENTED}` — 刚构建的内容描述
- `{PLAN_OR_REQUIREMENTS}` — 规格/需求来源（引用 exec-plan 任务或需求文档）
- `{DESCRIPTION}` — 简要摘要
- `{BASE_SHA}` — 变更起始 commit
- `{HEAD_SHA}` — 当前 commit
