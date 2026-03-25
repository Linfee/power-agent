<!-- verified: 2026-03-25 -->
<!-- scope: eval, metrics, skills -->

# Eval 框架

power-agent 轻量评估框架，用于追踪 Skill 执行质量、版本间改进效果与用户满意度。

## 设计原则

- **低摩擦**：Agent 自动采集，用户只需回答 1 个必答题
- **版本追踪**：每条记录含 skill-version，便于版本间对比
- **可跳过**：用户可跳过反馈，仍保留自动指标

## 评估维度

| 指标 | 来源 | 自动化 |
|------|------|--------|
| 任务完成率 | exec-plan checkbox | 全自动 |
| 修复循环次数 | 执行过程计数 | 全自动 |
| Escalation 次数 | 执行过程计数 | 全自动 |
| Batch 数量 | exec-plan 结构 | 全自动 |
| 假设验证轮数 | debugging 阶段 3 计数 | 全自动 |
| 端到端耗时 | 首次工具调用到完成时间差 | 全自动（精确到分钟） |
| 用户满意度 | 向用户提问 | 人工（可跳过） |

## 收集协议

支持 Eval 收集的 Skills：`exec-plan-runner`、`systematic-debugging`、`feature-dev`

每次 Skill 执行完成时：
1. 自动采集上表中的全自动指标
2. 写入 exec-plan 文件尾部（或当前上下文）
3. 向用户提问 1 个必答题 + 1 个可选备注
4. 用户跳过时标注 `feedback: skipped`，仍保存自动指标

## 非交互场景处理

当 Skill 在自动化或非交互上下文中运行时：
- 默认写入 `feedback: skipped`（不阻塞主流程）
- 不需要额外等待用户输入
- 自动指标仍正常写入

## Eval 记录格式

```markdown
<!-- eval: YYYY-MM-DD -->
<!-- skill: [skill-name] -->
<!-- skill-version: [version] -->
<!-- project: [project-name] -->
<!-- task: [任务简述] -->

## Eval 记录
- 任务完成率: N/N
- Batch 数: N
- 修复循环: N 次
- Escalation: N 次
- 耗时: Nmin

## 用户反馈
- 整体: [满意 / 一般 / 不满意 / skipped]
- 备注: [内容或 "-"]
```

## 存储位置

Eval 记录写入对应 exec-plan 文件尾部。历史记录可在 `skills/[skill-name]/eval-results/` 下归档（手动操作）。

## 版本追踪规范

- `skill-version` 从对应 SKILL.md frontmatter 的 `version` 字段读取
- `project` 从目标项目 git remote URL 或目录名推断
- 版本升级时更新 `VERSION` 文件并运行 `scripts/sync-version.sh`
