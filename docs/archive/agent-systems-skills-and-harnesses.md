---
type: Reference
scope:
  - skills/**
  - docs/**
---

# Agent systems, reusable skills, and harness engineering

> **Historical research, not current guidance.** This note preserves its original source selection and conclusions. See the [documentation index](../index.md) and [current decision](../adr/0014-current-baseline.md).

## Scope and selection

This note compares a deliberately small, high-signal set of first-party Anthropic and OpenAI engineering/product posts published in 2025–2026. It covers three connected concerns: agent-system architecture, reusable procedural capabilities, and the engineering harness around an agent. No older source is included: the selected recent posts directly cover the needed concepts.

## Selected posts

| Organization | Published | Post | Primary topic | Why it matters |
| --- | --- | --- | --- | --- |
| Anthropic | 2025-06-13 | [How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system) | Production orchestrator-worker research system: delegation, tool design, evaluations, observability, and reliability. | A concrete account of when parallel subagents are useful, how to bound their work, and why end-state evaluation and production tracing matter. |
| Anthropic | 2025-10-16 | [Equipping agents for the real world with Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills) | Filesystem-based, composable Skills: `SKILL.md`, optional scripts/resources, and progressive disclosure. | The clearest source for reusable agent capabilities: load only skill metadata initially, then detailed instructions and resources only when relevant; keep deterministic work in code. |
| Anthropic | 2025-11-26 | [Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) | Multi-context coding harness with an initializer, incremental coding sessions, feature inventory, progress artifacts, version control, and end-to-end verification. | Shows how a harness supplies durable state and a clean handoff between fresh contexts, preventing one-shotting, undocumented partial work, and premature completion. |
| Anthropic | 2026-03-24 | [Harness design for long-running application development](https://www.anthropic.com/engineering/harness-design-long-running-apps) | Planner-generator-evaluator architecture, explicit sprint contracts, browser-based QA, and removal of harness components that newer models no longer need. | Provides the most direct design lesson: separate generation from skeptical evaluation, use artifacts for coordination, and regularly test which scaffolding remains load-bearing. |
| OpenAI | 2025-03-11 | [New tools for building agents](https://openai.com/index/new-tools-for-building-agents/) | Responses API, built-in tools, Agents SDK orchestration, and tracing/inspection. | Establishes the platform primitives for production agents: tool use, single- and multi-agent orchestration, and observability are part of the engineering surface—not afterthoughts. |
| OpenAI | 2025-10-06 | [Introducing AgentKit](https://openai.com/index/introducing-agentkit/) | Versioned workflow composition, connector governance, embedded agent UIs, and evaluation tools such as trace grading. | Frames agent delivery as a lifecycle: compose and govern workflows, deploy them, then use datasets and trace-level evaluation to improve them. |
| OpenAI | 2026-02-11 | [Harness engineering: leveraging Codex in an agent-first world](https://openai.com/index/harness-engineering/) | Agent-first software engineering: repository-local knowledge, embedded skills, legible development and observability environments, feedback loops, and enforced invariants. | The most complete OpenAI account of harness engineering. It argues for a compact `AGENTS.md` as a map, structured repository knowledge as the system of record, agent-accessible QA/telemetry, and mechanical guardrails rather than prompt-only control. |

## Comparison

Both organizations describe the model as only one part of a reliable agent system. Anthropic emphasizes the operating pattern around the model: focused delegation, progressive disclosure, artifact handoffs across contexts, and independent evaluation. OpenAI emphasizes the engineering substrate and lifecycle: tool/orchestration primitives, versioned workflows, trace-based evaluation, repository knowledge, and an environment the agent can directly inspect and test.

The shared practical conclusion is to encode reusable procedure and state in versioned artifacts, expose high-signal tools and feedback to the agent, evaluate observable outcomes, and keep the harness no more complex than the current model and task require.

## Source policy

Every link above is a first-party page on `anthropic.com` or `openai.com`, verified during this research. Dates and titles are taken from the pages themselves.
