---
name: quant-collaboration
description: Apply PR review prerequisites and daily-brief rules when coordinating QuantStrategyLab PR delivery. Does not authorize dispatch, merge or production changes.
---
# Quant collaboration

Follow the repository [AGENTS.md](../../../AGENTS.md) and
[collaboration governance](../../collaboration-governance.md). This is a skill
candidate for review; publishing this file does not install it on a host.

- Use the current PR state, Draft flag, head/base and checks as source progress.
  Issue #36 is a daily derived brief; issue #38 is retired.
- The dedicated review-and-merge bot owns acceptance. Before merge require an
  authenticated `codex-review-state:v1` marker with `code_review.commit_sha`
  equal to the current head, `status: completed`, boolean finding flags and
  `has_unresolved_findings: false`. Re-read state before disposition. Marker
  completion alone does not satisfy base/scope review, CI or owner approval.
- Unknown, stale, absent or malformed evidence blocks merge. Never replace
  evidence with a label, worker report or edited PR description.
- Review before merge. Never request review on merged PRs or backfill markers.
  Retain historical exceptions and findings; corrections need an authorized
  new OPEN PR and its own review.
- Keep runtime, PAPER and production incident evidence separate from PR state.
  Preserve unresolved production incidents in the daily brief. Display private
  work only as PAS (private), without private links or repository identities.
- Use only existing authorized handoff paths. Distinguish dispatched, received
  and acknowledged receipts. This skill creates no scheduler, dispatch rights,
  configuration changes, merge rights or production authority.
