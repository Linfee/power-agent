# 词汇表格式

首先使用已有领域文档、CONTEXT 或 glossary 中承担该职责的位置，沿用其格式，不双写定义。以下是无既有约定时的轻量默认；只有出现已确认、值得未来复用的术语且获授权写入时才创建，不预建空文件。

## 单一上下文

默认在仓库根目录建立 `GLOSSARY.md`，简要描述上下文，并在自然分组下列出术语：

```md
# Ordering

接收和跟踪客户订单的业务上下文。

## Language

**Order**：客户提出的一组待履行购买请求。
_Avoid_：Transaction

**Customer**：提出订单的个人或组织。

**Invoice**：交付后向客户发出的付款请求。
_Avoid_：Bill, payment request
```

定义保持简短，表达概念是什么及必要的领域关系或不变量；同义名称存在歧义时注明首选与避免词。只记录项目领域特有概念，不填充通用编程术语，也不把词汇表写成实现计划。

为同一概念选择一个首选词，并在有实际歧义时列出应避免的同义词。通常用一两句话定义“它是什么”，需要时补充领域关系；不要把超时、错误类型或工具模式等通用编程概念塞进词汇表。术语自然形成多个主题时可按小标题分组；只有一个内聚主题时平铺即可。

## 多个上下文

先读取既有地图或领域导航，按真实业务边界定位定义。不同上下文中的同名概念可以分别定义，并解释关系；不将不同含义合并成一条全局定义。只有多个真实上下文且现有导航不足时，才按需建立 `GLOSSARY-MAP.md`，链接实际存在的领域文档并说明职责及关系；不强制每个上下文新增文件或 ADR 目录。不确定概念归属且查证无法解决时再问用户。

例如，确有 Ordering、Fulfillment、Billing 三个业务上下文且需要一张地图时，可以在项目已有导航中表达：

```md
# Glossary Map

## Contexts
- [Ordering](./src/ordering/GLOSSARY.md)：接收和跟踪订单
- [Fulfillment](./src/fulfillment/GLOSSARY.md)：管理仓库拣货和发货
- [Billing](./src/billing/GLOSSARY.md)：生成发票和处理付款

## Relationships
- Ordering → Fulfillment：前者发出 `OrderPlaced`，后者据此开始拣货。
- Fulfillment → Billing：前者发出 `ShipmentDispatched`，后者据此生成发票。
- Ordering ↔ Billing：共享 `CustomerId` 和 `Money` 的含义。
```

这些路径和事件只是示例，地图只描述实际存在的上下文及关系；若项目已有 CONTEXT 地图或其他权威入口，就在那里补充，不另建一份 glossary 地图。

若目标位置处于项目的 Knowledge Bundle，按 [dev-docs](../../dev-docs/SKILL.md) 的项目 profile 补齐适用的元数据；上面示例不是 Bundle 的完整文件模板。
