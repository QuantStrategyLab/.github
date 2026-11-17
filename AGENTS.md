# AGENTS.md

Rules for AI assistants and maintainers in `QuantStrategyLab/.github`. Reusable PR
governance actions live in `Pigbibi/PrGovernance`, not here.

## What this repository is

Organization-wide baseline: profile README, default `.github/PULL_REQUEST_TEMPLATE.md`,
`docs/STYLE_GUIDE.md`, reusable Gitleaks/deployment workflows, and `scripts/check_style.py`.
This `AGENTS.md` governs this repository only.

## Layout

- `docs/STYLE_GUIDE.md` & `scripts/check_style.py` — organization documentation standard and CI checker.
- `actions/` & `.github/workflows/` — reusable release, link, and `docs-acceptance.yml` workflows.
- `profile/README.md`, `CONTRIBUTING.md`, `SECURITY.md`, `CODE_OF_CONDUCT.md` — community baseline files.

## Local checks

Before pushing, verify every check passes:

```sh
python3 scripts/test_style.py
python3 scripts/check_style.py --phase 2
```

## Naming and documentation

- English is default; `.zh-CN.md` siblings are optional and kept accurate when updated.
- Document filenames use lowercase kebab-case (`README.md`, `AGENTS.md`, `CLAUDE.md` keep standard casing).
- Update `README.md` / `README.zh-CN.md` only when user-visible install, configuration, CLI, or public API behavior changes; never append `this PR` / `remains unchanged` notes, `P0-P6` phase headings, or sections after `## License` / `## 许可证`.

<!-- repository-files:begin -->
- Public repositories (with `LICENSE`) include `CONTRIBUTING.md`, `SECURITY.md`, `CODE_OF_CONDUCT.md`, and issue/PR templates (underscored filenames: `pull_request_template.md`); private ones require `SECURITY.md`.
- Public `SECURITY.md` covers disclosure only; never mix private rotation procedures into public files.
<!-- repository-files:end -->

## Do not

- Do not restore `.github/engineering.md`, duplicate `pr-governance/`, or commit `docs/plans/`, `docs/audits/`, `docs/changes/`, or `docs/acceptance-policy.md`.
- Do not change organization automation or branch protection without an owner request.

<!-- content-boundary:begin -->
- Public material carries no real resource names or accounts: use `gs://<bucket>/...`, `<account-id>`, and synthetic examples.
- Read bucket names, accounts, and hostnames from `vars.*`, env, or protected config; never commit hashes or identifiers that resolve to private objects.
- Judge whether a change is clean by `git diff` and `git ls-files`; `.gitignore` affects untracked files only.
<!-- content-boundary:end -->

## Commits and pull requests

- Use English Conventional Commits (`feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `perf`, `ci`, `build`) with headers ≤ 72 characters; fill in `.github/PULL_REQUEST_TEMPLATE.md` sections (`AI assistance`, `What changed`, `How verified`, `Why`, `Risk`).
- R2 paths require green CI, `ai-review` on the exact head SHA, and one clearing label (`agent-approved` after checks pass, or `owner-approved` only by owner authorization; never add/remove `owner-approved` yourself). Never push to `main`, force-push reviewed branches, or use `--admin`.

## Operational authorization

- Live-trading deployments, Kelly/stop-loss changes, real Secrets/IAM mutations, and destructive deletions always stay OFF unless explicitly authorized by the owner via [PROPOSAL.md](docs/deployment-workflows.md#live-deployment-boundary).
