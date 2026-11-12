#!/usr/bin/env python3
"""Exercise the reference checker against temporary repository consumers."""
from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


CHECKER = Path(__file__).with_name("check-skill-references.py")


class ReferenceCheckerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.workspace = tempfile.TemporaryDirectory(prefix="skill reference tests ")
        self.addCleanup(self.workspace.cleanup)
        self.root = Path(self.workspace.name) / "repo with spaces"
        self.root.mkdir()

    def write(self, name: str, content: str) -> Path:
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def run_check(self, *paths: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(CHECKER), "--repo", str(self.root), *paths],
            cwd=self.workspace.name,
            capture_output=True,
            text=True,
            check=False,
        )

    def test_broken_path_and_anchor_have_source_lines(self) -> None:
        self.write("README.md", "# Readme\n[missing](gone.md)\n[stale](page.md#gone)\n")
        self.write("page.md", "# Existing\n")
        result = self.run_check()
        self.assertEqual(result.returncode, 1)
        self.assertIn("README.md:2: missing local target: gone.md", result.stderr)
        self.assertIn("README.md:3: missing Markdown anchor: page.md#gone", result.stderr)

    def test_reference_links_and_undefined_full_reference(self) -> None:
        self.write(
            "README.md",
            "[one][Doc] [Doc][] [Doc]\n[absent][missing]\n"
            "[not-a-reference]\n\n[doc]: <guide with spaces.md#开始> \"Title\"\n",
        )
        self.write("guide with spaces.md", "# 开始\n")
        result = self.run_check()
        self.assertEqual(result.returncode, 1)
        self.assertIn("README.md:2: undefined link reference: missing", result.stderr)
        self.assertEqual(result.stderr.count("\n"), 1)

    def test_heading_slugs_duplicates_links_and_setext(self) -> None:
        self.write(
            "README.md",
            "[a](guide.md#标题) [b](guide.md#标题-1) [c](guide.md#标题-2)\n"
            "[link](guide.md#7-indexmd) [setext](guide.md#another-heading)\n"
            "[inline](guide.md#foo_bar-和-code) [id](guide.md#custom-id)\n",
        )
        self.write(
            "guide.md",
            "# 标题\n# 标题-1\n# 标题\n## 7. [index.md](https://example.com)\n"
            "Another Heading\n===\n# foo_bar 和 `code`\n<a id='custom-id'></a>\n",
        )
        result = self.run_check()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.write("README.md", "[absent duplicate](guide.md#标题-3)\n")
        self.assertIn("missing Markdown anchor", self.run_check().stderr)

    def test_fences_inline_code_comments_and_frontmatter_are_not_links(self) -> None:
        self.write(
            "skills/demo/SKILL.md",
            "---\ndescription: '[example](frontmatter-missing.md)'\n---\n"
            "# Demo\n````markdown\n[example](fenced-missing.md)\n```\n"
            "# False heading\n`scripts/fenced-missing.py`\n````\n"
            "~~~md\n[x](tilde-missing.md)\n~~~\n"
            "`[inline](inline-missing.md)` and ``[literal `code`](missing.md)``\n"
            "<!-- [hidden](hidden.md) -->\n    [example](indented-missing.md)\n"
            "Historical name `docs/retired-file.md` is not an explicit link.\n",
        )
        result = self.run_check()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.write("README.md", "[fake](skills/demo/SKILL.md#false-heading)\n")
        self.assertIn("missing Markdown anchor", self.run_check().stderr)

    def test_encoded_space_angle_paths_and_balanced_parentheses(self) -> None:
        self.write("docs/a folder/guide (v2).md", "# 中文 标题\n")
        self.write("docs/a folder/open (.md", "# Open\n")
        self.write(
            "README.md",
            "[angle](<docs/a folder/guide (v2).md#中文-标题>)\n"
            "[encoded](docs/a%20folder/guide%20(v2).md#%E4%B8%AD%E6%96%87-%E6%A0%87%E9%A2%98)\n"
            "[title](<docs/a folder/guide (v2).md> \"A title\")\n"
            "[angle unbalanced](<docs/a folder/open (.md#open>)\n",
        )
        result = self.run_check()
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_remote_and_explicit_template_targets_are_ignored(self) -> None:
        self.write(
            "README.md",
            "[web](https://example.com/missing) [mail](mailto:test@example.com)\n"
            "[cdn](//example.com/missing) [template](docs/{topic}.md)\n"
            "[variable]($REPO/docs/topic.md) [ellipsis](docs/.../topic.md)\n",
        )
        result = self.run_check()
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_skill_script_pointer_requires_installed_skill_asset(self) -> None:
        self.write(
            "skills/demo/SKILL.md",
            "# Demo\nRun `python3 scripts/local.py --name <value>`.\n"
            "Use `scripts/repository.py` or `scripts/missing.py`.\n",
        )
        self.write("skills/demo/scripts/local.py", "raise RuntimeError('must not execute')\n")
        self.write("scripts/repository.py", "raise RuntimeError('must not execute')\n")
        self.write("skills/demo/references/use.md", "Use `scripts/local.py`.\n")
        result = self.run_check()
        self.assertEqual(result.returncode, 1)
        self.assertIn(
            "skills/demo/SKILL.md:3: missing local target: scripts/repository.py", result.stderr,
        )
        self.assertIn(
            "skills/demo/SKILL.md:3: missing local target: scripts/missing.py", result.stderr,
        )
        self.assertEqual(result.stderr.count("\n"), 2)

    def test_skill_links_stay_within_relocatable_bundle(self) -> None:
        self.write("skills/shared/SKILL.md", "# Shared\n")
        guide = self.write(
            "skills/demo/references/guide.md",
            "# Guide\n[peer](../../shared/SKILL.md#shared)\n",
        )
        self.write(
            "skills/demo/SKILL.md",
            "# Demo\n[guide](references/guide.md#guide)\n",
        )
        self.assertEqual(self.run_check("skills").returncode, 0)

        self.write("docs/repository-only.md", "# Repository only\n")
        guide.write_text(
            "# Guide\n[unshipped](../../../docs/repository-only.md#repository-only)\n",
            encoding="utf-8",
        )
        self.write(
            "skills/demo/SKILL.md",
            f"# Demo\n[guide](references/guide.md#guide)\n[absolute]({guide.as_uri()})\n",
        )
        result = self.run_check("skills")
        self.assertEqual(result.returncode, 1)
        self.assertIn("skills/demo/references/guide.md:2:", result.stderr)
        self.assertIn("skills/demo/SKILL.md:3:", result.stderr)

    def test_skill_symlink_cannot_reach_repository_only_docs(self) -> None:
        self.write("skills/demo/SKILL.md", "# Demo\n")
        target = self.write("docs/repository-only.md", "# Repository only\n")
        alias = self.root / "skills/demo/references/guide.md"
        alias.parent.mkdir()
        alias.symlink_to(target)
        result = self.run_check("skills/demo/references/guide.md")
        self.assertEqual(result.returncode, 1)
        self.assertIn("skills/demo/references/guide.md:1:", result.stderr)

    def test_internal_symlink_is_valid_external_links_are_rejected(self) -> None:
        self.write("docs/real.md", "# Internal\n")
        (self.root / "docs/link.md").symlink_to("real.md")
        external = Path(self.workspace.name) / "private.md"
        external.write_bytes(b"\xff must not read")
        (self.root / "external.md").symlink_to(external)
        self.write("README.md", "[inside](docs/link.md#internal)\n[outside](external.md#secret)\n")
        result = self.run_check("README.md")
        self.assertEqual(result.returncode, 1)
        self.assertIn("README.md:2: target resolves outside repository", result.stderr)
        self.assertNotIn("codec", result.stderr)
        self.assertEqual(result.stderr.count("\n"), 1)

    def test_encoded_traversal_absolute_file_url_and_external_input_are_rejected(self) -> None:
        external = Path(self.workspace.name) / "private.md"
        external.write_bytes(b"\xff must not read")
        self.write("README.md", f"[escape](..%2Fprivate.md#secret)\n[file]({external.as_uri()})\n")
        result = self.run_check("README.md")
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stderr.count("target resolves outside repository"), 2)
        result = self.run_check(str(external))
        self.assertEqual(result.returncode, 1)
        self.assertIn("outside repository", result.stderr)
        self.assertNotIn("codec", result.stderr)

    def test_default_excludes_history_but_explicit_paths_include_it(self) -> None:
        self.write("README.md", "# Repository\n")
        self.write("docs/exec-plans/completed/old.md", "[old](missing.md)\n")
        self.write("docs/adr/old.md", "---\nstatus: superseded\n---\n[old](missing.md)\n")
        self.assertEqual(self.run_check().returncode, 0)
        result = self.run_check("docs/exec-plans/completed", "docs/adr/old.md")
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stderr.count("missing local target"), 2)

    def test_internal_directory_symlink_cycle_does_not_repeat_work(self) -> None:
        self.write("skills/demo/SKILL.md", "# Demo\n[local](references/guide.md)\n")
        self.write("skills/demo/references/guide.md", "# Guide\n")
        (self.root / "skills/demo/references/loop").symlink_to(
            self.root / "skills/demo", target_is_directory=True,
        )
        result = self.run_check()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("2 documents", result.stdout)

    def test_inline_html_examples_are_not_ids_and_emphasis_is_not_slug_text(self) -> None:
        self.write(
            "README.md",
            "[heading](guide.md#emphasis-and-strong)\n"
            "[fake](guide.md#inline-example)\n",
        )
        self.write(
            "guide.md",
            "# _Emphasis_ and __strong__\n`<a id='inline-example'></a>`\n",
        )
        result = self.run_check()
        self.assertEqual(result.returncode, 1)
        self.assertIn("README.md:2: missing Markdown anchor", result.stderr)
        self.assertEqual(result.stderr.count("\n"), 1)


if __name__ == "__main__":
    unittest.main()
