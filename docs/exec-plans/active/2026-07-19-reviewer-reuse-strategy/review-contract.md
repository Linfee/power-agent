---
type: Review Contract
scope:
  - code-review-workflow
---

# Reviewer 复用与风险分层审查 Review Contract

## Intent

- 将增强审查从默认双 reviewer 改为顺序策略：单主审多维审查、同 reviewer 优先验证修复、高重要性或高实现风险稳定后由全新 reviewer 独立终审。
- 保持平台无关；不支持 reviewer 继续时必须降级为新的替代 reviewer。
- Reviewer 通过当前 review session 的显式 manifest 使用 `.power-agent` 辅助资产；无 manifest 时不得扫描目录，资产不替代代码、diff、需求或新鲜验证。

## Scope

### In Scope
- `requesting-code-review` 主契约和 references。
- `receiving-code-review`、`plan-impl` 和项目级子代理生命周期规则，包括新增 ADR supersede ADR-0002。
- architecture、workflow、development、harness-engineering 和压力场景同步。
- per-run `review-assets.md`、`assets/`、内部/最终 reviewer manifest 输入与资产压力场景。

### Out of Scope
- 具体平台的 agent/message API。
- 实现或修复子代理复用。
- 规划阶段 reviewer Gate 和重要性/实现风险边界重定义。
- 全局共享 `.power-agent/assets/` 池和跨 review session 资产复用。

## Acceptance

- [ ] 一个 reviewer 明确负责完整多维主审，多维审查不再等同于默认多个 reviewer。
- [ ] 常规审查在主审及修复验证无阻塞后通过，不启动独立终审。
- [ ] 高重要性或高实现风险仅在主审收敛后启动一个此前未参与该目标审查的独立 reviewer 全量终审。
- [ ] 修复后优先由提出 finding 的同一 reviewer 产生新修复验证结论；不能继续同一 reviewer 时，新 reviewer 获得原 finding、修复说明、修复增量和验证证据后执行替代复审。
- [ ] Skill 契约不出现 OMP、Codex、Claude Code 或具体 agent/message 工具名称。
- [ ] 范围实质扩大、验收改变或风险升级触发新的完整审查，而不是继续窄范围复审。
- [ ] 显式并行双审仍有归并规则，但不再是高重要性或高实现风险默认路径。
- [ ] 新增 ADR-0007 supersede ADR-0002；ADR-0002 保留正文历史但改为 `status: superseded` 并以 `superseded_by` 指向 ADR-0007；所有直接引用同步到新决策。
- [ ] 每个 review session 可选提供 `review-assets.md`，至少声明 path、kind、purpose、scope、freshness、source，可选 sensitivity。
- [ ] 编排器显式提供当前 review session 的权威 run root；manifest 的路径和解析结果必须严格等于该 root 下的 `review-assets.md`。`path` 仅允许 root 的 `assets/` 内普通文件相对路径；旧 run、绝对路径、`..` traversal、manifest/asset symlink 和解析后越界目标都不得读取。
- [ ] scope 必须同时匹配当前 task/batch/final review 目标及适用 `paths=` 或 `finding=`；freshness 必须绑定 reviewer 可比较的当前 review basis（内部 review package、commit range 或编排器提供的 working-tree snapshot 标识）；source 必须给出可追溯生产者和生成命令、报告或原始证据引用。
- [ ] sensitivity 缺省为 `normal`；`restricted` 只有当前派发显式授权时可读。manifest 为 `not_applicable` 时不扫描 `.power-agent`。
- [ ] 字段缺失、未知、不可比较、不匹配，或文件缺失、越界、过期、未获授权时，不读取或不采信资产，只报告 evidence gap；不得扩大目录读取范围。
- [ ] 代码/Git diff、需求/exec-plan 和新鲜验证的事实优先于 report 与辅助 assets。

## Agent 自主边界

