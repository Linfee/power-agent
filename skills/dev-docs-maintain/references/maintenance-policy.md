# Dev Docs Maintenance Policy

## 1. OKF 与验证登记

`docs/` 是 OKF Bundle：除 `index.md`、`log.md` 外，每个 Markdown 文件都是 Concept Document，必须具有顶部 YAML frontmatter 和非空 `type`。

YAML frontmatter 是 Concept Document 元数据的唯一权威。每个 Concept 必须以可解析为 mapping 的顶部 YAML frontmatter 开始，并有非空 `type`；parser 必须完整消费支持的 YAML subset，任何裸 token、错误缩进、未消费内容或不完整语法都是 `invalid-frontmatter`，使该 Concept 在 scan 中 `blocked` 并拒绝 `record`。`scope`、`sources` 与 `status` 只在具有语义时声明。scanner 只将现存 scope 路径和显式 glob 纳入 source snapshot；路径形的概念范围不是 source。需要强制追踪或验证存在性的路径必须写入 `sources`。缺少 `verification` 时继承项目默认策略；显式 `verification: null` 是 `invalid-verification`，而 `verification: {}` 是有效 mapping，继承默认策略。运行时验证数据只属于 verification ledger。已弃用的 HTML header metadata（包括 `verified`、`scope` 与 `status`）不生产、不消费、不作为迁移输入；旧 `verified` 日期不写入验证登记。

Concept frontmatter 保存稳定配置：

```yaml
---
type: Domain
title: Payment Domain
description: Payment 领域的职责、边界和核心不变量。
tags: [domain, payment]
timestamp: 2026-07-10T00:00:00Z
scope:
  - src/payment/**
sources:
  - schemas/payment.yaml
verification:
  strategy: source-change-and-periodic
  target: P90D
---
```

验证运行状态保存在：

```text
docs/.okf/verification.json
```

该文件是机器维护的派生登记，不是 Concept Document。建议纳入 Git，以便不同 Agent 和定时任务共享验证基线。不要手工编辑；只能由本 Skill 随附的 `bundle_status.py record` 在完成验证后更新。

scanner 会在读写前 canonical resolve registry。默认或 `--registry` 指定的 registry 实体必须同时位于 repository 与目标 Bundle 内；`.okf` 目录、registry 或 lock 的任一符号链接越界都会被拒绝。lock 以 canonical Bundle 为固定 advisory-lock 身份创建，因此 registry alias 或 hardlink 不会产生第二个写者。

新建或修改 Concept 不自动表示已验证。没有可信登记时，scanner 将其视为 `unverified`；损坏或不完整的 Concept 登记会显式显示为 `blocked`。

## 2. 项目级默认策略

根 `docs/index.md` 可定义默认策略：
`freshness` 是 lifecycle gate：scanner 在判定状态和 `record` 资格前为每个 Concept 解析 effective strategy，并据此启用相应的 metadata 校验。规则可以只按类型声明；只有未匹配的 Concept 共享确定性的 source-tracking 需求时才设置 source-sensitive 全局默认，否则应省略默认或使用局部配置。该 gate 只认 YAML frontmatter，不能由 HTML header metadata 取代或绕过。

```yaml
---
okf_version: "0.1"
freshness:
  default_strategy: source-change-and-periodic
  default_target: P90D
  rules:
    - type: Playbook
      target: P30D
    - type: Decision
      strategy: historical
---
```

Concept 局部配置覆盖项目默认值。周期只用于重新验证调度，不是问题严重度。

支持的策略：

- `source-change`：文档或声明来源变化时重新验证；它不按 `target` 到期。
- `periodic`：文档变化仍需重新验证，达到 `target` 时为 `due`；声明来源内容变化不是 freshness 输入，不能单独触发 `dirty`，但声明来源缺失始终为 `blocked`。
- `source-change-and-periodic`：文档或声明来源变化、或达到 `target` 时重新验证；当前事实文档默认推荐。
- `historical`：用于 ADR 等决策文档；freshness 只检查文档自身、链接、YAML `status` 和 supersede 关系，声明来源内容变化不是 freshness 输入，也没有周期性到期，但声明来源缺失仍为 `blocked`。
- `generated`：通过生成源或机器契约重新验证；它是 source-sensitive，声明来源变化会触发重新验证。

对 effective strategy 为 `historical` 的 `type: Decision`，YAML `status` 必须是 `proposed`、`accepted` 或 `superseded`。`proposed` 与 `accepted` 不要求 supersede 字段；`superseded` 必须用相对当前 ADR 的 Markdown 路径声明 `superseded_by`，路径必须解析到 Bundle 内有可解析 frontmatter 的 Decision；该目标还必须以 `supersedes` 反向指回当前 ADR。缺失、不可解析、不存在、目标非 Decision 或双向关系不一致均为 metadata issue，scan 会阻止该 Concept，`record` 也会拒绝。

scanner 支持 `PnD` 和 `PnW` 格式，例如 `P30D`、`P12W`。

## 3. 状态判定

