# power-agent

An AI coding agent workflow system that combines two complementary methodologies:

- **[superpowers](https://github.com/obra/superpowers)** — A complete software development skill system for AI agents (currently tracking v5.0.5)
- **[Harness Engineering](https://openai.com/index/harness-engineering/)** — OpenAI's methodology for leveraging AI agents in engineering workflows (Ryan Lopopolo, Feb 2026)

The result is a cohesive, opinionated workflow: structured design exploration → TDD-driven exec plans → subagent-orchestrated parallel implementation → systematic debugging → doc gardening.

---

## Core philosophy

**Human steers, agent executes.** Humans design intent and own feedback loops; agents handle implementation closure. Every decision lives in the repo — agents can't see what isn't versioned.

Three principles from Harness Engineering:

1. **Repo as SSOT** — All knowledge must be versioned. What the agent can't see doesn't exist.
2. **Context as map, not encyclopedia** — `AGENTS.md` is a navigation index (~150 lines), not a wiki.
3. **Mechanical constraints over verbose prompts** — Linter/test rules outperform instruction walls.

---

## Skills

| Skill | Purpose |
|-------|---------|
| `feature-dev` | Eight-phase guided feature development (thin orchestrator connecting all other skills) |
| `discuss` | Design exploration before coding — spec doc with 2-3 approach comparison and spec reviewer loop |
| `writing-plans` | Convert spec/design into TDD-structured exec-plans with complete code snippets |
| `exec-plan-runner` | Execute exec-plans via one-shot subagents, parallel batches, two-phase code review |
| `dev-docs` | Doc router — delegates exec-plan to `writing-plans`, handles other doc types directly |
| `dev-docs-maintain` | Doc gardening — scan and fix stale docs after major features |
| `init-harness-engineering` | Bootstrap a project's Harness Engineering knowledge base from scratch |
| `systematic-debugging` | Four-phase root-cause-first debugging (no fixes without root cause analysis) |
| `test-driven-development` | RED-GREEN-REFACTOR enforcement with anti-pattern reference |
| `requesting-code-review` | Orchestrate code review via subagent with structured findings |
| `receiving-code-review` | Technical evaluation of review feedback (not performative agreement) |
| `verification-before-completion` | Evidence-first verification — no completion claims without fresh proof |
| `dispatching-parallel-agents` | Schedule independent tasks as parallel subagents |
| `harness-engineering-review` | Audit a project's agent workflow against Harness Engineering best practices |

### Workflow

```
discuss skill          ← optional: design exploration → spec doc
    ↓ (spec approved)
feature-dev skill
    ├── Phase 1-3: Context + Codebase exploration + Clarification
    ├── Phase 4:   Architecture design (human selects)
    ├── Phase 5:   writing-plans skill → exec-plan
    ├── Phase 6:   exec-plan-runner skill (TDD subagents, parallel)
    ├── Phase 7:   requesting-code-review skill
    └── Phase 8:   dev-docs-maintain skill

Bug / test failure → systematic-debugging skill
                         └── → test-driven-development + verification-before-completion
```

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

### As Cursor rules

Copy `.cursor/rules/power-agent.mdc` into your project's `.cursor/rules/` directory. This provides skill descriptions as Cursor context rules.

---

## Attribution

This project is inspired by and builds on:

- **superpowers** by [obra](https://github.com/obra/superpowers) — MIT License. Currently tracking **v5.0.5**. The following skills are derived from superpowers: `discuss` (from `brainstorming`), `writing-plans`, `exec-plan-runner` (merged with `subagent-driven-development`), `test-driven-development`, `requesting-code-review`, `receiving-code-review`, `verification-before-completion`, `dispatching-parallel-agents`, `systematic-debugging`.

- **Harness Engineering** — [Ryan Lopopolo, OpenAI, Feb 11, 2026](https://openai.com/index/harness-engineering/). The `harness-engineering-review`, `init-harness-engineering`, `dev-docs`, `dev-docs-maintain` skills and the overall repo-as-SSOT philosophy are derived from this methodology.

### Tracking upstream

This project tracks superpowers releases. When superpowers releases a new version, review the changelog and port relevant improvements:

| Upstream | Tracked version | Source |
|----------|----------------|--------|
| superpowers | v5.0.5 | https://github.com/obra/superpowers |
| Harness Engineering | Feb 2026 | https://openai.com/index/harness-engineering/ |
