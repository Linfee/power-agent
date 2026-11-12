---
type: Reference
scope:
  - exec-plans
---

# 执行计划目录

计划用于跨会话参照、人审或外部消费者，不是所有开发的前置条件。执行状态在项目选定的唯一 tracker；计划保存目标、关键决定、依赖、验收和状态源指针，不复制进度。研究、建议、内容和明确小任务不为形式进入本目录。

## 活动计划与历史

目前仓库内没有活动执行计划。执行状态在任务选定的 tracker；历史计划中的本地临时 tracker 指针只记录当时的位置，不保证仍可访问或恢复。

## 目录约定

`active/` 留给未来确有需要的仓内活动计划；`archive/` 保存不再作为活动状态的历史计划，不表示已经完成；`completed/` 保留此前记录为完成的历史。选择消费者确需的最小文件集合，不强制 review-contract、Gate 或任务卡。`YYYY-MM-DD-topic/` 是目录命名，不规定内容模板。

历史材料保留当时的状态、名称、格式和证据，不能当现行运行时指令。归档的计划包括[移除评测机制](archive/2026-08-03-remove-evaluation-mechanisms/plan.md)、[引入 codebase-design](archive/2026-08-03-codebase-design-skill/plan.md)和 [Matt 主干融合迁移](archive/2026-11-11-matt-power-agent-fusion/plan.md)；归档不改变或推断其原验收状态。
