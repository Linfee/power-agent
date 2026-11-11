#!/usr/bin/env python3
"""Exercise the wizard helpers without credentials or external services."""
from __future__ import annotations

import os
from pathlib import Path
import pty
import select
import signal
import stat
import subprocess
import tempfile
import termios
import time
import unittest

TEMPLATE = Path(__file__).with_name("template.sh").resolve()
BOOTSTRAP = 'source "$1" || [[ $? -eq 2 ]]; shift; "$@"'


class WizardTemplateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.directory = tempfile.TemporaryDirectory(prefix="power wizard ")
        self.root = Path(self.directory.name)
        self.target = self.root / ".env"

    def tearDown(self) -> None:
        self.directory.cleanup()

    def command(self, *arguments: str) -> list[str]:
        return ["bash", "-c", BOOTSTRAP, "wizard-test", str(TEMPLATE), *arguments]

    def run_helper(self, *arguments: str, answer: str = "") -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            self.command(*arguments), input=answer, text=True, capture_output=True, cwd=self.root
        )

    def test_unwritten_stages_refuse_to_run(self) -> None:
        result = subprocess.run(["bash", str(TEMPLATE)], cwd=self.root, capture_output=True)
        self.assertEqual(result.returncode, 2)
        self.assertFalse(self.target.exists())

    def test_secret_prompt_disables_terminal_echo_before_it_is_visible(self) -> None:
        master, slave = pty.openpty()
        # Hold execution immediately after the prompt to model preemption.
        gate = self.root / "prompt-gate"
        os.mkfifo(gate)
        bootstrap = ('printf() { builtin printf "$@"; '
                     'if [[ "$1" == "  %s " ]]; then IFS= read -r _ < "$WIZARD_TEST_GATE"; fi; }; '
                     + BOOTSTRAP)
        process = subprocess.Popen(
            ["bash", "-c", bootstrap, "wizard-test", str(TEMPLATE),
             "ask_secret", "WIZARD_VALUE_DEMO", "Enter secret:"],
            stdin=slave, stdout=slave, stderr=slave, cwd=self.root,
            env=dict(os.environ, WIZARD_TEST_GATE=str(gate)),
        )
        output = b""
        try:
            deadline = time.monotonic() + 5
            while b"Enter secret:" not in output and time.monotonic() < deadline:
                if select.select([master], [], [], 0.1)[0]:
                    output += os.read(master, 4096)
            self.assertIn(b"Enter secret:", output)
            self.assertFalse(termios.tcgetattr(slave)[3] & termios.ECHO)
            os.write(master, b"fixture-secret\n")
            with gate.open("w") as release:
                release.write("continue\n")
            deadline = time.monotonic() + 5
            while process.poll() is None and time.monotonic() < deadline:
                if select.select([master], [], [], 0.1)[0]:
                    output += os.read(master, 4096)
            self.assertIsNotNone(process.poll(), f"secret input did not finish; output={output!r}")
            exit_code = process.returncode
            self.assertEqual(exit_code, 0)
            while select.select([master], [], [], 0)[0]:
                output += os.read(master, 4096)
            self.assertNotIn(b"fixture-secret", output)
            self.assertTrue(termios.tcgetattr(slave)[3] & termios.ECHO)
        finally:
            os.close(master)
            os.close(slave)
            if process.poll() is None:
                process.terminate()
                process.wait(timeout=5)

    def test_secret_abort_restores_terminal_echo(self) -> None:
        for action in ("empty", "eof", signal.SIGINT, signal.SIGTERM):
            with self.subTest(action=action):
                master, slave = pty.openpty()
                pid_file = self.root / f"secret-reader-{action}"
                bootstrap = ('printf() { if [[ "$1" == "  %s " ]]; then '
                             'builtin printf "%s" "$BASHPID" > "$WIZARD_TEST_PID"; fi; '
                             'builtin printf "$@"; }; ' + BOOTSTRAP)
                process = subprocess.Popen(
                    ["bash", "-c", bootstrap, "wizard-test", str(TEMPLATE),
                     "ask_secret", "WIZARD_VALUE_DEMO", "Enter secret:"],
                    stdin=slave, stdout=slave, stderr=slave, cwd=self.root,
                    env=dict(os.environ, WIZARD_TEST_PID=str(pid_file)),
                )
                output = b""
                try:
                    deadline = time.monotonic() + 5
                    while b"Enter secret:" not in output and time.monotonic() < deadline:
                        if select.select([master], [], [], 0.1)[0]:
                            output += os.read(master, 4096)
                    self.assertIn(b"Enter secret:", output)
                    self.assertFalse(termios.tcgetattr(slave)[3] & termios.ECHO)
                    if action == "empty":
                        os.write(master, b"\n")
                    elif action == "eof":
                        os.write(master, b"\x04")
                    else:
                        os.kill(int(pid_file.read_text()), action)
                    deadline = time.monotonic() + 5
                    while time.monotonic() < deadline:
                        if process.poll() is not None and termios.tcgetattr(slave)[3] & termios.ECHO:
                            break
                        if select.select([master], [], [], 0.1)[0]:
                            output += os.read(master, 4096)
                    self.assertIsNotNone(process.poll(), f"abort did not finish: {action}")
                    self.assertNotEqual(process.returncode, 0)
                    self.assertTrue(termios.tcgetattr(slave)[3] & termios.ECHO)
                finally:
                    os.close(master)
                    os.close(slave)
                    if process.poll() is None:
                        process.kill()
                        process.wait(timeout=5)

    def test_decline_eof_and_nonterminal_secret_leave_target_unchanged(self) -> None:
        before = "PUBLIC=before\n"
        self.target.write_text(before)
        for answer in ("no\n", ""):
            result = self.run_helper("write_env", str(self.target), "PUBLIC", "after", answer=answer)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(self.target.read_text(), before)
            self.assertEqual(list(self.root.glob(".env.tmp.*")), [])
        self.assertNotEqual(self.run_helper("ask", "WIZARD_VALUE_NAME", "Name:").returncode, 0)
        secret = self.run_helper("ask_secret", "WIZARD_VALUE_TOKEN", "Token:", answer="fixture-only\n")
        self.assertNotEqual(secret.returncode, 0)
        self.assertNotIn("fixture-only", secret.stdout + secret.stderr)

    def test_confirmed_write_is_private_idempotent_and_preserves_other_keys(self) -> None:
        self.target.write_text("OTHER=kept\nTOKEN=old\n")
        for _ in range(2):
            result = self.run_helper("write_env", str(self.target), "TOKEN", "fixture-only", answer="yes\n")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(self.target.read_text(), "OTHER=kept\nTOKEN=fixture-only\n")
            self.assertEqual(stat.S_IMODE(self.target.stat().st_mode), 0o600)
            self.assertNotIn("fixture-only", result.stdout + result.stderr)
            self.assertEqual(list(self.root.glob(".env.tmp.*")), [])

    def test_ambiguous_and_symlink_targets_are_not_modified(self) -> None:
        before = 'TOKEN="quoted value"\n'
        self.target.write_text(before)
        result = self.run_helper("write_env", str(self.target), "TOKEN", "new", answer="yes\n")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.target.read_text(), before)
        alias = self.root / "alias.env"
        alias.symlink_to(self.target)
        self.assertNotEqual(self.run_helper("write_env", str(alias), "TOKEN", "new", answer="yes\n").returncode, 0)
        self.assertEqual(self.target.read_text(), before)
        self.assertEqual(list(self.root.glob(".env.tmp.*")), [])

    def test_interruption_removes_private_temporary_copy(self) -> None:
        before = b"EXISTING_SECRET=fixture-only\n" + b"UNCHANGED=value\n" * 100_000
        for interruption in (signal.SIGINT, signal.SIGTERM):
            with self.subTest(signal=interruption):
                target = self.root / f".env-{interruption.name}"
                temporary_pattern = f"{target.name}.tmp.*"
                target.write_bytes(before)
                process = subprocess.Popen(
                    self.command("write_env", str(target), "TOKEN", "new-value"),
                    stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    text=True, cwd=self.root, start_new_session=True,
                )
                try:
                    assert process.stdin is not None
                    process.stdin.write("yes\n")
                    process.stdin.close()
                    process.stdin = None
                    deadline = time.monotonic() + 5
                    while not list(self.root.glob(temporary_pattern)):
                        if process.poll() is not None or time.monotonic() >= deadline:
                            self.fail("writer did not reach the interruptible copy phase")
                        time.sleep(0.005)
                    os.killpg(process.pid, interruption)
                    stdout, stderr = process.communicate(timeout=10)
                    self.assertNotEqual(process.returncode, 0)
                    self.assertEqual(target.read_bytes(), before)
                    self.assertEqual(list(self.root.glob(temporary_pattern)), [])
                    self.assertNotIn("fixture-only", stdout + stderr)
                finally:
                    if process.poll() is None:
                        os.killpg(process.pid, signal.SIGKILL)
                        process.communicate()


if __name__ == "__main__":
    unittest.main()
