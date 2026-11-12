# Skill 调用机制

这是 `writing-for-agents` 的 Skill 专用分支：frontmatter、调用方式与 router skill。其余写法见 [主文件](../SKILL.md)。

## 调用方式

两种选择，交换两种负载：

- **模型可调用**的 Skill 保留 `description`，Agent 可自主触发，其他 Skill 也能到达它。人仍可输入名字：模型可调用总是**包含**人的可达性；description 只增加 Agent 的发现能力，从不移除人的。description 是该 Skill 的顶层上下文指针，被迫常驻：用永久上下文负载换发现性。内容全是参考的模型可调用 Skill 也是共享参考的一个家：其他 Skill 可以调用它，于是多个 Skill 需要的参考只放一处。机制：省略 `disable-model-invocation`，写面向模型的 description，携带触发分支（主文件的指针写法完全适用）。
- **用户可调用**的 Skill 把 description 从 Agent 的可达范围去掉：只有人输入名字才能调用，其他 Skill 也不行。零上下文负载，但花认知负载：你就是那个必须记住它存在的索引。机制：设置 `disable-model-invocation: true`；description 转为面向人：一行摘要，去掉触发词列表。

只有在 Agent 必须自行到达该 Skill，或其他 Skill 必须到达它时，才选模型可调用。如果它只会被手动触发，就做成用户可调用，不付上下文负载。

两个用户可调用 Skill 都需要的共享参考，不能放在任何一边：没有 description，两者都无法触发对方。把它推到 Skill 系统之外的普通文件：任何 Skill 都能指向的外部参考。

## 按调用方式拆分

拆分的调用切分（顺序切分在主文件）：当你有一个应当独立触发它的独特引导词（你实际会在提示词里用的触发词），或其他 Skill 必须到达它时，拆出一个模型可调用 Skill。你要为新的常驻 description 付上下文负载，所以独立可达性必须值这个价。

## Router skill

当用户可调用 Skill 多到记不住时，堆积的认知负载用 **router skill** 治：一个用户可调用的 Skill，点名其他 Skill 以及何时用哪个，让人只需记住一个而不是许多。它只能提示，永远不能触发它们：用户可调用 Skill 没有 description，除了人，没有东西能到达它们。

不同宿主的开关与发现行为可能不同（例如 Codex 的 `agents/openai.yaml`），以目标宿主和版本为准，不把元数据当通用访问控制。名称、描述或调用方式变化时同步项目入口与直接消费者，分别验证模型发现、用户显式调用和依赖可达性。
