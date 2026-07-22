---
name: dev-docs-maintain
description: |-
  当需要检查既有 `docs/` OKF Bundle 的健康状态、修复已发现的结构或知识漂移，或登记已经完成的验证时使用。不要用于首次撰写文档、裸“更新文档”或执行计划。
  Triggers: docs 健康检查, 知识库体检, OKF Bundle 检查, 验证登记, verification ledger, 文档漂移修复, dev-docs-maintain.
---

# 维护既有 Docs Bundle

本 Skill 只维护目标仓库中已经存在的 `docs/` OKF Knowledge Bundle，通过“确定性扫描 → 局部语义验证 → 修复 → 单写者登记 → 再扫描”保持它与仓库一致。新建长期知识应使用 `dev-docs`；软件资产变更的开发计划应使用 `writing-plans`。

## 路由判定

本 Skill 的对象是**已经存在的 Bundle 与 Concept 生命周期**，不是所有“更新文档”请求：

| 请求目标 | 去向 |
|---|---|
| 新建或修订稳定知识内容、补 ADR 或 Reference | `dev-docs` |
| 只检查既有 Bundle 是否健康或待验证 | 本 Skill `check-only` |
| 修复 scanner 已发现且证据明确的漂移 | 本 Skill `fix-safe` |
| 移动、拆分、合并 Concept 或重构目录 | 本 Skill `full-maintain`；会实际写入长期 Bundle、链接和索引。结构性写入仍是长期文档写入，不能因未新增语义事实就判断为“没有写文档” |
| 登记已完成的语义或可执行验证 | 本 Skill；仍须先 scan、核对证据、单写者 record、再 scan |
| 软件资产变更的实施、重构或迁移计划 | `writing-plans` |
| RFC、Proposal、普通设计文档共创 | `doc-coauthoring` |
| README、CHANGELOG、发布公告 | 不属于本 Skill |

用户只说“更新文档”且没有给出已有 Concept、变化来源、扫描目标或验证意图时，返回 `needs-evidence`，不得自行选择写知识或刷新状态。新公开 API、CLI、配置契约尚无任何 Concept 时，它是 **coverage candidate**：交给 `dev-docs` 判断是否创建长期知识，不能伪装成既有 Concept 的 `dirty`、`unverified` 或其他 freshness 状态。
`needs-evidence` 只用于连内容修订、健康检查或登记意图都无法判断的裸请求。只要用户已明确要求 `record` 或刷新 verification ledger，即使要求跳过扫描、证据不足或批量登记，仍路由到本 Skill 的 `fix-safe`：拒绝越过门禁，并从记录前扫描开始，而不是把它退回 `needs-evidence`。

Git diff、commit 时间和文档年龄只能帮助缩小候选范围，不能单独证明正文漂移或 `fresh`。**当现有证据只有 Git diff 时，`check-only` 优先级最高**：无论用户把动作描述为刷新时间、批量 `record` 还是验证登记，都必须先以 `check-only` 扫描，发现并核对具体语义证据后才能进入修复或登记。只有请求同时明确指出已更新的事实及其证据时，直接 `record` 意图才按 `fix-safe` 处理；仍不得通过 `record` 跳过门禁。

## 运行路径与参考资料

调用者必须在启动本 Skill 前提供两个绝对路径：

```bash
SKILL_DIR="/absolute/path/to/installed/skills/dev-docs-maintain" # 当前 SKILL.md 所在目录
REPO_ROOT="/absolute/path/to/target-repository"
BUNDLE_DIR="$REPO_ROOT/docs"
```

`SKILL_DIR` 不得从 `REPO_ROOT` 推导；Skill 可以通过 user-scope 插件安装在目标仓库外。Bundle 是 `$BUNDLE_DIR`，默认验证登记是 `$BUNDLE_DIR/.okf/verification.json`。scanner 会在读写前 canonical resolve 路径；默认或 `--registry` 指定的 registry 实体都必须同时位于 repository 与目标 Bundle 内。`.okf` 目录、registry 或 lock 的任一符号链接越界都会被拒绝；lock 始终以 canonical Bundle 为固定的 advisory-lock 身份创建，registry alias 或 hardlink 不能绕过单写者边界。以下命令均使用调用者提供的路径：

```bash
python3 "$SKILL_DIR/scripts/bundle_status.py" scan \
  --repo "$REPO_ROOT" \
  --bundle "$BUNDLE_DIR" \
  --format json \
  --output /tmp/dev-docs-status.json
```

| 资料 | 读取时机 |
|---|---|
| [维护策略](./references/maintenance-policy.md) | 判定 freshness、验证方法、登记资格、模式或 accepted ADR 边界时。 |
| [OKF 规范](./references/okf-v0.1.md) | 修复 frontmatter、Concept、链接或 Bundle 结构问题时。 |
| [脚本](./scripts/bundle_status.py) | 需要确认扫描报告字段、`record` 参数或脚本的明确失败原因时。 |

