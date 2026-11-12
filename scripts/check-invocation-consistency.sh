#!/usr/bin/env bash
# 校验调用方式、AGENTS.md 索引、Codex 元数据及正文具名依赖的可达性。
# 兼容 frontmatter 的宿主用 disable-model-invocation: true 表示手动调用；
# Codex 用 agents/openai.yaml 的 policy.allow_implicit_invocation: false。
# 用法：scripts/check-invocation-consistency.sh [repo-root]
set -euo pipefail

repo="${1:-$(cd "$(dirname "$0")/.." && pwd)}"
cd "$repo"

agents_md="AGENTS.md"
failed=0
manual_skills=""
section="$(awk '/^## Skill 速查/{f=1; next} /^## /{if(f) exit} f' "$agents_md")"

frontmatter() {
  awk '/^---$/{c++; next} c==1' "$1"
}

bool_value() {
  local file="$1" key="$2" value count
  value="$(awk -F ': *' -v key="$key" '{ field = $1; sub(/^[[:space:]]+/, "", field); if (field == key) { value = $2; sub(/[[:space:]]+#.*/, "", value); sub(/^[[:space:]]+/, "", value); sub(/[[:space:]]+$/, "", value); print value } }' "$file")"
  count="$(wc -l <<<"$value" | tr -d ' ')"
  if [[ "$count" -gt 1 ]]; then
    echo "DRIFT: $file 的 $key 重复声明。" >&2
    return 2
  fi
  case "$value" in
    true|false) printf '%s\n' "$value" ;;
    '') return 1 ;;
    *) echo "DRIFT: $file 的 $key 必须是 true 或 false。" >&2; return 2 ;;
  esac
}

codex_policy_bool() {
  local file="$1" value count
  value="$(awk '
    function emit_policy_value(line) {
      sub(/^[[:space:]]*allow_implicit_invocation:[[:space:]]*/, "", line)
      sub(/[[:space:]]+#.*/, "", line)
      sub(/[,}[:space:]].*$/, "", line)
      print line
      found = 1
    }
    /^[[:space:]]+policy:/ { invalid = 1; next }
    /^policy:/ {
      saw_policy = 1
      line = $0
      sub(/^[[:space:]]*policy:[[:space:]]*/, "", line)
      sub(/[[:space:]]+#.*/, "", line)
      if (line == "") { in_policy = 1; next }
      if (line ~ /^\{.*\}$/) {
        if (line ~ /allow_implicit_invocation:[[:space:]]*(true|false)/) {
          sub(/^.*allow_implicit_invocation:[[:space:]]*/, "", line)
          sub(/[,}[:space:]].*$/, "", line)
          print line
          found = 1
        }
        next
      }
      invalid = 1
      next
    }
    in_policy && /^[^[:space:]#][^:]*:/ { in_policy = 0 }
    in_policy {
      line = $0
      sub(/^[[:space:]]+/, "", line)
      if (line ~ /^allow_implicit_invocation:[[:space:]]*(true|false)([[:space:]]|#|$)/) emit_policy_value(line)
    }
    END {
      if (invalid || found > 1) exit 2
      if (!found) exit 1
    }
  ' "$file")"
  count="$(wc -l <<<"$value" | tr -d ' ')"
  if [[ "$count" -gt 1 ]]; then
    echo "DRIFT: $file 的 policy.allow_implicit_invocation 重复声明。" >&2
    return 2
  fi
  case "$value" in
    true|false) printf '%s\n' "$value" ;;
    '') return 1 ;;
    *) echo "DRIFT: $file 的 policy.allow_implicit_invocation 必须是 true 或 false。" >&2; return 2 ;;
  esac
}

