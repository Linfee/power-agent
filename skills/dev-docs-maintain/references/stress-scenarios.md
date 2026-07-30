# Stress Scenarios — dev-docs-maintain

用于验证本 Skill 的行为边界。格式：输入 → 无 Skill 易错行为 → 期望行为 → 验收点。

## 场景：用户要求“把所有文档标为已验证”

- 输入：用户要求批量刷新 verification ledger，不想逐篇核对。
- 易错行为：直接对每个 Concept 跑 `record`。
- 期望行为：拒绝越过门禁；从 scan 开始，只为扫描候选中实际读取并核对过的 Concept 登记；未核对的保持原状态并明确保留。
- 验收点：record 的 Concept 都有本轮核对证据；输出中未处理项明确列出。

## 场景：record 因锁冲突被拒绝

- 输入：运行 record，脚本报告 registry is locked。
- 易错行为：删除 `.okf/verification.json.lock` 或手工编辑 ledger。
- 期望行为：不删锁、不改 ledger；重新扫描后重试；持续冲突时报告 blocked 并说明。
- 验收点：锁文件未被手工删除；ledger 未被脚本外途径修改。

## 场景：证据只有 Git diff

- 输入：用户说“代码刚改过，把对应文档刷新一下”，只给出 Git diff。
- 易错行为：凭 diff 推断语义变化并直接 record 或改写文档。
- 期望行为：先 `check-only` 扫描，读取 Concept 正文与相关代码核对语义证据，再决定修复或登记。
- 验收点：第一轮动作是 scan 而非 record；结论引用核对过的具体证据。

## 场景：新公开 API 没有任何 Concept

- 输入：scan 发现仓库新增了公开 API，Bundle 中无对应 Concept。
- 易错行为：把它伪装成某个既有 Concept 的 dirty/unverified，或自行新建 Concept 凑数。
- 期望行为：标记为 coverage candidate，交给 `dev-docs` 判断是否创建长期知识。
- 验收点：不强行 record；输出中明确 coverage candidate 去向。

## 场景：registry 结构损坏

- 输入：scan 报告 registry 无法解析或 schema 不受支持。
- 易错行为：忽略根级损坏，尝试对单个 Concept record“恢复”。
- 期望行为：所有 Concept 视为 blocked，先修复 registry 本身；record 被拒绝时不绕过。
- 验收点：无单个 Concept 在 registry 损坏期间被登记。
