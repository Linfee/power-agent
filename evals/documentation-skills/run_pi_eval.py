#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import os
import shutil
import statistics
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 1
SKILL_PATHS = (Path("skills/dev-docs"), Path("skills/dev-docs-maintain"))
DEFAULT_CASES = Path(__file__).with_name("cases.json")
DEFAULT_MODEL = "cpa/glm-5.2"
DEFAULT_THINKING = "low"
INFRA_ERROR_MARKERS = (
    "connection reset",
    "connection refused",
    "network error",
    "service unavailable",
    "temporarily unavailable",
    "rate limit",
    "status 429",
    "status 502",
    "status 503",
    "status 504",
    "econnreset",
    "enotfound",
)
DECISION_FIELD_ORDER = (
    "route",
    "mode",
    "consumer_test",
    "coverage_candidate",
    "requires_scan_before_record",
    "write_long_term_docs",
    "redact_sensitive",
    "fresh_claim",
    "reason",
)
DECISION_FIELDS = set(DECISION_FIELD_ORDER)
BOOLEAN_DECISION_FIELDS = DECISION_FIELDS - {"route", "mode", "reason"}
ROUTES = {"dev-docs", "dev-docs-maintain", "writing-plans", "doc-coauthoring", "none", "needs-evidence"}
MODES = {"not-applicable", "check-only", "fix-safe", "full-maintain"}
CANONICAL_TIMEOUT_SECONDS = 120.0
CANONICAL_WARMUP = 2
CANONICAL_REPEAT = 2
CANONICAL_PI_VERSION = "0.75.5"

EVAL_INSTRUCTIONS = """你正在执行文档 Skill 行为评测。只做路由和工作流判断，不修改文件，不运行命令。

必须先使用 read 工具完整读取：
- skills/dev-docs/SKILL.md
- skills/dev-docs-maintain/SKILL.md

根据这两个 Skill 的当前契约判断用户请求。最终只输出一个 JSON object，不要 Markdown fence，不要额外文字。字段必须完整：
{
  "route": "dev-docs | dev-docs-maintain | writing-plans | doc-coauthoring | none | needs-evidence",
  "mode": "not-applicable | check-only | fix-safe | full-maintain",
  "consumer_test": false,
  "coverage_candidate": false,
  "requires_scan_before_record": false,
  "write_long_term_docs": false,
  "redact_sensitive": false,
  "fresh_claim": false,
  "reason": "一句简短理由"
}

字段含义：
- consumer_test：是否应对高价值 Concept 做 fresh-reader 任务测试。
- coverage_candidate：是否发现重要公开能力可能从未被文档化；它不是 freshness 状态。
- requires_scan_before_record：任何登记前是否必须先 scan 和核对证据。
- fresh_claim：是否可以仅凭请求中的现有信息宣称文档 fresh；缺少实际扫描和语义证据时必须为 false。

用户请求：
"""


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def hash_json_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def find_pi_binary(explicit: str | None) -> str:
    candidates: list[Path] = []
    if explicit:
        candidates.append(Path(explicit).expanduser())
    env_bin = os.environ.get("PI_AGENT_BIN")
    if env_bin:
        candidates.append(Path(env_bin).expanduser())
    path_bin = shutil.which("pi")
    if path_bin:
        candidates.append(Path(path_bin))
    candidates.append(Path.home() / ".pi/agent/npm/node_modules/.bin/pi")
    for candidate in candidates:
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return str(candidate.resolve())
    raise FileNotFoundError("Pi Agent executable not found; pass --pi-bin or set PI_AGENT_BIN")

def reject_symlink_components(path: Path) -> None:
    expanded = path.expanduser()
    absolute = expanded if expanded.is_absolute() else Path.cwd() / expanded
    current = Path(absolute.anchor)
    for part in absolute.parts[1:]:
        current /= part
        if current.is_symlink():
            raise ValueError(f"symlinked path components are not allowed: {current}")


def included_files(root: Path) -> dict[str, str]:
    files: dict[str, str] = {}
    for skill_path in SKILL_PATHS:
        absolute = root / skill_path
        if absolute.is_symlink():
            raise ValueError(f"symlinks are not allowed in evaluated Skill trees: {absolute}")
        if not absolute.is_dir():
            raise FileNotFoundError(f"missing skill directory: {absolute}")
        for path in sorted(absolute.rglob("*")):
            if path.is_symlink():
                raise ValueError(f"symlinks are not allowed in evaluated Skill trees: {path}")
            if path.is_dir() or path.name == ".DS_Store" or "__pycache__" in path.parts or path.suffix == ".pyc":
                continue
            relative = path.relative_to(root).as_posix()
            files[relative] = sha256_file(path)
    return files


def aggregate_file_hash(files: dict[str, str]) -> str:
    payload = "".join(f"{path}\0{digest}\n" for path, digest in sorted(files.items()))
    return sha256_bytes(payload.encode())


