# Knowledge Bundle 变更记录

## 2026-11-11

- 先完成 [Matt 主干融合设计](specs/2026-11-11-matt-power-agent-fusion.md)与[迁移计划](exec-plans/active/2026-11-11-matt-power-agent-fusion/plan.md)；随后用户批准本地实施。
- [ADR-0012](adr/0012-matt-led-skill-fusion.md)取代旧独立安装/调用政策：25 项整包能力、按需具名组合、POD 融合 TDD、唯一 tracker 与授权内连续推进。当前文档和分发随实现切换，验证以实际记录为准。
- 已运行的结构、隔离安装及代表性行为检查见[本地验证记录](exec-plans/active/2026-11-11-matt-power-agent-fusion/validation.md)；模型追问、歧义处理和生成向导的失败及未验证面均单独列出。

## 2026-09-07

- 新增 [知识导航初始化与演进决策](adr/0011-knowledge-navigation-lifecycle.md)，记录当时的能力边界；该决定的调用政策已由 ADR-0012 取代，历史正文保留。
