#!/usr/bin/env python3
"""Check explicit local Markdown links and Skill script pointers, without writes.

By default check root Markdown, skills/, and docs/ except completed/archived
documents and superseded ADRs. Explicit paths opt into historical documents.
Supports common single-line inline/reference links, ATX/setext anchors and IDs.
Fenced/indented code, comments, frontmatter and placeholder targets are ignored.
Relative links use the document directory. Bare scripts/... code pointers use
the owning Skill, never repository scripts/. Skill-local pointers must be
relative and remain inside the installed skills/ bundle, including symlinks;
references to sibling Skills are allowed. Other local paths stay in the
repository. Remote URLs are not fetched. Multiline link syntax and renderer
extensions require their own checks; arbitrary code-span filenames are not links.
This is a pointer check, not a Markdown renderer or semantic review.
"""
from __future__ import annotations

import argparse
import html
import re
import sys
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote, urlsplit


@dataclass(frozen=True)
class Reference:
    """A destination explicitly written in a source document."""

    line: int
    target: str
    kind: str = "link"
    error: str | None = None


@dataclass(frozen=True)
class Issue:
    """An invalid pointer, identified at its source location."""

    source: Path
    line: int
    target: str
    message: str


CODE_SPAN = re.compile(r"(?<!`)(`+)(?!`)(.*?)\1(?!`)")
DEFINITION = re.compile(r"^ {0,3}\[([^\]]+)\]:\s*(.+)$")
SCRIPT = re.compile(r"(?<![\w/.-])((?:\./|\.\./)*scripts/[^\s`'\"<>|]+)")
HISTORICAL_DIRS = {"completed", "archived", "archive"}


def blank(text: str) -> str:
    """Mask content while preserving offsets and line numbers."""
    return "".join("\n" if char == "\n" else " " for char in text)


def prose(text: str) -> str:
    """Remove non-prose blocks; retain line numbers for diagnostics."""
    text = re.sub(r"<!--.*?(?:-->|\Z)", lambda m: blank(m[0]), text, flags=re.S)
    lines = text.splitlines(keepends=True)
    fence: tuple[str, int] | None = None
    frontmatter = bool(lines and lines[0].strip() == "---")
    result: list[str] = []
    for index, line in enumerate(lines):
        if frontmatter:
            if index and line.strip() in {"---", "..."}:
                frontmatter = False
            result.append(blank(line))
            continue
        match = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line)
        if fence:
            if (
                match and match[1][0] == fence[0]
                and len(match[1]) >= fence[1] and not match[2].strip()
            ):
                fence = None
            result.append(blank(line))
        elif match:
            fence = (match[1][0], len(match[1]))
            result.append(blank(line))
        elif line.startswith(("    ", "\t")):
            result.append(blank(line))
        else:
            result.append(line)
    return "".join(result)


def unescape(text: str) -> str:
    """Decode Markdown escapes and entities, but leave URL decoding to paths."""
    return html.unescape(re.sub(r"\\([!\"#$%&'()*+,\-./:;<=>?@\[\]\\^_`{|}~])", r"\1", text))


def destination(raw: str) -> str:
    """Read an angle-wrapped path or a path with an optional quoted title."""
    raw = raw.strip()
    if raw.startswith("<") and ">" in raw:
        return unescape(raw[1:raw.index(">")])
    # Bare spaces are accepted for local filenames; a quoted suffix is a title.
    raw = re.sub(r"\s+(?:\"[^\"]*\"|'[^']*')\s*$", "", raw)
    return unescape(raw)


def closing(text: str, start: int, left: str, right: str) -> int | None:
    """Find the matching delimiter, respecting escapes and nested delimiters."""
    depth = 1
    index = start + 1
    while index < len(text):
        char = text[index]
        if char == "\\":
            index += 2
            continue
        if left == "(" and char == "<":
            angle_end = text.find(">", index + 1)
            if angle_end != -1:
                index = angle_end + 1
                continue
        if char == left:
            depth += 1
        elif char == right:
            depth -= 1
            if not depth:
                return index
        index += 1
    return None


def label_key(label: str) -> str:
    return " ".join(unescape(label).split()).casefold()


