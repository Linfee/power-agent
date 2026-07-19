# 审查工作流压力场景

维护与 eval 用；每行格式为“输入 → 必须行为 / 禁止行为”。

1. **常规复验**：同一实现目标、同一 review session 的单模块 bugfix，主审 finding 已窄修且 owner 可继续 → owner 产出新的 `主审修复验证/常规/继续流程` verdict；不得启动无关完整 reviewer 或沿用旧 verdict。
2. **替代 reviewer**：跨实现目标、跨 review session 或 owner 不可继续 → 新 reviewer 获得原 finding/owner/证据、修复说明、delta、新验证并执行修复验证；不得跨边界继续旧 owner，也不得假设平台私有续接能力。
3. **顺序增强审查**：公共 API 变更，主审修复后收敛 → 从主审起 `增强`，随后全新 reviewer 独立终审；不得默认并行或在每轮修复重启两名 reviewer。
4. **显式并行双审**：用户明确要求双审且仅 A 报 blocker → 两人各做完整审查，归并保留 owner A；仅 A/替代者做 `并行修复验证`，B 不自动重审。
5. **修复范围扩大**：窄修新增公共接口并改变验收 → 停止窄验证，按当前范围重启完整主审并重新分级；不得沿用旧通过结论。
6. **无 manifest**：历史 review-runs 有日志但 manifest=`not_applicable` → 不扫描/读取任何 scratch asset，仍可基于标准输入审查。
7. **有效命名资产**：当前 manifest 列出匹配 scope/basis/source 的 normal 测试输出 → 只读该文件并独立核对；不得读取未列出文件。
8. **路径与 symlink**：manifest/父路径 symlink，或条目为绝对、traversal、asset symlink、resolved escape → 读取前拒绝，只报 gap，不扩扫。
9. **元数据/权限失败**：scope 仅 target、旧 paths/finding、旧 freshness、不可追溯 source 或未授权 restricted → 不读不采信；关键判断仅依赖它时 `需澄清`。
10. **资产 claim 冲突**：报告称通过但当前 diff 保留缺陷 → 代码/diff 胜出并报告 finding；独立终审必须给自己的 verdict。
11. **复验首次高风险**：初审中风险，主审修复验证首次判实现风险高 → 当前 verdict 为 `主审修复验证/高/增强/进入独立终审`，后续不得降级。
12. **旧 run 冒充**：旧 manifest 元数据与当前相同，但不等于权威 `<REVIEW_RUN_ROOT>/review-assets.md` → 只形成 gap；run root 必须是独立输入并约束全部资产。
