---
name: writing-plans
description: 将设计/spec 拆解为 TDD 结构的可执行实现计划（exec-plan），包含完整代码片段、精确命令和计划审查循环。Use when: 有明确规格或需求、准备开始实现之前，或 dev-docs 委派 exec-plan 任务时。Triggers: '创建实现计划', 'exec-plan', 'writing-plans', '任务拆解', '实现计划'.
---

# Writing Plans — 创建实现计划

将设计或 spec 拆解为 **agent 可直接执行的细粒度任务**，让执行代理无需额外探索就能理解"做什么、怎么做、怎么验证"。

**声明于开始：** "我正在使用 writing-plans skill 创建实现计划。"

---

## Step 1: 预检与上下文加载

1. 确认 `AGENTS.md` 已加载，`docs/` 目录存在
2. 若用户提供了 spec 文件（`docs/specs/`），完整阅读它
3. 加载相关上下文：`docs/architecture.md`、`docs/arch-decisions/index.md`

## Step 2: 代码分析

启动 `explore` 子代理分析相关代码区域，收集：
- 关键文件路径、函数签名、模块边界
- 现有测试结构和测试运行命令
- 当前代码约定和模式

**读取** 子代理返回的关键文件后再继续。

## Step 3: 范围检查

若需求涵盖多个独立子系统 → 建议拆分为多个独立 exec-plan，每个单独走完 writing-plans → exec-plan-runner 循环。

## Step 4: 文件结构规划

写任务前先规划文件清单：
- 每个文件一个明确职责，按职责拆分而非按技术层级
- 标注需要修改的现有文件的大致行范围
- 遵循现有代码约定；只有在文件已过于庞大时才建议拆分

此结构决定任务分解边界。**每个任务产出自包含的变更集。**

## Step 5: 撰写计划

### 规模判断

- **小任务**（单模块或少量文件）→ 单文件：`docs/exec-plans/active/YYYY-MM-DD-title.md`
- **大需求**（跨多模块，需要独立方案设计）→ 目录：`docs/exec-plans/active/YYYY-MM-DD-title/`

### 计划文档头部（必须包含）

```markdown
<!-- verified: YYYY-MM-DD -->
<!-- scope: [涉及范围] -->
<!-- status: active -->

# [功能名] 实现计划

> **给执行代理：** 推荐使用 `exec-plan-runner` skill 执行此计划。
> 任务使用 checkbox (`- [ ]`) 语法追踪进度。

**目标：** [一句话描述构建什么]

**架构：** [2-3 句话描述实现方法]

**技术栈：** [关键技术/库]

---
```

### 任务结构（TDD 粒度）

每个任务是一个自包含的组件，每步是一个动作，**2-5 分钟**内完成：

````markdown
### Task N: [组件名]

**文件：**
- 创建: `exact/path/to/file.py`
- 修改: `exact/path/to/existing.py`（第 123-145 行附近）
- 测试: `tests/exact/path/to/test_file.py`

- [ ] **Step 1: 编写失败测试**

```python
def test_specific_behavior():
    result = function_under_test(input_value)
    assert result == expected_value
```

- [ ] **Step 2: 运行确认失败**

```bash
pytest tests/path/test_file.py::test_specific_behavior -v
# 预期: FAIL — NameError 或 AssertionError，说明功能尚未实现
```

- [ ] **Step 3: 编写最小实现**

```python
def function_under_test(input_value):
    return expected_value
```

- [ ] **Step 4: 运行确认通过**

```bash
pytest tests/path/test_file.py::test_specific_behavior -v
# 预期: PASS — 1 passed
```

- [ ] **Step 5: 运行全量测试，确认无回归**

```bash
pytest tests/ -v
# 预期: 所有测试通过，0 failed
```

- [ ] **Step 6: Commit**

```bash
git add tests/path/test_file.py src/path/file.py
git commit -m "feat: add [component name]"
```
````

**粒度规则：** 每步一个动作；代码完整写出，不写伪代码；命令可直接执行，含预期输出；DRY、YAGNI、TDD、频繁提交。

### 大需求目录结构

```
docs/exec-plans/active/YYYY-MM-DD-title/
├── README.md     # 入口：目标、里程碑、当前状态
├── design.md     # 技术方案：架构、数据模型、接口
├── tasks.md      # TDD 粒度任务拆解（同上格式）
└── decisions.md  # 过程决策日志
```

README.md 头部：
```markdown
<!-- verified: YYYY-MM-DD -->
<!-- scope: [涉及范围] -->
<!-- status: active -->

# [计划标题]

## 目标
[要达成什么，1-3 句话]

## 里程碑
| 阶段 | 内容 | 状态 |
|------|------|------|
| M1 | ... | ⏳ |

## 当前状态
[下一步从哪里开始]
```

## Step 6: Plan Reviewer 循环

计划写完后，按 `<writing-plans-path>/plan-reviewer-prompt.md` 模板 dispatch `tech-plan-reviewer` 子代理：

1. 若 **Issues Found** → 修复，重新 dispatch，最多 3 轮
2. 超过 3 轮仍有问题 → 向用户 escalate
3. 若 **Approved** → 进入 Step 7

## Step 7: 更新索引

1. 确保 `docs/exec-plans/active/` 下文件列表一致
2. 如新增了目录路径 → 更新 `AGENTS.md` 知识库导航

## Step 8: 执行交棒

> "计划已完成，保存至 `docs/exec-plans/active/<filename>`。选择执行方式：
>
> **1. exec-plan-runner（推荐）** — 分析任务依赖、并行调度子代理、TDD 驱动、阶段验证
>
> **2. 内联执行** — 在当前会话中按任务逐步执行"
