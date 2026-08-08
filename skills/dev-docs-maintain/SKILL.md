---
name: dev-docs-maintain
description: |-
  检查 `docs/` OKF Bundle 健康、修复已发现的结构或知识漂移、登记已完成验证时使用；不用于首次撰写文档、裸“更新文档”或执行计划。
  Triggers: docs 健康检查, 验证登记, 文档漂移修复, dev-docs-maintain.
---

# 维护既有 Docs Bundle

本 Skill 维护目标仓库中**已经存在**的 `docs/` OKF Knowledge Bundle，通过“扫描 → 局部语义验证 → 修复 → 单写者登记 → 再扫描”保持它与仓库一致。新建长期知识用 `dev-docs`；软件资产变更的开发计划用 `writing-plans`。

## 路由

按请求要改变的对象路由，不按“更新文档”这类关键词：

- 新建或修订知识内容、补 ADR / Reference → `dev-docs`
- 检查 Bundle 健康 → 本 Skill `check-only`
- 修复 scanner 已发现、证据明确的漂移 → 本 Skill `fix-safe`（默认模式）
- 移动、拆分、合并 Concept 或重构目录 → 本 Skill `full-maintain`；结构性写入也是长期文档写入，若同时改变知识语义，再由 `dev-docs` 修订内容
- 登记已完成的验证 → 本 Skill，但仍须走完“扫描 → 核对 → 登记 → 再扫描”全流程
- README / CHANGELOG / 公告 → 不属于本 Skill

三条边界：

- 用户只说“更新文档”且无法判断意图时，返回 `needs-evidence`，不要猜。但已明确要求 `record` 或刷新 ledger 的，按 `fix-safe` 从扫描开始并拒绝越过门禁，而不是退回 `needs-evidence`。
- 新公开 API / CLI / 配置契约尚无任何 Concept 时，它是 **coverage candidate**，交给 `dev-docs` 判断是否创建，不能伪装成既有 Concept 的 freshness 状态。
- Git diff、commit 时间、文档年龄只能缩小候选范围，不能单独证明漂移或 fresh。现有证据只有 Git diff 时，无论用户把动作描述成刷新时间、批量 `record` 还是验证登记，都先 `check-only` 扫描，核对到具体语义证据后才修复或登记。

## 运行前提

调用者必须提供两个绝对路径（`SKILL_DIR` 不得从 `REPO_ROOT` 推导，Skill 可以安装在目标仓库外）：

```bash
SKILL_DIR="/absolute/path/to/installed/skills/dev-docs-maintain"
REPO_ROOT="/absolute/path/to/target-repository"
BUNDLE_DIR="$REPO_ROOT/docs"
```

扫描（每轮开始和结束后各跑一次）：

```bash
python3 "$SKILL_DIR/scripts/bundle_status.py" scan \
  --repo "$REPO_ROOT" --bundle "$BUNDLE_DIR" \
  --format json --output /tmp/dev-docs-status.json
```

登记（同一 Bundle 一次只能一个写者；其他 Agent 完成语义核对后把证据交给单一登记者，不得手工编辑 ledger）：

```bash
python3 "$SKILL_DIR/scripts/bundle_status.py" record \
  --repo "$REPO_ROOT" --bundle "$BUNDLE_DIR" \
  --concept "$BUNDLE_DIR/domain/payment.md" \
  --method semantic --evidence human-review
```

脚本负责加锁、路径与 registry 结构校验。**脚本拒绝时不要绕过**：遇锁冲突不要手工删锁或改写 ledger，重新扫描后重试；registry 结构无效时 scan 会把所有 Concept 标为 `blocked` 并拒绝 record，先修复 registry 本身，不用单个 Concept 的登记掩盖根级损坏。

参考资料：

| 资料 | 读取时机 |
|---|---|
| [维护策略](./references/maintenance-policy.md) | 判定 freshness、验证方法、登记资格或 accepted ADR 边界时 |
| [OKF 规范](./references/okf-v0.1.md) | 修复 frontmatter、Concept、链接或 Bundle 结构时 |
| [脚本](./scripts/bundle_status.py) | 确认扫描报告字段、record 参数或脚本失败原因时 |

## scanner 输出语义

scanner 只做结构判定，不判断正文语义是否正确。状态含义：

- `dirty`：文档正文变化；source-sensitive 策略（`source-change`、`source-change-and-periodic`、`generated`）下声明来源内容变化也算。`periodic` 与 `historical` 不追踪来源内容，但任何策略下来源缺失都是 `blocked`。
- `unverified`：从未登记可信验证。
- `due`：有完整登记、策略含周期且已到点。
- `blocked`：来源缺失、结构无法建立快照或登记损坏。
- `fresh`：与最近完整登记一致且未到周期。`fresh` 只表示与登记一致，不是“内容绝对正确”的全仓库声明。