## 模式

- `check-only`：扫描和验证，不修改文档或验证登记。
- `fix-safe`：修复证据明确、不改变历史决策或 Concept 边界的问题；默认模式。
- `full-maintain`：允许移动、拆分、合并 Concept 和重构目录，并同步链接、index 与 log。

## 执行流程

### 1. 记录前扫描

先运行上面的 `scan`，读取 `summary`、`bundle_issues` 和 `queue`，并为要登记的每个 Concept 保留该扫描结果。脚本根据验证登记中的文档与来源指纹识别：
根 `docs/index.md` 的 freshness policy 是 lifecycle gate：scanner 在判定 queue 和登记资格前解析每个 Concept 的 effective strategy。按类型配置的 `Decision → historical` 会启用 ADR 的 YAML `status` 与双向 supersede 关系校验；没有共同 source-tracking 需求的 Concept 不应仅因默认策略而变成 source-sensitive。该 gate 只认 YAML frontmatter，不能用 HTML header metadata 复活或绕过。

- `dirty`：文档正文变化，或仅在 `source-change`、`source-change-and-periodic`、`generated` 这些 source-sensitive 策略下，所跟踪的声明来源内容变化；`periodic` 与 `historical` 不会只因声明来源内容变化而变为 `dirty`，但任何策略的声明来源缺失仍会 `blocked`；
- `unverified`：从未登记可信验证；
- `due`：完整可信登记存在、策略使用周期且达到其 `target`；
- `blocked`：来源缺失、结构无法建立快照或单个 Concept 的登记损坏/不完整；若整个 registry 结构无效（包括无法解析、根不是对象、`concepts` 缺失/不是对象、schema 不受支持，或必填顶层字段无效），必须同时报告 `invalid-verification-registry` bundle finding，并将每个已发现的 Concept 显式为 `blocked`，同时列出 metadata reasons `invalid-verification-registry` 与 `incomplete-verification-record`；
- `fresh`：文档及该策略定义的 freshness 输入与最近完整可信登记一致，且未达到适用的周期；

脚本只生成候选队列，不判断正文语义是否正确。

### 2. 局部加载并验证证据

只为候选 Concept 读取正文、`changed_sources` 和直接相关 diff、测试、配置、Schema、生成源、相关 ADR 及一阶链接。逐项核对职责、边界、不变量、关键流程、公开契约、命令和来源：

- 一致时可准备登记；
- 漂移时按模式修复后重新核对；
- 证据冲突、来源不可访问或边界不清时保留 `blocked`，不得刷新状态；
- effective strategy 为 `historical` 的 `type: Decision` 必须有 YAML `status`，且仅允许 `proposed`、`accepted` 或 `superseded`。`proposed` 与 `accepted` 不要求 supersede 字段；`superseded` 必须以相对当前 ADR 的 Markdown 路径声明 `superseded_by`，目标必须是 Bundle 内有可解析 frontmatter 的 Decision，并以 `supersedes` 反向指回当前 ADR。任一缺失、路径不可解析/不存在、目标非 Decision 或双向关系不一致都会成为 metadata issue 并拒绝 `record`；
- evidence 只能使用受控枚举 `human-review`、`automated-test` 或 `external-audit`，不得包含或表示命令、URL、凭据、认证头、Cookie、私有 URL query 或受限资料。

P0/P1/P2 只依据实际影响，不由 freshness 自动决定。

### 3. 修复长期知识

- 当前事实直接描述现在是什么；优先更新已有 Concept，只在知识独立且长期复用时新建。
- 文档元数据唯一权威是 YAML frontmatter。每个 Concept 必须以可解析为 mapping 的顶部 YAML frontmatter 开始，并具有非空 `type`；parser 必须完整消费支持的 YAML subset，裸 token、错误缩进、未消费内容或不完整语法都是 `invalid-frontmatter`，使 scan 变为 `blocked` 并令 `record` 拒绝。`scope`、`sources` 与 `status` 仅在有语义时声明。已弃用的 HTML header metadata（包括 `verified`、`scope` 与 `status` 注释）不生产、不消费、不作为迁移输入；旧日期绝不写入 ledger。
- 缺少 `verification` 时继承项目默认策略；显式 `verification: null` 是 `invalid-verification`，而 `verification: {}` 是有效 mapping，继承默认策略。运行时验证数据只属于 ledger，不能写回 YAML。
- 仅在新增、移动、删除 Concept 或导航语义改变时更新 `index.md`；仅将长期有意义的变化写入 `log.md`。
- 新决策通过新 ADR 表达，不能改写 accepted ADR；`timestamp` 只在正文语义变化时更新。

