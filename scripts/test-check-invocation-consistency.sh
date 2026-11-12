#!/usr/bin/env bash
# 最小回归：正常自动/手动调用，以及缺少 Codex metadata、布尔标志冲突。
set -euo pipefail

repo="$(cd "$(dirname "$0")/.." && pwd)"
checker="$repo/scripts/check-invocation-consistency.sh"
fixture="$(mktemp -d)"
trap 'rm -rf "$fixture"' EXIT

make_skill() {
  local name="$1" invocation="$2" metadata="$3"
  mkdir -p "$fixture/skills/$name"
  {
    printf '%s\n' '---' "name: $name" 'description: test'
    [[ -n "$invocation" ]] && printf '%s\n' "$invocation"
    printf '%s\n' '---' '# test'
  } >"$fixture/skills/$name/SKILL.md"
  if [[ "$metadata" == interface-only ]]; then
    mkdir -p "$fixture/skills/$name/agents"
    printf '%s\n' 'interface:' '  display_name: Test skill' >"$fixture/skills/$name/agents/openai.yaml"
  elif [[ -n "$metadata" ]]; then
    mkdir -p "$fixture/skills/$name/agents"
    printf '%s\n' 'policy:' "  allow_implicit_invocation: $metadata" >"$fixture/skills/$name/agents/openai.yaml"
  fi
}

write_index() {
  {
    printf '%s\n' '## Skill 速查'
    for row in "$@"; do printf '%s\n' "$row"; done
  } >"$fixture/AGENTS.md"
}

make_skill automatic '' interface-only
make_skill manual 'disable-model-invocation: true # compatible host manual mode' 'false # Codex manual mode'
write_index '| `automatic` | 自动调用 |' '| `manual` | 手动调用 |'
"$checker" "$fixture"

# 手动入口可以调用自动能力；示例和支持资料链接不是 Skill 调度。
printf '%s\n' 'Call the Skill tool with "automatic".' >>"$fixture/skills/manual/SKILL.md"
printf '%s\n' '`not-a-skill`' '```md' '`manual`' '```' \
  '[支持资料](../manual/references/example.md)' >>"$fixture/skills/automatic/SKILL.md"
"$checker" "$fixture"

printf '%s\n' '使用 `manual` 完成任务。' >>"$fixture/skills/automatic/SKILL.md"
if "$checker" "$fixture"; then
  echo 'expected automatic-to-manual dependency to fail' >&2
  exit 1
fi

make_skill automatic '' interface-only
printf '%s\n' '[调用入口](../manual/SKILL.md#test)' >>"$fixture/skills/automatic/SKILL.md"
if "$checker" "$fixture"; then
  echo 'expected linked manual Skill dependency to fail' >&2
  exit 1
fi

make_skill automatic '' interface-only
make_skill manual-peer 'disable-model-invocation: true' false
write_index '| `automatic` | 自动调用 |' '| `manual` | 手动调用 |' '| `manual-peer` | 手动调用 |'
printf '%s\n' 'Call the Skill tool with "manual-peer".' >>"$fixture/skills/manual/SKILL.md"
if "$checker" "$fixture"; then
  echo 'expected manual-to-manual dependency to fail' >&2
  exit 1
fi

rm -rf "$fixture/skills/manual-peer"
make_skill manual 'disable-model-invocation: true' false
write_index '| `automatic` | 自动调用 |' '| `manual` | 手动调用 |'

printf '%s\n' 'policy: {allow_implicit_invocation: false} # must reject automatic' >"$fixture/skills/automatic/agents/openai.yaml"
if "$checker" "$fixture"; then
  echo 'expected automatic Codex false to fail' >&2
  exit 1
fi

printf '%s\n' 'interface:' '  display_name: Test skill' >"$fixture/skills/automatic/agents/openai.yaml"
rm -f "$fixture/skills/manual/agents/openai.yaml"
if "$checker" "$fixture"; then
  echo 'expected missing Codex metadata to fail' >&2
  exit 1
fi

mkdir -p "$fixture/skills/manual/agents"
printf '%s\n' 'policy:' '  allow_implicit_invocation: true' >"$fixture/skills/manual/agents/openai.yaml"
if "$checker" "$fixture"; then
  echo 'expected conflicting Codex boolean to fail' >&2
  exit 1
fi

printf '%s\n' 'policy:' '  allow_implicit_invocation: false' >"$fixture/skills/manual/agents/openai.yaml"
write_index '| `automatic` | 手动调用 |' '| `manual` | 手动调用 |'
if "$checker" "$fixture"; then
  echo 'expected conflicting frontmatter/index boolean to fail' >&2
  exit 1
fi

write_index '| `automatic` | 自动调用 |' '| `manual` | 手动调用 |'
printf '%s\n' '---' 'name: renamed-but-not-moved' 'description: test' '---' '# test' >"$fixture/skills/automatic/SKILL.md"
if "$checker" "$fixture"; then
  echo 'expected directory/frontmatter name mismatch to fail' >&2
  exit 1
fi

make_skill automatic '' interface-only
write_index '| `automatic` | 自动调用 |' '| `manual` | 手动调用 |' '| `retired` | 自动调用 |'
if "$checker" "$fixture"; then
  echo 'expected retired index entry to fail' >&2
  exit 1
fi

echo 'OK: invocation consistency regressions covered.'
