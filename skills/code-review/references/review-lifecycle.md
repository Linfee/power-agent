# 审查生命周期

- 同一实现目标、同一 review session 的窄修，且 finding owner 可继续时，由 owner 产出新的修复验证 verdict；不启动无关完整 reviewer，也不沿用旧 verdict。
- 跨实现目标、跨 review session 或 owner 不可继续时，新 reviewer 必须取得原 finding、修复说明、delta 和新验证后再复验。
- 公共 API 变更从初始主审即进入增强路径；主审及其修复验证收敛后，由全新 reviewer 独立终审；不默认并行或每轮重启双审。
- 用户明确要求双审时，两名 reviewer 各自完整审查；仅 finding owner 或替代者验证其 blocker。
- 窄修新增公共接口或改变验收时，停止窄验证，重新分级并启动完整主审。
- 无有效 manifest 时不得扫描 scratch asset；有效 manifest 只允许读取当前 run、匹配 scope/basis/source 的命名普通文件。
- manifest 或路径含 symlink、绝对路径、traversal、解析后越界、过期或未授权 restricted asset 时，拒绝读取并报告 evidence gap。
- 资产 claim 与当前代码或 diff 冲突时，以代码/diff 为准；独立终审必须给出自己的 verdict。
- 主审修复验证首次判定高实现风险时，进入增强独立终审，不得降级。
- 只有当前权威 `.power-agent/review-runs/<run-id>/review-assets.md` 可作为 run root 的 manifest；历史 run 或普通目录均不可替代。
