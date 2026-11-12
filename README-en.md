# power-agent

A personal engineering skill list.

Assembled, adapted, and combined from several open-source agent-skill projects around an established workflow: implementation, diagnosis, design, review, delivery, and documentation. Not a general framework, team standard, or ready-to-use product; intended for personal workflows.

## Design choices

- Small tasks go straight to implementation. Specs, tickets, or maps appear only when dependencies, recovery, or coordination need them.
- Behavior changes start with red/green. Refactoring belongs to the review stage, once behavior is better covered.
- Diagnosis starts with a tight, red-capable loop that asserts the reported symptom; hypotheses come after that.
- Review uses two independent axes, requirements and engineering quality. They are merged only when explicitly requested.
- Automatic invocation fires as needed; manual entries only run when explicitly invoked. Direction, scope, trade-offs, and acceptance do not transfer to automation.
- Documentation goes into the project's existing authoritative location. Session notes, plans, and temporary conclusions are not long-term knowledge.
- Being auto-invocable does not grant permission to commit, push, publish, delete, or change production. Those still need specific authorization.

## How to use it

Describe the result. Automatic skills fire as needed; manual entries require an explicit invocation. There is no fixed pipeline, and no task needs to run the full set.

Common entry points, not a required sequence:

- A clear small task or existing issue → `implement`; `proof-oriented-development` selects the evidence for behavior changes.
- An unclear failure → `diagnosing-bugs`; build the loop before forming a root-cause theory.
- Unclear goals or disagreement over approach → `grilling`; use `grill-with-docs` when domain documents matter.
- A deliverable plan → `to-spec` / `to-tickets`; use `wayfinder` first for complex goals.
- A design or architecture comparison → `codebase-design` / `improve-codebase-architecture`; use `prototype` when running logic or actual UI is needed.
- Implementation finished → `code-review`; use `pr` when a delivery description is needed.

## Skills

24 skills: 15 model-invocable and 9 manual.

### Implementation and repair

| Skill | Purpose | Invocation |
|---|---|---|
| [`proof-oriented-development`](skills/proof-oriented-development/SKILL.md) | Implement behavior changes with red/green and risk-matched evidence | Auto |
| [`diagnosing-bugs`](skills/diagnosing-bugs/SKILL.md) | Find root causes with discriminating evidence; build a red-capable loop first | Auto |
| [`implement`](skills/implement/SKILL.md) | Complete a clear task or existing issue through implementation, verification, and repair | Auto |
| [`implement-spec`](skills/implement-spec/SKILL.md) | Run a tracker-backed task graph and verify the integrated result | Auto |

### Goals, design, and investigation

| Skill | Purpose | Invocation |
|---|---|---|
| [`grilling`](skills/grilling/SKILL.md) | Work the question tree in rounds until shared understanding is confirmed | Auto |
| [`grill-with-docs`](skills/grill-with-docs/SKILL.md) | Combine grilling with domain-modeling for document-heavy or domain-heavy discussions | Manual |
| [`domain-modeling`](skills/domain-modeling/SKILL.md) | Maintain terminology, context boundaries, and decision records worth keeping | Auto |
| [`to-spec`](skills/to-spec/SKILL.md) | Turn a goal into a deliverable, verifiable spec | Manual |
| [`to-tickets`](skills/to-tickets/SKILL.md) | Slice work by observable outcomes and real dependencies | Manual |
| [`triage`](skills/triage/SKILL.md) | Assess scope, duplication, missing information, and readiness | Manual |
| [`wayfinder`](skills/wayfinder/SKILL.md) | Separate decisions from implementation in complex work | Manual |
| [`codebase-design`](skills/codebase-design/SKILL.md) | Judge whether module depth, resource ownership, and interfaces actually reduce complexity | Auto |
| [`improve-codebase-architecture`](skills/improve-codebase-architecture/SKILL.md) | Find architecture improvements grounded in actual friction; produce a candidate report | Manual |
| [`research`](skills/research/SKILL.md) | Resolve technical unknowns with version-matched primary sources | Auto |
| [`prototype`](skills/prototype/SKILL.md) | Answer a design question with a single-file logic prototype or real UI variants | Auto |

### Review and delivery

| Skill | Purpose | Invocation |
|---|---|---|
| [`code-review`](skills/code-review/SKILL.md) | Review changes on requirements and engineering axes with locateable evidence | Auto |
| [`pr`](skills/pr/SKILL.md) | Draft a PR from the actual diff and evidence; publishing needs authorization | Auto |
| [`wizard`](skills/wizard/SKILL.md) | Generate safe scripts for setup that genuinely needs human input or approval | Auto |
| [`handoff`](skills/handoff/SKILL.md) | Hand off the goal, evidence, and authoritative state pointer | Manual |

### Knowledge and meta-skills

