#!/usr/bin/env python3
"""Run Gitleaks without exposing snippets, matches, identities or raw diagnostics."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("dir", "git"))
    parser.add_argument("path")
    parser.add_argument("--gitleaks", default="gitleaks")
    parser.add_argument("--config-path", default=str(ROOT / ".gitleaks.toml"))
    parser.add_argument("--fail-on-finding", choices=("true", "false"), default="true")
    parser.add_argument("--log-opts", default="--all")
    parser.add_argument("--summary", type=Path)
    args = parser.parse_args()

    # Missing inputs must not look like a clean scan. Resolve paths before using a temp cwd.
    target = Path(args.path).resolve(strict=True)
    config = Path(args.config_path).resolve(strict=True)
    if not config.is_file():
        raise ValueError("Invalid configuration")
    binary = args.gitleaks
    if "/" in binary:
        binary = str(Path(binary).resolve(strict=True))
    version = subprocess.run([binary, "version"], capture_output=True, check=True, text=True)
    if version.stdout.strip() != "8.30.1":
        raise ValueError("Unexpected Gitleaks version")

    with tempfile.TemporaryDirectory(prefix="publication-scan-") as temporary:
        scratch = Path(temporary)
        report = scratch / "redacted.json"
        ignore = scratch / "empty.ignore"
        ignore.write_text("", encoding="utf-8")
        command = [
            binary, args.mode, str(target), "--config", str(config),
            "--redact=100", "--no-banner", "--no-color", "--exit-code=10",
            "--ignore-gitleaks-allow", "--gitleaks-ignore-path", str(ignore),
            "--report-format=json", "--report-path", str(report),
        ]
        if args.mode == "git":
            command.append("--log-opts=" + args.log_opts)
        # Never forward scanner stderr, even on operational errors. It may contain source text.
        result = subprocess.run(command, cwd=target if target.is_dir() else target.parent,
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if result.returncode not in (0, 10):
            raise RuntimeError("Scanner failed")
        findings = json.loads(report.read_text(encoding="utf-8"))
        if not isinstance(findings, list) or bool(findings) != (result.returncode == 10):
            raise ValueError("Invalid scanner report")
        # Deliberately discard all other fields, including descriptions, links and fingerprints.
        safe = sorted({(str(item["File"]), str(item["RuleID"])) for item in findings})
        summary = {"findings": [{"path": path, "rule": rule} for path, rule in safe],
                   "count": len(safe)}
        if args.summary:
            args.summary.parent.mkdir(parents=True, exist_ok=True)
            args.summary.write_text(json.dumps(summary, ensure_ascii=True) + "\n", encoding="utf-8")
        for finding in summary["findings"]:
            print(json.dumps(finding, ensure_ascii=True))
        print(f"Secret scan: {len(safe)} file/rule finding(s)")
        return 1 if safe and args.fail_on_finding == "true" else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        print("Secret scan failed; check scanner installation, paths, configuration and Git refs.",
              file=sys.stderr)
        sys.exit(2)
