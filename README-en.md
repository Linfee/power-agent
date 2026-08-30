# power-agent

Power-Agent is a **Judgment + Verification + Domain Knowledge** pack for frontier coding models. It draws on [superpowers](https://github.com/obra/superpowers) and [OpenAI Harness Engineering](https://openai.com/index/harness-engineering/), without binding development work to a mandatory pipeline.

## Core ideas

Strong models need clear load-bearing judgments: the observable result the user needs, facts that change the solution, boundaries that must hold, and external evidence sufficient to accept the result.

- **Transferable judgment, verifiable results.** Execution may vary; completion claims must match fresh evidence.
- **Independent capabilities first.** Ordinary skills do not require another named skill to produce input or take over completion.
- **Choose tools from the situation.** The model selects tools, order, sub-agents, and parallelism from dependencies, risk, and write ownership.
- **Mechanize deterministic work.** Schemas, scripts, tests, and hooks enforce repeatable rules; prompts preserve domain judgment.
- **Authorization remains explicit.** External side effects, destructive actions, permissions, production, and sensitive data retain their real approval boundaries.

See [ADR-0010](docs/adr/0010-judgment-oriented-skills.md), [architecture](docs/architecture.md), and [working approach](docs/workflow.md) for the current design.

## Skills

| Skill | Independent judgment it provides |
|---|---|
| `discuss` | Whether goals, tradeoffs, and acceptance are clear enough to act |
| `writing-plans` | Whether a durable plan is useful and what future executors need from it |
| `codebase-design` | Whether module boundaries, interfaces, seams, and adapters reduce real complexity |
| `implement` | How to organize ordinary sub-agents around a goal or any existing plan |
| `proof-oriented-development` | How to make the smallest sufficient change and obtain matching evidence |
| `systematic-debugging` | Which explanation fits the observations, and where the root cause and fix boundary lie |
| `code-review` | Which findings would prevent safe, correct delivery |
| `finish-development` | Whether evidence supports completion and how to safely handle branch disposition |
| `writing-skills` | Whether a skill teaches transferable judgment |
| `harness-engineering-review` | Which harness mechanisms are load-bearing and which can be removed |
| `setup-power-agent` | What minimum agent knowledge a project lacks |
| `dev-docs` | Which stable knowledge belongs in project documentation |
| `dev-docs-maintain` | Whether that knowledge is healthy, current, and verifiable |

The documentation subsystem—`setup-power-agent`, `dev-docs`, and `dev-docs-maintain`—may collaborate when initialization, semantic writing, or mechanical maintenance creates a real knowledge gap. This is the only named collaboration exception, and it is not a fixed chain.

## Sub-agent support

Power-Agent assumes a host with ordinary sub-agents: it can send tasks and context, run independent work concurrently, and collect results. It does not use team mode, prescribe a concurrency number, or maintain a no-sub-agent fallback.

Parallelize only genuinely independent work. Establish a single integrator or serialize shared files, interfaces, and state. A sub-agent result is evidence to verify, not an automatic completion claim.

## Verification and branch disposition

Completion claims require fresh system-external evidence that matches the current result. Verification may run against a dirty worktree; only commit-bound actions such as committing, creating a PR, or merging need evidence tied to a specific commit.

When requested, `finish-development` assesses completion and helps safely handle a commit, PR, merge, retention, or discard. Every external or destructive action still requires explicit authorization at the point of action.

## Installation

### Droid

```bash
droid plugin marketplace add https://github.com/Linfee/power-agent
droid plugin install power-agent@power-agent --scope user
# Or share with a project through git
droid plugin install power-agent@power-agent --scope project
```

You can also install through `/plugins` → Browse.

### Claude Code

```bash
claude plugin marketplace add https://github.com/Linfee/power-agent
claude plugin install power-agent@power-agent --scope user
# Or share with a project through git
claude plugin install power-agent@power-agent --scope project
```

The local plugin manifest is `.claude-plugin/plugin.json`.

### Cursor, Factory, and Gemini

- Cursor: use `.cursor-plugin/plugin.json`, or copy `skills/` into a project.
- Factory: use `.factory-plugin/plugin.json`, or copy `skills/` into a project.
- Gemini: use `gemini-extension.json`; it loads `AGENTS.md` through `GEMINI.md`.

## Development

Read [the skill and harness design guide](docs/skill-and-harness-design.md) before changing a Skill. Run checks that match the change:

```bash
python3 scripts/check-description-length.py
bash scripts/check-invocation-consistency.sh
bash scripts/check-shared-references.sh
python3 -m unittest skills/dev-docs-maintain/scripts/test_bundle_status.py
```

The latter two apply only when the affected area needs them. See [development.md](docs/development.md) for maintenance conventions.

## Attribution

- [superpowers](https://github.com/obra/superpowers) — Jesse Vincent (obra), MIT License
- [Harness Engineering](https://openai.com/index/harness-engineering/) — Ryan Lopopolo, OpenAI