- 可自由决策：manifest 字段的 Markdown 表达、kind 枚举和压力场景组织；不得改变 path/scope/freshness/source/sensitivity 的最小校验语义。
- 不可自行决策：建立全局资产池、允许目录扫描、接受绝对/traversal/symlink/解析后越界路径、跨 session 复用资产、默认读取 restricted 资产、持久化敏感内容或绑定平台工具。
- 必须保持的不变量：原 reviewer 复验与增强独立终审语义不变；低/中重要性的初始主审或主审修复验证判定高实现风险时，当前有效强度升级为增强并进入独立终审；reviewer 只读权威当前 run 内显式命名且通过 target+paths/finding 等校验的资产；无 manifest 不扫描；无可比较 review basis 不采信 freshness；资产只是辅助证据。

## Proof

- 主证明：原审查场景继续成立，并新增场景证明低/中重要性的初始主审或主审修复验证发现高实现风险时升级增强且不遗漏独立终审；无 manifest 不扫描；有效 manifest 只读权威当前 run `assets/` 普通文件；旧 run、manifest/asset symlink、绝对/traversal/解析后越界、target+paths/finding 或其它字段不匹配与未授权 restricted 资产拒绝读取/采信；最终 reviewer 保持独立判断。
- 次证明：manifest 字段最小语义、权威 run root 与 containment、当前 review basis 输入、reference 路径、平台耦合排除、文档一致性和独立最终审查。
- 非证明：只检查 manifest 文件存在或扫描整个 `.power-agent`。
- 已知未验证面：不执行真实跨平台 sub-agent 生命周期和多媒体资产渲染 eval。

## Blockers / Escalation

遇到以下情况必须停止并请求确认：

- 必须依赖某个平台私有工具才能实现同 reviewer 复审语义。
- 需要破坏现有上下游状态协议才能表达新流程。
- 无法保证增强审查独立终审 reviewer 未参与此前审查。

## Risks

- 风险：同 reviewer 复审产生确认偏差。
  - 决策状态：已由用户确认通过增强审查独立终审缓解。
  - 缓解方式：复审检查修复增量和影响边界；增强审查最终由全新 reviewer 全量审查。
  - 执行期阻塞条件：修复范围实质扩大、验收改变或引入新的高风险边界时重新完整审查。
- 风险：运行时不支持继续已完成 reviewer。
  - 决策状态：已由用户确认采用新 reviewer 回退。
  - 缓解方式：替代 reviewer 接收原 finding、修复说明、相关 diff 和验证证据。
  - 执行期阻塞条件：无法向替代 reviewer 提供足以产生新 verdict 的上下文。
- 风险：manifest 误引用旧 run、目录外文件或敏感资产。
  - 决策状态：通过 per-run 相对路径、freshness/source/sensitivity 字段和拒绝规则闭合。
  - 缓解方式：只读取 manifest 明确列出的同 run 路径；不满足约束时报告证据缺口。
  - 执行期阻塞条件：需要读取未列出、跨 run 或 sensitivity 不允许的资产才能完成审查。

## Plan Review Gate

- Gate Revision：r2
- Plan Risk：medium
- Review Path：self-review + independent reviewer
- Plan Review Status：APPROVED
- Independent Review：approved
- Independent Review Basis：gate_revision=r2; kind=independent-review; record=history://ReviewAssetsPlanR2

## Plan Review History

### Gate Revision r1

- Gate Revision：r1
- Independent Review：approved
- Independent Review Basis：gate_revision=r1; kind=independent-review; record=history://FinalReusePlanReview

### Gate Revision r2

- Gate Revision：r2
- Independent Review：approved
- Independent Review Basis：gate_revision=r2; kind=independent-review; record=history://ReviewAssetsPlanR2

## Review Focus

- 顺序增强审查是否降低重复成本并保留高影响/高实现风险的独立视角。
- reviewer 继续规则是否能力导向、平台无关且有新 reviewer 回退。
- 内部审查、最终审查、反馈处理和项目级子代理规则是否一致。
- Review Assets Manifest 是否保持 per-run、显式命名、只读、可选与平台无关，并有无 manifest 时禁止扫描的确定性降级。
