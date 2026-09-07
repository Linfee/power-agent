# ADR Format

沿用仓库已有 ADR 位置与编号。尚无约定时，可存放在 `docs/adr/` 下，按 `0001-slug.md` 命名，例如 `0001-use-postgres.md`。

目录和文件只在有值得记录的真实决策时创建，初始化不预建空目录或占位 ADR。

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

- 未来工作需要复用、且不能仅从代码恢复的决策理由值得写 ADR，例如边界选择、替代方案的取舍或长期约束。可逆性、反直觉程度与取舍复杂度是判断线索，不是必须同时满足的条件。
- ADR 可以只有一个段落；不要为了“标准格式”填充无意义章节。
- 采用四位编号时扫描实际 ADR 目录的当前最大编号，加一后继续。
- 每个 ADR 的 YAML 必须声明 `type: Decision`、`verification.strategy: historical`，以及 `proposed`、`accepted` 或 `superseded` 之一的 `status`。元数据只写 YAML frontmatter；不得以 HTML `status`、`scope` 或 `verified` 注释替代，也不要写无语义的 `scope`。
- 决策获得采纳后将 YAML `status` 改为 `accepted`。取代现有 ADR 时，在同一次变更中建立双向关系：旧 ADR 设为 `status: superseded` 并以相对旧 ADR 的 Markdown 路径填写 `superseded_by: 0007-replacement.md`；新 ADR 以相对新 ADR 的路径填写 `supersedes: 0006-replaced.md`。两条路径必须互相指向对方。

## 何时跳过

- 局部、显然且能由代码或测试表达的实现细节。
- 对未来决策没有复用价值的临时选择。
- 仅重复实现现状，没有需要保留的背景或理由。
