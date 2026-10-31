#!/usr/bin/env python3
"""Check that links pointing into another repository still resolve.

`check_style.py` deliberately skips these: it cannot tell a genuine
cross-repository reference from a coincidence of basenames, so it records
"cross-repository reference, not checked" and moves on. That is the right call
for a checker that runs inside one repository, and it is exactly why a rename
in one repository can break links in another without anything going red.

This script is the other half. It reads every Markdown link in every
repository of an organisation, keeps the ones that point at a sibling, and
resolves them.

Resolution is against the remote default branch, not the working tree. A
shallow clone lags origin, and a clean working tree is not evidence that the
remote still has the file — that is the trap `sync_rules.py --check` was
written to avoid, and it applies here for the same reason.

Three outcomes, and only the first one fails:

  broken        the target path does not exist at the sibling's default branch
  unverifiable  the link pins a ref other than the default branch, which this
                script does not fetch; a link into a feature branch is not a
                defect, it is a reference this check cannot see
  pinned        the link pins a commit sha; a rename does not break it

Usage:
    python3 check_cross_repo_links.py --org quantstrategylab
    python3 check_cross_repo_links.py --org quantstrategylab --json
    python3 check_cross_repo_links.py --org quantstrategylab --root /tmp/org
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

# Where the clones live. Not a fixed path: this file is committed to a
# repository, and an absolute home directory in it names a machine rather than
# describing the job. The scheduled workflow passes `--root`; a local run
# starts from the current directory.
BASE = Path(os.environ.get("DOCS_WORKSPACE", ".")).resolve()
SKIP_REPOS = {"SmsPressureCluster"}

ORGS = {
    "pigbibi": ("repos", None),
    "gdeiassistant": ("repos", "GdeiAssistant"),
    "quantstrategylab": ("repos-quant", None),
}

LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
# https://github.com/<owner>/<repo>/(blob|tree)/<ref>/<path>
GH_REF = re.compile(
    r"https?://github\.com/([^/]+)/([^/]+)/(?:blob|tree)/([^/]+)/(.+?)(?:#.*)?$"
)
SHA = re.compile(r"[0-9a-f]{7,40}")


def org_repos(root: Path, prefix: str | None, shared_root: bool) -> dict[str, Path]:
    out: dict[str, Path] = {}
    if not root.is_dir():
        return out
    for path in sorted(root.iterdir()):
        if not path.is_dir() or not (path / ".git").exists() or path.name in SKIP_REPOS:
            continue
        if shared_root:
            # Pigbibi and GdeiAssistant live in one directory; the name is what
            # separates them.
            is_gdei = path.name.startswith("GdeiAssistant")
            if prefix is None and is_gdei:
                continue
            if prefix is not None and not is_gdei:
                continue
        out[path.name] = path
    return out


def git(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)


def default_branch(repo: Path) -> str:
    out = git(repo, "ls-remote", "--symref", "origin", "HEAD").stdout
    for line in out.splitlines():
        if line.startswith("ref:"):
            ref = line.split()[1]
            return ref.rsplit("/", 1)[-1]
    return "main"


def remote_head(repo: Path) -> tuple[str, str] | None:
    """Fetch the default branch and return (branch, commit)."""
    branch = default_branch(repo)
    fetched = git(repo, "fetch", "--quiet", "origin", branch, "--depth=1")
    if fetched.returncode != 0:
        return None
    sha = git(repo, "rev-parse", "FETCH_HEAD").stdout.strip()
    return (branch, sha) if sha else None

def tree_files(repo: Path, sha: str) -> set[str]:
    out = git(repo, "ls-tree", "-r", "--name-only", sha).stdout
    return {line for line in out.split("\n") if line}


def grep_links(repo: Path, sha: str) -> list[tuple[str, int, str]]:
    """Every line of every tracked Markdown file at `sha` that holds a link."""
    out = git(repo, "grep", "-n", "-I", "-E", r"\]\(", sha, "--", "*.md")
    found = []
    for line in out.stdout.split("\n"):
        if not line:
            continue
        parts = line.split(":", 3)
        if len(parts) != 4:
            continue
        _, rel, number, text = parts
        try:
            found.append((rel, int(number), text))
        except ValueError:
            continue
    return found


def resolve_relative(repo: Path, rel: str, target: str) -> str | None:
    """Turn a `../../Sibling/docs/x.md` link into a path inside the sibling."""
    clean = target.split("#")[0]
    if not clean or clean.startswith(("http", "mailto:", "/")):
        return None
    here = (repo / rel).parent
    try:
        return (here / clean).resolve().relative_to(repo.resolve().parent).as_posix()
    except ValueError:
        return None


def scan(repos: dict[str, Path]) -> tuple[list[dict], list[dict], int]:
    heads: dict[str, str] = {}
    branches: dict[str, str] = {}
    files: dict[str, set[str]] = {}
    for name, repo in repos.items():
        head = remote_head(repo)
        if head is None:
            print(f"warning: {name}: cannot fetch the default branch", file=sys.stderr)
            continue
        branches[name], heads[name] = head
        files[name] = tree_files(repo, head[1])

    broken: list[dict] = []
    unverifiable: list[dict] = []
    pinned = 0
    for name, repo in repos.items():
        if name not in heads:
            continue
        for rel, number, text in grep_links(repo, heads[name]):
            for match in LINK.finditer(text):
                url = match.group(1)
                hit = classify(url, name, rel, repos, branches)
                if hit is None:
                    continue
                target_repo, target_path, kind, note = hit
                if target_repo == name and kind == "relative":
                    continue  # inside this repository; check_style.py owns that
                if target_repo not in files:
                    continue  # another organisation, or not cloned here
                if kind == "pinned":
                    # A rename cannot break a link that pins a commit, so this
                    # is not a check that can fail — only one that was skipped.
                    pinned += 1
                    continue
                record = {
                    "from_repo": name,
                    "from_file": rel,
                    "line": number,
                    "url": url,
                    "kind": kind,
                    "target_repo": target_repo,
                    "target_path": target_path,
                }
                if note:
                    unverifiable.append({**record, "reason": note})
                elif target_path not in files[target_repo]:
                    broken.append(record)
    return broken, unverifiable, pinned


def classify(
    url: str, name: str, rel: str, repos: dict[str, Path], branches: dict[str, str]
) -> tuple[str, str, str, str] | None:
    """Return (target_repo, target_path, kind, unverifiable_reason)."""
    m = GH_REF.match(url)
    if m:
        _, target_repo, ref, path = m.groups()
        if SHA.fullmatch(ref):
            return target_repo, path, "pinned", "commit sha"
        branch = branches.get(target_repo)
        if branch is not None and ref != branch:
            return target_repo, path, "github-blob", f"ref {ref} is not the default branch"
        return target_repo, path, "github-blob", ""

    if url.startswith(("http", "#", "mailto")):
        return None
    resolved = resolve_relative(repos[name], rel, url)
    if resolved is None:
        return None
    head, _, path = resolved.partition("/")
    if not path:
        return None
    return head, path, "relative", ""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--org", required=True, choices=sorted(ORGS))
    ap.add_argument("--root", help="override the checkout directory")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    sub, prefix = ORGS[args.org]
    root = Path(args.root).expanduser().resolve() if args.root else BASE / sub
    repos = org_repos(root, prefix, shared_root=args.root is None)
    if not repos:
        print(f"{args.org}: no repositories found under {root}")
        return 1

    broken, unverifiable, pinned = scan(repos)

    if args.json:
        print(json.dumps(
            {"broken": broken, "unverifiable": unverifiable, "pinned": pinned},
            indent=2, ensure_ascii=False,
        ))
        return 1 if broken else 0

    if not broken:
        detail = f"{pinned} pinned" + (f", {len(unverifiable)} unverifiable" if unverifiable else "")
        print(
            f"{args.org}: no broken cross-repository links across {len(repos)} repositories"
            f" ({detail} not checked)"
        )
        return 0

    print(f"{args.org}: {len(broken)} broken cross-repository links across {len(repos)} repositories")
    for f in broken:
        print(f"  {f['from_repo']}/{f['from_file']}:{f['line']}")
        print(f"      -> {f['target_repo']}/{f['target_path']}  [{f['kind']}]")
        print(f"      {f['url']}")
    if unverifiable:
        print(f"\n  {len(unverifiable)} links could not be verified and are not counted above:")
        for f in unverifiable[:10]:
            print(f"    {f['from_repo']}/{f['from_file']}:{f['line']}  ({f['reason']})")
        if len(unverifiable) > 10:
            print(f"    ... {len(unverifiable) - 10} more")
    return 1


if __name__ == "__main__":
    sys.exit(main())
