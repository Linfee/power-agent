# ADR Format

ADR 存放在 `docs/adr/` 下，按 `0001-slug.md` 命名，例如 `0001-use-postgres.md`。

`setup-power-agent` 初始化时会创建 `docs/adr/` 目录；ADR 文件只在真实决策出现时写入。

## 模板

```md
---
type: Decision
status: proposed
verification:
  strategy: historical
---

# {Decision title}

{用 1-3 句话写清：背景是什么、做了什么决定、为什么。}
```

## 规则

- 只在三者同时满足时写 ADR：难以逆转、没有上下文会令人困惑、且存在真实权衡。
- ADR 可以只有一个段落；不要为了“标准格式”填充无意义章节。
- 编号时扫描 `docs/adr/` 当前最大四位编号，加一后继续。
- 每个 ADR 的 YAML 必须声明 `type: Decision`、`verification.strategy: historical`，以及 `proposed`、`accepted` 或 `superseded` 之一的 `status`。元数据只写 YAML frontmatter；不得以 HTML `status`、`scope` 或 `verified` 注释替代，也不要写无语义的 `scope`。
- 决策获得采纳后将 YAML `status` 改为 `accepted`。取代现有 ADR 时，在同一次变更中建立双向关系：旧 ADR 设为 `status: superseded` 并以相对旧 ADR 的 Markdown 路径填写 `superseded_by: 0007-replacement.md`；新 ADR 以相对新 ADR 的路径填写 `supersedes: 0006-replaced.md`。两条路径必须互相指向对方。

## 何时跳过

- 容易回滚的实现细节
- 显而易见、没有真实替代方案的选择
- 只是“现在不值得做”的临时性拒绝理由
