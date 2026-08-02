#!/usr/bin/env bash
# 校验 skills/*/SKILL.md frontmatter 的 disable-model-invocation 标志
# 与 AGENTS.md Skill 速查表的「手动调用」登记保持一致。
# user-invoked Skill 必须在速查表标注「手动调用」；model-invoked 不得标注。
# 调用方式（invocation mode）改动时必须运行本脚本，防止路由信息与 frontmatter 静默漂移。
set -euo pipefail

cd "$(dirname "$0")/.."

agents_md="AGENTS.md"
failed=0

for f in skills/*/SKILL.md; do
  name="$(basename "$(dirname "$f")")"

  # 只解析 frontmatter（第一个 --- 与第二个 --- 之间）；正文中的提及不算。
  if awk '/^---$/{c++; next} c==1' "$f" | grep -q '^disable-model-invocation: true'; then
    flag=yes
  else
  flag=no
  fi

  # 只解析「## Skill 速查」节（到下一个二级标题为止），按首列精确匹配技能行；
  # 正文其他位置的反引号提及（如调试路径）不得被误当登记。
  section="$(awk '/^## Skill 速查/{f=1; next} /^## /{if(f) exit} f' "$agents_md")"
  row="$(grep -E "^\|[[:space:]]*\`${name}\`[[:space:]]*\|" <<<"$section" || true)"
  if [[ -z "$row" ]]; then
    echo "DRIFT: $name 未在 $agents_md 的 Skill 速查表登记。" >&2
    failed=1
    continue
  fi
  if grep -q '手动调用' <<<"$row"; then
    marked=yes
  else
    marked=no
  fi

  if [[ "$flag" != "$marked" ]]; then
    echo "DRIFT: ${name} frontmatter disable-model-invocation=${flag}，但速查表「手动调用」标注=${marked}。" >&2
    failed=1
  fi
done

if [[ "$failed" -eq 0 ]]; then
  echo "OK: 调用方式标志与速查表登记一致。"
fi
exit "$failed"
