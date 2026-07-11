#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name("bundle_status.py")


class BundleStatusTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        self.outside = self.root / "outside"
        self.outside.mkdir()
        subprocess.run(["git", "init", "-q", str(self.repo)], check=True)
        subprocess.run(["git", "-C", str(self.repo), "config", "user.email", "test@example.com"], check=True)
        subprocess.run(["git", "-C", str(self.repo), "config", "user.name", "Test"], check=True)
        (self.repo / "docs").mkdir()
        (self.repo / "src").mkdir()
        (self.repo / "docs" / "index.md").write_text(
            """---
okf_version: "0.1"
freshness:
  default_strategy: source-change-and-periodic
  default_target: P90D
---
# Knowledge Bundle

- [Architecture](architecture.md)
""",
            encoding="utf-8",
        )
        (self.repo / "src" / "app.py").write_text("VALUE = 1\n", encoding="utf-8")
        (self.repo / "docs" / "architecture.md").write_text(
            """---
type: Architecture
title: Architecture
description: Current structure.
scope:
  - src/**
sources:
  - src/app.py
verification:
  strategy: source-change-and-periodic
  target: P90D
---

# Overview

Current structure.
""",
            encoding="utf-8",
        )
        subprocess.run(["git", "-C", str(self.repo), "add", "."], check=True)
        subprocess.run(["git", "-C", str(self.repo), "commit", "-qm", "initial"], check=True)
        self.registry = self.repo / "docs" / ".okf" / "verification.json"
        self.lock_path = self.registry.with_name(self.registry.name + ".lock")

    def tearDown(self) -> None:
        self.temp.cleanup()

    def run_json(
        self,
        *args: str,
        check: bool = True,
        now: str = "2026-07-10T00:00:00Z",
    ) -> dict:
        proc = subprocess.run(
            ["python3", str(SCRIPT), *args, "--repo", str(self.repo), "--now", now],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=check,
        )
        if not check and proc.returncode != 0:
            return {"returncode": proc.returncode, "stderr": proc.stderr}
        return json.loads(proc.stdout)

    def scan(self, *extra: str, now: str = "2026-07-10T00:00:00Z") -> dict:
        return self.run_json("scan", *extra, now=now)

    def record_as(
        self,
        method: str,
        *extra: str,
        check: bool = True,
        now: str = "2026-07-10T00:00:00Z",
    ) -> dict:
        return self.run_json(
            "record",
            "--concept",
            "docs/architecture.md",
            "--method",
            method,
            *extra,
            check=check,
            now=now,
        )

    def record_concept(
        self,
        concept: str,
        method: str = "semantic",
        *extra: str,
        check: bool = True,
    ) -> dict:
        return self.run_json(
            "record",
            "--concept",
            concept,
            "--method",
            method,
            *extra,
            check=check,
        )

    def report_concept(self, report: dict, path: str) -> dict:
        concepts = report.get("concepts") or report["queue"]
        return next(item for item in concepts if item["path"] == path)

    def record(self, *extra: str, check: bool = True) -> dict:
        return self.record_as("semantic", *extra, check=check)

    def assert_record_rejected(self, expected: str) -> None:
        result = self.record(check=False)
        self.assertEqual(result["returncode"], 2)
        self.assertIn(expected, result["stderr"])
        self.assertFalse(self.registry.exists())

    def test_new_concept_is_unverified(self) -> None:
        report = self.scan()
        self.assertEqual(report["queue"][0]["freshness"], "unverified")
        self.assertEqual(report["summary"]["states"]["unverified"], 1)

    def test_record_then_fresh(self) -> None:
        result = self.record(
            "--evidence",
            "human-review",
            "--evidence",
            "automated-test",
            "--evidence",
            "external-audit",
        )
        self.assertEqual(result["recorded"][0]["concept_id"], "architecture")
        report = self.scan("--include-fresh")
        concept = report["concepts"][0]
        self.assertEqual(concept["freshness"], "fresh")
        self.assertEqual(concept["verification_method"], "semantic")
        self.assertTrue(self.registry.exists())
        self.assertEqual(
            json.loads(self.registry.read_text(encoding="utf-8"))["concepts"]["architecture"]["evidence"],
            ["automated-test", "external-audit", "human-review"],
        )
        self.assertTrue(self.lock_path.exists())

    def test_evidence_is_controlled_and_credentials_never_persist(self) -> None:
        rejected_values = {
            "freeform-label": "payment-contract-reviewed",
            "github-classic-token": "ghp_abcdefghijklmnopqrstuvwxyz0123456789",
            "github-fine-grained-token": "github_pat_abcdefghijklmnopqrstuvwxyz0123456789",
            "slack-token": "xoxb-1234567890-abcdefghijklmnopqrstuvwxyz",
            "stripe-secret": "sk_live_abcdefghijklmnopqrstuvwxyz0123456789",
        }
        for kind, value in rejected_values.items():
            with self.subTest(kind=kind):
                result = self.record("--evidence", value, check=False)
                self.assertEqual(result["returncode"], 2)
                self.assertIn("invalid choice", result["stderr"])
                self.assertFalse(self.registry.exists())

    def test_source_change_marks_dirty(self) -> None:
        self.record()
        (self.repo / "src" / "app.py").write_text("VALUE = 2\n", encoding="utf-8")
        report = self.scan()
        item = report["queue"][0]
        self.assertEqual(item["freshness"], "dirty")
        self.assertIn("src/app.py", item["changed_sources"])
        self.assertFalse(item["document_changed"])

    def test_document_change_marks_dirty(self) -> None:
        self.record()
        path = self.repo / "docs" / "architecture.md"
        path.write_text(path.read_text(encoding="utf-8") + "\nMore detail.\n", encoding="utf-8")
        report = self.scan()
        item = report["queue"][0]
        self.assertEqual(item["freshness"], "dirty")
        self.assertTrue(item["document_changed"])

    def test_due_is_not_priority(self) -> None:
        self.record()
        report = self.scan(now="2027-01-10T00:00:00Z")
        item = report["queue"][0]
        self.assertEqual(item["freshness"], "due")
        self.assertNotIn("priority", item)

    def test_nonperiodic_strategies_ignore_targets_for_due(self) -> None:
        path = self.repo / "docs" / "architecture.md"
        original = path.read_text(encoding="utf-8")
        for strategy in ("historical", "source-change"):
            with self.subTest(strategy=strategy):
                path.write_text(
                    original.replace("source-change-and-periodic", strategy),
                    encoding="utf-8",
                )
                self.record()
                report = self.scan(now="2027-01-10T00:00:00Z")
                self.assertEqual(report["queue"], [])
                fresh = self.scan("--include-fresh", now="2027-01-10T00:00:00Z")
                self.assertEqual(fresh["concepts"][0]["freshness"], "fresh")


    def test_periodic_and_historical_ignore_source_changes_before_due(self) -> None:
        document = self.repo / "docs" / "architecture.md"
        original_document = document.read_text(encoding="utf-8")
        source = self.repo / "src" / "app.py"
        for strategy in ("periodic", "historical"):
            with self.subTest(strategy=strategy):
                document.write_text(
                    original_document.replace("source-change-and-periodic", strategy),
                    encoding="utf-8",
                )
                source.write_text("VALUE = 1\n", encoding="utf-8")
                self.record()
                source.write_text("VALUE = 2\n", encoding="utf-8")

                report = self.scan("--include-fresh")

                concept = report["concepts"][0]
                self.assertEqual(concept["freshness"], "fresh")
                self.assertEqual(concept["changed_sources"], [])
                self.assertEqual(report["summary"]["source_changes"], 0)

    def test_record_after_changes_converges_to_fresh(self) -> None:
        self.record()
        (self.repo / "src" / "app.py").write_text("VALUE = 2\n", encoding="utf-8")
        doc = self.repo / "docs" / "architecture.md"
        doc.write_text(doc.read_text(encoding="utf-8") + "\nUpdated behavior.\n", encoding="utf-8")
        dirty = self.scan()
        self.assertEqual(dirty["queue"][0]["freshness"], "dirty")
        self.record("--evidence", "human-review")
        fresh = self.scan("--include-fresh")
        self.assertEqual(fresh["concepts"][0]["freshness"], "fresh")

    def test_missing_source_blocks_and_record_refuses(self) -> None:
        path = self.repo / "docs" / "architecture.md"
        text = path.read_text(encoding="utf-8").replace("src/app.py", "src/missing.py")
        path.write_text(text, encoding="utf-8")
        report = self.scan()
        self.assertEqual(report["queue"][0]["freshness"], "blocked")
        self.assert_record_rejected("missing sources")

    def test_batch_record_is_atomic_when_a_concept_is_blocked(self) -> None:
        architecture = (self.repo / "docs" / "architecture.md").read_text(encoding="utf-8")
        (self.repo / "docs" / "secondary.md").write_text(
            architecture.replace("src/app.py", "src/missing.py"), encoding="utf-8"
        )

        result = self.run_json(
            "record",
            "--concept",
            "docs/architecture.md",
            "--concept",
            "docs/secondary.md",
            "--method",
            "semantic",
            check=False,
        )

        self.assertEqual(result["returncode"], 2)
        self.assertIn("missing sources", result["stderr"])
        self.assertFalse(self.registry.exists())

    def test_broken_link_blocks_and_record_refuses(self) -> None:
        path = self.repo / "docs" / "architecture.md"
        path.write_text(path.read_text(encoding="utf-8") + "\n[Missing](missing.md)\n", encoding="utf-8")
        report = self.scan()
        self.assertIn("missing.md", report["queue"][0]["broken_links"])
        self.assert_record_rejected("broken links")

    def test_blocking_metadata_prevents_record_without_ledger(self) -> None:
        path = self.repo / "docs" / "architecture.md"
        original = path.read_text(encoding="utf-8")
        cases = [
            (
                "unsupported-strategy",
                original.replace("strategy: source-change-and-periodic", "strategy: unsupported"),
            ),
            ("unsupported-target", original.replace("target: P90D", "target: P90M")),
            (
                "no-local-sources",
                original.replace(
                    "scope:\n  - src/**\nsources:\n  - src/app.py",
                    "scope: []\nsources: []",
                ),
            ),
        ]
        for expected, content in cases:
            with self.subTest(metadata_issue=expected):
                path.write_text(content, encoding="utf-8")
                self.assert_record_rejected(expected)


    def test_explicit_wrong_metadata_types_block_record(self) -> None:
        path = self.repo / "docs" / "architecture.md"
        original = path.read_text(encoding="utf-8")
        cases = [
            (
                "invalid-verification",
                original.replace(
                    "verification:\n  strategy: source-change-and-periodic\n  target: P90D",
                    "verification: []",
                ),
            ),
            (
                "invalid-scope",
                original.replace("scope:\n  - src/**", "scope: src/**"),
            ),
            (
                "invalid-sources",
                original.replace("sources:\n  - src/app.py", "sources: src/app.py"),
            ),
        ]
        for expected, content in cases:
            with self.subTest(metadata_issue=expected):
                path.write_text(content, encoding="utf-8")
                report = self.scan()
                concept = report["queue"][0]
                self.assertEqual(concept["freshness"], "blocked")
                self.assertIn(expected, concept["metadata_issues"])
                self.assert_record_rejected(expected)

    def test_verification_null_is_invalid_but_empty_mapping_inherits_policy(self) -> None:
        path = self.repo / "docs" / "architecture.md"
        original = path.read_text(encoding="utf-8")
        verification_block = "verification:\n  strategy: source-change-and-periodic\n  target: P90D"

        path.write_text(original.replace(verification_block, "verification:"), encoding="utf-8")
        null_verification = self.scan()
        null_concept = null_verification["queue"][0]
        self.assertEqual(null_concept["freshness"], "blocked")
        self.assertIn("invalid-verification", null_concept["metadata_issues"])
        self.assert_record_rejected("invalid-verification")

        for kind, replacement in (("absent", ""), ("empty-mapping", "verification: {}")):
            with self.subTest(kind=kind):
                path.write_text(original.replace(verification_block, replacement), encoding="utf-8")
                report = self.scan("--include-fresh")
                concept = report["concepts"][0]
                self.assertEqual(concept["freshness"], "unverified")
                self.assertEqual(concept["strategy"], "source-change-and-periodic")
                self.assertEqual(concept["target"], "P90D")
                self.assertNotIn("invalid-verification", concept["metadata_issues"])

        path.write_text(original.replace(verification_block, "verification: {}"), encoding="utf-8")
        self.assertEqual(self.record()["recorded"][0]["concept_id"], "architecture")
        self.assertEqual(self.scan("--include-fresh")["concepts"][0]["freshness"], "fresh")

    def test_complete_record_recovers_incomplete_ledger(self) -> None:
        self.registry.parent.mkdir()
        self.registry.write_text(
            json.dumps(
                {
                    "schema_version": "1.0",
                    "updated_at": None,
                    "head": None,
                    "concepts": {"architecture": {"path": "docs/architecture.md"}},
                }
            ),
            encoding="utf-8",
        )
        blocked = self.scan()
        self.assertIn("incomplete-verification-record", blocked["queue"][0]["metadata_issues"])

        result = self.record()

        self.assertEqual(result["recorded"][0]["concept_id"], "architecture")
        report = self.scan("--include-fresh")
        concept = report["concepts"][0]
        self.assertEqual(concept["freshness"], "fresh")
        self.assertNotIn("incomplete-verification-record", concept["metadata_issues"])
        self.assertTrue(self.lock_path.exists())

    def test_malformed_concept_records_are_blocked_and_recoverable(self) -> None:
        self.record()
        ledger = json.loads(self.registry.read_text(encoding="utf-8"))
        entry = ledger["concepts"]["architecture"]
        missing_method = {key: value for key, value in entry.items() if key != "method"}
        cases = [
            ("non-dict", ["not", "a", "record"]),
            ("missing-required-field", missing_method),
            ("invalid-method", {**entry, "method": "format-only"}),
            ("invalid-method-list", {**entry, "method": ["semantic"]}),
            ("invalid-method-mapping", {**entry, "method": {"name": "semantic"}}),
            ("invalid-path", {**entry, "path": "docs/other.md"}),
            ("invalid-type", {**entry, "type": "Other"}),
            ("invalid-verified-at", {**entry, "verified_at": "not-a-timestamp"}),
            ("invalid-sources-mapping", {**entry, "sources": []}),
            (
                "invalid-source-path",
                {
                    **entry,
                    "sources": {"https://example.test/source": next(iter(entry["sources"].values()))},
                },
            ),
            (
                "invalid-source-hash",
                {**entry, "sources": {"src/app.py": "sha256:not-a-hash"}},
            ),
            (
                "inconsistent-source-fingerprint",
                {**entry, "source_fingerprint": "sha256:" + "0" * 64},
            ),
        ]
        for kind, corrupted in cases:
            with self.subTest(kind=kind):
                ledger["concepts"]["architecture"] = corrupted
                self.registry.write_text(json.dumps(ledger), encoding="utf-8")
                report = self.scan()
                concept = report["queue"][0]
                self.assertEqual(concept["freshness"], "blocked")
                self.assertIn("incomplete-verification-record", concept["metadata_issues"])

        result = self.record()
        self.assertEqual(result["recorded"][0]["concept_id"], "architecture")
        self.assertEqual(self.scan("--include-fresh")["concepts"][0]["freshness"], "fresh")

    def test_root_corrupt_registry_blocks_every_concept_and_refuses_record(self) -> None:
        architecture = (self.repo / "docs" / "architecture.md").read_text(encoding="utf-8")
        (self.repo / "docs" / "secondary.md").write_text(architecture, encoding="utf-8")
        cases = {
            "malformed-json": ("{", "cannot parse verification registry"),
            "invalid-concepts-container": (
                json.dumps({"schema_version": "1.0", "concepts": []}),
                "must contain an object field named concepts",
            ),
            "unsupported-schema-version": (
                json.dumps(
                    {"schema_version": "9.9", "updated_at": None, "head": None, "concepts": {}}
                ),
                "unsupported schema_version",
            ),
            "missing-updated-at": (
                json.dumps({"schema_version": "1.0", "head": None, "concepts": {}}),
                "invalid updated_at value",
            ),
        }
        self.registry.parent.mkdir()
        for kind, (corrupted, message) in cases.items():
            with self.subTest(kind=kind):
                self.registry.write_text(corrupted, encoding="utf-8")
                report = self.scan("--include-fresh")

                self.assertEqual({item["freshness"] for item in report["concepts"]}, {"blocked"})
                for concept in report["concepts"]:
                    self.assertIn("invalid-verification-registry", concept["metadata_issues"])
                    self.assertIn("incomplete-verification-record", concept["metadata_issues"])
                self.assertIn(
                    "invalid-verification-registry",
                    {issue["code"] for issue in report["bundle_issues"]},
                )

                rejected = self.record(check=False)
                self.assertEqual(rejected["returncode"], 2)
                self.assertIn(message, rejected["stderr"])
                self.assertEqual(self.registry.read_text(encoding="utf-8"), corrupted)

    def test_continuity_requires_an_unchanged_complete_record(self) -> None:
        unverified = self.record_as("continuity", check=False)
        self.assertEqual(unverified["returncode"], 2)
        self.assertIn("continuity requires", unverified["stderr"])

        document = self.repo / "docs" / "architecture.md"
        original_document = document.read_text(encoding="utf-8")
        source = self.repo / "src" / "app.py"
        original_source = source.read_text(encoding="utf-8")
        self.record()
        self.assertEqual(self.record_as("continuity")["recorded"][0]["method"], "continuity")

        document.write_text(original_document + "\nChanged.\n", encoding="utf-8")
        self.assertEqual(self.scan()["queue"][0]["freshness"], "dirty")
        dirty_document = self.record_as("continuity", check=False)
        self.assertEqual(dirty_document["returncode"], 2)
        self.assertIn("continuity requires", dirty_document["stderr"])
        document.write_text(original_document, encoding="utf-8")

        source.write_text("VALUE = 2\n", encoding="utf-8")
        changed_source = self.scan()["queue"][0]
        self.assertEqual(changed_source["freshness"], "dirty")
        self.assertIn("src/app.py", changed_source["changed_sources"])
        dirty_source = self.record_as("continuity", check=False)
        self.assertEqual(dirty_source["returncode"], 2)
        self.assertIn("continuity requires", dirty_source["stderr"])
        source.write_text(original_source, encoding="utf-8")

        ledger = json.loads(self.registry.read_text(encoding="utf-8"))
        ledger["concepts"]["architecture"].pop("method")
        self.registry.write_text(json.dumps(ledger), encoding="utf-8")
        self.assertEqual(self.scan()["queue"][0]["freshness"], "blocked")
        corrupt = self.record_as("continuity", check=False)
        self.assertEqual(corrupt["returncode"], 2)
        self.assertIn("continuity requires", corrupt["stderr"])

        self.record()
        ledger = json.loads(self.registry.read_text(encoding="utf-8"))
        ledger["concepts"]["architecture"]["verified_at"] = "2026-01-01T00:00:00Z"
        self.registry.write_text(json.dumps(ledger), encoding="utf-8")
        self.assertEqual(self.scan(now="2027-01-10T00:00:00Z")["queue"][0]["freshness"], "due")
        due = self.record_as("continuity", now="2027-01-10T00:00:00Z")
        self.assertEqual(due["recorded"][0]["method"], "continuity")

    def test_structural_finding_prevents_freshness_ready(self) -> None:
        self.record()
        document = self.repo / "docs" / "architecture.md"
        document.write_text(
            document.read_text(encoding="utf-8") + "\n[Missing](missing.md)\n",
            encoding="utf-8",
        )
        ledger = json.loads(self.registry.read_text(encoding="utf-8"))
        document_hash = hashlib.sha256(document.read_bytes()).hexdigest()
        ledger["concepts"]["architecture"]["document_hash"] = f"sha256:{document_hash}"
        self.registry.write_text(json.dumps(ledger), encoding="utf-8")

        report = self.scan("--include-fresh")

        self.assertEqual(report["concepts"][0]["freshness"], "fresh")
        self.assertEqual(report["summary"]["structural_findings"], 1)
        self.assertFalse(report["summary"]["freshness_ready"])

    def test_stale_lock_file_does_not_block_record(self) -> None:
        self.lock_path.parent.mkdir()
        self.lock_path.write_text("interrupted holder\n", encoding="utf-8")

        result = self.record()

        self.assertEqual(result["recorded"][0]["concept_id"], "architecture")
        self.assertTrue(self.lock_path.exists())

    def test_live_advisory_lock_blocks_then_releases_after_process_kill(self) -> None:
        holder_code = (
            "import importlib.util, pathlib, sys, time\n"
            "spec = importlib.util.spec_from_file_location('bundle_status_holder', sys.argv[1])\n"
            "module = importlib.util.module_from_spec(spec)\n"
            "sys.modules[spec.name] = module\n"
            "spec.loader.exec_module(module)\n"
            "with module.VerificationRegistryLock(pathlib.Path(sys.argv[2])):\n"
            "    print('locked', flush=True)\n"
            "    time.sleep(60)\n"
        )
        holder = subprocess.Popen(
            ["python3", "-c", holder_code, str(SCRIPT), str(self.repo / "docs")],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        try:
            self.assertEqual(holder.stdout.readline().strip(), "locked")
            blocked = self.record(check=False)
            self.assertEqual(blocked["returncode"], 2)
            self.assertIn("locked", blocked["stderr"])

            holder.kill()
            holder.wait(timeout=10)
            recovered = self.record()
            self.assertEqual(recovered["recorded"][0]["concept_id"], "architecture")
        finally:
            if holder.poll() is None:
                holder.kill()
                holder.wait(timeout=10)
            holder.stdout.close()
            holder.stderr.close()


    def test_invalid_frontmatter_blocks_scan_and_record(self) -> None:
        document = self.repo / "docs" / "architecture.md"
        original = document.read_text(encoding="utf-8")
        cases = {
            "bare-token": original.replace("title: Architecture", "title: Architecture\nbare-token"),
            "wrong-indentation": original.replace(
                "  strategy: source-change-and-periodic",
                "   strategy: source-change-and-periodic",
            ),
        }
        for name, content in cases.items():
            with self.subTest(name=name):
                document.write_text(content, encoding="utf-8")
                report = self.scan()
                concept = self.report_concept(report, "docs/architecture.md")
                self.assertEqual(concept["freshness"], "blocked")
                self.assertIn("invalid-frontmatter", concept["metadata_issues"])
                self.assert_record_rejected("invalid-frontmatter")

    def test_urls_in_mapping_values_and_list_items_parse(self) -> None:
        document = self.repo / "docs" / "architecture.md"
        original = document.read_text(encoding="utf-8")
        document.write_text(
            original.replace(
                "description: Current structure.",
                "description: https://example.test/architecture\n"
                "resources:\n"
                "  - resource: https://example.test/resource\n"
                "    description: https://example.test/description\n"
                "  - https://example.test/list-item",
            ),
            encoding="utf-8",
        )

        concept = self.report_concept(self.scan(), "docs/architecture.md")

        self.assertEqual(concept["freshness"], "unverified")
        self.assertNotIn("invalid-frontmatter", concept["metadata_issues"])

    def test_invalid_index_frontmatter_is_bundle_issue_and_blocks_record(self) -> None:
        index = self.repo / "docs" / "index.md"
        cases = {
            "missing": ("# Knowledge Bundle\n", "missing-index-frontmatter"),
            "parse-error": (
                "---\nfreshness:\n  default_strategy: source-change-and-periodic\nbare-token\n---\n",
                "invalid-index-frontmatter",
            ),
            "non-mapping": ("---\n- a scalar list item\n---\n", "invalid-index-frontmatter"),
        }
        for name, (content, expected) in cases.items():
            with self.subTest(name=name):
                index.write_text(content, encoding="utf-8")
                report = self.scan("--include-fresh")
                self.assertIn(expected, {issue["code"] for issue in report["bundle_issues"]})
                self.assert_record_rejected(expected)

    def test_index_symlinks_are_rejected_for_scan_and_record(self) -> None:
        index = self.repo / "docs" / "index.md"
        original = index.read_text(encoding="utf-8")
        external = self.outside / "index.md"
        external.write_text(original, encoding="utf-8")
        internal = self.repo / "docs" / ".okf" / "index-target.md"
        internal.parent.mkdir()
        internal.write_text(original, encoding="utf-8")
        for name, target in (("external", external), ("internal", internal)):
            with self.subTest(name=name):
                index.unlink()
                os.symlink(target, index)

                report = self.scan("--include-fresh")

                self.assertIn(
                    "invalid-index-symlink", {issue["code"] for issue in report["bundle_issues"]}
                )
                self.assert_record_rejected("invalid-index-symlink")
                self.assertEqual(target.read_text(encoding="utf-8"), original)

    def test_existing_and_conceptual_scopes_are_classified_correctly(self) -> None:
        document = self.repo / "docs" / "architecture.md"
        original = document.read_text(encoding="utf-8")
        makefile = self.repo / "Makefile"
        makefile.write_text("BUILD = 1\n", encoding="utf-8")
        source = self.repo / "src" / "app.py"
        for scope, tracked in (("Makefile", makefile), ("src", source)):
            with self.subTest(scope=scope):
                if self.registry.exists():
                    self.registry.unlink()
                document.write_text(
                    original.replace(
                        "scope:\n  - src/**\nsources:\n  - src/app.py",
                        f"scope:\n  - {scope}\nsources: []",
                    ),
                    encoding="utf-8",
                )
                unverified = self.report_concept(self.scan(), "docs/architecture.md")
                self.assertEqual(unverified["missing_sources"], [])
                self.record()
                tracked.write_text(f"changed {scope}\n", encoding="utf-8")
                self.assertEqual(self.report_concept(self.scan(), "docs/architecture.md")["freshness"], "dirty")

        if self.registry.exists():
            self.registry.unlink()
        document.write_text(
            original.replace(
                "scope:\n  - src/**\nsources:\n  - src/app.py",
                "scope:\n  - src/*.py\nsources: []",
            ),
            encoding="utf-8",
        )
        glob_scope = self.report_concept(self.scan(), "docs/architecture.md")
        self.assertEqual(glob_scope["missing_sources"], [])
        self.record()
        source.write_text("changed glob\n", encoding="utf-8")
        self.assertEqual(self.report_concept(self.scan(), "docs/architecture.md")["freshness"], "dirty")

        for scope in ("current deployment topology", "docs/workflow"):
            with self.subTest(conceptual_scope=scope):
                document.write_text(
                    original.replace(
                        "scope:\n  - src/**\nsources:\n  - src/app.py",
                        f"scope:\n  - {scope}\nsources:\n  - src/app.py",
                    ),
                    encoding="utf-8",
                )
                conceptual_scope = self.report_concept(self.scan(), "docs/architecture.md")
                self.assertEqual(conceptual_scope["missing_sources"], [])

    def test_unique_temp_ledger_save_ignores_symlink(self) -> None:
        self.registry.parent.mkdir()
        sentinel = self.outside / "sentinel.json"
        sentinel.write_text("unchanged", encoding="utf-8")
        fixed_temporary = self.registry.with_suffix(self.registry.suffix + ".tmp")
        os.symlink(sentinel, fixed_temporary)

        self.record()

        self.assertEqual(sentinel.read_text(encoding="utf-8"), "unchanged")
        self.assertTrue(fixed_temporary.is_symlink())
        self.assertTrue(self.registry.is_file())
        self.assertEqual(list(self.registry.parent.glob(".verification.json.*.tmp")), [])

    def test_output_replaces_symlink_without_touching_target(self) -> None:
        output = self.repo / "scan-report.json"
        sentinel = self.outside / "output-target.json"
        sentinel.write_text("unchanged", encoding="utf-8")
        os.symlink(sentinel, output)

        completed = subprocess.run(
            [
                "python3",
                str(SCRIPT),
                "scan",
                "--repo",
                str(self.repo),
                "--now",
                "2026-07-10T00:00:00Z",
                "--output",
                str(output),
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(completed.stdout, "")
        self.assertEqual(sentinel.read_text(encoding="utf-8"), "unchanged")
        self.assertFalse(output.is_symlink())
        self.assertEqual(json.loads(output.read_text(encoding="utf-8"))["schema_version"], "2.0")
        self.assertEqual(list(output.parent.glob(f".{output.name}.*.tmp")), [])

    def test_external_concept_symlink_is_reported_and_skipped(self) -> None:
        external = self.outside / "escape.md"
        external.write_text("# Outside bundle\n", encoding="utf-8")
        os.symlink(external, self.repo / "docs" / "escape.md")

        report = self.scan("--include-fresh")

        self.assertEqual(report["summary"]["concepts"], 1)
        self.assertIn(
            "invalid-concept-symlink", {issue["code"] for issue in report["bundle_issues"]}
        )
        strict = self.run_json("scan", "--strict", check=False)
        self.assertEqual(strict["returncode"], 1)

    def test_internal_concept_symlinks_are_reported_and_skipped(self) -> None:
        alias = self.repo / "docs" / "architecture-alias.md"
        directory = self.repo / "docs" / "concept-directory.md"
        directory.mkdir()
        directory_alias = self.repo / "docs" / "directory-alias.md"
        os.symlink(self.repo / "docs" / "architecture.md", alias)
        os.symlink(directory, directory_alias)

        report = self.scan("--include-fresh")

        self.assertEqual(report["summary"]["concepts"], 1)
        self.assertEqual([concept["path"] for concept in report["concepts"]], ["docs/architecture.md"])
        issue_paths = {
            issue["path"]
            for issue in report["bundle_issues"]
            if issue["code"] == "invalid-concept-symlink"
        }
        self.assertTrue({"docs/architecture-alias.md", "docs/directory-alias.md"}.issubset(issue_paths))
        rejected = self.record_concept("docs/architecture-alias.md", check=False)
        self.assertEqual(rejected["returncode"], 2)
        self.assertIn("symbolic link", rejected["stderr"])
        self.assertFalse(self.registry.exists())

    def test_external_okf_symlink_is_rejected_before_scan_or_record(self) -> None:
        outside_registry = self.outside / "verification.json"
        outside_registry.write_text("do not modify", encoding="utf-8")
        os.symlink(self.outside, self.registry.parent)

        scan = self.run_json("scan", check=False)
        record = self.record(check=False)

        self.assertEqual(scan["returncode"], 2)
        self.assertEqual(record["returncode"], 2)
        self.assertIn("symbolic link", scan["stderr"])
        self.assertEqual(outside_registry.read_text(encoding="utf-8"), "do not modify")

    def test_lock_symlink_is_rejected_without_writing_target(self) -> None:
        self.registry.parent.mkdir()
        sentinel = self.outside / "lock-target"
        sentinel.write_text("unchanged", encoding="utf-8")
        os.symlink(sentinel, self.lock_path)

        rejected = self.record(check=False)

        self.assertEqual(rejected["returncode"], 2)
        self.assertIn("symbolic link", rejected["stderr"])
        self.assertEqual(sentinel.read_text(encoding="utf-8"), "unchanged")
        self.assertFalse(self.registry.exists())

    def test_hardlink_registry_alias_uses_the_bundle_lock(self) -> None:
        self.record()
        alias = self.registry.with_name("verification-alias.json")
        os.link(self.registry, alias)
        self.assertTrue(os.path.samefile(self.registry, alias))
        holder_code = (
            "import importlib.util, pathlib, sys, time\n"
            "spec = importlib.util.spec_from_file_location('bundle_status_holder', sys.argv[1])\n"
            "module = importlib.util.module_from_spec(spec)\n"
            "sys.modules[spec.name] = module\n"
            "spec.loader.exec_module(module)\n"
            "with module.VerificationRegistryLock(pathlib.Path(sys.argv[2])):\n"
            "    print('locked', flush=True)\n"
            "    time.sleep(60)\n"
        )
        holder = subprocess.Popen(
            ["python3", "-c", holder_code, str(SCRIPT), str(self.repo / "docs")],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        try:
            self.assertEqual(holder.stdout.readline().strip(), "locked")
            blocked = self.record("--registry", "docs/.okf/verification-alias.json", check=False)
            self.assertEqual(blocked["returncode"], 2)
            self.assertIn("locked", blocked["stderr"])

            holder.kill()
            holder.wait(timeout=10)
            recovered = self.record("--registry", "docs/.okf/verification-alias.json")
            self.assertEqual(recovered["recorded"][0]["concept_id"], "architecture")
        finally:
            if holder.poll() is None:
                holder.kill()
                holder.wait(timeout=10)
            holder.stdout.close()
            holder.stderr.close()

    def test_historical_decision_acceptance_and_supersession(self) -> None:
        def write_decision(name: str, status: str, relation: str = "") -> None:
            (self.repo / "docs" / name).write_text(
                f"""---
type: Decision
title: {name}
description: Decision lifecycle.
scope:
  - decision lifecycle
sources:
  - src/app.py
verification:
  strategy: historical
  target: P90D
status: {status}
{relation}---

# {name}
""",
                encoding="utf-8",
            )

        write_decision("accepted.md", "accepted")
        write_decision("proposed.md", "proposed")
        report = self.scan("--include-fresh")
        for path in ("docs/accepted.md", "docs/proposed.md"):
            concept = self.report_concept(report, path)
            self.assertEqual(concept["freshness"], "unverified")
            self.assertNotIn("invalid-historical-status", concept["metadata_issues"])
        self.assertEqual(self.record_concept("docs/accepted.md")["recorded"][0]["concept_id"], "accepted")

        write_decision("old.md", "superseded", "superseded_by: new.md\n")
        write_decision("new.md", "accepted", "supersedes: old.md\n")
        report = self.scan("--include-fresh")
        old = self.report_concept(report, "docs/old.md")
        self.assertEqual(old["freshness"], "unverified")
        self.assertFalse(old["metadata_issues"])
        self.assertEqual(self.record_concept("docs/old.md")["recorded"][0]["concept_id"], "old")

    def test_decision_inherits_historical_rule_and_gates_invalid_lifecycle(self) -> None:
        index = self.repo / "docs" / "index.md"
        index.write_text(
            index.read_text(encoding="utf-8").replace(
                "  default_target: P90D\n",
                "  default_target: P90D\n"
                "  rules:\n"
                "    - type: Decision\n"
                "      strategy: historical\n",
            ),
            encoding="utf-8",
        )
        cases = {
            "invalid-status": ("status: retired", "invalid-historical-status"),
            "invalid-supersession": (
                "status: superseded\nsuperseded_by: missing.md",
                "missing-superseded-by",
            ),
        }
        for name, (lifecycle, expected) in cases.items():
            with self.subTest(name=name):
                path = self.repo / "docs" / f"{name}.md"
                path.write_text(
                    "\n".join(
                        [
                            "---",
                            "type: Decision",
                            f"title: {name}",
                            "description: Decision lifecycle.",
                            "scope:",
                            "  - decisions",
                            "sources:",
                            "  - src/app.py",
                            lifecycle,
                            "---",
                            "",
                            f"# {name}",
                            "",
                        ]
                    ),
                    encoding="utf-8",
                )

                concept = self.report_concept(self.scan("--include-fresh"), f"docs/{name}.md")

                self.assertEqual(concept["strategy"], "historical")
                self.assertEqual(concept["freshness"], "blocked")
                self.assertIn(expected, concept["metadata_issues"])
                rejected = self.record_concept(f"docs/{name}.md", check=False)
                self.assertEqual(rejected["returncode"], 2)
                self.assertIn(expected, rejected["stderr"])

    def test_invalid_historical_decision_lifecycle_blocks_record(self) -> None:
        old = self.repo / "docs" / "old.md"
        new = self.repo / "docs" / "new.md"
        old_base = """---
type: Decision
title: Old
description: Old Decision.
scope:
  - decisions
sources:
  - src/app.py
verification:
  strategy: historical
  target: P90D
status: superseded
superseded_by: new.md
---

# Old
"""
        new_base = """---
type: Decision
title: New
description: New Decision.
scope:
  - decisions
sources:
  - src/app.py
verification:
  strategy: historical
  target: P90D
status: accepted
supersedes: old.md
---

# New
"""
        os.symlink(new, self.repo / "docs" / "new-alias.md")
        cases = {
            "invalid-status": (
                old_base.replace("status: superseded", "status: retired"),
                new_base,
                "invalid-historical-status",
            ),
            "missing-replacement": (
                old_base.replace("superseded_by: new.md\n", ""),
                new_base,
                "missing-superseded-by",
            ),
            "unpaired-replacement": (
                old_base,
                new_base.replace("supersedes: old.md", "supersedes: elsewhere.md"),
                "invalid-supersedes-relation",
            ),
            "symlinked-replacement": (
                old_base.replace("superseded_by: new.md", "superseded_by: new-alias.md"),
                new_base,
                "missing-superseded-by",
            ),
        }
        for name, (old_content, new_content, expected) in cases.items():
            with self.subTest(name=name):
                old.write_text(old_content, encoding="utf-8")
                new.write_text(new_content, encoding="utf-8")
                report = self.scan("--include-fresh")
                concept = self.report_concept(report, "docs/old.md")
                self.assertEqual(concept["freshness"], "blocked")
                self.assertIn(expected, concept["metadata_issues"])
                rejected = self.record_concept("docs/old.md", check=False)
                self.assertEqual(rejected["returncode"], 2)
                self.assertIn(expected, rejected["stderr"])

if __name__ == "__main__":
    unittest.main()