def references(text: str, check_scripts: bool) -> list[Reference]:
    """Extract explicit links, definitions, and optional script code pointers."""
    visible = prose(text)
    lines = visible.splitlines()
    definitions: dict[str, str] = {}
    definition_lines: set[int] = set()
    found: list[Reference] = []
    for number, line in enumerate(lines, 1):
        match = DEFINITION.match(line)
        if match:
            key = label_key(match[1])
            if key not in definitions:
                definitions[key] = destination(match[2])
                found.append(Reference(number, definitions[key]))
            definition_lines.add(number)
    for number, line in enumerate(lines, 1):
        if number in definition_lines:
            continue
        if check_scripts:
            for span in CODE_SPAN.finditer(line):
                for match in SCRIPT.finditer(span[2]):
                    target = match[1].rstrip(",;:")
                    if not target.endswith("/"):
                        found.append(Reference(number, target, "script"))
        masked = CODE_SPAN.sub(lambda m: blank(m[0]), line)
        index = 0
        while index < len(masked):
            if masked[index] == "\\":
                index += 2
                continue
            if masked[index] != "[":
                index += 1
                continue
            end = closing(masked, index, "[", "]")
            if end is None:
                break
            after = end + 1
            if after < len(masked) and masked[after] == "(":
                close = closing(masked, after, "(", ")")
                if close is not None:
                    found.append(Reference(number, destination(masked[after + 1:close])))
                    index = close + 1
                    continue
            elif after < len(masked) and masked[after] == "[":
                close = closing(masked, after, "[", "]")
                if close is not None:
                    key = label_key(masked[after + 1:close] or masked[index + 1:end])
                    if key not in definitions:
                        found.append(Reference(number, key, error="undefined link reference"))
                    index = close + 1
                    continue
            index = end + 1
    return found


def heading_slug(text: str) -> str:
    """Generate common GitHub-style slugs, including Chinese heading text."""
    text = re.sub(r"!?\[([^\]]+)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"!?\[([^\]]+)\]\[[^\]]*\]", r"\1", text)
    text = re.sub(r"<[^>]*>", "", text)
    text = unescape(text).lower()
    text = re.sub(r"(?<!\w)_{1,2}|_{1,2}(?!\w)", "", text)
    return "".join(
        "-" if char.isspace() else char
        for char in text
        if char.isspace() or char in "_-" or unicodedata.category(char)[0] in "LNM"
    )


def anchors(text: str) -> set[str]:
    """Collect heading IDs with duplicate suffixes, plus explicit HTML IDs."""
    visible = prose(text)
    tags = CODE_SPAN.sub(lambda m: blank(m[0]), visible)
    result = set(re.findall(
        r"<(?:a|[a-z][\w-]*)\b[^>]*\b(?:id|name)=[\"']([^\"']+)[\"']",
        tags, re.I,
    ))
    generated: set[str] = set()
    previous = ""
    for line in visible.splitlines():
        match = re.match(r"^ {0,3}#{1,6}\s+(.+?)\s*$", line)
        title = re.sub(r"\s+#+\s*$", "", match[1]) if match else None
        if title is None and previous.strip() and re.fullmatch(r" {0,3}(?:=+|-+)\s*", line):
            title = previous.strip()
        if title is not None:
            slug = heading_slug(title)
            candidate = slug
            suffix = 0
            while candidate in generated:
                suffix += 1
                candidate = f"{slug}-{suffix}"
            generated.add(candidate)
            result.add(candidate)
        previous = line
    return result


def is_placeholder(target: str) -> bool:
    """Only skip visibly templated paths, not arbitrary historical prose."""
    return bool(re.search(r"[<>{}*]|\$[A-Za-z_{]|\.\.\.|…", target))


def inside(path: Path, repo: Path, source: Path | None = None) -> Path:
    """Reject repository escapes and unshipped targets referenced from Skills."""
    resolved = path.resolve()
    if not resolved.is_relative_to(repo):
        raise ValueError("target resolves outside repository")
    if (
        source is not None
        and source.is_relative_to(repo / "skills")
        and not resolved.is_relative_to((repo / "skills").resolve())
    ):
        raise ValueError("target resolves outside installed Skill bundle")
    return resolved


def skill_root(source: Path, repo: Path) -> Path | None:
    """Find the owning Skill without inspecting files outside the repository."""
    for parent in source.parents:
        if not parent.is_relative_to(repo):
            break
        marker = parent / "SKILL.md"
        if marker.exists():
            inside(marker, repo, source)
            return parent
    return None


