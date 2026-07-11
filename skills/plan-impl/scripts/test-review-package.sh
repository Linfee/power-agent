#!/usr/bin/env bash
set -euo pipefail

script_dir=$(cd "$(dirname "$0")" && pwd -P)
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT

repo="$tmp/repo"
git init -q "$repo"
git -C "$repo" config user.name Test
git -C "$repo" config user.email test@example.com
mkdir -p "$repo/src" "$repo/docs"
printf 'base staged\n' > "$repo/src/staged.txt"
printf 'base unstaged\n' > "$repo/src/unstaged.txt"
printf 'base unrelated\n' > "$repo/docs/unrelated.txt"
git -C "$repo" add .
git -C "$repo" commit -qm initial

printf 'staged change\n' > "$repo/src/staged.txt"
git -C "$repo" add src/staged.txt
printf 'unstaged change\n' > "$repo/src/unstaged.txt"
printf 'new file content\n' > "$repo/src/new.txt"
printf 'unrelated change\n' > "$repo/docs/unrelated.txt"
printf 'literal pathspec content\n' > "$repo/:(exclude)docs"

mkdir "$repo/nested"
package=$(cd "$repo/nested" && "$script_dir/review-package" --base HEAD -- src)

rg -q 'staged change' "$package"
rg -q 'unstaged change' "$package"
rg -q 'new file content' "$package"
if rg -q 'unrelated change' "$package"; then
  echo "review package leaked a path outside the requested scope" >&2
  exit 1
fi

if [[ -n $(git -C "$repo" status --short -- .power-agent) ]]; then
  echo "scratch workspace is visible in git status" >&2
  exit 1
fi

ln -s "$tmp/missing-target" "$repo/dangling.diff"
if (cd "$repo" && "$script_dir/review-package" --base HEAD --output dangling.diff -- src) 2>/dev/null; then
  echo "review package overwrote a dangling output symlink" >&2
  exit 1
fi

if (cd "$repo" && "$script_dir/review-package" --base HEAD --output review.diff) 2>/dev/null; then
  echo "review package allowed a non-ignored output inside the repository" >&2
  exit 1
fi

literal_package=$(cd "$repo" && "$script_dir/review-package" --base HEAD -- ':(exclude)docs')
rg -q 'literal pathspec content' "$literal_package"
if rg -q 'unrelated change|staged change|unstaged change' "$literal_package"; then
  echo "review package interpreted a literal path as pathspec magic" >&2
  exit 1
fi

mkdir -p "$repo/.power-agent/review-runs" "$tmp/outside"
ln -s "$tmp/outside" "$repo/.power-agent/review-runs/symlink-run"
if (cd "$repo" && "$script_dir/review-workspace" symlink-run) 2>/dev/null; then
  echo "review workspace traversed a symbolic link" >&2
  exit 1
fi


first_workspace=$(cd "$repo" && "$script_dir/review-workspace" stable-run)
[[ -d "$first_workspace" ]]
if (cd "$repo" && "$script_dir/review-workspace" stable-run) 2>/dev/null; then
  echo "review workspace reused an existing run id" >&2
  exit 1
fi

echo "review-package tests passed"
