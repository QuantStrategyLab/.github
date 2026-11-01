# Shared secret scans

Scan publication content before it leaves a runner. PR checks and weekly history
scans provide additional coverage; a push made with `GITHUB_TOKEN` may not start
another workflow, so they cannot replace the publication guard.

## Scan before publishing

Use the [composite action](../actions/scan-before-publish/action.yml) immediately
before `git push` to a non-PR branch and before `actions/upload-artifact` in a
public repository. Stage the complete content in one directory and scan that
same directory. Do not change or add files between scanning and publishing.
Scan an extracted staging directory before packaging binary archives. A secret
scan does not determine whether financial, personal or operational data is safe
to publish; keep that data in approved private storage.

```yaml
# Earlier steps produce publish/ and prepare the commit to publish.
- name: Scan the publication directory
  uses: QuantStrategyLab/.github/actions/scan-before-publish@b0a90eb9ac1cf06aef3c9c6c289b4cf7d833cca3
  with:
    path: publish
- name: Publish the already scanned commit to the data branch
  run: git push origin HEAD:logs
```

For an artifact publisher:

```yaml
- name: Scan the artifact directory
  uses: QuantStrategyLab/.github/actions/scan-before-publish@b0a90eb9ac1cf06aef3c9c6c289b4cf7d833cca3
  with:
    path: publish
- uses: actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02 # v4
  with:
    name: public-diagnostics
    path: publish/
    retention-days: 3
```

For Git publication, scan every file
included in the new commits, including deletions and earlier commits containing
values; use the history scanner as well when publishing existing commits.
Prepare the commit from the scanned staging content only. For artifact uploads,
scan all uploaded paths, including paths introduced by globs. Do not use
`continue-on-error`, `if: always()` or `fail-on-finding: 'false'` on a publishing
path. Scanning an unrelated checkout does not cover another worktree or directory.

| Input | Required | Default | Meaning |
| --- | --- | --- | --- |
| `path` | Yes | none | One existing file or directory; workspace-relative or absolute. Use a common staging directory for multiple paths. |
| `config-path` | No | Shared config | Configuration file relative to the working directory, or absolute. Custom configs must extend the shared rules rather than replace them. |
| `fail-on-finding` | No | `'true'` | `'false'` reports findings without failing, for diagnostics only. Scanner errors still fail. |

The action supports Linux x64 and macOS x64/arm64 runners with Bash, Python 3,
Git, curl and tar. It downloads Gitleaks 8.30.1 and verifies the archive against a
platform-specific SHA-256 committed in the installer. No credentials or
third-party Gitleaks action license is needed.

## Shared rules and pre-commit

[`.gitleaks.toml`](../.gitleaks.toml) extends the pinned scanner's default rules.
It adds `telegram-bot-token-format`, matching
`\b\d{6,12}:A[A-Za-z0-9_-]{34}\b` without a keyword prerequisite, and
`json-credential-field`, matching double-quoted `token`, `bot_token` or `api_key`
fields with string values of at least eight characters. The JSON rule is
case-insensitive and permits whitespace and newlines between keys and values.
It has no entropy threshold. Empty strings and shorter placeholders are outside
that rule; this is a detection heuristic rather than a JSON schema validator.

The JSON fixture exception requires **both** the exact
`tests/fixtures/secret-scan/placeholder.json` path and a value matching
`^FAKE_[A-Z0-9_]{8,}$`. It does not exempt a test directory or disable default
rules. Telegram-shaped fixtures are built at runtime rather than committed.
The publication and reusable scanners ignore inline `gitleaks:allow` comments
and repository `.gitleaksignore` files; reviewed config allowlists remain active.

This repository's pre-commit hook uses the same config. When adopting the hook
in another repository, copy the shared config from the same reviewed immutable
revision, record its source revision, and keep `--redact` and
`--config=.gitleaks.toml` in the hook arguments. The hook revision is pinned to
Gitleaks 8.30.1. A local pre-commit hook complements CI; bots may not run hooks.

A custom config can use `[extend] path = "<shared-config-path>"`. Gitleaks resolves
extension paths from its working directory, so use an absolute path or one
relative to the scanned directory. Preserve the inherited default and shared
rules, and scope additional fixture exceptions to an exact path and fake value.

## Required PR and main check