for f in skills/*/SKILL.md; do
  name="$(basename "$(dirname "$f")")"
  printf -v pattern '^\\|[[:space:]]*`%s`[[:space:]]*\\|' "$name"
  row="$(grep -E "$pattern" <<<"$section" || true)"
  rows="$(wc -l <<<"$row" | tr -d ' ')"
  if [[ -z "$row" ]]; then
    echo "DRIFT: $name 未在 $agents_md 的 Skill 速查表登记。" >&2
    failed=1
    continue
  fi
  if [[ "$rows" -ne 1 ]]; then
    echo "DRIFT: $name 在 $agents_md 的 Skill 速查表重复登记。" >&2
    failed=1
    continue
  fi

  marked=no
  grep -q '手动调用' <<<"$row" && marked=yes

  fm_file="$(mktemp)"
  frontmatter "$f" >"$fm_file"
  declared_name="$(awk '/^name:[[:space:]]*/ { sub(/^name:[[:space:]]*/, ""); sub(/[[:space:]]+#.*/, ""); sub(/[[:space:]]+$/, ""); if (($0 ~ /^".*"$/) || ($0 ~ /^\047.*\047$/)) $0 = substr($0, 2, length($0) - 2); print }' "$fm_file")"
  if [[ "$declared_name" != "$name" ]]; then
    echo "DRIFT: $f 的 frontmatter name 必须与目录 $name 一致。" >&2
    failed=1
  fi
  if flag="$(bool_value "$fm_file" "disable-model-invocation")"; then
    :
  else
    status=$?
    rm -f "$fm_file"
    if [[ "$status" -eq 1 ]]; then
      flag=false
    else
      failed=1
      continue
    fi
  fi
  rm -f "$fm_file"

  manual=no
  [[ "$flag" == true ]] && manual=yes
  if [[ "$manual" == yes ]]; then
    manual_skills+=$'\n'"$name"
  fi
  expected_marked=no
  [[ "$manual" == yes ]] && expected_marked=yes
  if [[ "$marked" != "$expected_marked" ]]; then
    echo "DRIFT: ${name} frontmatter disable-model-invocation=${flag}，但速查表「手动调用」标注=${marked}。" >&2
    failed=1
  fi

  codex="skills/$name/agents/openai.yaml"
  if [[ -f "$codex" ]]; then
    if codex_flag="$(codex_policy_bool "$codex")"; then
      :
    else
      status=$?
      if [[ "$status" -eq 1 ]]; then
        codex_flag=true
      else
        echo "DRIFT: $codex 的 policy 必须是顶层 block 或 inline map，且 allow_implicit_invocation 必须是布尔值。" >&2
        failed=1
        continue
      fi
    fi
  else
    codex_flag=missing
  fi

  if [[ "$manual" == yes && "$codex_flag" != false ]]; then
    echo "DRIFT: $name 是手动调用，但 Codex metadata 必须声明 policy.allow_implicit_invocation: false。" >&2
    failed=1
  elif [[ "$manual" == no && "$codex_flag" == false ]]; then
    echo "DRIFT: $name 是自动调用，但 Codex metadata 禁用了隐式调用。" >&2
    failed=1
  fi
done

# 正文中的具名入口表示依赖；忽略 frontmatter、围栏示例和普通支持资料。
for f in skills/*/SKILL.md; do
  name="$(basename "$(dirname "$f")")"
  body="$(awk '
    NR == 1 && /^---$/ { header = 1; next }
    header { if ($0 == "---") header = 0; next }
    /^[[:space:]]*(```|~~~)/ { fenced = !fenced; next }
    !fenced { print }
  ' "$f")"
  while IFS= read -r target; do
    [[ -n "$target" && "$target" != "$name" ]] || continue
    printf -v dependency_pattern '(`%s`|"%s"|\\]\\(\\.\\./%s/SKILL\\.md([#)]|$))' "$target" "$target" "$target"
    if grep -Eq "$dependency_pattern" <<<"$body"; then
      echo "DRIFT: $name 的具名依赖 $target 是手动 Skill，不能自动调用。" >&2
      failed=1
    fi
  done <<<"$manual_skills"
done

while IFS= read -r indexed_name; do
  [[ -n "$indexed_name" ]] || continue
  if [[ ! -f "skills/$indexed_name/SKILL.md" ]]; then
    echo "DRIFT: $agents_md 登记了不存在的 Skill $indexed_name。" >&2
    failed=1
  fi
done < <(awk -F '`' '/^\|[[:space:]]*`[^`]+`[[:space:]]*\|/ { print $2 }' <<<"$section")

if [[ "$failed" -eq 0 ]]; then
  echo "OK: 索引、frontmatter、Codex 调用方式与具名依赖可达性一致。"
fi
exit "$failed"
