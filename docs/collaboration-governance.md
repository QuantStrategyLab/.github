# Collaboration governance

## Merge prerequisites

The dedicated review-and-merge bot owns PR acceptance and merge disposition.
Before any merge it reads the OPEN PR, full current head and base, changed scope,
native required checks and applicable owner authorization. It also requires a
trusted Codex App comment containing exactly one `codex-review-state:v1` record.
The `code_review.commit_sha` must equal the current full PR head,
`status` must be `completed`, and `has_unresolved_findings` must be `false`.
Both finding flags must be booleans. Findings previously reported and resolved
still require the bot's substantive disposition. Labels, descriptions and a
worker's own receipt cannot substitute for authenticated review evidence.

Missing, stale, malformed, ambiguous, running or unavailable evidence blocks
merge. Re-read the candidate and evidence immediately before disposition;
changes invalidate the previous snapshot. A head-bound marker does not prove
base or scope acceptance. Independent review, native gates and owner approval
remain separate requirements. Never bypass protection to satisfy this policy.

Review happens before merge. Never request a new review on a merged PR,
backfill a marker, or treat a later review as retrospective merge permission.
A historical missing-review exception stays recorded. Preserve existing
findings and evidence; an authorized correction uses a new OPEN PR with its
own review. A clean historical report does not prove deployment or runtime.

## Progress and daily brief

PR state is the source for source-delivery progress. Read current state, Draft
flag, full head/base, marker binding and required checks from the PR. Describe
OPEN/Draft as work under review, CLOSED without merge as closed, and MERGED as
source integrated. In the same record state whether its exact head has a
completed marker and unresolved findings. Unknown evidence remains unknown.

Issue #36 becomes a daily brief derived from those readbacks. It is not a
second mutable progress authority. Each entry links its PR where public and
records its observation time, owner, blocker and exact resume condition.
Preserve unresolved production incidents until production readback proves a
fix or the owner explicitly closes them. Source integration cannot close an
incident, PAPER qualification or runtime acceptance by itself. Private work is
shown only as PAS (private), with no private repository link or identity.

Issue #38 is retired as an instruction and progress channel. Historical content
remains historical; it cannot launch work or authorize an action. Use the
existing coordinator and typed callback receipts for authorized handoffs.
Daily brief describes cadence only: this proposal installs no timer, schedule,
issue editor or external message sender.

## Workflow prerequisite proposal

The reusable [observer](../.github/workflows/governance-acceptance.yml) accepts
`require-codex-marker: true` as an opt-in check. It fails unless authenticated,
current-head completed evidence has no unresolved findings. The existing pinned
policy supplies trusted App identities; callers cannot supply their own.
Read or integrity failures fail the check and publish only fixed diagnostic
fields. Two reads reject candidate or evidence drift. Each run is stateless.

The default remains `false` for existing shadow callers. The workflow always
returns `merge_authorized: false`; a successful prerequisite is necessary
evidence, never merge authority. This proposal changes no caller, trusted
identity, ruleset, branch protection or required-check list. Actual enforcement
requires a separately authorized integration with the dedicated bot and native
controls. Pin both the reusable workflow and policy to the same reviewed
immutable revision before an authorized caller adopts the prerequisite.

The [skill candidate](skills/quant-collaboration/SKILL.md) contains the matching
operator guidance. Repository presence does not install or update a host skill.
The [legacy exception queue](legacy-governance-exceptions.md) preserves the bounded
historical evidence request without requesting reviews on merged PRs.
