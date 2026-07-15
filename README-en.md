# power-agent

> **Early experimental project.** This is a personal experiment that integrates the [superpowers](https://github.com/obra/superpowers) skill system with OpenAI's [Harness Engineering](https://openai.com/index/harness-engineering/) methodology. It is still early: several core Harness Engineering practices, especially custom linters, application legibility, automated doc gardening, quality scoring, tech-debt tracking, and PR lifecycle automation, are not implemented yet.

An AI coding agent workflow system that combines two complementary methodologies:

- **[superpowers](https://github.com/obra/superpowers)** — A complete software development skill system for AI agents
- **[Harness Engineering](https://openai.com/index/harness-engineering/)** — OpenAI's methodology for leveraging AI agents in engineering workflows (Ryan Lopopolo, Feb 2026)

The result is a cohesive, opinionated workflow: structured design exploration → proof-oriented exec plans → compact exec-plan packages → agent-autonomous implementation loops → systematic debugging → doc gardening.

---

## Core philosophy

**Human steers, agent executes.** Humans design intent and own feedback loops; agents handle implementation closure. Every decision lives in the repo — agents can't see what isn't versioned.

Three principles from Harness Engineering:

1. **Repo as SSOT** — All knowledge must be versioned. What the agent can't see doesn't exist.
2. **Context as map, not encyclopedia** — `AGENTS.md` is a navigation index (~200 lines), not a wiki.
3. **Mechanical constraints over verbose prompts** — Linter/test rules outperform instruction walls.

---

## Skills

| Skill | Purpose |
|-------|---------|
| `discuss` | Requirement discussion and PRD refinement — clarify vague requirements, use HTML visual aids when useful, then run a conclusion review loop |
| `writing-plans` | Convert discussion conclusions, specs, or direct requirements into compact proof-oriented exec-plans, selecting self-review or independent review by risk |
| `plan-impl` | Execute or resume exec-plans; prefer team mode, hand review inputs off as scratch artifacts, use one internal reviewer for separate spec and quality verdicts, then run full review, verification, and finishing |
| `plan-impl-lightweight` | Lightweight path for medium-small tasks: scope_check, proof-oriented implementation, local verification, limited review/fix loop, and escalation to the full runner |
| `dev-docs` | Maintain durable engineering knowledge in `docs/` — stable system facts, boundaries, decision rationale, and integration references; hand execution, refactoring, migration, and task-breakdown plans to `writing-plans` |
| `dev-docs-maintain` | On demand, assess an existing `docs/` OKF Bundle’s health, repair structural or knowledge drift, and record completed verification in its verification ledger |
| `setup-power-agent` | Bootstrap a project's Harness Engineering knowledge base from scratch |
| `using-git-worktrees` | Detect or prepare isolated worktrees before large execution tasks |
| `writing-skills` | Create, modify, review, and pressure-test skills |
| `systematic-debugging` | Exploratory root-cause investigation with evidence, safety, and risk-proportionate performance/stability proof governing fix handoff |
| `proof-oriented-development` | Proof-oriented implementation loop with minimal relevant verification and Proof Block output |
| `requesting-code-review` | Orchestrate code review via subagent with structured findings |
| `receiving-code-review` | Technical evaluation of review feedback (not performative agreement) |
| `verification-before-completion` | Evidence-first verification — no completion claims without fresh proof |
| `harness-engineering-review` | Audit a project's agent workflow against Harness Engineering best practices |
| `finishing-a-development-branch` | Prompt for a dirty worktree or missing HEAD first, then wrap up a clean verified branch (merge/PR/keep/discard) |

### Workflow

```
discuss skill          ← optional: requirement discussion / PRD refinement → inline discussion conclusion (spec doc only when needed)
    ↓ (independent review passed)
writing-plans skill    ← create a compact proof-oriented exec-plan and choose self-review or independent review by plan risk
    ↓
plan-impl skill ← BOOTSTRAP(using-git-worktrees) → lightweight start notice → optional plan-impl-lightweight for medium-small tasks
                     └── prefer team mode; without team tools, fall back to proof-oriented implementation subagents in parallel or serial flow → scratch artifacts + one reviewer with two verdicts → full code review → worktree gate (commit dirty changes or create HEAD first) → verification → branch finishing

Bug / test failure → systematic-debugging skill
                         └── → proof-oriented-development → full code review → worktree gate → verification-before-completion
```

`requesting-code-review` is mandatory before final verification by default. Merge/PR handoff must not skip unresolved review findings unless the user explicitly asks to skip and the reason is recorded. `dev-docs-maintain` remains an on-demand doc maintenance skill, not a mandatory step for every development run.

---

## Installation

### As a Droid plugin (recommended)

```bash
# Add this repo as a marketplace
droid plugin marketplace add https://github.com/Linfee/power-agent

# Install the plugin (user scope — available across all projects)
droid plugin install power-agent@power-agent --scope user

# Or project scope — shared with teammates via git
droid plugin install power-agent@power-agent --scope project
```

Or via the interactive UI: `/plugins` → Browse tab.

### As a Claude Code plugin

Claude Code and Droid share a compatible plugin format. Install the same way via the Claude Code plugin manager, or copy the plugin directory and add it to your plugin path.

### As a Cursor plugin

Use `.cursor-plugin/plugin.json` via Cursor's plugin manager, or copy the `skills/` directory into a project manually.

### As a Factory plugin

Use `.factory-plugin/plugin.json` via Factory's plugin manager, or copy the `skills/` directory into a project manually.

### As a Gemini extension

Use `gemini-extension.json`; it points Gemini at `GEMINI.md`, which in turn loads `AGENTS.md`.

---

## Current status and known gaps

The repository currently provides the skill workflow, docs structure, ADRs, and local visual companion scripts. The following Harness Engineering capabilities are intentionally tracked as gaps rather than claimed as complete:

- **Mechanical constraints:** no project-level lint, formatter, CI, or custom structural tests are provided yet.
- **Application legibility:** no per-worktree app startup, log/metric query, browser-driving, or observability harness is provided.
- **Automated maintenance:** `dev-docs-maintain` is an on-demand skill, not a scheduled background agent that opens PRs.
- **Quality and debt tracking:** no `docs/quality.md`, golden-principles file, or tech-debt tracker exists yet.
- **PR lifecycle:** implementation can finish a branch, but there is no end-to-end PR creation, review-response, CI-fix, and merge loop.

---

## Attribution

This project is inspired by and builds on:

- **superpowers** by [obra](https://github.com/obra/superpowers) — MIT License. The following skills are derived from or inspired by superpowers: `discuss` (from `brainstorming`), `writing-plans`, `plan-impl` (merged with `subagent-driven-development`), `proof-oriented-development` (evolved from the original test-first implementation loop into proof-oriented implementation), `requesting-code-review`, `receiving-code-review`, `verification-before-completion`, `systematic-debugging`, `using-git-worktrees`, `writing-skills`.

- **Harness Engineering** — [Ryan Lopopolo, OpenAI, Feb 11, 2026](https://openai.com/index/harness-engineering/). The `harness-engineering-review`, `setup-power-agent`, `dev-docs`, `dev-docs-maintain` skills and the overall repo-as-SSOT philosophy are derived from this methodology.

### Tracking upstream

| Upstream | Source |
|----------|--------|
| superpowers | https://github.com/obra/superpowers |
| Harness Engineering | https://openai.com/index/harness-engineering/ |
