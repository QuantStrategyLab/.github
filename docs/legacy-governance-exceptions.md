# Legacy missing-review exception queue

This retained governance exception record tracks the requested eleven-item
historical batch. It does not authorize new reviews on merged PRs, backfilled
markers, corrective implementation or external actions. The first four
references and their order are supplied by the bounded task. The source that
identifies the remaining seven references is missing, so those slots remain
unassigned. This is an incomplete batch, not a claim of eleven verified PRs.

## Priority and evidence

The required first-four order is preserved. Production impact determines the
remaining order once their identities are available; do not guess candidates
from a larger search result. Each named item is MERGED with no matching
current-head marker observed in the readback. This says nothing about whether
an earlier independent review occurred or whether the change was deployed.

| Priority | Reference | Production impact | Evidence disposition | Next condition |
| --- | --- | --- | --- | --- |
| 1 | InteractiveBrokersPlatform #962 | Heartbeat diagnostics and notification policy | Missing current-head marker; runtime policy fix unproved | Retrieve existing evidence; preserve incident until authentic runtime readback |
| 2 | LongBridgePlatform #702 | PAPER identity validation and target selection | Missing current-head marker; historical report has a P2 target-selection finding | Preserve finding and existing repair ownership |
| 3 | QuantPlatformKit #771 | Shared setup contract and release bindings | Missing current-head marker; historical report has two P2 findings | Retain contract/lockfile findings and existing successor evidence |
| 4 | QuantAIService #462 | Monitor configuration and operational diagnosis | Missing current-head marker; historical report is CLEAN, runtime configuration still unproved | Retain clean report separately from the open production incident |
| 5 | Unassigned | Unknown | Original batch reference unavailable | Original batch identity source required |
| 6 | Unassigned | Unknown | Original batch reference unavailable | Original batch identity source required |
| 7 | Unassigned | Unknown | Original batch reference unavailable | Original batch identity source required |
| 8 | Unassigned | Unknown | Original batch reference unavailable | Original batch identity source required |
| 9 | Unassigned | Unknown | Original batch reference unavailable | Original batch identity source required |
| 10 | Unassigned | Unknown | Original batch reference unavailable | Original batch identity source required |
| 11 | Unassigned | Unknown | Original batch reference unavailable | Original batch identity source required |

## Batch handling contract

The established review-and-merge bot owns historical evidence disposition.
Retrieve already-existing reports and bind them to the original head and merge
commit; retain missing evidence explicitly. This queue requests evidence
reconciliation only. It does not dispatch review-after-merge. Concrete known
findings may inform a separately authorized new OPEN corrective PR, which must
pass current pre-merge review and gates. Never rewrite historical authorization.

A completed queue record needs the authenticated original eleven references,
production-impact order after the first four, current source state, original
head/merge bindings in approved evidence storage, existing findings, owner,
blocker and resume condition. Public records show any private reference only
as PAS (private), without links or private identity. No private evidence or
operational resource values belong in this document.
