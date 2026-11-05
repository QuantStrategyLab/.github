# Agent-cleared source changes and deployment authorization

Status: owner-authorized reconciliation; effective only after normal protected
merge. The current main gate continues to govern this candidate.

## Decision rule

AI reviews and the established merge bot handle every PR. There is no
filename-based owner-only approval branch, including governance, AI-service,
gate and trust-policy source changes. Classification still marks sensitive
paths as high risk; both filenames of a rename are checked.

Every PR, including low-risk prose and dependency updates, needs:

1. The newest marker-bearing comment from a trusted Codex Bot/App, using App IDs
   read from `.github/governance/policy.json` at the immutable base SHA. It must
   contain exactly one valid `codex-review-state:v1` marker. Comment IDs and times
   must be valid; a newer malformed marker supersedes an older clean receipt.
2. A completed review with `commit_sha` equal to the exact current head,
   boolean `has_any_findings` and `has_unresolved_findings=false`. Resolved
   findings are permitted. The head must contain the current live base tip,
   resolved with the branch/compare APIs rather than a cached PR base snapshot.
3. Successful required contexts discovered from classic protection and applicable
   rulesets, with exact App binding. Missing, skipped, neutral, pending, wrong-App
   or unreadable results block clearance. Legacy statuses cannot establish an
   App-bound identity. `risk-gate`, `pr-template` and `ai-review` are the only
   self-produced exceptions: this evaluation validates template/review locally
   and checks their expected publisher App. Every other context remains required.
4. A complete changed-file list and consistent rereads of PR bindings, filenames,
   reviews, checks, protection, label events, label receipts and live-base
   ancestry. Unknown or changing evidence never becomes approval.

High-risk changes also need a head-bound clearing label. After the exact-head
clean review and all other required contexts are green, an agent may add
`agent-approved`, record its addition in the ledger and wait for risk-gate.
The gate then says `NOT confirmed by the owner`. `owner-approved` remains an
optional personal confirmation; agents must never add or remove it. Neither
label bypasses review or required checks.

The separate recorder binds the authenticated label delivery's head, PR number
and uniquely matched timeline event to `clearing-label`. Evaluation requires the
same currently live event and the record on the current head. Revoked/re-added,
stale, delayed or ambiguous same-second events cannot reuse an old receipt.
Legacy commit statuses remain appendable: the receipt is a head/event binding,
not a cryptographic attestation of a human or a dedicated publisher. Restrict
status writers and require the independent review bot's fresh merge readback.
No token grants or settings are changed by this source patch.

## Recovery and trust

All events resolve to a per-repository/per-PR serialized writer without cancelling
an active evaluation. Base pushes, the existing six-hour sweep and PR closes
re-evaluate current open PRs through that same writer. Synchronize also refreshes
siblings still carrying a shared-head collision error. Different open PRs sharing
a head are blocked both before and after evidence collection; a closed PR cannot
publish over its former sibling's statuses.

The discovery matrix replaces self-dispatch for recovery, so `actions: write` is
unnecessary. The recorder remains independent of the evaluation concurrency group.
Check/status/comment events and the named native `workflow_run` triggers refresh
evidence. Maintain the workflow-name list when required native workflows change.
API errors use fixed redacted diagnostics. No job checks out or executes candidate
code, reads production secrets, changes labels, merges or deploys.

A passing status is a snapshot, not a transaction with mutable GitHub evidence.
Native protection and the established merge bot must recheck the exact candidate.
Offline tests do not prove hosted permissions, event delivery or runtime adoption.
Unreadable protection APIs block the gate. The shadow observer remains SHADOW,
with `merge_authorized=false`; its trust and required native contexts are unchanged.

## Live deployment boundary

Source merge is not deployment authority. Only deployment to live trading needs
owner authorization as the deployment touchpoint; actual Secrets/IAM changes and
destructive data/resource deletions still escalate to the owner. Removing a source
file is not by itself deletion of production data. Live trading, Kelly and all
stop-loss switches stay OFF. A label, Codex marker or green gate authorizes none
of these operations.

The following is a concrete **configuration sketch**, not an installed Environment
or a runnable deployer. Configure a fixed `live-trading` GitHub Environment using
one numeric owner reviewer ID, prevent self-review, disable administrator bypass,
and permit only protected branches:

```json
{
  "wait_timer": 0,
  "reviewers": [{"type": "User", "id": "<numeric-owner-id>"}],
  "prevent_self_review": true,
  "can_admins_bypass": false,
  "deployment_branch_policy": {
    "protected_branches": true,
    "custom_branch_policies": false
  }
}
```

Replace the placeholder with an actual number only in the authorized settings
operation. Verify plan/feature support first. The initiating agent must use its
own App/bot identity: a shared owner login cannot prove human approval and may
prevent the owner from approving their own run.

A trusted default-branch deployment workflow must use `workflow_dispatch`, accept
only a full candidate SHA, reject non-default-branch dispatch and arbitrary
targets/commands, and serialize deployment with `cancel-in-progress: false`.
Its credential-free preflight must validate main ancestry, independent review,
required checks, allowed target and verified artifact provenance/digest; dry-run
and display the exact target/revision/artifact/plan tuple before approval. The
live-mutating job must declare the following fixed boundary:

```yaml
if: github.ref == 'refs/heads/main'
environment:
  name: live-trading
permissions:
  contents: read
  id-token: write
```

After Environment approval, revalidate the frozen tuple; any change needs new
approval. Obtain only an environment-bound OIDC identity and deploy the verified
artifact through trusted workflow code. If local actions are used, checkout must
be pinned to the trusted workflow revision with `persist-credentials: false`.
Read back target revision/state afterward; unknown mutation results must not be
blindly retried. Approval is for the deployment scope, not each paper trade.

The cloud OIDC trust/role must bind repository, environment and the trusted
workflow identity/revision; no equivalent production secret or role may be
available outside the protected job. A required workflow policy check, executed
from independently protected trusted code, must reject missing/variable
Environments, production credentials/OIDC in other jobs, candidate-code execution
with production authority, extra triggers/targets and changes to the deployment
trust boundary. YAML alone cannot enforce cloud trust. Settings/trust writes must
remain outside implementation and merge agents' authority. Actual Secrets/IAM
changes and destructive deletion use similarly owner-protected scoped workflows.
This PR creates no Environment, cloud binding, workflow deployer or settings.

## Adoption and verification

This change applies only to this metadata repository until separately adopted.
The organization style guide documents the recommended contract; copying prose
does not change another repository's installed gate. Existing required checks
and branch protection remain mandatory. The root `PROPOSAL.md` naming exception
from the base is retained without widening other naming rules.

`node --test scripts/test-risk-gate.cjs scripts/test-governance-shadow.cjs` runs
actual embedded workflow code with fake native APIs. Run all Python style/scanner
suites, `python scripts/check_style.py --phase 2`, and actionlint when available.
Report focused/full counts and fail-before/pass-after evidence separately from
hosted checks. Rollback requires a separately authorized normal reviewed change;
never force-push, change labels or weaken native protection to roll back.
