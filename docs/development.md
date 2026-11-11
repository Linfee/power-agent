---
type: Playbook
scope:
  - development
---

# 开发指南

Power-Agent 是 Matt 主干的整包工程 Skill，辅以项目知识与确定性脚本。宿主必须支持普通 sub-agent；插件声明、结构通过与真实宿主行为是不同证据。

## 结构与约定

`skills/<name>/SKILL.md` 为 25 个平铺入口，`references/` 放按需知识，`scripts/` 放确定性操作，`agents/openai.yaml` 是可选界面/调用元数据。`grill-with-docs` 按 Matt 原版手动调用，其余入口允许模型调用；具名依赖随整包分发，不承诺单独安装。`AGENTS.md` 为能力地图，`CLAUDE.md` 与 `GEMINI.md` 只转引入口。

Skill 名称用小写连字符且与目录一致；description 只负责可区分触发，正文教承重判断与实际方法。格式无需统一章节；确有外部消费者的 schema、授权顺序和安全协议保持准确。修改先确认行为缺口并复用现有模式。迁入内容以固定 Matt 原版为底稿，保留方法、解释、示例、反例和模板，只按确认的差异局部适配，不以更短为目标；具体对照规则见[设计指南](skill-and-harness-design.md#以-matt-原版为内容底稿)。

支持文件相对实际安装位置解析，业务项目可能没有 `skills/`；脚本收到明确业务目录后必须安全切换，切换失败不能回落旧 cwd。整包改名须迁移所有当前消费者和 manifest，不留旧 alias。

## 选择检查

|改动|直接检查|
|---|---|
|description|`python3 scripts/check-description-length.py`|
|名称、目录、调用方式、速查表|`bash scripts/check-invocation-consistency.sh`；修改检查器时运行 `bash scripts/test-check-invocation-consistency.sh`|
|入口、链接、锚点或明确脚本指针|`python3 scripts/check-skill-references.py`，可传路径限定；修改检查器时运行 `python3 scripts/test-check-skill-references.py`|
|scanner、freshness、ledger|`python3 -m unittest skills/dev-docs-maintain/scripts/test_bundle_status.py`|
|可选审查 package/workspace CLI|`bash skills/implement/scripts/test-review-package.sh`|
|wizard 输入、确认与中断清理|`python3 skills/wizard/scripts/test-template.py`；`bash -n skills/wizard/scripts/template.sh`|
|plugin 或 marketplace|`claude plugin validate . --strict`，另做本地隔离加载消费|
|其他脚本或行为|最窄真实入口、沙盒、语法或风险边界场景|

引用检查器只读验证本地 Markdown 链接、锚点和明确脚本指针，不执行脚本、不保证远程 URL，不证明自然触发。默认略过 completed/archive 及 superseded Decision 正文；历史材料可显式检查。仓库内软链接可用，仓库外引用拒绝读取，参数见检查器 `--help`。

路由或精简需要行为对照时，保持输入、模型、工具、授权和验收一致，记录实际读取和执行轨迹。显式读取只能证明消费，不能称自然发现；目录匹配和模型自评不算行为证据。见 [`writing-for-agents` 判据](../skills/writing-for-agents/references/criteria.md)。

## 文档与状态

执行状态只在项目选定的 tracker；持久计划用于人审或恢复，handoff 引用权威状态，不复制进度。项目文档保存稳定事实、词汇和决定；优先复用现有 CONTEXT/glossary 与 ADR。

普通项目不强制引入 Bundle。本仓库已采用 Bundle：`docs/` 中除 `index.md`、`log.md` 的 Concept 有非空 `type`，ADR 为 `type: Decision`；`scope`、`sources`、策略有真实含义才声明。ledger 运行状态不写进 Concept，也不把未检查事实标 fresh。根 index 可为普通 Markdown；显式 YAML 仍须合法。

ADR 被取代时保持历史并双向链接 `supersedes` / `superseded_by`。命名使用 `NNNN-slug.md`、`YYYY-MM-DD-topic.md`、`YYYY-MM-DD-title/`。重大分工或长期知识变化同步现行文档与来源，不为普通修改新建仪式材料。

## 协作、授权与交付

子代理使用新上下文；依赖和写所有权决定并行，同一共享文件/状态只有一个整合者。结果是待核验证据，协调者负责组合行为与最终声明。不用 team mode、数字并发上限或无 sub-agent fallback。

完成授权内的本地实现、验证、适用审查与修复；明确建议、讨论、计划或草稿请求不扩张成实施。Git、发布、删除、秘密、权限和生产动作按具体授权执行。dirty working tree 可验证；commit-bound 动作另绑定被测内容和提交。报告只列真实运行结果、限制与未覆盖面。