def check_reference(
    source: Path, ref: Reference, repo: Path, cache: dict[Path, set[str]],
) -> Issue | None:
    """Check one pointer without executing scripts or following external files."""
    if ref.error:
        return Issue(source, ref.line, ref.target, ref.error)
    if is_placeholder(ref.target):
        return None
    if re.match(r"^[a-zA-Z][\w+.-]*:", ref.target) and not ref.target.lower().startswith("file:"):
        return None
    if ref.target.startswith("//"):
        return None
    try:
        url = urlsplit(ref.target)
        if url.scheme == "file" and url.netloc not in {"", "localhost"}:
            raise ValueError("external file host is not a repository path")
        path_text = unquote(url.path)
        fragment = unquote(url.fragment)
        if source.is_relative_to(repo / "skills") and Path(path_text).is_absolute():
            raise ValueError("Skill target must be relative to the installed bundle")
        target = source.parent / path_text if path_text else source
        if ref.kind == "script" and path_text.startswith("scripts/"):
            owner = skill_root(source, repo)
            target = (owner or source.parent) / path_text
        resolved = inside(target, repo, source)
        if not resolved.exists():
            raise ValueError("missing local target")
        if ref.kind == "script" and not resolved.is_file():
            raise ValueError("script target is not a file")
        if fragment and resolved.suffix.lower() in {".md", ".markdown"}:
            if resolved not in cache:
                cache[resolved] = anchors(resolved.read_text(encoding="utf-8"))
            if fragment not in cache[resolved]:
                raise ValueError("missing Markdown anchor")
    except (OSError, ValueError, RuntimeError) as error:
        return Issue(source, ref.line, ref.target, str(error))
    return None


def historical(path: Path, repo: Path) -> bool:
    """Recognize archival paths and explicit superseded frontmatter."""
    relative = path.relative_to(repo)
    if relative.parts[0] != "docs":
        return False
    if HISTORICAL_DIRS.intersection(relative.parts):
        return True
    text = path.read_text(encoding="utf-8")
    frontmatter = re.match(r"\A---\s*\n(.*?)\n---(?:\n|$)", text, re.S)
    return bool(frontmatter and re.search(
        r"^status:\s*[\"']?superseded[\"']?\s*$", frontmatter[1], re.M,
    ))


def collect(paths: list[Path], repo: Path, default: bool) -> tuple[list[Path], list[Issue]]:
    """Walk selected paths with a canonical-directory cycle guard."""
    files: set[Path] = set()
    seen: set[Path] = set()
    issues: list[Issue] = []
    pending = list(reversed(paths))
    while pending:
        path = pending.pop()
        if default and path.is_relative_to(repo):
            parts = path.relative_to(repo).parts
            if parts and parts[0] == "docs" and HISTORICAL_DIRS.intersection(parts):
                continue
        try:
            resolved = inside(path, repo, path)
            if not resolved.exists():
                raise ValueError("input path does not exist")
            if path.is_dir():
                if resolved in seen:
                    continue
                seen.add(resolved)
                pending.extend(sorted(
                    (p for p in path.iterdir() if not p.name.startswith(".")), reverse=True,
                ))
            elif path.suffix.lower() in {".md", ".markdown"}:
                if not default or not historical(path, repo):
                    files.add(path)
        except (OSError, ValueError, RuntimeError) as error:
            issues.append(Issue(path, 1, str(path), str(error)))
    return sorted(files), issues


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "paths", nargs="*",
        help="files/directories, relative to repo; explicit paths include history",
    )
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parent.parent)
    args = parser.parse_args(argv)
    repo = args.repo.resolve()
    if not repo.is_dir():
        parser.error("--repo must name an existing directory")
    paths = [repo / path for path in args.paths] if args.paths else [
        *sorted(repo.glob("*.md")),
        *(repo / name for name in ("skills", "docs") if (repo / name).exists()),
    ]
    files, issues = collect(paths, repo, not args.paths)
    cache: dict[Path, set[str]] = {}
    count = 0
    for source in files:
        try:
            refs = references(
                inside(source, repo, source).read_text(encoding="utf-8"),
                skill_root(source, repo) is not None,
            )
            for ref in refs:
                count += 1
                issue = check_reference(source, ref, repo, cache)
                if issue:
                    issues.append(issue)
        except (OSError, ValueError, RuntimeError) as error:
            issues.append(Issue(source, 1, str(source), str(error)))
    for issue in issues:
        name = issue.source.relative_to(repo) if issue.source.is_relative_to(repo) else issue.source
        print(f"{name}:{issue.line}: {issue.message}: {issue.target}", file=sys.stderr)
    print(
        f"{'FAIL' if issues else 'OK'}: {len(files)} documents, "
        f"{count} explicit pointers, {len(issues)} issues"
    )
    return 1 if issues else 0


if __name__ == "__main__":
    sys.exit(main())