def git_value(root: Path, *args: str) -> str:
    proc = subprocess.run(
        ["git", "-C", str(root), *args],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return proc.stdout.strip()


def make_snapshot(source_root: Path, snapshot_root: Path) -> dict[str, Any]:
    reject_symlink_components(source_root)
    for skill_path in SKILL_PATHS:
        reject_symlink_components(source_root / skill_path)
    source_root = source_root.resolve()
    snapshot_root = snapshot_root.resolve()
    included_files(source_root)
    if snapshot_root.exists():
        raise FileExistsError(f"snapshot root already exists: {snapshot_root}")
    (snapshot_root / "skills").mkdir(parents=True)
    for skill_path in SKILL_PATHS:
        source = source_root / skill_path
        destination = snapshot_root / skill_path
        shutil.copytree(
            source,
            destination,
            symlinks=True,
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store"),
        )
    files = included_files(snapshot_root)
    dirty_diff = subprocess.run(
        ["git", "-C", str(source_root), "diff", "--binary", "--", *(str(p) for p in SKILL_PATHS)],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ).stdout
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "created_at": now_iso(),
        "source_root": str(source_root),
        "source_head": git_value(source_root, "rev-parse", "HEAD"),
        "source_dirty_diff_sha256": sha256_bytes(dirty_diff),
        "snapshot_root": str(snapshot_root),
        "tree_sha256": aggregate_file_hash(files),
        "files": files,
    }
    manifest_path = snapshot_root / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for skill_path in SKILL_PATHS:
        for path in sorted((snapshot_root / skill_path).rglob("*"), reverse=True):
            path.chmod(0o555 if path.is_dir() else 0o444)
        (snapshot_root / skill_path).chmod(0o555)
    return manifest


def verify_manifest(input_root: Path, manifest_path: Path) -> tuple[bool, dict[str, Any]]:
    input_root = input_root.resolve()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    expected_files = manifest.get("files")
    schema_valid = (
        manifest.get("schema_version") == SCHEMA_VERSION
        and isinstance(expected_files, dict)
        and bool(expected_files)
        and all(isinstance(path, str) and isinstance(digest, str) for path, digest in expected_files.items())
    )
    actual_files = included_files(input_root)
    actual_tree = aggregate_file_hash(actual_files)
    expected_files = expected_files if isinstance(expected_files, dict) else {}
    missing = sorted(set(expected_files) - set(actual_files))
    extra = sorted(set(actual_files) - set(expected_files))
    changed = sorted(path for path in set(expected_files) & set(actual_files) if expected_files[path] != actual_files[path])
    result = {
        "input_root": str(input_root),
        "manifest": str(manifest_path.resolve()),
        "schema_valid": schema_valid,
        "expected_tree_sha256": manifest.get("tree_sha256"),
        "actual_tree_sha256": actual_tree,
        "missing": missing,
        "extra": extra,
        "changed": changed,
    }
    verified = schema_valid and not missing and not extra and not changed and actual_tree == manifest.get("tree_sha256")
    return verified, result


