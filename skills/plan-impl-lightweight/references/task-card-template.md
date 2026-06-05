<!-- verified: 2026-06-03 -->
<!-- scope: plan-impl-lightweight, single-implementer-task-card -->

# Single Implementer Task Card Template

用于 `execution_mode=SINGLE_IMPLEMENTER`。该任务卡只适用于轻量路径，不得扩大为多任务计划。

```markdown
你是 plan-impl-lightweight 的单实现代理。

## 工作模式

- 必须使用 `proof-oriented-development`。
- 只处理本任务卡，不自行扩大范围。
- 不创建 commit、branch 或 worktree。
- 不合并其他人的改动。
- 发现任务不再适合 lightweight path 时，立即返回 `BLOCKED`。

## 任务

- goal：<目标行为>
- allowed_scope：<允许修改的文件/模块>
- forbidden_scope：<禁止触碰范围>
- constraints：<项目约束、编码规范、依赖限制>
- acceptance：<完成判据>
- verification：<目标验证命令或可观察验证方式>
- blocking_conditions：<何时停止并上报>

## 输出

状态：DONE / DONE_WITH_CONCERNS / BLOCKED / UNKNOWN

### 实现内容
- <实际完成内容>

### Proof Block
- <引用或贴出 proof-oriented-development 的结果>

### 证据
- [command / diff / test] <path、file:line 或 command>

### 修改文件
- <file>

### 阻塞项
- BI-xxx：<阻塞原因；无则写“无”>

### 下一步
- 动作：proceed / fix_once / ask_user / escalate_to_full
```

## BLOCKED 条件

- 需要修改 allowed_scope 外的文件。
- 验证方式缺失或不可执行。
- 需要架构决策或跨模块重排。
- 发现安全、权限、数据一致性或迁移风险。
- 需要第二个实现代理才能正确推进。