| Skill | Purpose | Invocation |
|---|---|---|
| [`dev-docs`](skills/dev-docs/SKILL.md) | Write, revise, and verify durable development knowledge | Auto |
| [`knowledge-navigation`](skills/knowledge-navigation/SKILL.md) | Design or evolve repository knowledge retrieval paths | Manual |
| [`writing-for-agents`](skills/writing-for-agents/SKILL.md) | Write skills, AGENTS.md, and reference material that change agent decisions | Auto |
| [`retro`](skills/retro/SKILL.md) | Improve the harness from session or project evidence instead of stacking prohibitions | Manual |
| [`setup-power-agent`](skills/setup-power-agent/SKILL.md) | Fill the minimum agent entrypoint, tracker, and domain pointers | Auto |

## Installation

Install the whole bundle; standalone skill installation is not supported. Host-specific steps, version limits, and trust conditions are in [host compatibility](docs/agent-compatibility.md).

### Claude Code

```bash
claude plugin marketplace add https://github.com/Linfee/power-agent
claude plugin install power-agent@power-agent --scope user
# Or share configuration with a project
claude plugin install power-agent@power-agent --scope project
```

For a local checkout: `claude --plugin-dir /absolute/path/to/power-agent`. A marketplace catalog and `.claude-plugin/plugin.json` are included. Manifest validation is not runtime validation of every host.

### Codex

```bash
codex plugin marketplace add /absolute/path/to/power-agent
```

Installation is marketplace registration plus desktop-app enablement; the CLI has no `plugin install` subcommand. After registration, install and enable in the Codex desktop app's Plugins page, then start a new session. Non-managed hooks must be reviewed and trusted in `/hooks`, and re-reviewed after definition changes. The IDE extension does not support plugins; successful marketplace registration does not prove that skills or rules were delivered.

### OMP

```bash
# Local checkout is linked, not copied into an independent snapshot
omp plugin install /absolute/path/to/power-agent
omp plugin list
```

Load for one session with `omp --extension /absolute/path/to/power-agent`. Local installation writes host configuration and initializes the extension in a new session.

In the observed OMP 18.18.9 / Bun 1.4.0 environment, a native `github:` install requests the GitHub tarball API and returns 404. Do not work around this by making a private repository public or embedding a token. For an independent snapshot, follow the `gh api` + `npm pack` + `bun add file:` path in [host compatibility](docs/agent-compatibility.md#omp).

### pi

```bash
pi install git:github.com/Linfee/power-agent
# Or a local checkout
pi install /absolute/path/to/power-agent
# Project-scoped install, subject to host trust confirmation
pi install --local /absolute/path/to/power-agent
```

Use `pi list` to inspect configured packages. Personal scope writes host settings; `--local` writes project settings, and a project package loads only after the host trusts the project.

### Cursor

Install from Customize when a marketplace is available, or follow Cursor's local plugin instructions to place the whole plugin under `~/.cursor/plugins/local/power-agent`, then restart or reload the window and inspect Customize. Team marketplaces and local imports are subject to organization policy. On some versions, skills with `disable-model-invocation: true` disappear from the command menu; verify against the target version.

### Droid

```bash
droid plugin marketplace add https://github.com/Linfee/power-agent
droid plugin install power-agent@power-agent --scope user
# Or share configuration with a project
droid plugin install power-agent@power-agent --scope project
```

## Development

Maintenance follows the same rules the list asks agents to use: state the behavior gap, change the skill, then run structural checks and only the necessary real-world scenarios. See [development](docs/development.md) and [skill design](docs/skill-and-harness-design.md).

```bash
python3 scripts/check-description-length.py
bash scripts/check-invocation-consistency.sh
python3 scripts/check-skill-references.py
node --test tests/*.test.cjs
node scripts/sync-plugin-rules.cjs --check
```

Script and behavioral changes also need evidence exercising their actual contract; reachable references alone do not prove execution.

## Status

Personal use, continuously adjusted. No promise of a stable API, backward compatibility, or fitness for every team. Skill count, invocation modes, and content may change. The current baseline is [ADR-0014](docs/adr/0014-current-baseline.md); earlier decisions, the fusion design, and old plans remain in the [ADR index](docs/adr/index.md) and [historical archive](docs/archive/index.md), not as current instructions.

## Sources and license

Not designed from scratch. Main references:

- [Matt Pocock Skills](https://github.com/mattpocock/skills), MIT; pinned source `4ae2317ddb22b046e26455e4f9c9b3aaaf62212d`.
- [superpowers](https://github.com/obra/superpowers), Jesse Vincent, MIT.
- [Ponytail](https://github.com/DietrichGebert/ponytail/tree/96608e078b2d5ea607c5c3b8b5a54d1c1fba6846) v5.3.3, DietrichGebert, MIT; minimal-change and host-integration inspiration, with no separate Ponytail install.
- PR visual guidance retains Dex Horthy / HumanLayer `show-me` credits.
- [Harness Engineering](https://openai.com/index/harness-engineering/) is a methodological reference, not MIT-licensed software copied into this bundle.

Per-skill sources and trade-offs are in the [historical fusion design](docs/archive/2026-11-11-matt-power-agent-fusion.md); third-party notices are in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). License terms are in [LICENSE](LICENSE).