### 4. 单写者登记

在当前仓库中一次只能有一个 Agent 或进程运行 `record`。其他 Agent 可以扫描和完成语义核对，但必须把证据交给单一登记者；不得手工编辑 `$BUNDLE_DIR/.okf/verification.json`。

完成验证且记录前扫描无阻塞结构问题后，单一登记者运行：

```bash
python3 "$SKILL_DIR/scripts/bundle_status.py" record \
  --repo "$REPO_ROOT" \
  --bundle "$BUNDLE_DIR" \
  --concept "$BUNDLE_DIR/domain/payment.md" \
  --method semantic \
  --evidence human-review
```

`--evidence` 可重复指定，但 CLI 和已有 ledger 记录都只接受 `human-review`、`automated-test`、`external-audit` 三个值（写入时去重并排序）。其他任何文本均被拒绝，尤其是命令、URL、query、header、密钥、令牌、认证信息或原始证据；它不是命令日志或原始证据的存放处。

允许的方法：

- `continuity`：只适用于已有完整可信登记、当前状态为 `fresh` 或 `due`，且 metadata、来源、链接和覆盖关系仍有效的 Concept；它只能延续策略定义的未变化 freshness 输入。对 `periodic` 与 `historical`，来源不是 freshness 输入，故仅来源变化仍可保持 `fresh`/`due` 并允许 `continuity` 刷新快照；source-sensitive 策略的来源变化会成为 `dirty`，不能使用它。它不能创建或重置基线，也不能恢复 `unverified`、`dirty` 或损坏的登记。
- `semantic`：对照代码、测试、配置或 Schema 核对关键声明；在所有现行结构门禁通过后，可恢复当前 Concept 的不完整登记。
- `executable`：在 `semantic` 基础上实际执行命令、示例或生成验证；在所有现行结构门禁通过后，可恢复当前 Concept 的不完整登记。

`record` 必须拒绝缺失来源、broken link 和所有文档 metadata 结构问题。损坏或不完整的单个 Concept 登记必须在扫描中显式显示为 `blocked` / `incomplete-verification-record`；只有本轮 `semantic` 或 `executable` 验证在当前文档、链接、来源和 metadata 均完整时，新的完整登记才可替代它。若整个 registry 结构无效（包括无法解析、根不是对象、`concepts` 缺失/不是对象、schema 不受支持，或必填顶层字段无效），扫描必须报告 `invalid-verification-registry` bundle finding，并将每个已发现的 Concept 标为 `blocked`，同时暴露 `invalid-verification-registry` 与 `incomplete-verification-record`；`record` 必须拒绝，不能以单个 Concept 恢复或掩盖根级损坏。不得批量登记未读取、未核对的 Concept，`check-only` 不调用 `record`。

同一 Bundle 使用持久的 `$BUNDLE_DIR/.okf/verification.json.lock` 文件和以 canonical Bundle 固定的操作系统 advisory exclusive lock 协调写者。registry 在读写前 canonical resolve，默认或 `--registry` 指定的 registry 必须同时位于 repository 与 Bundle 内；`.okf`、registry 或 lock 的任一越界符号链接都会被拒绝。取得该固定锁身份的登记者在同一锁内读取、批量更新并原子替换 ledger；registry alias 或 hardlink 不会产生第二个写锁。锁文件可在进程退出后保留，它本身不表示有活跃写者；锁由操作系统在持有者退出或被终止时释放。遇锁冲突，不得手工删除锁文件、改写 ledger 或以其他方式绕过；重新扫描后重试。

### 5. 记录后扫描与收敛

每次修复或 `record` 后再次运行相同的 `scan`，确认已处理 Concept 不再是 `dirty`、`unverified` 或 `due`，且未新增 broken link、missing source 或 frontmatter 问题。未处理和 `blocked` 项必须明确保留。只有扫描范围内的候选都已验证或明确阻塞时，才能声称本轮维护完成；`fresh` 不是全仓库绝对正确的声明。

## 稳定输出 contract

最终输出必须是 Markdown，始终按以下顺序包含这些二级标题；没有对应内容时写“无”或“无需”，不得省略：

## 状态

写明 `DONE`、`DONE_WITH_CONCERNS` 或 `BLOCKED`，以及一句结论。

## 范围

列出目标仓库、Bundle、扫描/修复/登记涉及的 Concept 和明确排除项。

## 变更/修复

列出修复的结构或知识漂移、登记动作，或确认无需修改的结果。

## 证据

列出记录前后扫描、核对过的权威来源、验证方法和实际执行的命令；未执行的操作不得声称完成。

## 剩余问题/风险

列出 `dirty`、`due`、`blocked`、锁冲突、来源访问限制或未处理结构问题；无则写“无”。

## 下一步

给出明确的后续动作；无需动作时写“无需”。
