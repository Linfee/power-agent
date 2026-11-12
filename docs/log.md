# Knowledge Bundle 变更记录

## 2026-11-12

- 按当前 0.2.0 的 Skill、实现与元数据，将 ADR-0001 至 0013 归并为 [ADR-0014](adr/0014-current-baseline.md)；旧记录移入 `adr/archive/`，保留历史正文、原取代链和与新基线的双向关系。
- 当前架构、工作方式、开发、Harness 与 Skill 设计统一指向新基线；融合设计和早期评估移入[历史资料](archive/index.md)，旧 `active/` 计划移入[计划归档](exec-plans/README.md)，不据此宣布计划已完成。
- 修正仍宣称只有一个手动 Skill 的判据及 OMP 安装来源限制；这次维护不改变 Skill 调用策略、hook 行为或用户安装，不创建或刷新验证 ledger。
- 修正文档扫描器不识别多条 ADR 取代关系的问题，保留单条路径写法和逐条双向校验；验证登记流程不变。

## 2026-11-11

- 先完成 [Matt 主干融合设计](archive/2026-11-11-matt-power-agent-fusion.md)与[迁移计划](exec-plans/archive/2026-11-11-matt-power-agent-fusion/plan.md)；随后用户批准本地实施。
- [ADR-0012](adr/archive/0012-matt-led-skill-fusion.md)取代旧独立安装/调用政策：25 项整包能力、按需具名组合、POD 融合 TDD、唯一 tracker 与授权内连续推进。该记录现已归档，当前基线见 ADR-0014。
- 当时运行的结构、隔离安装及代表性行为检查保存在[历史验证记录](exec-plans/archive/2026-11-11-matt-power-agent-fusion/validation.md)；其失败、版本和未验证面仍保留，不外推到当前安装。
- 按用户后续要求原样恢复 `grilling` 与 `grill-with-docs` 的 Matt 固定版本正文及调用元数据；后者回到手动调用，前者保留问题树逐轮访谈与用户共同理解确认。同步现行入口与设计，不改其他 Skill 正文。
- 进一步按 Matt 原版内容深度重整其余 20 个对应入口及 references，补回实操方法、理由、反例、示例与模板；轻量化不再以正文或参考文件更短为目标。保留已确认融合差异和两个原版讨论入口，同步[设计判据](skill-and-harness-design.md#以-matt-原版为内容底稿)及[历史来源覆盖与验证](exec-plans/archive/2026-11-11-matt-power-agent-fusion/validation.md#原版内容深度重整)。

## 2026-09-07

- 新增 [知识导航初始化与演进决策](adr/archive/0011-knowledge-navigation-lifecycle.md)，记录当时的能力边界；该决定后经 ADR-0012 更新，现与其他旧决定归并至 ADR-0014，历史正文保留。
