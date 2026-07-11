#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).with_name("run_pi_eval.py")
SPEC = importlib.util.spec_from_file_location("run_pi_eval", MODULE_PATH)
assert SPEC and SPEC.loader
RUNNER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RUNNER)


class PiEvalRunnerTests(unittest.TestCase):
    def test_parse_pi_jsonl_uses_final_assistant_message(self) -> None:
        stdout = "\n".join(
            [
                json.dumps({"type": "session", "version": 3}),
                json.dumps({"type": "tool_execution_start", "toolName": "read"}),
                json.dumps(
                    {
                        "type": "message_end",
                        "message": {
                            "role": "assistant",
                            "content": [{"type": "text", "text": '{"route":"dev-docs"}'}],
                            "provider": "cpa",
                            "model": "glm-5.2",
                            "stopReason": "stop",
                            "usage": {"input": 10, "output": 5, "totalTokens": 15},
                        },
                    }
                ),
            ]
        )
        parsed = RUNNER.parse_pi_jsonl(stdout)
        self.assertEqual(parsed["text"], '{"route":"dev-docs"}')
        self.assertEqual(parsed["usage"]["total_tokens"], 15)
        self.assertEqual(parsed["tool_names"], ["read"])

    def test_parse_pi_jsonl_rejects_malformed_event(self) -> None:
        with self.assertRaisesRegex(ValueError, "malformed event"):
            RUNNER.parse_pi_jsonl('{"type":"tool_execution_start"}\nnot-json')

    def test_extract_json_object_accepts_code_fence(self) -> None:
        decision = self.decision(route="none")
        parsed = RUNNER.extract_json_object(f"```json\n{json.dumps(decision)}\n```")
        self.assertEqual(parsed, decision)

    def test_extract_json_object_recovers_unescaped_reason_quotes(self) -> None:
        text = (
            '{"route":"dev-docs-maintain","mode":"fix-safe","consumer_test":false,'
            '"coverage_candidate":false,"requires_scan_before_record":true,'
            '"write_long_term_docs":false,"redact_sensitive":false,"fresh_claim":false,'
            '"reason":"不能凭"刚更新"声称"}'
        )
        parsed = RUNNER.extract_json_object(text)
        self.assertEqual(parsed["route"], "dev-docs-maintain")
        self.assertTrue(parsed["requires_scan_before_record"])

    def test_extract_json_object_rejects_missing_fixed_field(self) -> None:
        decision = self.decision()
        del decision["reason"]
        with self.assertRaisesRegex(ValueError, "exactly these fields"):
            RUNNER.extract_json_object(json.dumps(decision))

    def test_score_output_compares_only_oracle_fields(self) -> None:
        score = RUNNER.score_output(
            {"route": "dev-docs", "mode": "not-applicable", "reason": "extra"},
            {"route": "dev-docs", "mode": "check-only"},
        )
        self.assertEqual(score["score"], 0.5)
        self.assertEqual(score["matched"], ["route"])
        self.assertIn("mode", score["mismatches"])

    def test_safety_invariants_reject_false_fresh_claim(self) -> None:
        failures = RUNNER.safety_invariant_failures("route-current-fact", {"fresh_claim": True})
        self.assertEqual(len(failures), 1)

    def test_rescore_applies_global_safety_invariants(self) -> None:
        cases = [{"id": "route-current-fact", "critical": True, "expected": {"route": "dev-docs"}}]
        result = {
            "samples": [
                {
                    **self.sample("route-current-fact", 1, 1.0, 1.0, 100),
                    "parsed": self.decision(route="dev-docs", fresh_claim=True),
                    "raw_text": json.dumps(self.decision(route="dev-docs", fresh_claim=True)),
                    "raw_stdout": self.pi_stdout(json.dumps(self.decision(route="dev-docs", fresh_claim=True))),
                    "expected": {"route": "dev-docs"},
                }
            ]
        }
        normalized = RUNNER.rescore_result(result, cases)
        self.assertEqual(normalized["samples"][0]["score"], 0.0)
        self.assertEqual(normalized["summary"]["critical_failures"], ["route-current-fact"])

    def test_rescore_rejects_saved_partial_decision(self) -> None:
        cases = [{"id": "case", "critical": True, "expected": {"route": "dev-docs"}}]
        result = {
            "samples": [
                {
                    **self.sample("case", 1, 1.0, 1.0, 100),
                    "parsed": {"route": "dev-docs", "fresh_claim": False},
                    "raw_text": json.dumps({"route": "dev-docs", "fresh_claim": False}),
                    "raw_stdout": self.pi_stdout(json.dumps({"route": "dev-docs", "fresh_claim": False})),
                }
            ]
        }
        with self.assertRaisesRegex(ValueError, "exactly these fields"):
            RUNNER.rescore_result(result, cases)

    def test_rescore_requires_raw_parsed_consistency_and_sticky_parse_error(self) -> None:
        cases = [{"id": "case", "critical": True, "expected": {"route": "dev-docs"}}]
        parsed = self.decision(route="dev-docs")
        mismatch = {
            "samples": [
                {
                    **self.sample("case", 1, 1.0, 1.0, 100),
                    "parsed": parsed,
                    "raw_text": json.dumps(self.decision(route="none")),
                    "raw_stdout": self.pi_stdout(json.dumps(self.decision(route="none"))),
                }
            ]
        }
        with self.assertRaisesRegex(ValueError, "does not match raw_stdout"):
            RUNNER.rescore_result(mismatch, cases)

        sticky = {
            "samples": [
                {
                    **self.sample("case", 1, 0.0, 1.0, 100),
                    "parsed": None,
                    "parse_error": "assistant output does not contain a JSON object",
                    "raw_text": "not-json",
                    "raw_stdout": self.pi_stdout("not-json"),
                }
            ]
        }
        normalized = RUNNER.rescore_result(sticky, cases)
        self.assertEqual(normalized["samples"][0]["parse_error"], "assistant output does not contain a JSON object")
        self.assertEqual(normalized["samples"][0]["score"], 0.0)

        no_event_sample = {
            **self.sample("case", 1, 0.0, 1.0, 100),
            "parsed": None,
            "parse_error": "Pi JSONL did not contain a final assistant message",
            "raw_text": "",
            "raw_stdout": "",
        }
        with self.assertRaisesRegex(ValueError, "provider exists without a parsed Pi event"):
            RUNNER.rescore_result({"samples": [no_event_sample]}, cases)
        no_event_sample["provider"] = None
        no_event_sample["model"] = None
        no_event_sample["stop_reason"] = None
        no_event_sample["usage"] = {"total_tokens": 0}
        no_event_sample["tool_names"] = []
        no_event_sample["event_count"] = 0
        no_event = RUNNER.rescore_result({"samples": [no_event_sample]}, cases)
        self.assertEqual(no_event["samples"][0]["score"], 0.0)

    def test_combine_results_uses_all_samples(self) -> None:
        cases = [{"id": "case", "critical": False}]
        first = self.result(behavior=1.0, critical=[], p50=1, p95=1, tokens=100)
        rerun = self.result(behavior=1.0, critical=[], p50=2, p95=2, tokens=120)
        first["samples"] = [self.sample("case", 1, 1.0, 1.0, 100)]
        rerun["samples"] = [self.sample("case", 1, 0.5, 2.0, 120)]
        combined = RUNNER.combine_results(first, rerun, cases)
        self.assertEqual(combined["summary"]["case_scores"]["case"], 0.5)
        self.assertEqual(combined["summary"]["sample_count"], 2)

    def test_combine_results_replaces_infrastructure_failures(self) -> None:
        cases = [{"id": "case", "critical": False}]
        first = self.result(behavior=0.0, critical=[], p50=1, p95=1, tokens=100)
        failed_sample = self.sample("case", 1, 0.0, 1.0, 100)
        failed_sample["infrastructure_error"] = True
        failed_sample["provider"] = "cpa"
        failed_sample["model"] = "glm-5.2"
        first["samples"] = [failed_sample]
        rerun = self.result(behavior=1.0, critical=[], p50=2, p95=2, tokens=120)
        rerun["samples"] = [self.sample("case", 1, 1.0, 2.0, 120)]
        combined = RUNNER.combine_results(first, rerun, cases, replace_infrastructure_errors=True)
        self.assertEqual(combined["summary"]["infrastructure_error_count"], 0)
        self.assertEqual(combined["summary"]["sample_count"], 1)

        mixed_sample = self.sample("case", 1, 0.0, 1.0, 100)
        mixed_sample["infrastructure_error"] = True
        mixed_sample["forbidden_tools"] = ["bash"]
        first["samples"] = [mixed_sample]
        sticky = RUNNER.combine_results(first, rerun, cases, replace_infrastructure_errors=True)
        self.assertEqual(sticky["summary"]["infrastructure_error_count"], 1)
        self.assertEqual(sticky["summary"]["forbidden_tool_calls"], 1)
        self.assertEqual(sticky["summary"]["sample_count"], 2)

        parse_sample = self.sample("case", 1, 0.0, 1.0, 100)
        parse_sample["infrastructure_error"] = True
        parse_sample["parse_error"] = "assistant output must contain exactly these fields"
        first["samples"] = [parse_sample]
        parse_sticky = RUNNER.combine_results(first, rerun, cases, replace_infrastructure_errors=True)

        null_mismatch = self.sample("case", 1, 0.0, 1.0, 100)
        null_mismatch["infrastructure_error"] = True
        null_mismatch["provider"] = "cpa"
        null_mismatch["model"] = "glm-5.2"
        null_mismatch["mismatches"] = {"route": {"expected": "none", "actual": None}}
        first["samples"] = [null_mismatch]
        mismatch_sticky = RUNNER.combine_results(first, rerun, cases, replace_infrastructure_errors=True)
        self.assertEqual(mismatch_sticky["summary"]["infrastructure_error_count"], 1)
        self.assertEqual(mismatch_sticky["summary"]["sample_count"], 2)
        self.assertEqual(parse_sticky["summary"]["parse_error_count"], 1)
        self.assertEqual(parse_sticky["summary"]["sample_count"], 2)

    def test_summarize_uses_worst_repeat_per_case(self) -> None:
        cases = [
            {"id": "critical", "critical": True},
            {"id": "normal", "critical": False},
        ]
        samples = [
            self.sample("critical", 1, 1.0, 1.0, 100),
            self.sample("critical", 2, 0.5, 3.0, 120),
            self.sample("normal", 1, 1.0, 2.0, 110),
            self.sample("normal", 2, 1.0, 4.0, 130),
        ]
        summary = RUNNER.summarize_run(cases, samples)
        self.assertEqual(summary["case_scores"], {"critical": 0.5, "normal": 1.0})
        self.assertEqual(summary["behavior_score"], 0.75)
        self.assertEqual(summary["critical_failures"], ["critical"])
        self.assertEqual(summary["performance"]["wall_p50_seconds"], 2.5)
        self.assertEqual(summary["performance"]["wall_p95_seconds"], 4.0)
        self.assertEqual(summary["performance"]["average_total_tokens"], 115.0)

    def test_compare_runs_enforces_behavior_and_performance(self) -> None:
        baseline = self.result(behavior=0.8, critical=[], p50=10, p95=20, tokens=100)
        candidate = self.result(behavior=0.9, critical=[], p50=10.5, p95=23, tokens=110)
        comparison = RUNNER.compare_runs(baseline, candidate)
        self.assertTrue(comparison["passed"])

        candidate["summary"]["performance"]["wall_p95_seconds"] = 25
        failed = RUNNER.compare_runs(baseline, candidate)
        self.assertFalse(failed["passed"])
        self.assertTrue(any("wall_p95_seconds" in item for item in failed["failures"]))

        candidate = self.result(behavior=0.9, critical=[], p50=10.5, p95=23, tokens=110)
        candidate["config"]["pi_version"] = "different"
        protocol_failure = RUNNER.compare_runs(baseline, candidate)
        self.assertFalse(protocol_failure["passed"])
        self.assertIn("config.pi_version differs", protocol_failure["failures"])

        unbound_baseline = self.result(behavior=0.8, critical=[], p50=10, p95=20, tokens=100)
        unbound_baseline["manifest"] = None
        manifest_failure = RUNNER.compare_runs(unbound_baseline, self.result(behavior=0.9, critical=[], p50=10.5, p95=23, tokens=110))
        self.assertFalse(manifest_failure["passed"])
        self.assertIn("baseline is not bound to a verified snapshot manifest", manifest_failure["failures"])

        parse_failure_candidate = self.result(behavior=1.0, critical=[], p50=10.5, p95=23, tokens=110)
        parse_failure_candidate["summary"]["parse_error_count"] = 1
        parse_failure = RUNNER.compare_runs(baseline, parse_failure_candidate)
        self.assertFalse(parse_failure["passed"])
        self.assertIn("candidate had 1 parse errors", parse_failure["failures"])

        model_failure_candidate = self.result(behavior=1.0, critical=[], p50=10.5, p95=23, tokens=110)
        model_failure_candidate["samples"] = [{"case_id": "case", "provider": None, "model": None}]
        model_failure = RUNNER.compare_runs(baseline, model_failure_candidate)
        self.assertFalse(model_failure["passed"])
        self.assertTrue(any("used provider None" in item for item in model_failure["failures"]))

    def test_validate_canonical_result_checks_sample_order(self) -> None:
        cases = [{"id": "case", "critical": True, "prompt": "prompt", "expected": {"route": "none"}}]
        result = self.result(behavior=1.0, critical=[], p50=1, p95=1, tokens=100)
        first_sample = self.sample("case", 1, 1.0, 1.0, 100)
        first_sample["parsed"] = {"route": "none"}
        second_sample = self.sample("case", 2, 1.0, 1.0, 100)
        second_sample["parsed"] = {"route": "none"}
        result["samples"] = [first_sample, second_sample]
        RUNNER.validate_canonical_result(result, cases, "same", "candidate")
        result["config"]["repeat"] = 1
        with self.assertRaisesRegex(ValueError, "non-canonical config.repeat"):
            RUNNER.validate_canonical_result(result, cases, "same", "candidate")
        result["config"]["repeat"] = 2
        with self.assertRaisesRegex(ValueError, "corpus_sha256"):
            RUNNER.validate_canonical_result(result, cases, "other", "candidate")
        result["kind"] = "baseline"
        with self.assertRaisesRegex(ValueError, "does not match expected"):
            RUNNER.validate_canonical_result(result, cases, "same", "candidate")

    def test_load_cases_rejects_noncanonical_schema(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "cases.json"
            data = {
                "schema_version": 1,
                "output_fields": list(RUNNER.DECISION_FIELD_ORDER),
                "cases": [{"id": "case", "critical": True, "prompt": "prompt", "expected": {"fresh_claim": False}}],
            }
            path.write_text(json.dumps(data), encoding="utf-8")
            RUNNER.load_cases(path)
            data["output_fields"] = ["route"]
            with self.assertRaisesRegex(ValueError, "canonical corpus identity"):
                RUNNER.load_canonical_corpus(path)
            path.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "canonical decision fields"):
                RUNNER.load_cases(path)

    def test_included_files_rejects_symlinks(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for relative in RUNNER.SKILL_PATHS:
                directory = root / relative
                directory.mkdir(parents=True)
                (directory / "SKILL.md").write_text("skill\n", encoding="utf-8")
            link = root / RUNNER.SKILL_PATHS[0] / "linked.md"
            link.symlink_to("SKILL.md")
            with self.assertRaisesRegex(ValueError, "symlinks are not allowed"):
                RUNNER.included_files(root)

    def test_manifest_verification_detects_changes(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for relative in RUNNER.SKILL_PATHS:
                directory = root / relative
                directory.mkdir(parents=True)
                (directory / "SKILL.md").write_text(f"name: {relative.name}\n", encoding="utf-8")
            files = RUNNER.included_files(root)
            manifest = {
                "schema_version": 1,
                "tree_sha256": RUNNER.aggregate_file_hash(files),
                "files": files,
            }
            manifest_path = root / "manifest.json"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            ok, _ = RUNNER.verify_manifest(root, manifest_path)
            self.assertTrue(ok)
            manifest_sha = RUNNER.sha256_file(manifest_path)
            baseline = {
                "input_root": str(root),
                "skill_tree_sha256": manifest["tree_sha256"],
                "manifest": {
                    "verified": True,
                    "sha256": manifest_sha,
                    "tree_sha256": manifest["tree_sha256"],
                },
            }
            bound = RUNNER.bind_manifest(baseline, manifest_path)
            self.assertTrue(bound["manifest"]["verified"])
            (root / RUNNER.SKILL_PATHS[0] / "SKILL.md").write_text("changed\n", encoding="utf-8")
            ok, result = RUNNER.verify_manifest(root, manifest_path)
            self.assertFalse(ok)
            self.assertEqual(result["changed"], ["skills/dev-docs/SKILL.md"])
            forged = {"schema_version": 1, "tree_sha256": manifest["tree_sha256"], "files": {}}
            manifest_path.write_text(json.dumps(forged), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "does not match manifest"):
                RUNNER.bind_manifest(baseline, manifest_path)

    @staticmethod
    def pi_stdout(text: str) -> str:
        events = [
            {"type": "tool_execution_start", "toolName": "read"},
            {"type": "tool_execution_start", "toolName": "read"},
            {
                "type": "message_end",
                "message": {
                    "role": "assistant",
                    "content": [{"type": "text", "text": text}],
                    "provider": "cpa",
                    "model": "glm-5.2",
                    "stopReason": "stop",
                    "usage": {"input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0, "totalTokens": 100},
                },
            },
        ]
        return "\n".join(json.dumps(event) for event in events)

    @staticmethod
    def decision(**overrides: object) -> dict:
        value = {
            "route": "dev-docs",
            "mode": "not-applicable",
            "consumer_test": False,
            "coverage_candidate": False,
            "requires_scan_before_record": False,
            "write_long_term_docs": True,
            "redact_sensitive": False,
            "fresh_claim": False,
            "reason": "reason",
        }
        value.update(overrides)
        return value

    @staticmethod
    def sample(case_id: str, repeat: int, score: float, wall: float, tokens: int) -> dict:
        return {
            "case_id": case_id,
            "repeat": repeat,
            "score": score,
            "provider": "cpa",
            "model": "glm-5.2",
            "stop_reason": "stop",
            "exit_code": 0,
            "timed_out": False,
            "parse_error": None,
            "wall_seconds": wall,
            "usage": {"input": 0, "output": 0, "cache_read": 0, "cache_write": 0, "total_tokens": tokens},
            "tool_names": ["read", "read"],
            "forbidden_tools": [],
            "event_count": 3,
            "infrastructure_error": False,
        }

    @staticmethod
    def result(*, behavior: float, critical: list[str], p50: float, p95: float, tokens: float) -> dict:
        files = RUNNER.included_files(Path.cwd())
        tree = RUNNER.aggregate_file_hash(files)
        return {
            "schema_version": 1,
            "protocol_version": 1,
            "kind": "candidate",
            "corpus_sha256": "same",
            "input_root": str(Path.cwd()),
            "skill_tree_sha256": tree,
            "skill_files": files,
            "input_tree_sha256_before": tree,
            "input_tree_sha256_after": tree,
            "manifest": {"verified": True, "tree_sha256": tree},
            "config": {
                "pi_version": "0.75.5",
                "model": "cpa/glm-5.2",
                "thinking": "low",
                "timeout_seconds": 120.0,
                "warmup": 2,
                "repeat": 2,
                "tools": ["read"],
            },
            "samples": [],
            "summary": {
                "behavior_score": behavior,
                "critical_failures": critical,
                "forbidden_tool_calls": 0,
                "safety_invariant_failures": 0,
                "nonzero_exit_count": 0,
                "timeout_count": 0,
                "parse_error_count": 0,
                "infrastructure_error_count": 0,
                "performance": {
                    "wall_p50_seconds": p50,
                    "wall_p95_seconds": p95,
                    "average_total_tokens": tokens,
                    "average_tool_calls": 2.0,
                },
            },
        }


if __name__ == "__main__":
    unittest.main()
