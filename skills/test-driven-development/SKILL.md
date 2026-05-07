---
name: test-driven-development
description: |-
  实现功能或已确认根因的 bugfix 时使用，采用务实的增量测试循环（Pragmatic test-first）。
  关注局部行为的测试与实现闭环，不承担全量回归验证职责。
  Triggers: 实现功能, TDD, 测试驱动, 已确认根因的 bugfix, 编写代码.
version: 1.2.5
---

# 务实测试驱动（Pragmatic test-first）

以最小增量推进实现与测试，优先保证新增或变更行为有可运行证据。你可以根据任务上下文选择先写失败测试、先写最小实现，或两者小步交替推进。

**铁律：**
```
没有终端跑通的目标测试，就没有声称完成的增量改动
```

## 入口保护

- 若用户只描述 bug、测试失败或异常行为，且没有根因证据，先使用 `systematic-debugging`。
- 只有当 `systematic-debugging` 输出 `状态：FIXABLE`，或用户提供了可验证根因与目标行为时，才进入本 Skill 做 bugfix。
- 本 Skill 可以验证修复是否成立，但不负责在根因未知时直接猜测修复。

---

## 核心流程：增量闭环

### 1. 选择最小变更单元
将需求拆成可在一次循环内完成的最小行为变更，避免跨多个独立目标同时改动。

### 2. 构建局部测试证据
围绕当前变更单元补充或更新目标测试：
- 测试命名清晰，覆盖真实行为
- 优先验证业务边界与关键分支
- 仅在必要时使用 mock

### 3. 实现并对齐预期
编写最小实现使目标行为满足预期，避免顺手扩张范围。

### 4. 强制终端验证（当前增量）
在声称该增量完成前，必须运行与本次变更直接相关的测试，并确认看到通过输出。
```bash
# 运行目标测试并确认通过
pytest tests/path/test.py::test_name -v
# 或对应的 npm test / pnpm test / go test 等命令
```

### 5. 必要时重构并复测
若存在明显重复或可读性问题，可在当前增量内重构；重构后再次运行目标测试确认未破坏行为。

---

## 决策与 AskUser 触发

默认采用“就地推进”原则：在非阻断选择上，按项目现有约定做最小风险决策并继续执行。

仅在以下风险场景触发 AskUser：

1. **高风险且不可逆**
   - 数据模型/Schema 变更
   - 对外 API 语义破坏或删除
2. **高风险且边界不清**
   - 鉴权、权限、隐私数据处理逻辑改动
   - 并发一致性或事务边界调整
3. **高影响范围且需求不明确**
   - 跨多个模块联动修改，且目标边界或验收标准不清晰

不再使用固定文件数阈值作为触发条件。

---

## 职责边界

本 Skill 负责：
- 增量实现与目标测试的闭环
- 当前改动范围内的可运行验证证据

本 Skill 不负责：
- 全量测试套件回归判定
- 发布前系统级验收

全量回归与最终完成验证交由 `verification-before-completion`。

---

## 完成验收清单（本 Skill）

在标记当前增量完成前：

- [ ] 当前功能或已确认根因 bugfix 的目标行为有对应测试
- [ ] 已在终端运行目标测试并看到 PASS 输出
- [ ] 改动范围保持在当前增量目标内
- [ ] 若涉及高风险场景，已触发 AskUser 并获得明确决策

---

## 已确认根因的 Bugfix 示例

```python
# 1) 为当前增量准备目标测试
def test_rejects_empty_email():
    result = submit_form(email='')
    assert result['error'] == 'Email required'

# 2) 编写最小实现
def submit_form(email):
    if not email.strip():
        return {'error': 'Email required'}
    ...

# 3) 终端验证当前增量
# 执行: pytest tests/test_form.py::test_rejects_empty_email -v
# 看到 PASS 后，当前增量可结束。
```