Copy [the PR caller template](../workflow-templates/required-gitleaks.yml) into
`.github/workflows/required-gitleaks.yml` in the adopting repository. It runs on
`pull_request` and `push` to `main`, without path filters. The shared workflow
checks out full history and scans the base-to-head commit range with the same
config; missing comparison refs fail instead of producing a clean result.

With the template's unchanged names, the exact required status-check name is
**`Secret scan / Gitleaks`**. The reusable job name is `Gitleaks`; the caller's
job name is `Secret scan`. Keep both names stable. This repository retains its
existing `Gitleaks` check and additionally exercises the reusable caller.
Selecting a required check is a separate repository settings change; these
files do not enable branch protection or rulesets.

## Weekly all-branch history scan

Copy [the weekly caller template](../workflow-templates/weekly-gitleaks.yml) into
`.github/workflows/weekly-gitleaks.yml` on each adopting repository's default
branch. Its weekly cron is Monday at 04:23 UTC; GitHub may delay scheduled runs.
It also provides `workflow_dispatch` for a separately authorized manual run.

```yaml
name: Weekly all-branch secret scan
on:
  schedule:
    - cron: '23 4 * * 1'
  workflow_dispatch:
permissions:
  contents: read
jobs:
  secret-scan:
    name: Secret scan
    uses: QuantStrategyLab/.github/.github/workflows/gitleaks.yml@WORKFLOW_SHA
    with:
      full-history: true
```

The [shared workflow](../.github/workflows/gitleaks.yml) uses `fetch-depth: 0`,
then `git fetch origin '+refs/heads/*:refs/remotes/origin/*'` and
`gitleaks git --log-opts=--all`. This includes the full history of remote
`logs`, `state` and other data branches, even when the default branch is clean.
The public-repository fetch uses no persisted checkout credentials. The scan
fails on findings. A later successful artifact upload does not clear that failure.

All scans use `--redact=100`. Scanner stdout and stderr are suppressed even on
errors. A temporary redacted JSON report is reduced to file paths, rule names
and a count, then discarded. Only `summary.json` is uploaded for a weekly scan,
with three-day retention, including when findings fail the scan. No raw reports,
SARIF source snippets, matched values, commit messages, authors, fingerprints or
notification payloads are published. Operational failures produce a generic
error and no success summary. The workflow does not send external notifications;
use its failed status to route alerts through an approved existing notifier.

## Repository hygiene and registered exceptions

New workflows that push to non-PR branches or upload sensitive-looking
directories need a reviewed registration identifying the workflow path,
destination, reason and immediately preceding `scan-before-publish` step.
Sensitive-looking directories include reports, logs, state, session exports and
credential material. Registration does not make private data publishable.

The existing registered repositories are listed below. These historical entries
are rollout candidates, not evidence that their workflows already run this scan.
During adoption, register each exact workflow and its scan before publishing.

| Registered repository | Publication scope to review |
| --- | --- |
| `QuantStrategyLab/SchwabTokenAutoRefresher` | `logs` branch |
| `QuantStrategyLab/CryptoLivePoolPipelines` | `logs` branch |
| `Pigbibi/PushPlusSmsToTelegram` | Intended `state` branch |
| `Pigbibi/TelegramAutoSignBot` | `logs` branch |
| `Pigbibi/GoogleVoicePulseBot` | `logs` branch |

This change supplies shared tooling and caller templates. Adoption in other
repositories and any automated hygiene enforcement are separate changes.

## Maintenance and local checks

Run `bash scripts/install-gitleaks.sh <temporary-bin-directory>` and then
`GITLEAKS_BIN=<temporary-bin-directory>/gitleaks python3 scripts/test_secret_scan.py`.
The harness constructs fake values at runtime, tests clean and failing scans,
checks output for accidental value disclosure and verifies a removed value on a
remote data branch remains detectable in history.

The reusable workflow checks out scanner helpers at an explicit full commit SHA.
When changing helpers or the shared config, commit and test those changes first,
then update that pin to the helper commit. Caller templates pin the shared
workflow to an immutable commit too. Adopt a new reviewed SHA explicitly; do not
replace pins with moving branches or tags.

References: [Gitleaks configuration and scanning commands](https://github.com/gitleaks/gitleaks/tree/v8.30.1)
and [GitHub reusable workflows](https://docs.github.com/en/actions/how-tos/reuse-automations/reuse-workflows).
