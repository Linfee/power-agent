---
name: dev-docs-maintain
description: |-
  检查 `docs/` OKF Bundle 健康、修复已发现的结构或知识漂移、登记已完成验证时使用；不用于首次撰写文档、裸“更新文档”或执行计划。
  Triggers: docs 健康检查, 验证登记, 文档漂移修复, dev-docs-maintain.
---

# 维护既有 Docs Bundle

检查目标仓库已有的 `docs/` OKF Bundle，修复证据明确的漂移，登记逐篇完成的验证。scanner 检查结构与登记一致性；正文是否正确仍需对照权威来源判断。`fresh` 不代表内容绝对正确，freshness 状态也不决定问题严重度。

## 范围与证据

从请求和项目确定维护对象。只有会改变权威来源、生命周期或目标选择的歧义无法消除时才澄清；已明确要求刷新 ledger 的，先扫描并核对登记资格。

Git diff、commit 时间和文档年龄只用于筛选候选。为候选读取正文、`changed_sources` 与直接相关的代码、测试、配置、Schema、生成源、ADR 及一阶链接，核对职责、边界、不变量、公开契约和命令。证据冲突、来源不可访问或边界不清时保留未验证面，不登记；scanner 已标为 `blocked` 的项不得靠刷新状态掩盖。

- 无争议的当前事实、命令、链接、来源路径、frontmatter 和受影响的 index/log 可在授权范围内修复；修复后重新核对。仅做格式修改不等于完成验证。
- 移动、重命名、拆分、合并、删除 Concept 或改变 Bundle 边界需要对应目标与授权。新增知识或实质语义修订按需使用 `dev-docs`；不存在 Bundle 时按需使用 `setup-power-agent`。纯扫描和登记可独立完成。
- 新契约尚无 Concept 是 coverage candidate，不能伪装成 freshness 问题。从当前代码不能反推决策已经获批，也不能重写 accepted ADR 的历史结论。
- 仅当 `CONTEXT.md` 明确约定避免词时修复术语漂移。`timestamp` 只随正文语义变化更新；运行时验证数据留在 ledger。

## 登记与完成

每轮先扫描建立结构门禁，命令见 [CLI：定位与扫描](references/cli-operations.md#定位与扫描)。根据报告选取本轮候选；遇到需要解释的状态或结构问题，再读 [状态判定](references/maintenance-policy.md#3-状态判定) 或 [OKF 规范](references/okf-v0.1.md)。

只有逐篇完成验证，且证据仍覆盖当前内容，才可登记：`semantic` 对照权威来源核对关键声明；`executable` 在此基础上实际执行命令、示例或契约验证。`continuity` 仅延续已有且未变化的可信基线，不能恢复 `dirty`、`unverified` 或损坏登记；使用前核对 [验证登记规则](references/maintenance-policy.md#4-验证登记规则)。

修复和登记按依赖、证据有效期、失败影响组成有界批次。同一 `method` 与 `evidence` 的已验证 Concept 可 [原子批量登记](references/cli-operations.md#登记已验证的-concept)，一个条目的证据不能推广给其他条目。日期到期、格式已修、命令准备好了，都不是登记依据。

同一 Bundle 只允许一个 ledger 写者；其他 Agent 可交付逐篇证据，由单一登记者处理。只通过脚本加锁更新，不手工编辑 ledger、删锁或绕过路径与结构校验。拒绝时按 [故障处理](references/cli-operations.md#脚本拒绝时) 定位；不能用单条登记覆盖 registry 根级损坏。

批次结束扫描；失败、结构变化或新证据使先前扫描失效时提前扫描，再处理适用门禁。最终扫描可复用末批结果：已登记目标应不再是 `dirty`、`unverified` 或 `due`，且未新增 frontmatter、链接或来源问题。本轮候选全部验证或明确阻塞后，报告扫描结果、逐篇核对的来源、验证方法与实际执行证据；未处理项如实保留，不为完成声明刷新它们。

策略配置、元数据迁移、ADR 生命周期及 ledger 机器协议按需查 [维护策略](references/maintenance-policy.md)，不要求常规任务通读。
