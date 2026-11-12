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

24 skills: 14 model-invocable and 10 manual.

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
| [`setup-power-agent`](skills/setup-power-agent/SKILL.md) | Fill the minimum agent entrypoint, tracker, and domain pointers | Manual |

## Installation

Install the whole bundle; standalone skill installation is not supported. Host-specific steps, version limits, and trust conditions are in [host compatibility](docs/agent-compatibility.md).

### Claude Code

```bash
claude plugin marketplace add https://github.com/Linfee/power-agent
claude plugin install power-agent@power-agent --scope user
# Or share configuration with a project
claude plugin install power-agent@power-agent --scope project
```

The repository includes a marketplace catalog and `.claude-plugin/plugin.json`. After installation, verify plugin, hook, and skill loading in a new session; catalog validation is not runtime validation of every host.

### Codex

```bash
codex plugin marketplace add Linfee/power-agent
codex plugin add power-agent@power-agent
```

Start a new session after installation; the desktop app's Plugins page shows enablement. Non-managed hooks must be reviewed and trusted in `/hooks`, and re-reviewed after definition changes. The IDE extension does not support plugins; successful marketplace registration does not prove that skills or rules were delivered.

### OMP

```bash
omp plugin install github:Linfee/power-agent
omp plugin list
```

Installation writes host configuration and initializes the extension in a new session; `omp plugin list` confirms that the plugin is registered and enabled.

### pi

```bash
pi install git:github.com/Linfee/power-agent
# Project-scoped install; --approve trusts this project for the command
pi install git:github.com/Linfee/power-agent --local --approve
```

Use `pi list --approve` to include project-scoped packages. Personal scope writes host settings; `--local` writes project settings, and a project package loads only after the host trusts the project.

### Cursor

Personal installation goes through Cursor Marketplace: search for Power-Agent in **Customize** and install it. Availability depends on the target version; a public Git repository alone is not a personal plugin source.

Teams and Enterprise admins can import the public repository through **Dashboard → Plugins & MCPs → Import from Repo**, then install from Customize. On some versions, skills with `disable-model-invocation: true` disappear from the command menu; verify against the target version.

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

Personal use, continuously adjusted. No promise of a stable API, backward compatibility, or fitness for every team. Skill count, invocation modes, and content may change. The current baseline is [ADR-0014](docs/adr/0014-current-baseline.md); earlier ADR numbers and history remain in Git history, while archived bodies were removed and are not current instructions.

## Sources and license

Not designed from scratch. Main references:

- [Matt Pocock Skills](https://github.com/mattpocock/skills), MIT; pinned source `4ae2317ddb22b046e26455e4f9c9b3aaaf62212d`.
- [superpowers](https://github.com/obra/superpowers), Jesse Vincent, MIT.
- [Ponytail](https://github.com/DietrichGebert/ponytail/tree/96608e078b2d5ea607c5c3b8b5a54d1c1fba6846) v5.3.3, DietrichGebert, MIT; minimal-change and host-integration inspiration, with no separate Ponytail install.
- PR visual guidance retains Dex Horthy / HumanLayer `show-me` credits.
- [Harness Engineering](https://openai.com/index/harness-engineering/) is a methodological reference, not MIT-licensed software copied into this bundle.

Per-skill sources and trade-offs were recorded in the historical fusion design, now removed with the archive; the record remains available in Git history. Third-party notices are in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). License terms are in [LICENSE](LICENSE).
