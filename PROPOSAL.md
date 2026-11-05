# Automated approval for ordinary high-risk paths

Status: proposal for owner decision. Opening this Draft PR does not adopt it.

## Problem and rationale

The current path gate requires an owner-applied label for every high-risk
change, including ordinary strategy, risk and runtime code. It ignores an
already completed, clean Codex review and passing required checks. The proposed
policy removes that repeated manual step while keeping owner control over
sensitive operations and the gate's trust configuration.

## Decision rule

Low-risk paths retain their existing behavior. For other paths, inspect both
current and previous filenames before any docs or tests exemption.

An ordinary high-risk change passes `risk-gate` only when all of these hold:

1. The newest marker from a trusted Codex App is exactly one well-formed
   `codex-review-state:v1` comment marker. The App IDs come from the existing
   policy at the immutable trusted base revision, never the PR's candidate tree.
2. Its `code_review.commit_sha` equals the current PR head, its status is
   `completed`, and `has_unresolved_findings` is the boolean `false`.
   `has_any_findings` must also be a boolean; resolved findings are permitted.
   A newer running, malformed or unresolved marker supersedes an older clean one.
3. All required contexts from classic branch protection and applicable rulesets
   are discovered and successful for the same head. Missing protection evidence,
   missing results, skipped/neutral checks, wrong App bindings and API errors
   block automatic approval. Legacy statuses cannot prove an App-bound identity
   and therefore cannot satisfy such a requirement.
4. No changed or previous path matches the owner-only list below. An old owner
   label cannot substitute for missing automated evidence on ordinary high-risk
   paths.

`risk-gate` is the output of this decision, so it cannot be its own prerequisite.
The locally validated `pr-template` result is published before the required-check
read. These are the only two self-produced contexts; their expected App binding
is checked. Every other required job stays mandatory. Native branch protection
and the required-check list stay unchanged.

## Owner-only paths

These are the exact implemented globs. Paths are converted from camelCase to
snake_case and lowercased before matching. `*` stays within one path segment;
`**/` matches zero or more directory segments. Broad credential, trading and
infrastructure families intentionally keep ambiguous files under owner control.
There is no docs, tests, examples or fixtures exemption for this list.

```text
**/*secret*
**/*secret*/**
**/*credential*
**/*credential*/**
**/.env*
**/*.pem
**/*.key
**/*.p12
**/*.pfx
**/*iam*
**/*iam*/**
**/*service_account*
**/*service_account*/**
**/*serviceaccount*
**/*serviceaccount*/**
**/*permission*
**/*permission*/**
**/*role_binding*
**/*role_binding*/**
**/*deploy*
**/*deploy*/**
**/*release*
**/*release*/**
**/*.tf
**/*.tfvars
**/dockerfile*
**/docker-compose*
**/compose.y*ml
**/vercel.json
**/wrangler.*
**/firebase.json
**/k8s/**
**/kubernetes/**
**/*trad*
**/*trad*/**
**/*execution*
**/*execution*/**
**/*executor*
**/*executor*/**
**/*order*
**/*order*/**
**/*broker*
**/*broker*/**
**/*kelly*
**/*kelly*/**
**/*stop*loss*
**/*stop*loss*/**
.github/governance/**
.github/workflows/risk-gate.yml
**/codeowners
```

The list includes the gate itself, its trust policy and CODEOWNERS because a PR
must not grant itself authority by modifying those files. Broker, order and
execution paths stay owner-only even when a filename does not say live. Kelly
and stop-loss paths stay protected; this proposal enables no trading feature.
Other workflow changes still require the automated high-risk rule.

Owner-only paths retain the existing verified owner-label event predicate.
This proposal neither strengthens that legacy human-identity proof nor allows
an agent to add/remove a label. A label is not operational authorization to
execute a deployment or trade.

## Execution and evidence freshness

The privileged workflow executes trusted workflow code only. It adds read-only
check access; status publication remains its only write capability. It never
checks out or executes a PR, reads secrets, writes labels, merges or deploys.
The existing shadow observer and its report-only policy are unchanged.

PR/comment/check/status events refresh evidence. The existing native CI workflows
also trigger reevaluation through `workflow_run`, because GitHub Actions check
events do not reliably trigger other workflows. The explicit workflow-name list
must be maintained if required native workflows are renamed or added. A manual
workflow dispatch remains an existing recovery entry, with no new schedule.

A read-only discovery job resolves every event to PR numbers. All event types
then share one concurrency group per PR without cancellation. Replaced pending
events evaluate the same PR; unrelated PRs never replace each other in the queue.
Each evaluation reconstructs evidence after restart; no persisted approval is
reused. It rereads PR head/base/body/labels, changed paths, owner events or
review/check/protection evidence before publishing. A mismatch or read failure
blocks the decision. API exception text and user bodies are never logged.

The final status is a snapshot, not a transaction with GitHub's mutable evidence.
Events refresh it and native branch protection still enforces checks at merge.
No local test proves hosted token permissions, event delivery or runtime adoption.
If protection APIs are unreadable to the installed token, the gate blocks;
this Draft PR requests no settings or permission changes outside workflow scope.

## Scope and adoption

Only this organization's metadata repository changes. Other repositories and
callers pinned to older revisions do not adopt this proposal automatically.
The workflow diff, local rules, tests and this decision document form one review
unit. The root filename `PROPOSAL.md` is explicitly requested for this decision;
the naming checker permits only this root path, while nested uppercase proposal
filenames remain invalid. No security or identifier rule is relaxed.

This PR stays Draft for the owner's decision and the established review bot.
The current base-branch risk gate still governs this PR. Opening it does not
satisfy its own approval gate and does not authorize merge, undraft, labels,
repository/organization settings, deployment or live activation.

## Validation

`node --test scripts/test-risk-gate.cjs` executes the actual embedded workflow
script with fake native API data. It checks the positive decision, invalid or
stale review markers, required checks and App identities, protected paths,
renames, event routing, read failures, redaction, concurrent evaluations and
snapshot drift. The existing CI test job runs these tests alongside the shadow
engine tests. Run all available Python checker/scanner tests and the phase-2 docs
checker before publication. The PR description records the actual results.

## Rollback

Through a separately authorized reviewed change, restore the previous
`risk-gate.yml` and the corresponding AGENTS approval wording, remove the added
risk tests from the CI command and revert this proposal's document/name-only
changes. Keep every existing native required check, the owner-only controls and
branch protection enabled. Reevaluate affected open PRs under the restored gate
using its existing workflow-dispatch input; do not reuse successful statuses
from the proposed policy as proof of legacy owner approval. No deployment,
settings edit, history rewrite or label change is part of this Draft PR.
