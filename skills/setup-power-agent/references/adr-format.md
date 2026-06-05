# ADR Format

ADR 存放在 `docs/arch-decisions/` 下，按 `DD-NNN-title.md` 命名，例如 `DD-001-use-postgres.md`。

## 模板

```md
# {Decision title}

{用 1-3 句话写清：背景是什么、做了什么决定、为什么。}
```

## 规则

- 只在三者同时满足时写 ADR：难以逆转、没有上下文会令人困惑、且存在真实权衡。
- ADR 可以只有一个段落；不要为了“标准格式”填充无意义章节。
- 编号时扫描 `docs/arch-decisions/` 当前最大 `DD-NNN` 编号，加一后继续。

## 何时跳过

- 容易回滚的实现细节
- 显而易见、没有真实替代方案的选择
- 只是“现在不值得做”的临时性拒绝理由
