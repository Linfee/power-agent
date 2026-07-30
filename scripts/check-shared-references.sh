#!/usr/bin/env bash
# 校验跨 skill 共享的 reference 文件保持一致。
# 这些文件在每个使用它的 skill 内各存一份（skill 可独立安装，不能跨 skill 相对引用），
# 靠本脚本防止静默漂移：修改任一副本后必须同步其余副本。
set -euo pipefail

cd "$(dirname "$0")/.."

# 每行一对：canonical|copy
pairs=(
  "skills/dev-docs/references/okf-v0.1.md|skills/dev-docs-maintain/references/okf-v0.1.md"
)

failed=0
for pair in "${pairs[@]}"; do
  a="${pair%%|*}"
  b="${pair##*|}"
  if ! cmp -s "$a" "$b"; then
    echo "DRIFT: $a 与 $b 不一致，请同步后重跑。" >&2
    failed=1
  fi
done

if [[ "$failed" -eq 0 ]]; then
  echo "OK: 共享 reference 文件一致。"
fi
exit "$failed"
