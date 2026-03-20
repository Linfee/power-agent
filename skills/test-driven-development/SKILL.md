---
name: test-driven-development
description: 实现任何功能或 bugfix 时使用，强制 RED-GREEN-REFACTOR 循环。没有先失败的测试就没有生产代码。Triggers: '实现功能', 'TDD', '测试驱动', 'bugfix', '编写代码'.
---

# 测试驱动开发（TDD）

先写测试，观察失败，写最小代码使其通过。

**铁律：**
```
没有先失败的测试就没有生产代码
```

测试前写了代码？删除它，重新开始。无例外。

---

## RED → GREEN → REFACTOR

### RED — 编写失败测试

写一个最小测试展示期望行为：
- 一个行为，清晰命名
- 测试真实行为，而不是 mock
- 不可避免时才使用 mock

### 验证 RED — 强制执行，绝不跳过

```bash
# 运行目标测试，确认它因为功能缺失而失败
pytest tests/path/test.py::test_name -v
# 或对应的测试命令
```

确认：测试失败（不是错误）；因为功能缺失而失败，不是拼写错误。

**测试立即通过？** 你在测试现有行为，修复测试。

### GREEN — 最小实现

写最简单的代码使测试通过，不添加额外功能，不提前优化，不 YAGNI。

### 验证 GREEN — 强制执行

```bash
# 确认目标测试通过，且其他测试未破坏
pytest tests/ -v
```

### REFACTOR — 清理

只在绿色后重构：移除重复、改善命名、提取辅助工具。保持测试绿色，不添加行为。

### 重复

为下一个行为重复循环。

---

## 完成验收清单

在标记工作完成前：

- [ ] 每个新函数/方法都有测试
- [ ] 每个测试在实现前观察到失败
- [ ] 每个测试因预期原因失败（功能缺失，非拼写错误）
- [ ] 写了最小代码使测试通过
- [ ] 所有测试通过，输出干净
- [ ] 全量测试套件无回归

---

## 常见合理化借口（一律拒绝）

| 借口 | 现实 |
|------|------|
| "太简单不需要测试" | 简单代码也会坏，测试只需 30 秒 |
| "我之后再写测试" | 测试立即通过证明不了任何事 |
| "已经手动测试过" | 临时 ≠ 系统化，无法重新运行 |
| "删除 X 小时的工作是浪费" | 沉没成本谬误，保留未验证代码才是技术债 |
| "TDD 太教条，我在务实" | TDD 比调试快，这才是务实 |

---

## 红旗 — 停止并重新开始

- 测试前写代码
- 测试立即通过
- 无法解释测试为何失败
- "就这一次"

**所有这些都意味着：删除代码，用 TDD 重新开始。**

---

## Bugfix 示例

```python
# RED
def test_rejects_empty_email():
    result = submit_form(email='')
    assert result['error'] == 'Email required'

# 验证 RED: pytest → FAIL — assert None == 'Email required'

# GREEN
def submit_form(email):
    if not email.strip():
        return {'error': 'Email required'}
    ...

# 验证 GREEN: pytest → PASS
```