`docs/index.md` 的 freshness policy 是 lifecycle gate：按类型配置的策略决定 Concept 是否 source-sensitive（如 `Decision → historical` 启用 ADR 的 YAML `status` 与 supersede 校验）；没有共同 source-tracking 需求的 Concept 不应仅因默认策略变成 source-sensitive。该 gate 只认 YAML frontmatter，不能用已弃用的 HTML header metadata 复活或绕过。

## 流程

### 1. 扫描定候选

运行 scan，读取 `summary`、`bundle_issues`、`queue`，为要登记的每个 Concept 保留该扫描结果。

### 2. 局部验证

只为候选 Concept 读取正文、`changed_sources` 和直接相关的 diff、测试、配置、Schema、生成源、相关 ADR 及一阶链接，逐项核对职责、边界、不变量、公开契约、命令和来源：

- 一致 → 可登记；漂移 → 按模式修复后重新核对；证据冲突、来源不可访问或边界不清 → 保留 `blocked`，不刷新状态。
- 术语漂移：正文出现 `CONTEXT.md` 显式标记的避免词时，按漂移修复为推荐词；`CONTEXT.md` 不存在或未约定避免词时跳过本项。
- `historical` 策略的 `type: Decision` 必须有 YAML `status`（`proposed` / `accepted` / `superseded`）；`superseded` 必须以 Bundle 内可解析的相对路径声明 `superseded_by`，且目标 Decision 以 `supersedes` 指回。关系不完整时 record 会被拒绝。
- `--evidence` 只接受 `human-review` / `automated-test` / `external-audit`，不能写入命令、URL、凭据或原始证据。
- P0/P1/P2 按实际影响定，不由 freshness 状态自动决定。

### 3. 修复

- 当前事实直接描述现在是什么；优先更新已有 Concept，只在知识独立且长期复用时新建。
- 元数据唯一权威是文件顶部 YAML frontmatter，`type` 必须非空；`scope` / `sources` / `status` 只在有实际语义时声明。缺 `verification` 时继承项目默认策略；`verification: null` 非法，`verification: {}` 合法。运行时验证数据只属于 ledger，不写回 YAML。
- 已弃用的 HTML header metadata（`verified`、`scope`、`status` 注释）不生产、不消费、不作为迁移输入；旧日期绝不写入 ledger。
- 仅在新增、移动、删除 Concept 或导航语义变化时更新 `index.md`；仅把长期有意义的变化写入 `log.md`。
- 新决策写新 ADR，不改写 accepted ADR；`timestamp` 只在正文语义变化时更新。

### 4. 登记

三种方法：

- `continuity`：仅用于已有完整登记、当前 `fresh` / `due` 且策略定义的 freshness 输入未变的 Concept。它只能延续未变化的 freshness 输入，不能创建或重置基线，也不能恢复 `unverified`、`dirty` 或损坏的登记；source-sensitive 策略下来源变化后不能用。
- `semantic`：对照代码、测试、配置或 Schema 核对关键声明；结构门禁通过后可恢复当前 Concept 的不完整登记。
- `executable`：在 `semantic` 基础上实际执行命令、示例或生成验证；同样可恢复不完整登记。

record 会拒绝缺失来源、broken link 和 metadata 结构问题。不要批量登记没读过、没核对过的 Concept；`check-only` 不调用 record。

### 5. 再扫描收敛

每次修复或 record 后重跑同一 scan：确认已处理 Concept 不再是 `dirty` / `unverified` / `due`，且未新增 broken link、missing source 或 frontmatter 问题。未处理和 `blocked` 项明确保留。只有扫描范围内的候选都已验证或明确阻塞，才能声称本轮维护完成。

## 输出 contract

最终输出为 Markdown，始终按顺序包含这六个二级标题；没有内容时写“无”或“无需”，不省略：

1. `## 状态`：`DONE` / `DONE_WITH_CONCERNS` / `BLOCKED` + 一句结论。
2. `## 范围`：目标仓库、Bundle、涉及的 Concept 与明确排除项。
3. `## 变更/修复`：修复的漂移、登记动作，或确认无需修改的结果。
4. `## 证据`：记录前后扫描、核对过的来源、验证方法和实际执行的命令；未执行的不得声称完成。
5. `## 剩余问题/风险`：`dirty` / `due` / `blocked`、锁冲突、来源访问限制或未处理结构问题。
6. `## 下一步`：明确动作；无需动作写“无需”。
