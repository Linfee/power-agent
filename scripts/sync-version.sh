#!/usr/bin/env bash
# sync-version.sh — 读取 VERSION 文件，批量更新所有 SKILL.md 的 version 字段
# 用法: bash scripts/sync-version.sh
# 若 SKILL.md 无 version 字段则追加，有则更新
# 依赖: python3（系统自带）

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
VERSION_FILE="$ROOT_DIR/VERSION"

if [[ ! -f "$VERSION_FILE" ]]; then
  echo "错误：未找到 VERSION 文件（$VERSION_FILE）" >&2
  exit 1
fi

VERSION=$(cat "$VERSION_FILE" | tr -d '[:space:]')

python3 - "$ROOT_DIR" "$VERSION" <<'PYEOF'
import sys, re
from pathlib import Path

root = Path(sys.argv[1])
version = sys.argv[2]
print(f"目标版本: {version}\n")

updated = 0
errors = 0

for skill_file in sorted(root.glob('skills/*/SKILL.md')):
    skill_name = skill_file.parent.name
    try:
        content = skill_file.read_text()
        if not content.startswith('---'):
            raise ValueError("不以 --- 开头，无法处理 frontmatter")
        lines = content.split('\n')
        close_idx = next(
            (i for i in range(1, len(lines)) if lines[i].strip() == '---'),
            None
        )
        if close_idx is None:
            raise ValueError("未找到 frontmatter 结束符 ---")
        fm = lines[1:close_idx]
        rest = lines[close_idx:]
        if any(l.startswith('version:') for l in fm):
            fm = [re.sub(r'^version:.*', f'version: {version}', l) for l in fm]
            action = "更新"
        else:
            fm.append(f'version: {version}')
            action = "追加"
        skill_file.write_text('\n'.join(['---'] + fm + rest))
        print(f"✅ 已{action}: {skill_name} -> {version}")
        updated += 1
    except Exception as e:
        print(f"❌ 失败: {skill_name}: {e}")
        errors += 1

print(f"\n---\n处理完成：{updated} 个，{errors} 个失败\n")
if errors:
    sys.exit(1)

print("版本一致性校验...")
bad = 0
for skill_file in sorted(root.glob('skills/*/SKILL.md')):
    m = re.search(r'^version:\s*(.+)$', skill_file.read_text(), re.MULTILINE)
    fv = m.group(1).strip() if m else 'missing'
    if fv != version:
        print(f"❌ {skill_file.parent.name} = {fv}")
        bad += 1
if bad:
    print(f"校验失败：{bad} 个不一致")
    sys.exit(1)
print(f"✅ 版本同步完成：所有 SKILL.md = {version}")
PYEOF
