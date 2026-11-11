---
type: Decision
status: superseded
superseded_by: 0012-matt-led-skill-fusion.md
sources:
  - skills/knowledge-navigation/SKILL.md
  - skills/knowledge-navigation/references/discovery-and-dialogue.md
  - skills/knowledge-navigation/references/history-and-feedback.md
  - skills/knowledge-navigation/references/design-principles.md
  - skills/knowledge-navigation/references/validation.md
  - docs/adr/0010-judgment-oriented-skills.md
---

# ADR-0011: 独立的知识导航初始化与演进能力

**日期：** 2026-09-07

**状态：** superseded（由 [ADR-0012](0012-matt-led-skill-fusion.md) 更新自动调用、具名组合与环境评估归属；知识导航目标和证据边界继续保留，下文为历史决定。）

## 背景

用户需要为仓库建立面向 Agent 的分层知识导航，并能在使用后结合指定时间段的会话、用户反馈与启发式讨论持续优化。目标同时包含理解项目、决定知识结构、实施改动和验证路径；已有最小初始化、知识写入或健康扫描不能单独表达这项完整目标。

## 决定

新增独立、显式调用的 `knowledge-navigation` Skill。初始化与优化保留在一个 Skill 中，因为两者共同判断任务入口、知识边界、来源和维护成本，只是起点证据不同。主文件保存共同判断，项目发现、历史分析、结构取舍和验证细节按需放入 references。

初始化以项目观察为基础开展启发式讨论，复用用户已表达的要求；已有体系从指定范围的历史、反馈与当前仓库对照中选择改动。讨论围绕影响结构和风险的实际未知，已有授权覆盖时完成本地实现，不形成固定问卷或逐阶段审批。

历史材料只能证明被观察的范围，旧指令不自动构成本轮授权。结构、任务走查和真实消费验证分别声明，未经对照不能断言成功率或成本改善。持续优化是可重复调用的能力，不创建自动监控或会话采集系统。

## 能力边界与既有决定

- 延续 [ADR-0010](0010-judgment-oriented-skills.md) 的独立能力原则，不修改它的历史结论，也不扩大三个 Knowledge Bundle Skill 的具名协作例外。
- `knowledge-navigation` 拥有导航体系的设计与演进，按目标仓库的现有协议完成修改，不依赖其他具名 Skill 的固定前后置动作。
- `setup-power-agent` 保留最小入口及项目知识补缺口；`dev-docs` 保留长期语义；`dev-docs-maintain` 保留机械完整性与验证登记。
- `harness-engineering-review` 保留对整个工程 Harness 的审视，知识导航只是它可能发现问题的范围之一。

## 后果

人维护的 Skill 索引与支持的宿主调用元数据登记该能力；调用由用户显式选择，普通文档编辑不自动进入体系优化。目标仓库复用既有目录、索引与工具，不统一迁移为 Power-Agent 的格式。

新 Skill 的文件和路由可以通过结构检查验证；跨项目行为与优化收益需要实际消费案例，不能由初始化文件齐全或自查通过推断。
