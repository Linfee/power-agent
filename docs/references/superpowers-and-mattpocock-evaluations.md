---
type: Reference
scope:
  - /Users/linfee/dev/workspace/ai-skills/superpowers/**
  - /Users/linfee/dev/workspace/ai-skills/mattpocock-skills/**
sources:
  - /Users/linfee/dev/workspace/ai-skills/superpowers/docs/testing.md
  - /Users/linfee/dev/workspace/ai-skills/superpowers/CLAUDE.md
  - /Users/linfee/dev/workspace/ai-skills/mattpocock-skills/package.json
  - /Users/linfee/dev/workspace/ai-skills/mattpocock-skills/.github/workflows/release.yml
---

# Superpowers 与 mattpocock-skills 的评测机制

本笔记只基于本地检出；未运行任何测试或评测命令，亦未修改两个上游仓库。这里的“Skill 行为评测”指用真实模型会话衡量指令是否触发、是否遵循；它不同于检查脚本、清单、插件接线或目标项目代码的回归/集成测试。

| 仓库 | 专用 Skill/模型行为评测 | 仓内自动化测试 | 当前可用的仓级入口 |
| --- | --- | --- | --- |
| Superpowers | 有：Drill，设计为真实 CLI/tmux 会话加 LLM verifier；但该检出的 `evals/` 缺失。 | 有，位于 `tests/`；包括确定性插件测试，也有直接调用 Claude 的窄范围回归/集成检查。 | 目录级 `run-*.sh`、Node `npm test`，以及 Claude Code runner。Drill 命令仅有文档，不能在此检出中执行。 |
| mattpocock-skills | 未发现。 | 未发现仓级测试套件或 runner。 | `package.json` 只有 Changesets 的 `changeset`、`version`；release workflow 只安装依赖并运行 Changesets。 |

## Superpowers

### 行为评测：独立的 Drill harness

`/Users/linfee/dev/workspace/ai-skills/superpowers/docs/testing.md:3-7,24-35` 明确把 `evals/` 与 `tests/` 分开：前者用 Python/Drill 驱动 Claude Code、Codex、Gemini CLI 的真实 tmux 会话，并以 LLM actor/verifier 判定 Skill compliance；场景应在 `evals/scenarios/*.yaml`。文档给出的入口是：

```bash
cd /Users/linfee/dev/workspace/ai-skills/superpowers/evals
uv sync --extra dev
export ANTHROPIC_API_KEY=…
uv run drill run triggering-test-driven-development -b claude
```

这是评测的**文档化入口**，不是本次已执行的命令。该本地检出没有 `evals/`：`/Users/linfee/dev/workspace/ai-skills/superpowers/.gitignore:10-13` 说明它是为本地开发克隆的独立仓库，且不随已发布插件分发；`CLAUDE.md:102-104` 指向独立的 `superpowers-evals`。因此无法从此工作区核验具体 scenario、prompt/fixture、grader rubric、原始会话记录、分数或聚合结果。

评测契约是 Skill 在真实会话中的遵循情况，而非仅文本出现。例如新 harness 的固定验收输入是 `Let's make a react todo list`；通过条件是在写代码前自动触发 `brainstorming`，且 PR 要附完整 clean-session transcript（`/Users/linfee/dev/workspace/ai-skills/superpowers/CLAUDE.md:72-91`；`/Users/linfee/dev/workspace/ai-skills/superpowers/.github/PULL_REQUEST_TEMPLATE.md:70-107`）。对会改变行为的 Skill 内容，维护规则还要求多会话 adversarial pressure testing 和 PR 中的 before/after 结果（`/Users/linfee/dev/workspace/ai-skills/superpowers/CLAUDE.md:93-104`、`/Users/linfee/dev/workspace/ai-skills/superpowers/.github/PULL_REQUEST_TEMPLATE.md:109-128`）。这些是要求的评测证据，不是自动证明每个 PR 已产生的结果。

限制：Drill 场景耗时 3–30+ 分钟，当前不进 CI（`/Users/linfee/dev/workspace/ai-skills/superpowers/docs/testing.md:35`）；其单独克隆及本地缺失意味着上述命令、产物和评分不可在本次研究中复现或审计。

### 仓内 tests：接线回归测试与相邻的模型驱动检查

`/Users/linfee/dev/workspace/ai-skills/superpowers/docs/testing.md:8-22` 把 `tests/` 定义为插件/非-LLM代码的 Bash、Node、Python 测试，列举 brainstorm server、OpenCode loading/caching/tool registration、Codex sync、Kimi manifest 等。这些不是 Drill 的 Skill-compliance eval。

可运行入口随目录而变，主要是：

```bash
cd /Users/linfee/dev/workspace/ai-skills/superpowers/tests/claude-code && ./run-skill-tests.sh
cd /Users/linfee/dev/workspace/ai-skills/superpowers/tests/claude-code && ./run-skill-tests.sh --integration
cd /Users/linfee/dev/workspace/ai-skills/superpowers/tests/opencode && ./run-tests.sh [--integration]
cd /Users/linfee/dev/workspace/ai-skills/superpowers/tests/explicit-skill-requests && ./run-all.sh
node --test /Users/linfee/dev/workspace/ai-skills/superpowers/tests/pi/test-pi-extension.mjs
```

Claude runner 的默认项目测试是 `test-worktree-path-policy.sh`、`test-sdd-workspace.sh`、`test-subagent-driven-development.sh`；`--integration` 额外加入 SDD integration test（`/Users/linfee/dev/workspace/ai-skills/superpowers/tests/claude-code/run-skill-tests.sh:25-95`）。OpenCode runner 的默认检查是 loading/caching，`--integration` 才运行 tools/priority（`/Users/linfee/dev/workspace/ai-skills/superpowers/tests/opencode/run-tests.sh:17-80`）。每个 runner 以进程退出码及 PASS/FAIL/SKIP summary 产出结果（`/Users/linfee/dev/workspace/ai-skills/superpowers/tests/claude-code/run-skill-tests.sh:102-190`；`/Users/linfee/dev/workspace/ai-skills/superpowers/tests/opencode/run-tests.sh:87-165`）。

其中两类会直接调用模型，仍应和 Drill 分开：

- `/Users/linfee/dev/workspace/ai-skills/superpowers/tests/claude-code/test-subagent-driven-development.sh` 通过 `claude -p` 问九个固定问题，再以大小写不敏感的 regex/顺序断言回答中有 workflow 关键词（`/Users/linfee/dev/workspace/ai-skills/superpowers/tests/claude-code/test-helpers.sh:4-129`；`/Users/linfee/dev/workspace/ai-skills/superpowers/tests/claude-code/test-subagent-driven-development.sh:1-179`）。源文件自己说明它测的是“description-recall”，不是实际行为；`/Users/linfee/dev/workspace/ai-skills/superpowers/docs/testing.md:17-20` 同样标注其无 Drill counterpart。
- `/Users/linfee/dev/workspace/ai-skills/superpowers/tests/claude-code/test-subagent-driven-development-integration.sh` 在临时 Node 项目中让 Claude 执行一个两任务计划。它读取 Claude JSONL，严格断言 Skill tool 被调用、至少两个 Agent/Task dispatch、至少一次 task-tracking；并检查 `src/math.js` 的 `add`/`multiply` 文本、测试文件存在、`npm test` 成功、提交数大于 2（`/Users/linfee/dev/workspace/ai-skills/superpowers/tests/claude-code/test-subagent-driven-development-integration.sh:35-189,200-286`）。它还运行 token-usage 分析（同文件:299-305）。

后者的脚本开头及 README 宣称会验证“plan read once”、完整 task text、自审、review 顺序、独立 spec review 与 review loop（`/Users/linfee/dev/workspace/ai-skills/superpowers/tests/claude-code/test-subagent-driven-development-integration.sh:24-30`；`/Users/linfee/dev/workspace/ai-skills/superpowers/tests/claude-code/README.md:97-116`），但当前可见的失败计数断言只覆盖 tool 调用/数量、产物、`npm test`、提交数；“extra features”只是 WARN，不会使测试失败（`/Users/linfee/dev/workspace/ai-skills/superpowers/tests/claude-code/test-subagent-driven-development-integration.sh:289-296`）。故不能把 README 的完整流程列表当作该脚本目前逐项自动断言的证据。

`/Users/linfee/dev/workspace/ai-skills/superpowers/tests/explicit-skill-requests/run-test.sh` 是另一种窄模型回归：它将固定 prompt 交给 `claude -p --output-format stream-json`，检查 stream JSON 是否含匹配的 `Skill` invocation，并检查第一次 Skill 前是否有其他工具调用（`/Users/linfee/dev/workspace/ai-skills/superpowers/tests/explicit-skill-requests/run-test.sh:1-129`）。这检查显式点名 Skill 的触发顺序，不评估完成任务的质量或 Skill 的全面遵循。

可保留/观察的本地测试工件有限：常规 Claude helper 使用 `mktemp` 后删除输出（`/Users/linfee/dev/workspace/ai-skills/superpowers/tests/claude-code/test-helpers.sh:4-28`）；SDD integration 的临时项目会在 `EXIT` 时删除，而 Claude 会话 JSONL 留在 `~/.claude/projects/...` 并被脚本分析（`/Users/linfee/dev/workspace/ai-skills/superpowers/tests/claude-code/test-subagent-driven-development-integration.sh:35-40,162-198`）。显式 Skill 测试则保留 `/tmp/superpowers-tests/<timestamp>/...` 下的 prompt 副本和 `claude-output.json`（`/Users/linfee/dev/workspace/ai-skills/superpowers/tests/explicit-skill-requests/run-test.sh:27-76`）。这些是诊断日志，不是标准化的 Drill 分数或长期结果库。

## mattpocock-skills

此检出没有专用 eval harness、`evals/` 目录、仓级 test script、测试框架配置或 `*.test`/`*.spec` 测试文件。该结论的直接正面依据是 `/Users/linfee/dev/workspace/ai-skills/mattpocock-skills/package.json:1-20`：只有 `changeset` 与 `version` scripts，dev dependencies 也只有 Changesets；release CI 仅执行 `npm ci` 和 Changesets 的 version/tag 操作（`/Users/linfee/dev/workspace/ai-skills/mattpocock-skills/.github/workflows/release.yml:1-37`）。本地根配置/目录检索也没有发现 Vitest/Jest/Playwright 配置、测试目录或评测/benchmark/grader/fixture/snapshot 目录。

仓库提供的是**给被应用目标项目的测试方法**，不是对自身 Skills 的可执行评测：

- `/Users/linfee/dev/workspace/ai-skills/mattpocock-skills/skills/engineering/tdd/SKILL.md:12-36` 要求测试穿过已确认的公共 seam、断言独立预期值，并逐个 red→green vertical slice。`/Users/linfee/dev/workspace/ai-skills/mattpocock-skills/skills/engineering/tdd/tests.md:5-76` 给出 integration-style public API 与反例（内部 mock、私有方法、重新计算预期值）。这些是测试质量规范和示例，不是该仓库运行的测试。
- `/Users/linfee/dev/workspace/ai-skills/mattpocock-skills/skills/engineering/implement/SKILL.md:7-15` 指示 agent 在**目标项目**经常跑 typecheck/单文件测试、最后跑全量测试，但没有指定项目无关的具体命令或提供 runner。
- `/Users/linfee/dev/workspace/ai-skills/mattpocock-skills/skills/engineering/diagnosing-bugs/SKILL.md:18-29,51-58,108-132` 要求为实际 bug 构造可红可绿、确定、快速、可由 agent 运行的反馈 loop；可能是 unit/integration/e2e test、curl、fixture + known-good snapshot、browser assertion、trace replay、fuzz、bisection 或 differential run。修复时，把最小复现写成回归测试，再重跑原始复现。它评估的是被诊断系统的用户症状，不是 Skill 的模型行为。

这些运行可以产生目标项目的 test 输出、fixture/snapshot、capture trace/log，以及人机 loop 的 captured values；最后一种模板会打印 `KEY=VALUE` 给 agent 解析（`/Users/linfee/dev/workspace/ai-skills/mattpocock-skills/skills/engineering/diagnosing-bugs/scripts/hitl-loop.template.sh:1-42`）。它们由目标项目和一次诊断决定，仓内没有固定场景、golden answer、grader、分数或结果归档。

`/Users/linfee/dev/workspace/ai-skills/mattpocock-skills/skills/engineering/code-review/SKILL.md:6-89` 的 Standards/Spec 双轴和并行 subagents 是 diff 审查流程；它产出 findings，而非可重复、带基准样本和判分器的 Skill eval。因而也不应把 review 当作本仓的评测基础设施。

## 对比与采用边界

Superpowers 明确把“真实模型行为 + LLM verifier”的 Drill scenario eval 与仓内回归/集成测试分层，并以 PR transcript、adversarial sessions、before/after 结果作为变更证据。代价是评测慢、未进 CI，且此本地检出不含 harness 或其评分工件。mattpocock-skills 则编码了目标项目的 TDD、诊断反馈环和代码审查实践；截至本地可见源，它没有衡量这些 Skill 本身是否被模型正确触发或遵循的仓级机制。两者的目标项目测试都不能替代前者的 Skill 行为评测。
