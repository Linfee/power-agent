# power-agent

An AI coding agent workflow system that combines two complementary methodologies:

- **[superpowers](https://github.com/obra/superpowers)** — A complete software development skill system for AI agents (currently tracking v5.1.0)
- **[Harness Engineering](https://openai.com/index/harness-engineering/)** — OpenAI's methodology for leveraging AI agents in engineering workflows (Ryan Lopopolo, Feb 2026)

The result is a cohesive, opinionated workflow: structured design exploration → TDD-driven exec plans → subagent-orchestrated parallel implementation → systematic debugging → doc gardening.

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
| `discuss` | Design exploration before coding — spec doc with 2-3 approach comparison and spec reviewer loop |
| `writing-plans` | Convert spec/design into TDD-structured exec-plans with executable task cards |
| `exec-plan-runner` | Execute or resume exec-plans with dependency batches, conflict checks, review/fix convergence, verification, and finishing |
| `dev-docs` | Doc router — delegates exec-plan to `writing-plans`, handles other doc types directly |
| `dev-docs-maintain` | Doc gardening — scan and fix stale, missing, or invalid docs on demand |
| `init-harness-engineering` | Bootstrap a project's Harness Engineering knowledge base from scratch |
| `using-git-worktrees` | Detect or prepare isolated worktrees before large execution tasks |
| `writing-skills` | Create, modify, review, and pressure-test skills |
| `systematic-debugging` | Four-phase root-cause-first debugging (no fixes without root cause analysis) |
| `test-driven-development` | Pragmatic incremental test loop with anti-pattern reference |
| `requesting-code-review` | Orchestrate code review via subagent with structured findings |
| `receiving-code-review` | Technical evaluation of review feedback (not performative agreement) |
| `verification-before-completion` | Evidence-first verification — no completion claims without fresh proof |
| `dispatching-parallel-agents` | Schedule independent tasks as parallel subagents |
| `harness-engineering-review` | Audit a project's agent workflow against Harness Engineering best practices |
| `finishing-a-development-branch` | Wrap up a completed branch (merge/PR/keep/discard) |

### Workflow

```
discuss skill          ← optional: design exploration → spec doc
    ↓ (spec approved)
writing-plans skill    ← create TDD-structured exec-plan
    ↓
exec-plan-runner skill ← BOOTSTRAP(using-git-worktrees) → TDD subagents, parallel
                     └── internal review → verification → branch finishing

Bug / test failure → systematic-debugging skill
                         └── → test-driven-development + verification-before-completion
```

`requesting-code-review` is mandatory before merge/PR by default unless the user explicitly asks to skip it and the reason is recorded. `dev-docs-maintain` remains an on-demand doc maintenance skill, not a mandatory step for every development run.

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

---

## Attribution

This project is inspired by and builds on:

- **superpowers** by [obra](https://github.com/obra/superpowers) — MIT License. Currently tracking **v5.1.0**. The following skills are derived from superpowers: `discuss` (from `brainstorming`), `writing-plans`, `exec-plan-runner` (merged with `subagent-driven-development`), `test-driven-development`, `requesting-code-review`, `receiving-code-review`, `verification-before-completion`, `dispatching-parallel-agents`, `systematic-debugging`, `using-git-worktrees`, `writing-skills`.

- **Harness Engineering** — [Ryan Lopopolo, OpenAI, Feb 11, 2026](https://openai.com/index/harness-engineering/). The `harness-engineering-review`, `init-harness-engineering`, `dev-docs`, `dev-docs-maintain` skills and the overall repo-as-SSOT philosophy are derived from this methodology.

### Tracking upstream

This project tracks superpowers releases. When superpowers releases a new version, review RELEASE-NOTES and port relevant improvements:

| Upstream | Tracked version | Source |
|----------|----------------|--------|
| superpowers | v5.1.0 | https://github.com/obra/superpowers |
| Harness Engineering | Feb 2026 | https://openai.com/index/harness-engineering/ |