def load_cases(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("unsupported cases schema")
    if data.get("output_fields") != list(DECISION_FIELD_ORDER):
        raise ValueError("output_fields must exactly match the canonical decision fields")
    cases = data.get("cases")
    if not isinstance(cases, list) or not cases:
        raise ValueError("cases must be a non-empty list")
    ids = [case.get("id") for case in cases]
    if any(not isinstance(case_id, str) or not case_id for case_id in ids):
        raise ValueError("every case needs a non-empty id")
    if len(ids) != len(set(ids)):
        raise ValueError("case ids must be unique")
    for case in cases:
        if type(case.get("critical")) is not bool:
            raise ValueError(f"case {case['id']} critical must be boolean")
        if not isinstance(case.get("prompt"), str) or not case["prompt"]:
            raise ValueError(f"case {case['id']} needs a prompt")
        expected = case.get("expected")
        if not isinstance(expected, dict) or not expected:
            raise ValueError(f"case {case['id']} needs expected fields")
        if not set(expected).issubset(DECISION_FIELDS):
            raise ValueError(f"case {case['id']} contains unknown expected fields")
        if "route" in expected and expected["route"] not in ROUTES:
            raise ValueError(f"case {case['id']} has invalid expected route")
        if "mode" in expected and expected["mode"] not in MODES:
            raise ValueError(f"case {case['id']} has invalid expected mode")
        for key in set(expected) & BOOLEAN_DECISION_FIELDS:
            if type(expected[key]) is not bool:
                raise ValueError(f"case {case['id']} expected {key} must be boolean")
        if "reason" in expected and (not isinstance(expected["reason"], str) or not expected["reason"]):
            raise ValueError(f"case {case['id']} expected reason must be non-empty")
    return data

def load_canonical_corpus(path: Path) -> tuple[dict[str, Any], str]:
    resolved = path.resolve()
    actual_sha = hash_json_file(resolved)
    canonical_sha = hash_json_file(DEFAULT_CASES.resolve())
    if actual_sha != canonical_sha:
        raise ValueError("cases file does not match the canonical corpus identity")
    return load_cases(resolved), actual_sha


def extract_text(message: dict[str, Any]) -> str:
    return "".join(
        part.get("text", "")
        for part in message.get("content", [])
        if isinstance(part, dict) and part.get("type") == "text"
    )


def parse_pi_jsonl(stdout: str) -> dict[str, Any]:
    events: list[dict[str, Any]] = []
    for line in stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Pi JSONL contains malformed event: {exc}") from exc
        if not isinstance(event, dict):
            raise ValueError("Pi JSONL event must be an object")
        events.append(event)
    assistant_message: dict[str, Any] | None = None
    tool_names: list[str] = []
    for event in events:
        if event.get("type") == "tool_execution_start":
            tool_names.append(str(event.get("toolName", "")))
        if event.get("type") == "message_end":
            message = event.get("message")
            if isinstance(message, dict) and message.get("role") == "assistant":
                assistant_message = message
    if assistant_message is None:
        for event in reversed(events):
            if event.get("type") == "agent_end":
                messages = event.get("messages") or []
                assistant_message = next(
                    (message for message in reversed(messages) if isinstance(message, dict) and message.get("role") == "assistant"),
                    None,
                )
                if assistant_message:
                    break
    if assistant_message is None:
        raise ValueError("Pi JSONL did not contain a final assistant message")
    usage = assistant_message.get("usage") or {}
    return {
        "event_count": len(events),
        "text": extract_text(assistant_message),
        "provider": assistant_message.get("provider"),
        "model": assistant_message.get("model"),
        "stop_reason": assistant_message.get("stopReason"),
        "usage": {
            "input": int(usage.get("input") or 0),
            "output": int(usage.get("output") or 0),
            "cache_read": int(usage.get("cacheRead") or 0),
            "cache_write": int(usage.get("cacheWrite") or 0),
            "total_tokens": int(usage.get("totalTokens") or 0),
        },
        "tool_names": tool_names,
    }


def validate_decision(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError("assistant output JSON must be an object")
    if set(value) != DECISION_FIELDS:
        raise ValueError(f"assistant output must contain exactly these fields: {sorted(DECISION_FIELDS)}")
    if value["route"] not in ROUTES or value["mode"] not in MODES:
        raise ValueError("assistant output contains an invalid route or mode")
    for key in BOOLEAN_DECISION_FIELDS:
        if type(value[key]) is not bool:
            raise ValueError(f"assistant output field {key} must be boolean")
    if not isinstance(value["reason"], str) or not value["reason"].strip():
        raise ValueError("assistant output reason must be a non-empty string")
    return value


def extract_json_object(text: str) -> dict[str, Any]:
    stripped = text.strip()
    if stripped.startswith("```"):
        lines = stripped.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        stripped = "\n".join(lines).strip()
    start = stripped.find("{")
    end = stripped.rfind("}")
    if start < 0 or end < start:
        raise ValueError("assistant output does not contain a JSON object")
    candidate = stripped[start : end + 1]
    try:
        value = json.loads(candidate)
    except json.JSONDecodeError:
        reason_marker = '"reason"'
        reason_start = candidate.find(reason_marker)
        prefix = candidate[:reason_start]
        if reason_start < 0 or not prefix.rstrip().endswith(","):
            raise
        value = json.loads(f'{prefix}{reason_marker}:"<unparseable>"}}')
    return validate_decision(value)


def score_output(parsed: dict[str, Any] | None, expected: dict[str, Any]) -> dict[str, Any]:
    if parsed is None:
        return {
            "score": 0.0,
            "matched": [],
            "mismatches": {key: {"expected": value, "actual": None} for key, value in expected.items()},
        }
    matched: list[str] = []
    mismatches: dict[str, Any] = {}
    for key, expected_value in expected.items():
        actual = parsed.get(key)
        if actual == expected_value:
            matched.append(key)
        else:
            mismatches[key] = {"expected": expected_value, "actual": actual}
    return {
        "score": len(matched) / len(expected),
        "matched": matched,
        "mismatches": mismatches,
    }

def safety_invariant_failures(case_id: str, parsed: dict[str, Any] | None) -> list[str]:
    if parsed is None:
        return []
    failures: list[str] = []
    if parsed.get("fresh_claim") is not False:
        failures.append("fresh_claim must be false without executed scan and semantic evidence")
    if case_id in {"stress-git-diff-only", "stress-record-without-scan"}:
        if parsed.get("requires_scan_before_record") is not True:
            failures.append("record-related requests must require scan before record")
    if case_id == "stress-sensitive-integration" and parsed.get("redact_sensitive") is not True:
        failures.append("sensitive integration material must be redacted")
    return failures


def is_infrastructure_error(stderr: str) -> bool:
    lowered = stderr.lower()
    return any(marker in lowered for marker in INFRA_ERROR_MARKERS)


def run_pi_sample(
    *,
    pi_bin: str,
    input_root: Path,
    case: dict[str, Any],
    repeat_index: int,
    model: str,
    thinking: str,
    timeout: float,
) -> dict[str, Any]:
    prompt = EVAL_INSTRUCTIONS + case["prompt"]
    command = [
        pi_bin,
        "--mode",
        "json",
        "--no-session",
        "--no-extensions",
        "--no-prompt-templates",
        "--no-themes",
        "--no-context-files",
        "--no-skills",
        "--skill",
        str(SKILL_PATHS[0]),
        "--skill",
        str(SKILL_PATHS[1]),
        "--tools",
        "read",
        "--model",
        model,
        "--thinking",
        thinking,
        "-p",
        prompt,
    ]
    started = time.monotonic()
    stdout = ""
    stderr = ""
    exit_code = 0
    timed_out = False
    try:
        proc = subprocess.run(
            command,
            cwd=input_root,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
        )
        stdout = proc.stdout
        stderr = proc.stderr
        exit_code = proc.returncode
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout if isinstance(exc.stdout, str) else ""
        stderr = exc.stderr if isinstance(exc.stderr, str) else ""
        exit_code = 124
        timed_out = True
    wall_seconds = time.monotonic() - started
    parsed_event: dict[str, Any] | None = None
    parsed_output: dict[str, Any] | None = None
    parse_error: str | None = None
    try:
        parsed_event = parse_pi_jsonl(stdout)
        parsed_output = extract_json_object(parsed_event["text"])
    except (ValueError, json.JSONDecodeError) as exc:
        parse_error = str(exc)
    scored = score_output(parsed_output, case["expected"])
    safety_failures = safety_invariant_failures(case["id"], parsed_output)
    tool_names = parsed_event["tool_names"] if parsed_event else []
    forbidden_tools = [name for name in tool_names if name != "read"]
    if safety_failures:
        scored["score"] = 0.0
    if exit_code != 0 or timed_out or parse_error or forbidden_tools:
        scored["score"] = 0.0
    return {
        "case_id": case["id"],
        "critical": bool(case.get("critical")),
        "repeat": repeat_index,
        "expected": case["expected"],
        "parsed": parsed_output,
        "score": scored["score"],
        "matched": scored["matched"],
        "mismatches": scored["mismatches"],
        "safety_failures": safety_failures,
        "wall_seconds": wall_seconds,
        "exit_code": exit_code,
        "timed_out": timed_out,
        "parse_error": parse_error,
        "stderr": stderr[-4000:],
        "provider": parsed_event.get("provider") if parsed_event else None,
        "model": parsed_event.get("model") if parsed_event else None,
        "stop_reason": parsed_event.get("stop_reason") if parsed_event else None,
        "usage": parsed_event.get("usage") if parsed_event else {"total_tokens": 0},
        "tool_names": tool_names,
        "forbidden_tools": forbidden_tools,
        "event_count": parsed_event.get("event_count", 0) if parsed_event else 0,
        "infrastructure_error": is_infrastructure_error(stderr),
        "raw_text": parsed_event.get("text", "") if parsed_event else "",
        "raw_stdout": stdout,
    }


def nearest_rank(values: list[float], percentile: float) -> float:
    if not values:
        raise ValueError("cannot compute percentile of empty values")
    ordered = sorted(values)
    rank = max(1, math.ceil(percentile * len(ordered)))
    return ordered[rank - 1]


def summarize_run(cases: list[dict[str, Any]], samples: list[dict[str, Any]]) -> dict[str, Any]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for sample in samples:
        grouped.setdefault(sample["case_id"], []).append(sample)
    case_scores: dict[str, float] = {}
    critical_failures: list[str] = []
    for case in cases:
        case_samples = grouped.get(case["id"], [])
        case_score = min((float(sample["score"]) for sample in case_samples), default=0.0)
        case_scores[case["id"]] = case_score
        if case.get("critical") and (not case_samples or any(float(sample["score"]) < 1.0 for sample in case_samples)):
            critical_failures.append(case["id"])
    behavior_score = statistics.fmean(case_scores.values()) if case_scores else 0.0
    successful = [sample for sample in samples if sample["exit_code"] == 0 and not sample["timed_out"] and not sample["parse_error"]]
    walls = [float(sample["wall_seconds"]) for sample in successful]
    tokens = [float(sample["usage"].get("total_tokens") or 0) for sample in successful]
    tool_calls = [float(len(sample["tool_names"])) for sample in successful]
    performance = {
        "wall_p50_seconds": statistics.median(walls) if walls else None,
        "wall_p95_seconds": nearest_rank(walls, 0.95) if walls else None,
        "average_total_tokens": statistics.fmean(tokens) if tokens else None,
        "average_tool_calls": statistics.fmean(tool_calls) if tool_calls else None,
    }
    return {
        "behavior_score": behavior_score,
        "case_scores": case_scores,
        "critical_failures": critical_failures,
        "sample_count": len(samples),
        "successful_sample_count": len(successful),
        "forbidden_tool_calls": sum(len(sample["forbidden_tools"]) for sample in samples),
        "safety_invariant_failures": sum(len(sample.get("safety_failures", [])) for sample in samples),
        "nonzero_exit_count": sum(1 for sample in samples if sample["exit_code"] != 0),
        "timeout_count": sum(1 for sample in samples if sample["timed_out"]),
        "parse_error_count": sum(1 for sample in samples if sample["parse_error"]),
        "infrastructure_error_count": sum(1 for sample in samples if sample["infrastructure_error"]),
        "performance": performance,
    }


def run_eval(args: argparse.Namespace) -> int:
    input_root = Path(args.input_root).resolve()
    cases_path = Path(args.cases).resolve()
    corpus, corpus_sha256 = load_canonical_corpus(cases_path)
    canonical_args = {
        "model": DEFAULT_MODEL,
        "thinking": DEFAULT_THINKING,
        "timeout": CANONICAL_TIMEOUT_SECONDS,
        "warmup": CANONICAL_WARMUP,
        "repeat": CANONICAL_REPEAT,
    }
    for key, expected in canonical_args.items():
        if getattr(args, key) != expected:
            raise ValueError(f"non-canonical {key}: {getattr(args, key)!r} != {expected!r}")
    if args.kind == "baseline" and not args.manifest:
        raise ValueError("baseline runs require --manifest")
    manifest_identity: dict[str, Any] | None = None
    if args.manifest:
        manifest_path = Path(args.manifest).resolve()
        ok, verification = verify_manifest(input_root, manifest_path)
        if not ok:
            print(json.dumps({"error": "manifest verification failed", "verification": verification}, ensure_ascii=False, indent=2), file=sys.stderr)
            return 2
        manifest_data = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest_identity = {
            "path": str(manifest_path),
            "sha256": sha256_file(manifest_path),
            "tree_sha256": manifest_data.get("tree_sha256"),
            "verified": True,
        }
    initial_files = included_files(input_root)
    initial_tree_sha256 = aggregate_file_hash(initial_files)
    if manifest_identity and initial_tree_sha256 != manifest_identity["tree_sha256"]:
        raise ValueError("pre-run Skill tree does not match the verified manifest")
    pi_bin = find_pi_binary(args.pi_bin)
    version_proc = subprocess.run(
        [pi_bin, "--version"],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    pi_version = (version_proc.stdout.strip() or version_proc.stderr.strip())
    if pi_version != CANONICAL_PI_VERSION:
        raise ValueError(f"non-canonical Pi version: {pi_version!r} != {CANONICAL_PI_VERSION!r}")
    cases = corpus["cases"]
    expected_provider, expected_model = requested_model_identity(args.model)
    for _ in range(args.warmup):
        warmup_sample = run_pi_sample(
            pi_bin=pi_bin,
            input_root=input_root,
            case=cases[0],
            repeat_index=0,
            model=args.model,
            thinking=args.thinking,
            timeout=args.timeout,
        )
        warmup_model_mismatch = (
            (expected_provider is not None and warmup_sample.get("provider") != expected_provider)
            or warmup_sample.get("model") != expected_model
        )
        if (
            warmup_sample["exit_code"] != 0
            or warmup_sample["timed_out"]
            or warmup_sample["parse_error"]
            or warmup_sample["forbidden_tools"]
            or warmup_sample["infrastructure_error"]
            or warmup_model_mismatch
        ):
            print(json.dumps({"error": "warmup failed", "sample": warmup_sample}, ensure_ascii=False, indent=2), file=sys.stderr)
            return 2
    samples: list[dict[str, Any]] = []
    for repeat_index in range(1, args.repeat + 1):
        for case in cases:
            sample = run_pi_sample(
                pi_bin=pi_bin,
                input_root=input_root,
                case=case,
                repeat_index=repeat_index,
                model=args.model,
                thinking=args.thinking,
                timeout=args.timeout,
            )
            samples.append(sample)
            print(
                f"[{repeat_index}/{args.repeat}] {case['id']}: score={sample['score']:.3f} "
                f"wall={sample['wall_seconds']:.2f}s tokens={sample['usage'].get('total_tokens', 0)}",
                file=sys.stderr,
            )
    final_files = included_files(input_root)
    final_tree_sha256 = aggregate_file_hash(final_files)
    if final_files != initial_files or final_tree_sha256 != initial_tree_sha256:
        print(json.dumps({"error": "Skill input tree changed during evaluation"}, ensure_ascii=False), file=sys.stderr)
        return 2
    result = {
        "schema_version": SCHEMA_VERSION,
        "protocol_version": 1,
        "created_at": now_iso(),
        "kind": args.kind,
        "input_root": str(input_root),
        "skill_tree_sha256": initial_tree_sha256,
        "skill_files": initial_files,
        "input_tree_sha256_before": initial_tree_sha256,
        "input_tree_sha256_after": final_tree_sha256,
        "manifest": manifest_identity,
        "corpus_path": str(cases_path),
        "corpus_sha256": corpus_sha256,
        "config": {
            "pi_version": pi_version,
            "model": args.model,
            "thinking": args.thinking,
            "timeout_seconds": args.timeout,
            "warmup": args.warmup,
            "repeat": args.repeat,
            "tools": ["read"],
        },
        "summary": summarize_run(cases, samples),
        "samples": samples,
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result["summary"], ensure_ascii=False, indent=2))
    return 0


def rescore_result(result: dict[str, Any], cases: list[dict[str, Any]]) -> dict[str, Any]:
    normalized = copy.deepcopy(result)
    case_map = {case["id"]: case for case in cases}
    for sample in normalized.get("samples", []):
        case = case_map.get(sample.get("case_id"))
        if case is None:
            raise ValueError(f"unknown case in result: {sample.get('case_id')}")
        saved_parsed = sample.get("parsed")
        saved_parse_error = sample.get("parse_error")
        raw_stdout = sample.get("raw_stdout")
        if not isinstance(raw_stdout, str):
            raise ValueError(f"sample {sample.get('case_id')} is missing raw_stdout")
        reparsed_event: dict[str, Any] | None = None
        reparsed: dict[str, Any] | None = None
        current_parse_error: str | None = None
        try:
            reparsed_event = parse_pi_jsonl(raw_stdout)
            reparsed = extract_json_object(reparsed_event["text"])
        except (ValueError, json.JSONDecodeError) as exc:
            current_parse_error = str(exc)
        if saved_parse_error:
            if saved_parsed is not None:
                raise ValueError(f"sample {sample.get('case_id')} has both parsed output and parse_error")
            if current_parse_error != saved_parse_error:
                raise ValueError(f"sample {sample.get('case_id')} parse_error does not match raw_stdout")
        else:
            if current_parse_error:
                raise ValueError(f"sample {sample.get('case_id')} raw_stdout no longer parses: {current_parse_error}")
            if saved_parsed != reparsed:
                raise ValueError(f"sample {sample.get('case_id')} parsed output does not match raw_stdout")
            sample["parsed"] = validate_decision(reparsed)
        if reparsed_event is not None:
            event_fields = {
                "raw_text": reparsed_event["text"],
                "provider": reparsed_event["provider"],
                "model": reparsed_event["model"],
                "stop_reason": reparsed_event["stop_reason"],
                "usage": reparsed_event["usage"],
                "tool_names": reparsed_event["tool_names"],
                "event_count": reparsed_event["event_count"],
            }
            for key, expected in event_fields.items():
                if sample.get(key) != expected:
                    raise ValueError(f"sample {sample.get('case_id')} {key} does not match raw_stdout")
        else:
            empty_event_fields = {
                "raw_text": "",
                "provider": None,
                "model": None,
                "stop_reason": None,
                "usage": {"total_tokens": 0},
                "tool_names": [],
                "event_count": 0,
            }
            for key, expected in empty_event_fields.items():
                if sample.get(key) != expected:
                    raise ValueError(f"sample {sample.get('case_id')} {key} exists without a parsed Pi event")
        scored = score_output(sample.get("parsed"), case["expected"])
        safety_failures = safety_invariant_failures(case["id"], sample.get("parsed"))
        forbidden_tools = sample.get("forbidden_tools") or [
            name for name in sample.get("tool_names", []) if name != "read"
        ]
        if sample.get("exit_code") != 0 or sample.get("timed_out") or sample.get("parse_error") or forbidden_tools or safety_failures:
            scored["score"] = 0.0
        sample.update(
            expected=case["expected"],
            critical=bool(case.get("critical")),
            score=scored["score"],
            matched=scored["matched"],
            mismatches=scored["mismatches"],
            forbidden_tools=forbidden_tools,
            safety_failures=safety_failures,
        )
    normalized["summary"] = summarize_run(cases, normalized.get("samples", []))
    return normalized


def bind_manifest(result: dict[str, Any], manifest_path: Path) -> dict[str, Any]:
    manifest_path = manifest_path.resolve()
    manifest_sha = sha256_file(manifest_path)
    input_root_value = result.get("input_root")
    if not isinstance(input_root_value, str) or not input_root_value:
        raise ValueError("baseline result is missing input_root")
    verified, verification = verify_manifest(Path(input_root_value), manifest_path)
    if not verified:
        raise ValueError(f"baseline snapshot does not match manifest: {verification}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    recorded = result.get("manifest") or {}
    if (
        recorded.get("verified") is not True
        or recorded.get("sha256") != manifest_sha
        or recorded.get("tree_sha256") != manifest.get("tree_sha256")
        or manifest.get("tree_sha256") != result.get("skill_tree_sha256")
    ):
        raise ValueError("baseline result manifest identity does not match the verified snapshot")
    bound = copy.deepcopy(result)
    bound["manifest"] = {
        "path": str(manifest_path),
        "sha256": manifest_sha,
        "tree_sha256": manifest.get("tree_sha256"),
        "verified": True,
    }
    return bound


def requested_model_identity(requested: str) -> tuple[str | None, str]:
    if "/" in requested:
        provider, model = requested.split("/", 1)
        return provider, model
    return None, requested


def actual_model_failures(result: dict[str, Any], label: str) -> list[str]:
    expected_provider, expected_model = requested_model_identity(str(result.get("config", {}).get("model", "")))
    failures: list[str] = []
    for sample in result.get("samples", []):
        allow_missing = label == "baseline" and (
            sample.get("exit_code") != 0 or sample.get("timed_out") or sample.get("parse_error")
        )
        actual_provider = sample.get("provider")
        actual_model = sample.get("model")
        if expected_provider is not None and actual_provider != expected_provider and not (allow_missing and actual_provider is None):
            failures.append(f"{label} sample {sample.get('case_id')} used provider {actual_provider}")
        if actual_model != expected_model and not (allow_missing and actual_model is None):
            failures.append(f"{label} sample {sample.get('case_id')} used model {actual_model}")
    return failures


def replaceable_infrastructure_sample(sample: dict[str, Any], result: dict[str, Any]) -> bool:
    if not sample.get("infrastructure_error"):
        return False
    if sample.get("parse_error") or sample.get("forbidden_tools") or sample.get("safety_failures"):
        return False
    if sample.get("mismatches"):
        return False
    expected_provider, expected_model = requested_model_identity(str(result.get("config", {}).get("model", "")))
    if expected_provider is not None and sample.get("provider") != expected_provider:
        return False
    if sample.get("model") != expected_model:
        return False
    return True


def validate_canonical_result(
    result: dict[str, Any],
    cases: list[dict[str, Any]],
    corpus_sha256: str,
    expected_kind: str,
) -> None:
    if result.get("schema_version") != SCHEMA_VERSION or result.get("protocol_version") != 1:
        raise ValueError("result schema_version or protocol_version is not canonical")
    if result.get("kind") != expected_kind:
        raise ValueError(f"result kind {result.get('kind')!r} does not match expected {expected_kind!r}")
    config = result.get("config") or {}
    expected_config = {
        "pi_version": CANONICAL_PI_VERSION,
        "model": DEFAULT_MODEL,
        "thinking": DEFAULT_THINKING,
        "timeout_seconds": CANONICAL_TIMEOUT_SECONDS,
        "warmup": CANONICAL_WARMUP,
        "repeat": CANONICAL_REPEAT,
        "tools": ["read"],
    }
    for key, expected in expected_config.items():
        if config.get(key) != expected:
            raise ValueError(f"non-canonical config.{key}: {config.get(key)!r} != {expected!r}")
    if result.get("corpus_sha256") != corpus_sha256:
        raise ValueError("result corpus_sha256 does not match the canonical corpus")
    if (
        result.get("input_tree_sha256_before") != result.get("skill_tree_sha256")
        or result.get("input_tree_sha256_after") != result.get("skill_tree_sha256")
    ):
        raise ValueError("result is not bound to one unchanged Skill input tree")
    input_root_value = result.get("input_root")
    if not isinstance(input_root_value, str) or not input_root_value:
        raise ValueError("result is missing input_root")
    actual_files = included_files(Path(input_root_value).resolve())
    if actual_files != result.get("skill_files") or aggregate_file_hash(actual_files) != result.get("skill_tree_sha256"):
        raise ValueError("saved result does not match the current Skill input tree")
    for sample in result.get("samples", []):
        if sample.get("parsed") is None and not sample.get("parse_error"):
            raise ValueError("result contains a null parsed output without a parse_error")
    expected_sequence = [
        (repeat, case["id"])
        for repeat in range(1, CANONICAL_REPEAT + 1)
        for case in cases
    ]
    actual_sequence = [(sample.get("repeat"), sample.get("case_id")) for sample in result.get("samples", [])]
    if actual_sequence != expected_sequence:
        raise ValueError("result samples do not match the canonical case order and repeat count")


def combine_results(
    first: dict[str, Any],
    rerun: dict[str, Any],
    cases: list[dict[str, Any]],
    *,
    replace_infrastructure_errors: bool = False,
) -> dict[str, Any]:
    if first.get("corpus_sha256") != rerun.get("corpus_sha256"):
        raise ValueError("rerun corpus differs")
    if first.get("skill_tree_sha256") != rerun.get("skill_tree_sha256"):
        raise ValueError("rerun skill tree differs")
    for key in ("pi_version", "model", "thinking", "timeout_seconds", "warmup", "repeat", "tools"):
        if first.get("config", {}).get(key) != rerun.get("config", {}).get(key):
            raise ValueError(f"rerun config.{key} differs")
    combined = copy.deepcopy(first)
    combined["kind"] = f"{first.get('kind', 'run')}+rerun"
    first_samples = copy.deepcopy(first.get("samples", []))
    if replace_infrastructure_errors:
        first_samples = [
            sample for sample in first_samples if not replaceable_infrastructure_sample(sample, first)
        ]
    combined["samples"] = first_samples + copy.deepcopy(rerun.get("samples", []))
    combined["summary"] = summarize_run(cases, combined["samples"])
    combined["rerun_created_at"] = rerun.get("created_at")
    return combined


def rerun_is_eligible(comparison: dict[str, Any], baseline: dict[str, Any], candidate: dict[str, Any]) -> bool:
    if baseline["summary"].get("infrastructure_error_count") or candidate["summary"].get("infrastructure_error_count"):
        return True
    failures = comparison.get("failures", [])
    return bool(failures) and all(item.startswith(("wall_p50_seconds", "wall_p95_seconds")) for item in failures)


def compare_runs(baseline: dict[str, Any], candidate: dict[str, Any]) -> dict[str, Any]:
    failures: list[str] = []
    advisories: list[str] = []
    if baseline.get("corpus_sha256") != candidate.get("corpus_sha256"):
        failures.append("corpus_sha256 differs")
    baseline_manifest = baseline.get("manifest") or {}
    if not baseline_manifest.get("verified") or baseline_manifest.get("tree_sha256") != baseline.get("skill_tree_sha256"):
        failures.append("baseline is not bound to a verified snapshot manifest")
    for key in ("pi_version", "model", "thinking", "timeout_seconds", "warmup", "repeat", "tools"):
        if baseline.get("config", {}).get(key) != candidate.get("config", {}).get(key):
            failures.append(f"config.{key} differs")
    failures.extend(actual_model_failures(baseline, "baseline"))
    failures.extend(actual_model_failures(candidate, "candidate"))
    base_summary = baseline["summary"]
    cand_summary = candidate["summary"]
    if base_summary.get("critical_failures"):
        advisories.append("pre-change baseline critical failures: " + ", ".join(base_summary["critical_failures"]))
    if cand_summary["behavior_score"] + 1e-12 < base_summary["behavior_score"]:
        failures.append(
            f"behavior score regressed: {cand_summary['behavior_score']:.6f} < {base_summary['behavior_score']:.6f}"
        )
    if cand_summary["critical_failures"]:
        failures.append("critical cases failed: " + ", ".join(cand_summary["critical_failures"]))
    if cand_summary["forbidden_tool_calls"]:
        failures.append(f"candidate used {cand_summary['forbidden_tool_calls']} forbidden tools")
    if cand_summary.get("safety_invariant_failures"):
        failures.append(f"candidate violated {cand_summary['safety_invariant_failures']} safety invariants")
    if cand_summary.get("nonzero_exit_count"):
        failures.append(f"candidate had {cand_summary['nonzero_exit_count']} nonzero exits")
    if cand_summary.get("timeout_count"):
        failures.append(f"candidate had {cand_summary['timeout_count']} timeouts")
    if cand_summary.get("parse_error_count"):
        failures.append(f"candidate had {cand_summary['parse_error_count']} parse errors")
    if cand_summary["infrastructure_error_count"]:
        failures.append(f"candidate had {cand_summary['infrastructure_error_count']} infrastructure errors")
    thresholds = {
        "wall_p50_seconds": 1.10,
        "wall_p95_seconds": 1.20,
        "average_total_tokens": 1.15,
    }
    ratios: dict[str, float | None] = {}
    for metric, multiplier in thresholds.items():
        base_value = base_summary["performance"].get(metric)
        cand_value = cand_summary["performance"].get(metric)
        if base_value is None or cand_value is None or base_value <= 0:
            failures.append(f"cannot compare performance metric {metric}")
            ratios[metric] = None
            continue
        ratio = cand_value / base_value
        ratios[metric] = ratio
        if ratio > multiplier:
            failures.append(f"{metric} regressed: ratio {ratio:.4f} > {multiplier:.2f}")
    base_tools = base_summary["performance"].get("average_tool_calls")
    cand_tools = cand_summary["performance"].get("average_tool_calls")
    if base_tools is not None and cand_tools is not None and cand_tools > base_tools + 0.01:
        advisories.append(f"average tool calls increased: {base_tools:.3f} -> {cand_tools:.3f}")
    return {
        "passed": not failures,
        "failures": failures,
        "advisories": advisories,
        "behavior": {
            "baseline": base_summary["behavior_score"],
            "candidate": cand_summary["behavior_score"],
        },
        "performance_ratios": ratios,
        "baseline_skill_tree_sha256": baseline.get("skill_tree_sha256"),
        "candidate_skill_tree_sha256": candidate.get("skill_tree_sha256"),
    }


def normalized_result(
    path: Path,
    cases: list[dict[str, Any]],
    corpus_sha256: str,
    expected_kind: str,
    manifest: Path | None = None,
) -> dict[str, Any]:
    result = rescore_result(json.loads(path.read_text(encoding="utf-8")), cases)
    if manifest:
        result = bind_manifest(result, manifest)
    validate_canonical_result(result, cases, corpus_sha256, expected_kind)
    return result


def normalize_command(args: argparse.Namespace) -> int:
    corpus, corpus_sha256 = load_canonical_corpus(Path(args.cases))
    result_path = Path(args.input)
    raw = json.loads(result_path.read_text(encoding="utf-8"))
    kind = raw.get("kind")
    if kind not in {"baseline", "candidate", "rerun"}:
        raise ValueError(f"unsupported result kind: {kind!r}")
    if kind == "baseline" and not args.manifest:
        raise ValueError("normalizing a baseline requires --manifest")
    normalized = rescore_result(raw, corpus["cases"])
    if args.manifest:
        normalized = bind_manifest(normalized, Path(args.manifest))
    validate_canonical_result(normalized, corpus["cases"], corpus_sha256, kind)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(normalized, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(normalized["summary"], ensure_ascii=False, indent=2))
    return 0


def compare_command(args: argparse.Namespace) -> int:
    corpus, corpus_sha256 = load_canonical_corpus(Path(args.cases))
    cases = corpus["cases"]
    manifest = Path(args.baseline_manifest)
    baseline = normalized_result(Path(args.baseline), cases, corpus_sha256, "baseline", manifest)
    candidate = normalized_result(Path(args.candidate), cases, corpus_sha256, "candidate")
    comparison = compare_runs(baseline, candidate)
    if bool(args.baseline_rerun) != bool(args.candidate_rerun):
        raise ValueError("paired rerun requires both --baseline-rerun and --candidate-rerun")
    if args.baseline_rerun:
        initial_comparison = comparison
        if not rerun_is_eligible(initial_comparison, baseline, candidate):
            comparison = {
                **initial_comparison,
                "passed": False,
                "failures": initial_comparison["failures"] + ["paired rerun is not eligible for these failures"],
                "rerun_used": False,
            }
        else:
            baseline_rerun = normalized_result(Path(args.baseline_rerun), cases, corpus_sha256, "rerun", manifest)
            candidate_rerun = normalized_result(Path(args.candidate_rerun), cases, corpus_sha256, "rerun")
            combined_baseline = combine_results(
                baseline,
                baseline_rerun,
                cases,
                replace_infrastructure_errors=bool(baseline["summary"].get("infrastructure_error_count")),
            )
            combined_candidate = combine_results(
                candidate,
                candidate_rerun,
                cases,
                replace_infrastructure_errors=bool(candidate["summary"].get("infrastructure_error_count")),
            )
            comparison = compare_runs(combined_baseline, combined_candidate)
            comparison["rerun_used"] = True
            comparison["initial_comparison"] = initial_comparison
    else:
        comparison["rerun_used"] = False
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(comparison, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(comparison, ensure_ascii=False, indent=2))
    return 0 if comparison["passed"] else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Pi Agent eval for dev-docs workflow Skills")
    subparsers = parser.add_subparsers(dest="command", required=True)

    snapshot = subparsers.add_parser("snapshot", help="freeze complete pre-change Skill directories")
    snapshot.add_argument("--source-root", default=".")
    snapshot.add_argument("--snapshot-root", required=True)

    verify = subparsers.add_parser("verify", help="verify an input tree against a snapshot manifest")
    verify.add_argument("--input-root", required=True)
    verify.add_argument("--manifest", required=True)

    run = subparsers.add_parser("run", help="run the canonical Pi Agent corpus")
    run.add_argument("--kind", choices=("baseline", "candidate", "rerun"), required=True)
    run.add_argument("--input-root", required=True)
    run.add_argument("--manifest")
    run.add_argument("--cases", default=str(DEFAULT_CASES))
    run.add_argument("--output", required=True)
    run.add_argument("--pi-bin")
    run.add_argument("--model", default=DEFAULT_MODEL)
    run.add_argument("--thinking", default=DEFAULT_THINKING)
    run.add_argument("--timeout", type=float, default=120.0)
    run.add_argument("--warmup", type=int, default=2)
    run.add_argument("--repeat", type=int, default=2)

    normalize = subparsers.add_parser("normalize", help="rescore a saved run and bind an optional manifest")
    normalize.add_argument("--input", required=True)
    normalize.add_argument("--output", required=True)
    normalize.add_argument("--cases", default=str(DEFAULT_CASES))
    normalize.add_argument("--manifest")

    compare = subparsers.add_parser("compare", help="compare candidate against baseline gates")
    compare.add_argument("--baseline", required=True)
    compare.add_argument("--candidate", required=True)
    compare.add_argument("--baseline-manifest", required=True)
    compare.add_argument("--baseline-rerun")
    compare.add_argument("--candidate-rerun")
    compare.add_argument("--cases", default=str(DEFAULT_CASES))
    compare.add_argument("--output")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        if args.command == "snapshot":
            manifest = make_snapshot(Path(args.source_root), Path(args.snapshot_root))
            print(json.dumps(manifest, ensure_ascii=False, indent=2))
            return 0
        if args.command == "verify":
            ok, result = verify_manifest(Path(args.input_root), Path(args.manifest))
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0 if ok else 1
        if args.command == "run":
            return run_eval(args)
        if args.command == "normalize":
            return normalize_command(args)
        if args.command == "compare":
            return compare_command(args)
    except (FileNotFoundError, FileExistsError, ValueError, subprocess.CalledProcessError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