- `fresh`：文档和该策略定义的 freshness 输入与完整可信登记一致，且未达到适用的周期。
- `dirty`：文档变化，或 `source-change`、`source-change-and-periodic`、`generated` 策略所跟踪的来源快照变化。
- `unverified`：没有可信登记。
- `due`：完整可信登记存在且内容未变，且带周期策略达到 `target`。
- `blocked`：声明来源不存在、策略无法建立快照或单个 Concept 的验证登记损坏/不完整；若整个 registry 结构无效（包括无法解析、根不是对象、`concepts` 缺失/不是对象、schema 不受支持，或必填顶层字段无效），必须同时报告 `invalid-verification-registry` bundle finding，并将每个已发现的 Concept 显式为 `blocked`，同时列出 `invalid-verification-registry` 与 `incomplete-verification-record`。

状态与 P0/P1/P2 正交。只有 Agent 完成语义核对后才能判定实际问题等级。

## 4. 验证登记规则

只有完成对应验证后才能运行 `record`：

| method | 最低要求 |
|---|---|
| `continuity` | 仅已有完整可信登记、当前状态为 `fresh` 或 `due`，且 metadata、来源、链接和覆盖关系有效时可用；它只能延续策略定义的未变化 freshness 输入。`periodic` 与 `historical` 不把来源当 freshness 输入，因此仅来源变化仍可保持 `fresh`/`due` 并允许 `continuity` 刷新快照；source-sensitive 策略的来源变化会成为 `dirty`，不能使用它。不能创建/重置基线，也不能恢复 `unverified`、`dirty` 或不完整登记。 |
| `semantic` | 对照代码、测试、配置、Schema 或权威资料核对关键声明。 |
| `executable` | 在 semantic 基础上实际执行命令、示例、生成器或契约测试。 |

验证失败或只做格式修改时不更新登记。`record` 只能处理当前文档、metadata、链接与来源均有效的 Concept；缺失来源、broken link 或任一 document metadata 问题都会使其拒绝登记。

扫描必须把损坏或不完整的单个 Concept 登记显式标为 `blocked` / `incomplete-verification-record`。只有当前文档、链接、来源和 metadata 均完整，且本轮完成 `semantic` 或 `executable` 验证时，新的完整记录才可覆盖该条目；`continuity` 绝不能恢复或重置它。这一恢复不能掩盖任何其他 document metadata、link 或 source 问题。整个 registry 结构无效（包括无法解析、根不是对象、`concepts` 缺失/不是对象、schema 不受支持，或必填顶层字段无效）时，扫描必须报告 `invalid-verification-registry` bundle finding，并把每个已发现的 Concept 标为 `blocked`，同时报告 `invalid-verification-registry` 与 `incomplete-verification-record`；`record` 必须拒绝，不能以任何单个 Concept 覆盖根级损坏，也不得手工篡改 ledger。

ledger 中的 evidence 只能是可公开、脱敏的受控枚举：`human-review`、`automated-test`、`external-audit`。CLI 与已有 ledger 记录均不接受任何其他值，尤其不得写入命令、URL、query、header、密钥、令牌、认证头、Cookie、私有 URL query、原始证据或受限资料。

同一 Bundle 一次只能有一个 `record` 写者。脚本使用以 canonical Bundle 为固定身份的持久 `$BUNDLE_DIR/.okf/verification.json.lock` 文件和操作系统 advisory exclusive lock 协调写入；registry 在读写前 canonical resolve，默认或 `--registry` 指定的 registry 必须同时在 repo 与 Bundle 内，且 `.okf`、registry 或 lock 的任一越界符号链接都会被拒绝。登记者在锁内读取、批量更新并原子替换 ledger；registry alias 或 hardlink 不能产生第二个写锁。锁文件可在进程退出后保留，不能以文件是否存在判断有活跃写者；操作系统会在写者退出或被终止时释放 advisory lock。遇锁冲突不得手工删除锁文件、改写 ledger 或绕过锁；重新扫描后重试。

`record` 保存：

- `verified_at`
- `verified_commit`
- `method`
- `document_hash`
- 所有策略的 `source_fingerprint` 和每个来源文件的内容 hash（用于快照/溯源和 ledger 完整性检查；只有 source-sensitive 策略把它们作为 freshness 输入）
- 可选的受控 evidence 枚举（`human-review`、`automated-test`、`external-audit`）

因此即使 Git 被 rebase 或 squash，scanner 仍可通过内容指纹识别所有策略的文档变化，以及 source-sensitive 策略的来源变化。

每次成功 `record` 后都要重新 `scan`，确认目标不再是 `dirty`、`unverified` 或 `due`，并确认没有新增 frontmatter、链接或来源问题。若未收敛，保留状态并报告，不以登记动作替代修复。

## 5. 维护边界

`fix-safe` 可以：

- 修复确定的当前事实、命令、链接和来源路径；
- 补齐无争议的 OKF frontmatter；
- 更新受影响的 index/log；
- 登记已完成的验证。

需要 `full-maintain`：

- 移动、重命名、拆分、合并或删除 Concept；
- 大范围目录重构；
- 改变 Bundle 边界。

禁止：

- 因日期到期直接刷新登记；
- 批量记录未验证 Concept；
- 从当前代码反推一个新决策已经获批；
- 重写 accepted ADR 的历史结论；
- 用模型记忆替代不可访问的权威来源。
