# Governance shadow engine

The reusable `governance-acceptance.yml` workflow observes pull requests without
changing merge authorization. It is public and can be called from repositories
under any owner. Both the workflow reference and `policy-revision` must use the
same full, reviewed central commit. There are no inherited secrets, candidate
checkouts, comment writes, status writes or merge operations.

## Caller contract

Use `pull_request` with opened, synchronize, reopened, edited and ready-for-review
events. Pass the event pull request number, `mode: SHADOW` and the central policy
revision. Use the dedicated `Governance shadow observation` job name; do not add
it to required checks or replace an existing check. Read-only contents, pull
requests and issues permissions suffice. Existing required checks remain separate.
The public workflow requires no organization access-setting change. Hosting
restrictions or an unavailable pin must be reported rather than bypassed.

## Observations and evidence

The engine reads all changed files and verifies file counts, aggregate additions
and deletions, and hunk lengths. Missing or binary patches are unknown. It hashes
the complete scope and central policy. Authority-related paths and prose, test
changes and modified Markdown are conservatively R2; ordinary source changes
are R1. Only narrowly constrained added explanatory prose is an R0 candidate.
These are heuristic observations, never semantic review acceptance.

Native reviews and owner comments may carry a JSON record containing
`schema_version: 1`, `kind: review` or `kind: owner`, `repository`, numeric `pr`,
full `head` and `base`, `scope`, `policy`, `decision: approve` or `decision: revoke`,
`expires_at` and `findings: []`. Findings may also contain optional
`kind: advisory` advice, or `kind: defect` records with a reviewed disposition of
`resolved`, `false_positive` or `obsolete`; unresolved or malformed defects block
review evidence. Digest values come from the candidate summary.
An independent review also needs an APPROVED native review at that head.
Only human identities listed in the pinned policy qualify; the author cannot
approve their own work. Owner comments edited after creation do not qualify.
Newer invalid or revoked bound records dominate older approvals. No label or
provider availability supplies authorization. Default identity lists are empty,
so R1/R2 observations remain pending until a separately reviewed source policy
establishes identities. No identities or settings are provisioned by this pilot.
An unresolved change request survives comment-only reviews and can be cleared
only by a valid later approval from that reviewer or dismissal of the request.

An optional `codex_app_ids` list enables a separate observation of the native
Codex summary comment. The source must be a bot posted through a configured
GitHub App and its review state must name the current head. The observation
distinguishes running, stale, malformed and unresolved findings. An empty list
leaves this observation unconfigured. This signal does not establish full
coverage or base binding, does not accept a review, and never authorizes merge.
Multiple receipt blocks in one comment are ambiguous and reported as unknown.

The final read compares the candidate and evidence with the initial reads.
Failures produce UNKNOWN and a failed, non-required observation job. Reports use
fixed fields, candidate bindings and counts; paths, titles, patches, identities,
comment text and raw API errors are never exported. A green workflow means the
observer ran; it never means the pull request is approved.

## Limits and promotion

`merge_authorized` is always false. Required-check acceptance, baseline-red
exceptions, durable writer admission, atomic freshness, event completeness,
merge-queue support and identity independence from execution are not established.
Review/comment and base-only changes do not currently schedule a new observation;
a later pull request event refreshes the snapshot. This is suitable only for
report-only comparison, not enforcement. There is no persistent decision cache:
parallel or restarted observations independently re-read native state and cannot
mutate repository state. No deployment, publication or live operation is added.

Keep the central PR and pilot callers under review. Callers pin the central
candidate commit; merge the reviewed central source before integrating callers.
The PR check run can exercise the pinned public candidate before that merge,
subject to repository Actions policy. Promote only after native runtime evidence
and separately approved identity, required-check and event-freshness changes.
Rollback consists of reverting only the new caller through a normal reviewed PR;
existing gates stay in place.

## Local verification

Run `node --test scripts/test-governance-shadow.cjs`, the existing Python checker
and secret-scan tests, and `python scripts/check_style.py --phase 2`. The new
`Governance shadow tests` workflow exercises the exact inline reusable code with
fake API responses. Offline tests do not prove hosted execution or adoption.
