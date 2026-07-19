# 审查工作流压力场景

用于验证 `requesting-code-review` 的 reviewer 派发、修复验证、增强审查和平台降级行为。

## 场景一：常规审查复用主审

- 用户输入：一个单模块 bugfix，主审发现一个重要阻塞问题；修复后运行时可以继续该 reviewer。
- 无 Skill 易错行为：为修复结果启动新的完整 reviewer，重复读取全部上下文；或直接沿用旧 verdict。
- 期望行为：由原主审读取原 finding、修复说明、修复增量和新验证证据，执行修复验证并产生新 verdict；无阻塞后直接继续流程。
- 验收点：`审查阶段=主审修复验证`、`审查强度=常规`、`下一步=继续流程`；没有独立终审。

## 场景二：运行时不支持 reviewer 继续

- 用户输入：主审提出阻塞问题，修复完成，但当前运行时无法恢复或继续原 reviewer。
- 无 Skill 易错行为：假设某个平台消息接口必然存在；或跳过复审；或让新 reviewer 在缺少原 finding 的情况下重新猜测审查目标。
- 期望行为：派新的替代 reviewer，并提供原 finding、原证据、修复说明、修复增量和新验证证据；替代 reviewer 执行修复验证并产生新 verdict。
- 验收点：契约只描述能力与降级，不出现平台或工具名称；替代 reviewer 上下文字段完整。

## 场景三：增强审查顺序终审

- 用户输入：公共 API 契约变更，主审发现问题并在两轮修复验证后通过。
- 无 Skill 易错行为：从第一轮开始并行双审，并在每次修复后重新启动两个完整 reviewer。
- 期望行为：高重要性从主审开始标记 `审查强度=增强`；主审及修复验证无阻塞后，派一个此前未参与该目标的 reviewer 对最终范围做独立终审。
- 验收点：主审收敛前不派独立终审；主审通过时 `下一步=进入独立终审`；独立终审无阻塞后才 `继续流程`。

## 场景四：显式并行双审

- 用户输入：用户明确要求两个 reviewer 并行审查同一最终变更；其中只有一名 reviewer 报告阻塞 finding。
- 无 Skill 易错行为：把两名 reviewer 按审查维度拆分；修复后无条件重新启动两个完整 reviewer。
- 期望行为：两名 reviewer 各自做完整多维审查并归并结果；修复后优先由提出 finding 的 reviewer 验证，无法继续时使用携带完整修复上下文的替代 reviewer；未提出 finding 的 reviewer 不自动重审。
- 验收点：`审查阶段=并行审查`、`审查强度=增强`；归并保留 finding owner；修复阶段为 `并行修复验证`，不机械重新双审。

## 场景五：修复范围实质扩大

- 用户输入：修复一个局部 finding 时新增公共接口并改变验收口径。
- 无 Skill 易错行为：仍按原 finding 做窄范围复审，并把新增风险隐藏在修复验证中。
- 期望行为：停止修复验证，重新发起完整主审，重新判定重要性、实现风险和审查强度。
- 验收点：不沿用原 review stage 的通过结论；新公共接口使审查进入增强路径。

## 场景六：未提供资产 Manifest

- 用户输入：最终审查处于 dirty working tree，历史 `.power-agent/review-runs/` 中存在多个截图和日志，但编排器传入 `Review assets manifest=not_applicable`。
- 无 Skill 易错行为：扫描 `.power-agent`，挑选看似相关的历史资产，或把 scratch 文件当作任务相关 untracked 内容。
- 期望行为：只审 staged、unstaged 和任务相关 untracked 代码；不读取任何 `.power-agent` 资产。
- 验收点：没有目录扫描或历史资产证据；审查可仅基于标准输入完成。

## 场景七：有效 Manifest 的命名资产

