<!-- verified: 2026-03-25 -->
<!-- scope: skills, docs, scripts -->
<!-- status: active -->

# Harness Insights Enhancement 实现计划

> **给执行代理：** 推荐使用 `exec-plan-runner` skill 执行此计划。
> 任务使用 checkbox (`- [ ]`) 语法追踪进度。

**目标：** 基于 Harness Engineering + Anthropic 工程博文洞察，对 power-agent 体系实施 3 个 Phase 的增强：Phase 1 核心流程加固、Phase 2 Gate 重构与审查自动化、Phase 3 版本管理与 Eval 框架。

**架构：** 本项目为纯 prompt/skill 工程项目，无代码文件，所有变更为 Markdown 文件编辑。Skill 文件位于 `skills/*/SKILL.md`，辅助文件位于各 skill 目录，工具脚本位于 `scripts/`，设计决策位于 `docs/arch-decisions/`。

**技术栈：** Markdown、Shell Script（scan-antipatterns.sh、sync-version.sh）

**branch:** feat/harness-insights-enhancement

---

## 里程碑

| 阶段 | 内容 | 状态 |
|------|------|------|
| M1 - Phase 1 | exec-plan-runner + systematic-debugging + feature-dev 核心流程加固 | ⏳ |
| M2 - Phase 2 | Gate 重构 + 审查自动化 + 反模式检测 | ⏳ |
| M3 - Phase 3 | 版本管理机制 + Eval 框架 + 验证增强 | ⏳ |

## 当前状态

准备开始。从 Batch 1 开始，并行执行 Task 1-3。

## 验收标准

1. 所有 16 个 `skills/*/SKILL.md` 含 `version: 1.0.0` frontmatter 字段
2. `scripts/sync-version.sh` 运行后输出"版本同步完成"，无错误
3. `scripts/scan-antipatterns.sh` 在示例调用下正常输出报告
4. 所有 DD 文件路径在 `docs/arch-decisions/index.md` 中有对应条目
5. `docs/eval-framework.md` 存在，格式完整
6. exec-plan-runner SKILL.md 包含 Bootstrap、Session Log、输出粒度控制、精简 Escalation 四项变更
