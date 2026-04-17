---
name: test-driven-development
description: "实现任何功能或 bugfix 时使用，强制 RED-GREEN-REFACTOR 循环。没有先失败的测试就没有生产代码。Triggers: 实现功能, TDD, 测试驱动, bugfix, 编写代码."
version: 1.0.0
---

# 务实测试驱动（Pragmatic TDD）

你可以同时编写测试和实现代码，但严禁在未运行测试命令并看到成功输出前声称任务完成。代码与测试并举，终端结果说话。

**铁律：**
```
没有终端跑通的测试，就没有声称完成的代码
```

---

## 核心流程：实现与验证

### 1. 编写代码与测试 (并行)
在同一个响应中，你可以同时生成：
- 最小的业务实现代码
- 验证该行为的测试代码（清晰命名、测试真实行为，尽量少用 mock）

### 2. 强制终端验证 (GREEN)
在声称任务完成前，**必须**在终端运行对应的测试命令，并确认看到绿色的通过输出。
```bash
# 运行目标测试，确保它能通过
pytest tests/path/test.py::test_name -v
# 或对应的 npm test 等命令
```

### 3. 重构 (REFACTOR)
如果测试通过，但代码结构不佳（重复、命名模糊），请自主进行重构，然后**再次运行测试**以确认无回归。

---

## 智能门控与高风险拦截

在开发过程中采取**“乐观决策”**原则：面对多个非致命的技术选择时，选择最符合当前项目约定的一个，并在回复中用一句话说明理由，然后直接推进。

**只有遇到以下情况时，才必须停下来向用户确认（AskUser）：**
1. **破坏性变更**：修改数据库 Schema、删除或重构现有对外 API。
2. **敏感阻断**：需要外部 API Key、牵涉用户隐私。
3. **巨大的范围蔓延**：预计需要修改超过 8 个文件，或需要引入全新的重量级框架。

---

## 完成验收清单

在标记工作完成前：

- [ ] 新功能或 Bugfix 拥有对应的测试用例
- [ ] **已在终端运行测试**，并看到了通过（PASS）的输出
- [ ] 全量测试套件无回归（运行 `pytest tests/` 或相应的全量测试）
- [ ] 没有引入破坏性变更（如果有，已获得用户批准）

---

## Bugfix 示例

```python
# 1. 并行编写实现与测试
def test_rejects_empty_email():
    result = submit_form(email='')
    assert result['error'] == 'Email required'

def submit_form(email):
    if not email.strip():
        return {'error': 'Email required'}
    ...

# 2. 强制终端验证
# 执行: pytest tests/test_form.py::test_rejects_empty_email -v
# 必须看到 PASS 输出后，才可结束任务。
```