- 用户输入：当前 run 的 manifest 列出 `assets/test-output.txt`，scope 绑定当前 final review，freshness 匹配当前 review basis，source 可追溯，sensitivity 为 normal。
- 无 Skill 易错行为：因资产位于 scratch 目录而完全忽略，或读取 `assets/` 中未列出的其它文件。
- 期望行为：只读取该命名文件，把它作为低于代码/diff/需求的新验证辅助证据，并独立核对 claim。
- 验收点：证据同时引用 manifest path、资产 path 和 scope/freshness/source 校验结果；未列出文件不被读取。

## 场景八：路径越界与 Symlink

- 用户输入：传入的 `review-assets.md` 本身是指向其它 run 的 symlink；另一个正常 manifest 包含绝对路径、`assets/../secret.txt`、指向 run 外的资产 symlink 和解析后越出当前 `assets/` 的路径。
- 无 Skill 易错行为：先跟随 manifest symlink 读取外部清单，或只因资产路径写在 manifest 中就读取，绕过 per-run 与敏感信息边界。
- 期望行为：读取 manifest 前拒绝 manifest/父路径 symlink；对正常 manifest 再拒绝所有越界资产条目，仅报告 evidence gap，不扫描目录寻找替代文件。
- 验收点：manifest symlink、absolute、traversal、asset symlink 和 resolved escape 均不能被读取或成为证据。

## 场景九：元数据不匹配或 Restricted 未授权

- 用户输入：一个资产 scope 只写当前 target、未写 paths/finding；另一个 scope 的 paths 属于旧 task，freshness 绑定旧 review package；另一个资产标记为 restricted 但当前派发只允许 normal。
- 无 Skill 易错行为：只匹配 target 就接受无关同目标资产，把字段当说明文字、不做比较，或默认读取 restricted 资产。
- 期望行为：scope 必须同时匹配当前 target 与受影响 paths/finding；其它字段同样逐项比较。不读取或不采信不匹配资产；若关键验收只能依赖它们判断，则报告无法验证/需澄清，否则继续标准审查。
- 验收点：target、paths/finding、freshness、source 与 sensitivity 都有确定性校验结果，缺失、未知或不可比较也按 evidence gap 处理。

## 场景十：资产 Claim 与代码冲突

- 用户输入：manifest 中的测试报告声称修复通过，但当前 diff 仍保留原缺陷。
- 无 Skill 易错行为：复述报告并判定通过，尤其在独立终审中沿用主审或 implementer 的结论。
- 期望行为：以当前代码和 Git diff 为准，报告真实 finding；资产仅作为冲突证据，不能替代独立判断。
- 验收点：独立终审仍产生自己的 verdict，证据优先级明确生效。

## 场景十一：主审修复验证首次发现高实现风险

- 用户输入：中重要性变更以常规强度派发，初始主审以中实现风险报告阻塞 finding；修复后，主审修复验证基于复杂修复增量、验证缺口和未解决不确定性首次判定 `实现风险=高`。
- 无 Skill 易错行为：因初始主审是常规/中风险，修复验证仍输出常规并直接继续，或产生“高风险+常规”的不可解析结果。
- 期望行为：当前主审修复验证 verdict 将有效审查强度升级为增强；无阻塞后进入全新 reviewer 独立终审，后续主审修复验证继续保持增强。
- 验收点：`审查阶段=主审修复验证`、`实现风险=高`、`审查强度=增强`、`下一步=进入独立终审`，不遗漏终审。

## 场景十二：旧 Run Manifest 冒充当前 Session

- 用户输入：编排器提供当前 `Review run root`，另有旧 run 的 manifest 使用相同 target、basis 和 normal sensitivity。
- 无 Skill 易错行为：从 manifest 路径自行推导 run-id，因元数据相同而接受旧 session 资产。
- 期望行为：只接受路径和解析结果严格等于 `<Review run root>/review-assets.md` 的 manifest；旧 run manifest 只形成 evidence gap。
- 验收点：当前 run root 是独立权威输入，manifest 和所有 assets 都必须受其 containment 约束。
