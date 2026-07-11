#!/usr/bin/env python3
"""Scan and record verification state for an OKF-style docs bundle.

The tool is deliberately deterministic. It detects document/source changes,
metadata problems, missing sources, broken local links and expired verification
records. It does not decide whether prose is semantically correct; an Agent must
perform that verification before using the ``record`` command.

No third-party Python dependency is required.
"""

from __future__ import annotations

import argparse
import errno
import fnmatch
import glob
import hashlib
import json
import os
import re
import stat
import subprocess
import sys
import tempfile
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path, PurePosixPath
from typing import Any, Iterable
from urllib.parse import unquote

FRONTMATTER_BOUNDARY = "---"
FENCE_RE = re.compile(r"```.*?```|~~~.*?~~~", re.DOTALL)
MARKDOWN_LINK_RE = re.compile(r"(?<!!)\[[^\]]*\]\(([^)]+)\)")
DURATION_RE = re.compile(r"^P(?:(?P<weeks>\d+)W|(?P<days>\d+)D)$", re.IGNORECASE)
URL_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*://")
PATH_HINT_RE = re.compile(r"[/*?\[\]\\]|(?:^|/)[^/]+\.[A-Za-z0-9_-]+$")
SUPPORTED_METHODS = {"continuity", "semantic", "executable"}
SUPPORTED_STRATEGIES = {
    "source-change",
    "periodic",
    "source-change-and-periodic",
    "historical",
    "generated",
}

SHA256_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
SUPPORTED_EVIDENCE = frozenset({"human-review", "automated-test", "external-audit"})
REQUIRED_RECORD_FIELDS = {
    "path",
    "type",
    "verified_at",
    "verified_commit",
    "method",
    "document_hash",
    "source_fingerprint",
    "sources",
}


class BundleError(RuntimeError):
    pass


def directory_open_flags() -> int:
    return os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)


def file_open_flags(flags: int) -> int:
    return flags | getattr(os, "O_NOFOLLOW", 0)


def open_directory_no_symlinks(root: Path, relative: Path, create: bool) -> int:
    """Open a directory below ``root`` without traversing symlinks.

    The returned descriptor owns the final directory. POSIX ``dir_fd`` calls
    keep parent replacement races from redirecting registry artifacts.
    """
    if any(part in {"", ".", ".."} for part in relative.parts):
        raise BundleError(f"unsafe registry directory: {relative}")
    descriptor = os.open(root, directory_open_flags())
    try:
        for part in relative.parts:
            if create:
                try:
                    os.mkdir(part, 0o700, dir_fd=descriptor)
                except FileExistsError:
                    pass
            try:
                child = os.open(part, directory_open_flags(), dir_fd=descriptor)
            except OSError as exc:
                if exc.errno == errno.ELOOP:
                    raise BundleError(f"registry path must not traverse a symbolic link: {part}") from exc
                raise
            os.close(descriptor)
            descriptor = child
        return descriptor
    except BaseException:
        os.close(descriptor)
        raise


class VerificationRegistryLock:
    """A nonblocking bundle-scoped advisory lock for verification ledger writes."""

    def __init__(self, bundle_root: Path) -> None:
        self.bundle_root = bundle_root
        self.path = self.bundle_root / ".okf" / "verification.json.lock"
        self.descriptor: int | None = None

    def __enter__(self) -> "VerificationRegistryLock":
        parent_descriptor = open_directory_no_symlinks(self.bundle_root, Path(".okf"), create=True)
        try:
            descriptor = os.open(
                self.path.name,
                file_open_flags(os.O_CREAT | os.O_RDWR),
                0o600,
                dir_fd=parent_descriptor,
            )
        except OSError as exc:
            if exc.errno == errno.ELOOP:
                raise BundleError(f"verification registry lock must not be a symbolic link: {self.path}") from exc
            raise BundleError(f"cannot open verification registry lock: {self.path}") from exc
        finally:
            os.close(parent_descriptor)
        try:
            if not stat.S_ISREG(os.fstat(descriptor).st_mode):
                raise BundleError(f"verification registry lock must be a regular file: {self.path}")
            if os.name == "nt":
                import msvcrt

                if os.lseek(descriptor, 0, os.SEEK_END) == 0:
                    os.write(descriptor, b"\0")
                os.lseek(descriptor, 0, os.SEEK_SET)
                msvcrt.locking(descriptor, msvcrt.LK_NBLCK, 1)
            else:
                import fcntl

                fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:
            os.close(descriptor)
            raise BundleError(f"verification registry is locked: {self.path}") from exc
        except BaseException:
            os.close(descriptor)
            raise
        self.descriptor = descriptor
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        if self.descriptor is None:
            return
        try:
            if os.name == "nt":
                import msvcrt

                os.lseek(self.descriptor, 0, os.SEEK_SET)
                msvcrt.locking(self.descriptor, msvcrt.LK_UNLCK, 1)
            else:
                import fcntl

                fcntl.flock(self.descriptor, fcntl.LOCK_UN)
        finally:
            os.close(self.descriptor)
            self.descriptor = None


@dataclass
class Finding:
    code: str
    message: str
    path: str | None = None


@dataclass
class ConceptSnapshot:
    path: str
    concept_id: str
    type: str | None
    title: str | None
    freshness: str
    strategy: str | None
    target: str | None
    verified_at: str | None
    verified_commit: str | None
    verification_method: str | None
    document_changed: bool
    changed_sources: list[str] = field(default_factory=list)
    missing_sources: list[str] = field(default_factory=list)
    broken_links: list[str] = field(default_factory=list)
    metadata_issues: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    @property
    def candidate(self) -> bool:
        return self.freshness != "fresh" or bool(
            self.missing_sources or self.broken_links or self.metadata_issues
        )


@dataclass
class ScanReport:
    schema_version: str
    generated_at: str
    repo_root: str
    bundle: str
    registry: str
    head: str | None
    policy: dict[str, Any]
    summary: dict[str, Any]
    queue: list[dict[str, Any]]
    bundle_issues: list[dict[str, Any]]
    concepts: list[dict[str, Any]] | None = None


# ---------------------------------------------------------------------------
# Git and time helpers
# ---------------------------------------------------------------------------


