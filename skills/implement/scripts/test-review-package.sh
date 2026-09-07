#!/usr/bin/env bash
set -euo pipefail

source_script_dir=$(cd "$(dirname "$0")" && pwd -P)
tmp=$(mktemp -d)
tmp=$(cd "$tmp" && pwd -P)
trap 'rm -rf "$tmp"' EXIT

# Exercise an installed Skill separately from the target repository, including
# spaces in both paths. The scripts must locate each other without relying on cwd.
script_dir="$tmp/skill installation/scripts"
mkdir -p "$script_dir"
cp "$source_script_dir/review-package" "$source_script_dir/review-workspace" "$script_dir/"
repo="$tmp/target repo"
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

mkdir "$repo/nested cwd"
package=$(cd "$repo/nested cwd" && "$script_dir/review-package" --base HEAD -- src)

case "$package" in
  "$repo"/.power-agent/review-runs/*) ;;
  *) echo "review package was created outside the target repository" >&2; exit 1 ;;
esac

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

# Relative explicit output remains relative to the calling directory, while the
# path scope stays relative to the repository root.
mkdir "$repo/nested cwd/ignored output"
printf 'nested cwd/ignored output/\n' > "$repo/.git/info/exclude"
explicit_package=$(cd "$repo/nested cwd" && "$script_dir/review-package" --base HEAD --output "ignored output/review.diff" -- src)
[[ "$explicit_package" == "$repo/nested cwd/ignored output/review.diff" ]]
rg -q 'staged change' "$explicit_package"
if rg -q 'unrelated change' "$explicit_package"; then
  echo "explicit package scope was not relative to the target repository root" >&2
  exit 1
fi

# Execute the documented entry point without inheriting errexit. Add only an
# explicit, valid ignored output so an output-path rejection cannot hide a bad cd.
example="$tmp/documented-entrypoint.sh"
awk '
  /^```bash$/ { in_example = 1; next }
  in_example && /^```$/ { exit }
  in_example {
    if ($0 ~ /scripts\/review-package"/) {
      sub(/ --base /, " --output \"$REVIEW_OUTPUT\" --base ")
    }
    print
  }
' "$source_script_dir/../SKILL.md" > "$example"
[[ -s "$example" ]]
example_output="$repo/nested cwd/ignored output/documented-success.diff"
(cd "$repo" && TARGET_REPO="$repo" IMPLEMENT_SKILL_DIR="${script_dir%/scripts}" \
  BASE_SHA=HEAD REVIEW_OUTPUT="$example_output" bash +e "$example") >/dev/null
rg -q 'staged change' "$example_output"

printf 'not a directory\n' > "$tmp/non-directory target"
for invalid_target in "$tmp/missing target" "$tmp/non-directory target"; do
  failed_output="$repo/nested cwd/ignored output/failed-$(basename "$invalid_target").diff"
  if (cd "$repo" && TARGET_REPO="$invalid_target" IMPLEMENT_SKILL_DIR="${script_dir%/scripts}" \
    BASE_SHA=HEAD REVIEW_OUTPUT="$failed_output" bash +e "$example") >/dev/null 2>&1; then
    echo "documented entry point continued after entering the target failed" >&2
    exit 1
  fi
  if [[ -e "$failed_output" ]]; then
    echo "documented entry point created a package in the caller's old repository" >&2
    exit 1
  fi
done

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
