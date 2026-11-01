#!/usr/bin/env python3
"""Exercise the publication guard and full-history scanner with runtime-only fake data."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCANNER = ROOT / "scripts/scan-secrets.py"
BINARY = os.environ.get("GITLEAKS_BIN", "gitleaks")


class SecretScanTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="secret-scan-test-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.target = self.root / "publish"
        self.target.mkdir()
        self.summary = self.root / "summary.json"
        # No full token-shaped string is ever stored in the repository or test output.
        self.fake = "123456789" + ":" + "A" * 35
        self.json_value = "synthetic" + "-credential-value-" + "x" * 12

    def write(self, name, text):
        path = self.target / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def scan(self, expected, mode="dir", extra=()):
        result = subprocess.run(
            [sys.executable, str(SCANNER), mode, str(self.target), "--gitleaks", BINARY,
             "--summary", str(self.summary), *extra], capture_output=True, text=True,
        )
        # Assert booleans so a regression cannot print the captured output or fake values.
        self.assertTrue(result.returncode == expected, "Unexpected scanner exit code")
        output = result.stdout + result.stderr
        for value in (self.fake, self.json_value, "private-source-marker"):
            self.assertTrue(value not in output, "Output contained a protected test value")
        if self.summary.exists():
            text = self.summary.read_text()
            for value in (self.fake, self.json_value, "private-source-marker"):
                self.assertTrue(value not in text, "Summary contained a protected test value")
            summary = json.loads(text)
            self.assertTrue(set(summary) == {"findings", "count"}, "Unexpected summary fields")
            self.assertTrue(all(set(item) == {"path", "rule"} for item in summary["findings"]),
                            "Unexpected finding fields")
            return summary
        return None

    def test_clean_directory_passes(self):
        self.write("report.json", json.dumps({"status": "ok", "token": ""}))
        summary = self.scan(0)
        self.assertTrue(summary["count"] == 0)

    def test_bare_telegram_format_fails_without_keyword(self):
        self.write("report.txt", "private-source-marker " + self.fake)
        summary = self.scan(1)
        self.assertTrue(any(x["rule"] == "telegram-bot-token-format" for x in summary["findings"]))

    def test_json_field_names_fail(self):
        for field in ("token", "bot_token", "api_key"):
            with self.subTest(field=field):
                self.write("report.json", json.dumps({field: self.json_value}))
                summary = self.scan(1)
                self.assertTrue(any(x["rule"] == "json-credential-field" for x in summary["findings"]))

    def test_fixture_allowlist_requires_path_and_synthetic_value(self):
        name = "tests/fixtures/secret-scan/placeholder.json"
        placeholder = "FAKE_" + "PLACEHOLDER_VALUE"
        self.write(name, json.dumps({"token": placeholder}))
        self.scan(0)
        self.write("report.json", json.dumps({"token": placeholder}))
        self.scan(1)
        (self.target / "report.json").unlink()
        self.write(name, json.dumps({"token": self.json_value}))
        self.scan(1)

    def test_diagnostics_can_allow_findings(self):
        self.write("report.txt", self.fake)
        summary = self.scan(0, extra=("--fail-on-finding", "false"))
        self.assertTrue(summary["count"] > 0)

    def test_missing_target_and_bad_config_fail_even_in_diagnostic_mode(self):
        self.target.rmdir()
        self.scan(2, extra=("--fail-on-finding", "false"))
        self.target.mkdir()
        bad_config = self.root / "invalid.toml"
        bad_config.write_text("[invalid")
        self.scan(2, extra=("--config-path", str(bad_config), "--fail-on-finding", "false"))

    def test_ignore_comments_do_not_bypass_publication_guard(self):
        self.write("report.txt", self.fake + " # gitleaks:allow")
        self.scan(1)

    def git(self, *args):
        subprocess.run(["git", "-C", str(self.target), *args],
                       check=True, capture_output=True)

    def test_all_branch_history_finds_deleted_data_branch_value(self):
        self.git("init", "--quiet", "-b", "main")
        self.git("config", "user.name", "Synthetic Test")
        self.git("config", "user.email", "synthetic@example.invalid")
        self.write("README.md", "Clean default branch")
        self.git("add", ".")
        self.git("commit", "--quiet", "-m", "test: add clean main")
        self.git("checkout", "--quiet", "-b", "logs")
        self.write("old-report.txt", self.fake)
        self.git("add", ".")
        self.git("commit", "--quiet", "-m", "test: add synthetic history fixture")
        (self.target / "old-report.txt").unlink()
        self.git("add", "-u")
        self.git("commit", "--quiet", "-m", "test: remove synthetic fixture")
        self.git("checkout", "--quiet", "main")
        # Reproduce the workflow's fresh clone and explicit fetch of every remote branch.
        remote = self.target
        self.target = self.root / "clone"
        subprocess.run(["git", "clone", "--quiet", "--no-local", "--single-branch",
                        "--branch", "main", str(remote), str(self.target)],
                       check=True, capture_output=True)
        self.git("fetch", "--quiet", "origin", "+refs/heads/*:refs/remotes/origin/*")
        self.scan(0)
        self.scan(0, mode="git", extra=("--log-opts=HEAD",))
        summary = self.scan(1, mode="git")
        self.assertTrue(any(x["path"] == "old-report.txt" for x in summary["findings"]))

    def test_default_rules_are_preserved(self):
        value = "ghp_" + "bC3dE4fG5hI6jK7lM8nO9pQ0rS1tU2vW3xY4"
        self.write("report.txt", value)
        summary = self.scan(1)
        self.assertTrue(any(x["rule"] == "github-pat" for x in summary["findings"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