def run_git(repo: Path, args: list[str], check: bool = True) -> str:
    proc = subprocess.run(
        ["git", "-C", str(repo), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if check and proc.returncode != 0:
        raise BundleError(proc.stderr.strip() or f"git {' '.join(args)} failed")
    return proc.stdout.strip()


def find_repo_root(candidate: Path) -> Path:
    output = run_git(candidate, ["rev-parse", "--show-toplevel"], check=False)
    return Path(output).resolve() if output else candidate.resolve()


def current_head(repo: Path) -> str | None:
    return run_git(repo, ["rev-parse", "HEAD"], check=False) or None


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    normalized = value.strip()
    if normalized.endswith("Z"):
        normalized = normalized[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def format_datetime(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def parse_duration(value: str | None) -> timedelta | None:
    if not value:
        return None
    match = DURATION_RE.fullmatch(value.strip())
    if not match:
        return None
    if match.group("weeks"):
        return timedelta(weeks=int(match.group("weeks")))
    return timedelta(days=int(match.group("days")))


# ---------------------------------------------------------------------------
# Minimal YAML frontmatter parser
# ---------------------------------------------------------------------------


def strip_inline_comment(value: str) -> str:
    quote: str | None = None
    for index, char in enumerate(value):
        if char in {'"', "'"}:
            if quote == char:
                quote = None
            elif quote is None:
                quote = char
        elif char == "#" and quote is None and index > 0 and value[index - 1].isspace():
            return value[:index].rstrip()
    return value


class YamlSubsetError(ValueError):
    pass


def split_inline_list(value: str) -> list[str]:
    parts: list[str] = []
    current: list[str] = []
    quote: str | None = None
    for char in value:
        if char in {'"', "'"}:
            if quote == char:
                quote = None
            elif quote is None:
                quote = char
            current.append(char)
        elif char == "," and quote is None:
            parts.append("".join(current).strip())
            current = []
        else:
            current.append(char)
    if quote is not None:
        raise YamlSubsetError("unterminated quoted scalar")
    parts.append("".join(current).strip())
    return parts


def parse_scalar(raw: str) -> Any:
    value = strip_inline_comment(raw).strip()
    if not value:
        return ""
    if value.startswith(('"', "'")) or value.endswith(('"', "'")):
        if len(value) < 2 or value[0] != value[-1] or value[0] not in {'"', "'"}:
            raise YamlSubsetError("unterminated quoted scalar")
        return value[1:-1]
    if value == "{}":
        return {}
    if value.startswith("[") or value.endswith("]"):
        if not (value.startswith("[") and value.endswith("]")):
            raise YamlSubsetError("malformed inline list")
        inner = value[1:-1].strip()
        return [] if not inner else [parse_scalar(item) for item in split_inline_list(inner)]
    lowered = value.lower()
    if lowered in {"true", "false"}:
        return lowered == "true"
    if lowered in {"null", "none", "~"}:
        return None
    if re.fullmatch(r"-?\d+", value):
        return int(value)
    return value


def tokenize_yaml(lines: list[str]) -> list[tuple[int, int, str]]:
    tokens: list[tuple[int, int, str]] = []
    for line_number, raw_line in enumerate(lines, start=1):
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        leading = raw_line[: len(raw_line) - len(raw_line.lstrip())]
        if "\t" in leading:
            raise YamlSubsetError(f"line {line_number}: tabs are not valid indentation")
        indent = len(raw_line) - len(raw_line.lstrip(" "))
        tokens.append((line_number, indent, raw_line.strip()))
    return tokens


def list_item(content: str) -> bool:
    return content == "-" or content.startswith("- ")


def mapping_item(content: str) -> bool:
    return ":" in content and not (
        bool(URL_RE.match(content)) or content.startswith(("mailto:", "tel:"))
    )


def mapping_key(content: str, line_number: int) -> tuple[str, str]:
    key, raw_value = content.split(":", 1)
    key = key.strip()
    if not key:
        raise YamlSubsetError(f"line {line_number}: mapping key is empty")
    return key, raw_value


def parse_yaml_subset(lines: list[str]) -> dict[str, Any]:
    """Parse the documented YAML subset and reject every unsupported token."""
    tokens = tokenize_yaml(lines)
    if not tokens:
        return {}
    if tokens[0][1] != 0:
        raise YamlSubsetError(f"line {tokens[0][0]}: frontmatter root must be unindented")

    def parse_block(index: int, indent: int) -> tuple[Any, int]:
        line_number, current_indent, content = tokens[index]
        is_list = current_indent == indent and list_item(content)
        if is_list:
            result: list[Any] = []
            while index < len(tokens):
                line_number, current_indent, content = tokens[index]
                if current_indent < indent:
                    break
                if current_indent > indent:
                    raise YamlSubsetError(f"line {line_number}: unexpected indentation")
                if not list_item(content):
                    raise YamlSubsetError(f"line {line_number}: expected a list item")
                rest = content[1:].strip()
                index += 1
                if not rest:
                    if index < len(tokens) and tokens[index][1] > indent:
                        item, index = parse_block(index, tokens[index][1])
                    else:
                        item = None
                    result.append(item)
                    continue
                if mapping_item(rest):
                    key, raw_value = mapping_key(rest, line_number)
                    item_dict: dict[str, Any] = {}
                    if raw_value.strip():
                        item_dict[key] = parse_scalar(raw_value)
                    elif index < len(tokens) and tokens[index][1] > indent:
                        nested, index = parse_block(index, tokens[index][1])
                        item_dict[key] = nested
                    else:
                        item_dict[key] = None
                    if index < len(tokens) and tokens[index][1] > indent:
                        nested, index = parse_block(index, tokens[index][1])
                        if not isinstance(nested, dict):
                            raise YamlSubsetError(
                                f"line {tokens[index - 1][0]}: list mapping continuation must be a mapping"
                            )
                        item_dict.update(nested)
                    result.append(item_dict)
                else:
                    result.append(parse_scalar(rest))
            return result, index

        result_dict: dict[str, Any] = {}
        while index < len(tokens):
            line_number, current_indent, content = tokens[index]
            if current_indent < indent:
                break
            if current_indent > indent:
                raise YamlSubsetError(f"line {line_number}: unexpected indentation")
            if list_item(content):
                raise YamlSubsetError(f"line {line_number}: list item is invalid in a mapping")
            if not mapping_item(content):
                raise YamlSubsetError(f"line {line_number}: bare token is not valid frontmatter")
            key, raw_value = mapping_key(content, line_number)
            index += 1
            if raw_value.strip():
                result_dict[key] = parse_scalar(raw_value)
            elif index < len(tokens) and tokens[index][1] > indent:
                nested, index = parse_block(index, tokens[index][1])
                result_dict[key] = nested
            else:
                result_dict[key] = None
        return result_dict, index

    parsed, consumed = parse_block(0, 0)
    if consumed != len(tokens):
        line_number = tokens[consumed][0]
        raise YamlSubsetError(f"line {line_number}: unconsumed frontmatter token")
    if not isinstance(parsed, dict):
        raise YamlSubsetError("frontmatter root must be a mapping")
    return parsed


def read_markdown(path: Path) -> tuple[dict[str, Any], str, bool, str, str | None]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0].strip() != FRONTMATTER_BOUNDARY:
        return {}, text, False, text, None
    end: int | None = None
    for index in range(1, len(lines)):
        if lines[index].strip() == FRONTMATTER_BOUNDARY:
            end = index
            break
    if end is None:
        return {}, text, True, text, "frontmatter boundary is not closed"
    body = "\n".join(lines[end + 1 :])
    try:
        metadata = parse_yaml_subset(lines[1:end])
    except YamlSubsetError as exc:
        return {}, body, True, text, str(exc)
    return metadata, body, True, text, None


def as_string(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, (str, int, float, bool)):
        text = str(value).strip()
        return text or None
    return None


def as_string_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []


# ---------------------------------------------------------------------------
# Bundle policy and path handling
# ---------------------------------------------------------------------------


def resolve_policy(index_meta: dict[str, Any], concept_type: str | None) -> dict[str, Any]:
    freshness = index_meta.get("freshness")
    if not isinstance(freshness, dict):
        freshness = {}
    default_strategy = as_string(freshness.get("default_strategy"))
    default_target = as_string(freshness.get("default_target"))
    rules = freshness.get("rules") if isinstance(freshness.get("rules"), list) else []
    selected: dict[str, Any] = {}
    if concept_type:
        for rule in rules:
            if isinstance(rule, dict) and as_string(rule.get("type")) == concept_type:
                selected.update(rule)
    return {
        "strategy": as_string(selected.get("strategy")) or default_strategy,
        "target": as_string(selected.get("target")) or default_target,
        "raw": {
            "default_strategy": default_strategy,
            "default_target": default_target,
            "rules": rules,
        },
    }


def effective_policy(meta: dict[str, Any], index_meta: dict[str, Any]) -> tuple[str | None, str | None]:
    inherited = resolve_policy(index_meta, as_string(meta.get("type")))
    verification = meta.get("verification")
    if not isinstance(verification, dict):
        verification = {}
    strategy = as_string(verification.get("strategy")) or inherited["strategy"]
    target = as_string(verification.get("target")) or inherited["target"]
    return strategy, target


def is_url(value: str) -> bool:
    return bool(URL_RE.match(value)) or value.startswith(("mailto:", "tel:"))


def path_like(value: str) -> bool:
    return bool(PATH_HINT_RE.search(value)) or value.startswith((".", "/"))


def normalize_pattern(value: str) -> str | None:
    stripped = value.strip()
    if not stripped or is_url(stripped) or stripped.startswith("#"):
        return None
    return stripped.lstrip("/").removeprefix("./")


def scope_declares_source(repo_root: Path, value: str) -> bool:
    """Treat scope as a source only when it is path-shaped or names a real repo path."""
    pattern = normalize_pattern(value)
    if pattern is None:
        return False
    if path_like(value):
        return True
    candidate = (repo_root / pattern).resolve()
    try:
        candidate.relative_to(repo_root)
    except ValueError:
        return False
    return candidate.exists()


def is_ignored_path(path: Path, repo_root: Path, registry_path: Path) -> bool:
    try:
        relative = path.resolve().relative_to(repo_root)
    except ValueError:
        return True
    if ".git" in relative.parts:
        return True
    if path.resolve() == registry_path.resolve():
        return True
    return any(part == ".okf" for part in relative.parts)


def files_for_pattern(repo_root: Path, pattern: str, registry_path: Path) -> list[Path]:
    candidate = repo_root / pattern
    paths: list[Path] = []
    if any(char in pattern for char in "*?["):
        paths = [Path(item) for item in glob.glob(str(candidate), recursive=True)]
    elif candidate.exists():
        if candidate.is_dir():
            paths = list(candidate.rglob("*"))
        else:
            paths = [candidate]
    result: list[Path] = []
    for path in paths:
        if not path.is_file() or is_ignored_path(path, repo_root, registry_path):
            continue
        try:
            path.resolve().relative_to(repo_root)
        except ValueError:
            continue
        result.append(path.resolve())
    return sorted(set(result))


def discover_concepts(bundle_root: Path, repo_root: Path) -> tuple[list[Path], list[Finding]]:
    concepts: list[Path] = []
    issues: list[Finding] = []
    resolved_bundle = bundle_root.resolve()
    for path in bundle_root.rglob("*.md"):
        if path.name in {"index.md", "log.md"} or ".okf" in path.parts or ".git" in path.parts:
            continue
        if path.is_symlink():
            issues.append(
                Finding(
                    "invalid-concept-symlink",
                    "Concept documents must not be symbolic links",
                    path.relative_to(repo_root).as_posix(),
                )
            )
            continue
        if path.is_file():
            concepts.append(path)
    return sorted(concepts), issues


def concept_id_for(path: Path, bundle_root: Path) -> str:
    return path.resolve().relative_to(bundle_root.resolve()).with_suffix("").as_posix()


# ---------------------------------------------------------------------------
# Hashing and verification registry
# ---------------------------------------------------------------------------


def sha256_bytes(content: bytes) -> str:
    return "sha256:" + hashlib.sha256(content).hexdigest()


def hash_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def source_fingerprint_for(sources: dict[str, str]) -> str:
    canonical = json.dumps(sources, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return sha256_bytes(canonical.encode("utf-8"))


def is_safe_evidence_label(value: Any) -> bool:
    return isinstance(value, str) and value in SUPPORTED_EVIDENCE


def validate_evidence_labels(evidence: Iterable[str]) -> list[str]:
    labels = list(evidence)
    if not all(is_safe_evidence_label(label) for label in labels):
        allowed = ", ".join(sorted(SUPPORTED_EVIDENCE))
        raise BundleError(f"evidence must be one of: {allowed}")
    return sorted(set(labels))


def is_valid_source_path(value: Any) -> bool:
    if not isinstance(value, str) or not value or "\\" in value or "\0" in value:
        return False
    path = PurePosixPath(value)
    return (
        not value.startswith("/")
        and not is_url(value)
        and path.as_posix() == value
        and all(part not in {".", ".."} for part in path.parts)
    )


def is_valid_verification_record(
    entry: Any,
    expected_path: str,
    expected_type: str | None,
) -> bool:
    if not isinstance(entry, dict) or not REQUIRED_RECORD_FIELDS.issubset(entry):
        return False
    if entry["path"] != expected_path:
        return False
    if not isinstance(entry["type"], str) or entry["type"] != expected_type:
        return False
    if not isinstance(entry["method"], str) or entry["method"] not in SUPPORTED_METHODS:
        return False
    if not isinstance(entry["verified_at"], str) or parse_datetime(entry["verified_at"]) is None:
        return False
    if entry["verified_commit"] is not None and (
        not isinstance(entry["verified_commit"], str) or not entry["verified_commit"].strip()
    ):
        return False
    if not isinstance(entry["document_hash"], str) or not SHA256_RE.fullmatch(entry["document_hash"]):
        return False
    sources = entry["sources"]
    if not isinstance(sources, dict) or any(
        not is_valid_source_path(path) or not isinstance(content_hash, str) or not SHA256_RE.fullmatch(content_hash)
        for path, content_hash in sources.items()
    ):
        return False
    if (
        not isinstance(entry["source_fingerprint"], str)
        or entry["source_fingerprint"] != source_fingerprint_for(sources)
    ):
        return False
    if "evidence" in entry and (
        not isinstance(entry["evidence"], list)
        or not all(is_safe_evidence_label(label) for label in entry["evidence"])
    ):
        return False
    return True


def source_snapshot(
    repo_root: Path,
    registry_path: Path,
    meta: dict[str, Any],
) -> tuple[dict[str, str], str, list[str], list[str]]:
    scope_values = as_string_list(meta.get("scope"))
    source_values = as_string_list(meta.get("sources"))
    declared = source_values + [
        item for item in scope_values if scope_declares_source(repo_root, item)
    ]
    patterns: list[str] = []
    missing: list[str] = []
    files: set[Path] = set()
    for raw in declared:
        pattern = normalize_pattern(raw)
        if not pattern:
            continue
        patterns.append(pattern)
        matches = files_for_pattern(repo_root, pattern, registry_path)
        if not matches:
            missing.append(raw)
        files.update(matches)
    hashes = {
        path.relative_to(repo_root).as_posix(): hash_file(path)
        for path in sorted(files)
    }
    return hashes, source_fingerprint_for(hashes), sorted(set(missing)), patterns


def changed_source_paths(previous: dict[str, Any], current: dict[str, str]) -> list[str]:
    old = previous if isinstance(previous, dict) else {}
    changed = {
        path
        for path in set(old) | set(current)
        if old.get(path) != current.get(path)
    }
    return sorted(changed)


def empty_ledger() -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "updated_at": None,
        "head": None,
        "concepts": {},
    }


def registry_parent_descriptor(path: Path, bundle_root: Path, create: bool) -> int:
    try:
        relative = path.parent.relative_to(bundle_root)
    except ValueError as exc:
        raise BundleError(f"registry must be inside the bundle: {path}") from exc
    return open_directory_no_symlinks(bundle_root, relative, create)


def load_ledger(path: Path, bundle_root: Path) -> tuple[dict[str, Any], Finding | None]:
    try:
        parent_descriptor = registry_parent_descriptor(path, bundle_root, create=False)
    except FileNotFoundError:
        return empty_ledger(), None
    except (OSError, BundleError) as exc:
        return empty_ledger(), Finding(
            "invalid-verification-registry",
            f"cannot safely open verification registry: {exc}",
            path.as_posix(),
        )
    try:
        try:
            descriptor = os.open(path.name, file_open_flags(os.O_RDONLY), dir_fd=parent_descriptor)
        except FileNotFoundError:
            return empty_ledger(), None
        except OSError as exc:
            return empty_ledger(), Finding(
                "invalid-verification-registry",
                f"cannot safely open verification registry: {exc}",
                path.as_posix(),
            )
    finally:
        os.close(parent_descriptor)
    try:
        if not stat.S_ISREG(os.fstat(descriptor).st_mode):
            raise OSError("verification registry must be a regular file")
        handle = os.fdopen(descriptor, "r", encoding="utf-8")
        descriptor = None
        with handle:
            data = json.load(handle)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        if descriptor is not None:
            os.close(descriptor)
        return empty_ledger(), Finding(
            "invalid-verification-registry",
            f"cannot parse verification registry: {exc}",
            path.as_posix(),
        )
    if not isinstance(data, dict) or not isinstance(data.get("concepts"), dict):
        return empty_ledger(), Finding(
            "invalid-verification-registry",
            "verification registry must contain an object field named concepts",
            path.as_posix(),
        )
    if data.get("schema_version") != "1.0":
        return empty_ledger(), Finding(
            "invalid-verification-registry",
            "verification registry has an unsupported schema_version",
            path.as_posix(),
        )
    if "updated_at" not in data or (
        data["updated_at"] is not None
        and (
            not isinstance(data["updated_at"], str)
            or parse_datetime(data["updated_at"]) is None
        )
    ):
        return empty_ledger(), Finding(
            "invalid-verification-registry",
            "verification registry has an invalid updated_at value",
            path.as_posix(),
        )
    if "head" not in data or (
        data["head"] is not None
        and (not isinstance(data["head"], str) or not data["head"].strip())
    ):
        return empty_ledger(), Finding(
            "invalid-verification-registry",
            "verification registry has an invalid head value",
            path.as_posix(),
        )
    return data, None


def create_temporary_registry_file(parent_descriptor: int, leaf_name: str) -> tuple[int, str]:
    for _ in range(64):
        temporary = f".{leaf_name}.{os.urandom(16).hex()}.tmp"
        try:
            descriptor = os.open(
                temporary,
                file_open_flags(os.O_CREAT | os.O_EXCL | os.O_WRONLY),
                0o600,
                dir_fd=parent_descriptor,
            )
        except FileExistsError:
            continue
        if not stat.S_ISREG(os.fstat(descriptor).st_mode):
            os.close(descriptor)
            try:
                os.unlink(temporary, dir_fd=parent_descriptor)
            except OSError:
                pass
            raise BundleError("temporary verification registry file is not regular")
        return descriptor, temporary
    raise BundleError("cannot allocate a unique temporary verification registry file")


def save_ledger(path: Path, bundle_root: Path, ledger: dict[str, Any]) -> None:
    payload = json.dumps(ledger, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    parent_descriptor = registry_parent_descriptor(path, bundle_root, create=True)
    descriptor: int | None = None
    temporary: str | None = None
    try:
        descriptor, temporary = create_temporary_registry_file(parent_descriptor, path.name)
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            descriptor = None
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        try:
            existing = os.stat(path.name, dir_fd=parent_descriptor, follow_symlinks=False)
        except FileNotFoundError:
            pass
        else:
            if stat.S_ISLNK(existing.st_mode):
                raise BundleError(f"verification registry must not be a symbolic link: {path}")
        os.replace(temporary, path.name, src_dir_fd=parent_descriptor, dst_dir_fd=parent_descriptor)
        temporary = None
        os.fsync(parent_descriptor)
    finally:
        if descriptor is not None:
            os.close(descriptor)
        if temporary is not None:
            try:
                os.unlink(temporary, dir_fd=parent_descriptor)
            except FileNotFoundError:
                pass
        os.close(parent_descriptor)


# ---------------------------------------------------------------------------
# Link and concept scanning
# ---------------------------------------------------------------------------


def strip_code_fences(body: str) -> str:
    return FENCE_RE.sub("", body)


def broken_local_links(path: Path, body: str, bundle_root: Path) -> list[str]:
    broken: list[str] = []
    for raw_target in MARKDOWN_LINK_RE.findall(strip_code_fences(body)):
        target = raw_target.strip().split()[0].strip("<>")
        if not target or target.startswith("#") or is_url(target):
            continue
        target = unquote(target.split("#", 1)[0].split("?", 1)[0])
        if not target:
            continue
        candidate = bundle_root / target.lstrip("/") if target.startswith("/") else path.parent / target
        if candidate.exists() or (candidate.suffix == "" and (candidate / "index.md").exists()):
            continue
        broken.append(raw_target.strip())
    return sorted(set(broken))


def concept_metadata_type_issues(meta: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    for key in ("type", "title", "description"):
        if key in meta and not isinstance(meta[key], str):
            issues.append(f"invalid-{key}")
    for key in ("scope", "sources"):
        if key in meta and (
            not isinstance(meta[key], list)
            or any(not isinstance(value, str) or not value.strip() for value in meta[key])
        ):
            issues.append(f"invalid-{key}")
    if "verification" in meta:
        verification = meta["verification"]
        if not isinstance(verification, dict):
            issues.append("invalid-verification")
        else:
            for key in ("strategy", "target"):
                if key in verification and not isinstance(verification[key], str):
                    issues.append(f"invalid-verification-{key}")
    return issues

def read_bundle_index(
    bundle_root: Path, repo_root: Path
) -> tuple[dict[str, Any], str, list[Finding]]:
    index_path = bundle_root / "index.md"
    location = index_path.relative_to(repo_root).as_posix()
    try:
        index_mode = os.lstat(index_path).st_mode
    except FileNotFoundError:
        return {}, "", [Finding("missing-index", "docs/index.md is missing", location)]
    except OSError as exc:
        return {}, "", [
            Finding("invalid-index-frontmatter", f"cannot inspect index.md: {exc}", location)
        ]
    if stat.S_ISLNK(index_mode):
        return {}, "", [
            Finding("invalid-index-symlink", "index.md must not be a symbolic link", location)
        ]
    if not stat.S_ISREG(index_mode):
        return {}, "", [
            Finding("invalid-index-frontmatter", "index.md must be a regular file", location)
        ]
    try:
        metadata, body, has_frontmatter, _, frontmatter_error = read_markdown(index_path)
    except (OSError, UnicodeDecodeError) as exc:
        return {}, "", [
            Finding("invalid-index-frontmatter", f"cannot read index frontmatter: {exc}", location)
        ]
    if not has_frontmatter:
        return {}, body, [
            Finding(
                "missing-index-frontmatter",
                "index.md must start with YAML frontmatter",
                location,
            )
        ]
    if frontmatter_error or not isinstance(metadata, dict):
        message = frontmatter_error or "index frontmatter root must be a mapping"
        return {}, body, [Finding("invalid-index-frontmatter", message, location)]
    return metadata, body, []


def resolve_decision_relation(raw: Any, source_path: Path, bundle_root: Path) -> Path | None:
    if not isinstance(raw, str) or not raw.strip():
        return None
    candidate = Path(raw)
    if candidate.is_absolute():
        return None
    requested = Path(os.path.abspath(source_path.parent / candidate))
    try:
        requested.relative_to(bundle_root.resolve())
    except ValueError:
        return None
    try:
        reject_symlink_components(requested, bundle_root.resolve(), "Decision relation")
    except BundleError:
        return None
    target = requested.resolve()
    if (
        not target.is_file()
        or target.suffix.lower() != ".md"
        or target.name in {"index.md", "log.md"}
        or ".okf" in target.parts
    ):
        return None
    return target


def historical_decision_issues(meta: dict[str, Any], path: Path, bundle_root: Path) -> list[str]:
    status = meta.get("status")
    if not isinstance(status, str) or status not in {"proposed", "accepted", "superseded"}:
        return ["invalid-historical-status"]
    if status != "superseded":
        return []

    replacement = resolve_decision_relation(meta.get("superseded_by"), path, bundle_root)
    if replacement is None:
        return ["missing-superseded-by"]
    try:
        replacement_meta, _, has_frontmatter, _, parse_error = read_markdown(replacement)
    except OSError:
        return ["invalid-superseded-by"]
    if parse_error or not has_frontmatter or replacement_meta.get("type") != "Decision":
        return ["invalid-superseded-by"]
    reverse = resolve_decision_relation(replacement_meta.get("supersedes"), replacement, bundle_root)
    if reverse is None or reverse != path.resolve():
        return ["invalid-supersedes-relation"]
    return []


def scan_concept(
    path: Path,
    repo_root: Path,
    bundle_root: Path,
    registry_path: Path,
    index_meta: dict[str, Any],
    ledger_entry: Any,
    registry_invalid: bool,
    now: datetime,
) -> tuple[ConceptSnapshot, dict[str, Any]]:
    meta, body, has_frontmatter, full_text, frontmatter_error = read_markdown(path)
    relative = path.resolve().relative_to(repo_root).as_posix()
    concept_id = concept_id_for(path, bundle_root)
    concept_type = as_string(meta.get("type"))
    title = as_string(meta.get("title"))
    strategy, target = effective_policy(meta, index_meta)

    metadata_issues = concept_metadata_type_issues(meta)
    notes: list[str] = []
    if not has_frontmatter:
        metadata_issues.append("missing-frontmatter")
    if frontmatter_error:
        metadata_issues.append("invalid-frontmatter")
    if not concept_type:
        metadata_issues.append("missing-type")
    if strategy and strategy not in SUPPORTED_STRATEGIES:
        metadata_issues.append("unsupported-strategy")
    duration = parse_duration(target)
    if target and duration is None:
        metadata_issues.append("unsupported-target")
        notes.append("scanner supports PnD and PnW targets")
    if concept_type == "Decision" and strategy == "historical":
        metadata_issues.extend(historical_decision_issues(meta, path, bundle_root))

    source_hashes, source_fingerprint, missing_sources, patterns = source_snapshot(
        repo_root, registry_path, meta
    )
    source_sensitive = strategy in {"source-change", "source-change-and-periodic", "generated"}
    no_local_sources = source_sensitive and not patterns
    if no_local_sources:
        notes.append("no local scope/sources available for deterministic source-change detection")
        metadata_issues.append("no-local-sources")

    document_hash = sha256_bytes(full_text.encode("utf-8"))
    links = broken_local_links(path, body, bundle_root)

    record_invalid = ledger_entry is not None and not is_valid_verification_record(
        ledger_entry, relative, concept_type
    )
    if registry_invalid:
        metadata_issues.append("invalid-verification-registry")
    if registry_invalid or record_invalid:
        metadata_issues.append("incomplete-verification-record")
    entry = (
        ledger_entry
        if not registry_invalid and not record_invalid and isinstance(ledger_entry, dict)
        else None
    )
    verified_at_raw = entry["verified_at"] if entry else None
    verified_at = parse_datetime(verified_at_raw)
    verified_commit = entry["verified_commit"] if entry else None
    method = entry["method"] if entry else None

    document_changed = False
    changed_sources: list[str] = []
    if entry:
        document_changed = entry["document_hash"] != document_hash
        if source_sensitive and entry["source_fingerprint"] != source_fingerprint:
            changed_sources = changed_source_paths(entry["sources"], source_hashes)

    due = bool(
        strategy in {"periodic", "source-change-and-periodic"}
        and verified_at
        and duration
        and verified_at + duration <= now
    )

    if missing_sources or registry_invalid or record_invalid or no_local_sources or metadata_issues:
        freshness = "blocked"
    elif not entry:
        freshness = "unverified"
    elif document_changed or changed_sources:
        freshness = "dirty"
    elif due:
        freshness = "due"
    else:
        freshness = "fresh"

    if not duration:
        notes.append("no supported target; time-bounded freshness cannot be asserted")

    snapshot_data = {
        "path": relative,
        "concept_id": concept_id,
        "type": concept_type,
        "strategy": strategy,
        "target": target,
        "document_hash": document_hash,
        "source_fingerprint": source_fingerprint,
        "sources": source_hashes,
        "missing_sources": missing_sources,
    }

    return (
        ConceptSnapshot(
            path=relative,
            concept_id=concept_id,
            type=concept_type,
            title=title,
            freshness=freshness,
            strategy=strategy,
            target=target,
            verified_at=verified_at_raw,
            verified_commit=verified_commit,
            verification_method=method,
            document_changed=document_changed,
            changed_sources=changed_sources,
            missing_sources=missing_sources,
            broken_links=links,
            metadata_issues=sorted(set(metadata_issues)),
            notes=notes,
        ),
        snapshot_data,
    )


def queue_sort_key(result: ConceptSnapshot) -> tuple[int, str]:
    order = {"blocked": 0, "dirty": 1, "unverified": 2, "due": 3, "fresh": 4}
    return order.get(result.freshness, 9), result.path


def build_scan_report(
    repo_root: Path,
    bundle_root: Path,
    registry_path: Path,
    now: datetime,
    include_fresh: bool,
) -> ScanReport:
    if not bundle_root.exists() or not bundle_root.is_dir():
        raise BundleError(f"bundle directory does not exist: {bundle_root}")

    bundle_issues: list[Finding] = []
    index_path = bundle_root / "index.md"
    index_meta, body, index_issues = read_bundle_index(bundle_root, repo_root)
    bundle_issues.extend(index_issues)
    if not index_issues:
        for link in broken_local_links(index_path, body, bundle_root):
            bundle_issues.append(
                Finding("broken-index-link", link, index_path.relative_to(repo_root).as_posix())
            )

    ledger, ledger_issue = load_ledger(registry_path, bundle_root)
    if ledger_issue:
        try:
            ledger_issue.path = registry_path.relative_to(repo_root).as_posix()
        except ValueError:
            pass
        bundle_issues.append(ledger_issue)
    entries = ledger.get("concepts", {}) if isinstance(ledger.get("concepts"), dict) else {}

    concepts, concept_link_issues = discover_concepts(bundle_root, repo_root)
    bundle_issues.extend(concept_link_issues)
    concept_ids = {concept_id_for(path, bundle_root) for path in concepts}
    for orphan in sorted(set(entries) - concept_ids):
        bundle_issues.append(
            Finding(
                "orphan-verification-record",
                f"verification record has no matching Concept: {orphan}",
                registry_path.relative_to(repo_root).as_posix(),
            )
        )

    results: list[ConceptSnapshot] = []
    for path in concepts:
        concept_id = concept_id_for(path, bundle_root)
        result, _ = scan_concept(
            path,
            repo_root,
            bundle_root,
            registry_path,
            index_meta,
            entries.get(concept_id),
            ledger_issue is not None,
            now,
        )
        results.append(result)

    results.sort(key=queue_sort_key)
    queue = [result for result in results if result.candidate]
    states = {state: 0 for state in ["fresh", "due", "dirty", "unverified", "blocked"]}
    for result in results:
        states[result.freshness] += 1

    structural = len(bundle_issues) + sum(
        bool(item.missing_sources or item.broken_links or item.metadata_issues)
        for item in results
    )
    summary = {
        "concepts": len(results),
        "states": states,
        "candidates": len(queue),
        "document_changes": sum(item.document_changed for item in results),
        "source_changes": sum(bool(item.changed_sources) for item in results),
        "structural_findings": structural,
        "freshness_ready": bool(results)
        and structural == 0
        and not any(item.freshness != "fresh" for item in results),
    }

    policy = resolve_policy(index_meta, None)["raw"]
    return ScanReport(
        schema_version="2.0",
        generated_at=format_datetime(now),
        repo_root=str(repo_root),
        bundle=bundle_root.relative_to(repo_root).as_posix(),
        registry=registry_path.relative_to(repo_root).as_posix(),
        head=current_head(repo_root),
        policy=policy,
        summary=summary,
        queue=[asdict(item) for item in queue],
        bundle_issues=[asdict(item) for item in bundle_issues],
        concepts=[asdict(item) for item in results] if include_fresh else None,
    )


# ---------------------------------------------------------------------------
# Recording successful verification
# ---------------------------------------------------------------------------


def resolve_concept_path(raw: str, repo_root: Path, bundle_root: Path) -> Path:
    candidate = Path(raw)
    if candidate.is_absolute():
        requested = Path(os.path.abspath(candidate))
    else:
        repo_candidate = Path(os.path.abspath(repo_root / candidate))
        bundle_candidate = Path(os.path.abspath(bundle_root / candidate))
        requested = (
            repo_candidate
            if repo_candidate.exists() or repo_candidate.is_symlink()
            else bundle_candidate
        )
    try:
        requested.relative_to(bundle_root.resolve())
    except ValueError as exc:
        raise BundleError(f"concept must be inside the bundle: {raw}") from exc
    reject_symlink_components(requested, bundle_root.resolve(), "concept")
    path = requested.resolve()
    if not path.exists() or not path.is_file():
        raise BundleError(f"concept does not exist: {raw}")
    if path.name in {"index.md", "log.md"} or path.suffix.lower() != ".md":
        raise BundleError(f"not a Concept Document: {raw}")
    if ".okf" in path.parts:
        raise BundleError(f"verification registry files are not Concepts: {raw}")
    return path


def record_verification(
    repo_root: Path,
    bundle_root: Path,
    registry_path: Path,
    concepts: Iterable[str],
    method: str,
    evidence: list[str],
    now: datetime,
) -> dict[str, Any]:
    if method not in SUPPORTED_METHODS:
        raise BundleError(f"unsupported verification method: {method}")
    evidence_labels = validate_evidence_labels(evidence)

    index_meta, _, index_issues = read_bundle_index(bundle_root, repo_root)
    if index_issues:
        raise BundleError(
            "cannot record; strategy index is unavailable: "
            + ", ".join(issue.code for issue in index_issues)
        )

    with VerificationRegistryLock(bundle_root):
        ledger, issue = load_ledger(registry_path, bundle_root)
        if issue:
            raise BundleError(issue.message)
        entries = ledger.setdefault("concepts", {})
        if not isinstance(entries, dict):
            raise BundleError("verification registry concepts field is invalid")

        head = current_head(repo_root)
        recorded: list[dict[str, Any]] = []
        updates: list[tuple[str, dict[str, Any]]] = []
        for raw in concepts:
            path = resolve_concept_path(raw, repo_root, bundle_root)
            concept_id = concept_id_for(path, bundle_root)
            result, snapshot = scan_concept(
                path,
                repo_root,
                bundle_root,
                registry_path,
                index_meta,
                entries.get(concept_id),
                False,
                now,
            )
            if method == "continuity" and result.freshness not in {"fresh", "due"}:
                raise BundleError(
                    f"cannot record {concept_id}; continuity requires an existing unchanged "
                    "fresh or due verification record"
                )
            if result.missing_sources:
                raise BundleError(
                    f"cannot record {concept_id}; missing sources: "
                    + ", ".join(result.missing_sources)
                )
            if result.broken_links:
                raise BundleError(
                    f"cannot record {concept_id}; broken links: "
                    + ", ".join(result.broken_links)
                )
            metadata_issues = list(result.metadata_issues)
            if method in {"semantic", "executable"}:
                metadata_issues = [
                    issue
                    for issue in metadata_issues
                    if issue != "incomplete-verification-record"
                ]
            if metadata_issues:
                raise BundleError(
                    f"cannot record {concept_id}; blocking metadata issues: "
                    + ", ".join(metadata_issues)
                )

            entry = {
                "path": snapshot["path"],
                "type": snapshot["type"],
                "verified_at": format_datetime(now),
                "verified_commit": head,
                "method": method,
                "document_hash": snapshot["document_hash"],
                "source_fingerprint": snapshot["source_fingerprint"],
                "sources": snapshot["sources"],
            }
            if evidence_labels:
                entry["evidence"] = evidence_labels
            updates.append((concept_id, entry))
            recorded.append({"concept_id": concept_id, "path": snapshot["path"], "method": method})

        for concept_id, entry in updates:
            entries[concept_id] = entry
        ledger["schema_version"] = "1.0"
        ledger["updated_at"] = format_datetime(now)
        ledger["head"] = head
        save_ledger(registry_path, bundle_root, ledger)
        return {
            "registry": registry_path.relative_to(repo_root).as_posix(),
            "verified_at": format_datetime(now),
            "head": head,
            "recorded": recorded,
        }


# ---------------------------------------------------------------------------
# Presentation and CLI
# ---------------------------------------------------------------------------


def render_markdown(report: ScanReport) -> str:
    summary = report.summary
    states = summary["states"]
    lines = [
        "# Bundle Status",
        "",
        f"- Bundle: `{report.bundle}`",
        f"- Registry: `{report.registry}`",
        f"- HEAD: `{report.head or 'unavailable'}`",
        f"- Concepts: {summary['concepts']}",
        "- Freshness: "
        + ", ".join(
            f"{name}={states.get(name, 0)}"
            for name in ["fresh", "dirty", "unverified", "due", "blocked"]
        ),
        f"- Changed documents: {summary['document_changes']}",
        f"- Concepts with changed sources: {summary['source_changes']}",
        f"- Structural findings: {summary['structural_findings']}",
        f"- Freshness ready: {'yes' if summary['freshness_ready'] else 'no'}",
    ]
    if report.bundle_issues:
        lines.extend(["", "## Bundle issues"])
        for issue in report.bundle_issues:
            location = f" `{issue['path']}`" if issue.get("path") else ""
            lines.append(f"- **{issue['code']}**{location}: {issue['message']}")
    if report.queue:
        lines.extend(["", "## Verification queue"])
        for item in report.queue:
            reasons: list[str] = []
            if item["document_changed"]:
                reasons.append("document changed")
            if item["changed_sources"]:
                reasons.append("changed sources: " + ", ".join(item["changed_sources"][:5]))
            if item["missing_sources"]:
                reasons.append("missing sources: " + ", ".join(item["missing_sources"]))
            if item["broken_links"]:
                reasons.append(f"broken links: {len(item['broken_links'])}")
            if item["metadata_issues"]:
                reasons.append("metadata: " + ", ".join(item["metadata_issues"]))
            if not reasons:
                reasons.append(item["freshness"])
            lines.append(f"- `{item['path']}` — **{item['freshness']}**; " + "; ".join(reasons))
    return "\n".join(lines) + "\n"


def write_output(payload: str, output: str | None) -> None:
    if not output:
        sys.stdout.write(payload)
        return

    path = Path(output)
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
        temporary = ""
    finally:
        if temporary:
            try:
                os.unlink(temporary)
            except FileNotFoundError:
                pass


def add_common_paths(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--repo", default=".", help="repository root or a path inside it")
    parser.add_argument("--bundle", default="docs", help="bundle path relative to repository root")
    parser.add_argument(
        "--registry",
        help="verification registry path relative to repository root; default: <bundle>/.okf/verification.json",
    )
    parser.add_argument("--now", help="override current UTC time with an ISO 8601 timestamp")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    scan = subparsers.add_parser("scan", help="scan the bundle and emit a verification queue")
    add_common_paths(scan)
    scan.add_argument("--format", choices=["json", "markdown"], default="json")
    scan.add_argument("--output", help="write report to this path instead of stdout")
    scan.add_argument("--include-fresh", action="store_true", help="include all Concept details")
    scan.add_argument(
        "--strict",
        action="store_true",
        help="exit 1 when candidates or bundle issues exist",
    )

    record = subparsers.add_parser("record", help="record successful verification for selected Concepts")
    add_common_paths(record)
    record.add_argument("--concept", action="append", required=True, help="Concept path; repeat as needed")
    record.add_argument("--method", choices=sorted(SUPPORTED_METHODS), required=True)
    record.add_argument(
        "--evidence",
        action="append",
        choices=sorted(SUPPORTED_EVIDENCE),
        default=[],
        help="optional controlled evidence classification; repeat from the listed values",
    )
    record.add_argument("--output", help="write result JSON to this path instead of stdout")
    return parser


def absolute_path_from(base: Path, raw: str) -> Path:
    candidate = Path(raw)
    if not candidate.is_absolute():
        candidate = base / candidate
    return Path(os.path.abspath(candidate))


def reject_symlink_components(path: Path, root: Path, label: str) -> None:
    try:
        relative = path.relative_to(root)
    except ValueError as exc:
        raise BundleError(f"{label} must be inside {root}") from exc
    current = root
    for part in relative.parts:
        current = current / part
        try:
            mode = os.lstat(current).st_mode
        except FileNotFoundError:
            return
        if stat.S_ISLNK(mode):
            raise BundleError(f"{label} must not traverse a symbolic link: {current}")


def resolve_runtime_paths(args: argparse.Namespace) -> tuple[Path, Path, Path, datetime]:
    repo_root = find_repo_root(Path(args.repo))
    requested_bundle = absolute_path_from(repo_root, args.bundle)
    reject_symlink_components(requested_bundle, repo_root, "bundle")
    bundle_root = requested_bundle.resolve()
    try:
        bundle_root.relative_to(repo_root)
    except ValueError as exc:
        raise BundleError("bundle must be inside the repository") from exc

    requested_registry = (
        absolute_path_from(repo_root, args.registry)
        if args.registry
        else bundle_root / ".okf" / "verification.json"
    )
    try:
        requested_registry.relative_to(bundle_root)
    except ValueError as exc:
        raise BundleError("registry must be inside the target bundle") from exc
    reject_symlink_components(requested_registry, bundle_root, "registry")
    registry_path = requested_registry.resolve()
    try:
        registry_path.relative_to(repo_root)
        registry_path.relative_to(bundle_root)
    except ValueError as exc:
        raise BundleError("registry must be inside the repository and target bundle") from exc

    now = parse_datetime(args.now) if args.now else utc_now()
    if now is None:
        raise BundleError("--now is not a valid ISO 8601 timestamp")
    return repo_root, bundle_root, registry_path, now


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        repo_root, bundle_root, registry_path, now = resolve_runtime_paths(args)
        if args.command == "scan":
            report = build_scan_report(repo_root, bundle_root, registry_path, now, args.include_fresh)
            payload = (
                json.dumps(asdict(report), ensure_ascii=False, indent=2) + "\n"
                if args.format == "json"
                else render_markdown(report)
            )
            write_output(payload, args.output)
            if args.strict and (report.summary["candidates"] or report.bundle_issues):
                return 1
            return 0

        result = record_verification(
            repo_root,
            bundle_root,
            registry_path,
            args.concept,
            args.method,
            args.evidence,
            now,
        )
        write_output(json.dumps(result, ensure_ascii=False, indent=2) + "\n", args.output)
        return 0
    except (OSError, BundleError) as exc:
        print(f"bundle-status: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
