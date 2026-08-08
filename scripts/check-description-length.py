#!/usr/bin/env python3
"""校验 skills/*/SKILL.md frontmatter description 的估算 token 长度。

规则（writing-skills）：description 尽量控制在约 100 token，硬上限约 110。
本脚本不引入第三方依赖，用按字符类别加权的估算器近似 cl100k token 数，
误差约 ±10，因此 fail 阈值取 115（≈ 真实 110 + 估算余量）。

用法：scripts/check-description-length.py；超限退出码 1。
"""
from __future__ import annotations

import math
import re
import sys
from pathlib import Path

FAIL_THRESHOLD = 115  # 估算 token；约等于真实 110 硬上限

CJK_PUNCT = "，。；：（）、“”—…《》"


def estimate_tokens(text: str) -> int:
    """cl100k 近似估算：CJK 字 ≈1.15，中文标点 ≈1.2，拉丁词按长度折算，其余符号 ≈0.6。"""
    cjk = sum(1 for c in text if "一" <= c <= "鿿")
    cjk_punct = sum(1 for c in text if c in CJK_PUNCT)
    latin = sum(max(1, round(len(w) / 4)) for w in re.findall(r"[A-Za-z]+", text))
    other = sum(
        1
        for c in text
        if not c.isspace() and not "一" <= c <= "鿿" and c not in CJK_PUNCT and not c.isalpha()
    )
    return math.ceil(1.15 * cjk + 1.2 * cjk_punct + latin + 0.6 * other)


def extract_description(path: Path) -> str | None:
    """解析 frontmatter 的 description（支持 `|-` 块与单行两种写法）。"""
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0] != "---":
        return None
    i = 1
    while i < len(lines) and lines[i] != "---":
        line = lines[i]
        if line.startswith("description:"):
            value = line[len("description:"):].strip()
            if value and value not in ("|-", "|", ">-", ">"):
                return value
            block: list[str] = []
            i += 1
            while i < len(lines) and (lines[i].startswith("  ") or not lines[i].strip()):
                block.append(lines[i].strip())
                i += 1
            return " ".join(part for part in block if part)
        i += 1
    return None


def main() -> int:
    repo = Path(__file__).resolve().parent.parent
    failed = 0
    rows = []
    for skill in sorted(repo.glob("skills/*/SKILL.md")):
        name = skill.parent.name
        desc = extract_description(skill)
        if desc is None:
            print(f"DRIFT: {name} 缺少 frontmatter description。", file=sys.stderr)
            failed = 1
            continue
        rows.append((estimate_tokens(desc), name))

    for tokens, name in sorted(rows, reverse=True):
        marker = "  OVER" if tokens > FAIL_THRESHOLD else ""
        print(f"{tokens:>4} est  {name}{marker}")
        if tokens > FAIL_THRESHOLD:
            failed = 1

    if failed:
        print(
            f"FAIL: description 超过硬上限（估算 >{FAIL_THRESHOLD}，约真实 110 token）。"
            "压缩方式见 skills/writing-skills。",
            file=sys.stderr,
        )
    else:
        print("OK: 所有 Skill description 在长度上限内（目标 ~100 token）。")
    return failed


if __name__ == "__main__":
    sys.exit(main())
