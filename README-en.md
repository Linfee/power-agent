# power-agent

A Matt-led engineering skill bundle, combining [Matt Pocock’s skills](https://github.com/mattpocock/skills) with Power-Agent’s proof-oriented development (POD), causal diagnosis, engineering judgment, project knowledge, and **continuous execution within authorization**.

## Usage

Describe the result. A clear small task or existing issue goes straight to implementation; discuss genuine uncertainty and create specs/tickets only when dependencies, coordination, or recovery need them. The user does not manually relay every skill transition.

Automated behavioral changes default to red/green/refactor. Continue through relevant verification, review, and repairs, but a request for advice, discussion, or a draft does not authorize implementation or publication. Commits, pushes, PRs, merges, secrets, permissions, and production changes retain their explicit authorization boundaries.

All 25 skills are **model-invocable and distributed together**. Named dependencies are intentional; standalone skill installation is not supported. The host needs ordinary sub-agents with fresh contexts. Parallelism follows dependencies and write ownership. One tracker owns execution state; documentation and handoffs do not duplicate progress.

## Skills

| Skill | Result |
|---|---|
| [`proof-oriented-development`](skills/proof-oriented-development/SKILL.md) | Implement behavior with red/green/refactor and evidence for the real risk |
| [`code-review`](skills/code-review/SKILL.md) | Review requirements and engineering quality with actionable evidence |
| [`diagnosing-bugs`](skills/diagnosing-bugs/SKILL.md) | Find causes using discriminating evidence, not plausible patches |
| [`codebase-design`](skills/codebase-design/SKILL.md) | Judge module depth, resource ownership, and useful interfaces |
| [`grilling`](skills/grilling/SKILL.md) | Resolve facts and ask only consequential preference questions |
| [`grill-with-docs`](skills/grill-with-docs/SKILL.md) | Preserve agreed discussion outcomes in the right knowledge source |
| [`domain-modeling`](skills/domain-modeling/SKILL.md) | Reuse domain terminology and record consequential decisions |
| [`to-spec`](skills/to-spec/SKILL.md) | Turn a goal into an actionable, verifiable spec |
| [`to-tickets`](skills/to-tickets/SKILL.md) | Slice work by observable outcomes and real dependencies |
| [`implement`](skills/implement/SKILL.md) | Complete a clear task or existing issue with implementation and proof |
| [`implement-spec`](skills/implement-spec/SKILL.md) | Execute a task graph from one tracker and verify the integrated result |
| [`triage`](skills/triage/SKILL.md) | Triage scope, duplicates, missing information, and readiness |
| [`wayfinder`](skills/wayfinder/SKILL.md) | Separate decisions from implementation in complex work |
| [`improve-codebase-architecture`](skills/improve-codebase-architecture/SKILL.md) | Find architectural improvements grounded in actual friction |
| [`research`](skills/research/SKILL.md) | Resolve technical unknowns with version-matched primary sources |
| [`prototype`](skills/prototype/SKILL.md) | Answer a design question with running logic or actual UI |
| [`pr`](skills/pr/SKILL.md) | Draft a PR from the actual diff and evidence; publish only when authorized |
| [`wizard`](skills/wizard/SKILL.md) | Generate safe scripts for setup that genuinely needs human input |
| [`handoff`](skills/handoff/SKILL.md) | Carry intent, evidence, and the authoritative state pointer |
| [`writing-for-agents`](skills/writing-for-agents/SKILL.md) | Write agent instructions and skills that change useful decisions |
| [`retro`](skills/retro/SKILL.md) | Improve the harness from session or project evidence |
| [`dev-docs`](skills/dev-docs/SKILL.md) | Preserve durable knowledge using the project’s documentation conventions |
| [`dev-docs-maintain`](skills/dev-docs-maintain/SKILL.md) | Scan knowledge and safely record verification that actually occurred |
| [`knowledge-navigation`](skills/knowledge-navigation/SKILL.md) | Build or improve knowledge retrieval paths for actual tasks |
| [`setup-power-agent`](skills/setup-power-agent/SKILL.md) | Fill the minimum agent entrypoint and selected tracker/domain pointers |

## Installation

### Claude Code

```bash
claude plugin marketplace add https://github.com/Linfee/power-agent
claude plugin install power-agent@power-agent --scope user
# Or share configuration with a project
claude plugin install power-agent@power-agent --scope project
```

For a local checkout: `claude --plugin-dir /absolute/path/to/power-agent`. A marketplace catalog and `.claude-plugin/plugin.json` are included. Manifest validation is not runtime validation of every host.

### Droid

```bash
droid plugin marketplace add https://github.com/Linfee/power-agent
droid plugin install power-agent@power-agent --scope user
# Or share configuration with a project
droid plugin install power-agent@power-agent --scope project
```

### Other hosts

Cursor and Factory manifests are `.cursor-plugin/plugin.json` and `.factory-plugin/plugin.json`. Alternatively install the complete `skills/` contents in the host’s supported skill location, preserving sibling directories. Confirm the host’s loading behavior and ordinary sub-agent support.

`gemini-extension.json` references the project entrypoint through `GEMINI.md`; this does not establish installation or discovery of the 25 skills. Configure whole-bundle discovery separately and verify the host capabilities.

## Development

See [development.md](docs/development.md) and [the skill design guide](docs/skill-and-harness-design.md). Common checks:

```bash
python3 scripts/check-description-length.py
bash scripts/check-invocation-consistency.sh
python3 scripts/check-skill-references.py
python3 -m unittest skills/dev-docs-maintain/scripts/test_bundle_status.py
```

Run the last command when the knowledge tooling changes. Script and behavioral changes also need evidence exercising their actual contract; reachable references alone do not prove execution.

## Design and attribution

See [architecture](docs/architecture.md), [workflow](docs/workflow.md), and [ADR-0012](docs/adr/0012-matt-led-skill-fusion.md). The [fusion design](docs/specs/2026-11-11-matt-power-agent-fusion.md) records per-skill sources, retained judgment, integration, deletions, and acceptance.

- Matt Pocock Skills, MIT; pinned source `4ae2317ddb22b046e26455e4f9c9b3aaaf62212d`.
- [superpowers](https://github.com/obra/superpowers), Jesse Vincent, MIT.
- PR visual guidance retains Dex Horthy / HumanLayer `show-me` credits and its MIT notice.
- [Harness Engineering](https://openai.com/index/harness-engineering/) is a methodological reference, not MIT-licensed software copied into this bundle.

See [LICENSE](LICENSE) and [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) for permission terms and third-party attribution.
