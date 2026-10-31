# ADR 0001: Evolve architecture through compatible boundaries

Status: proposed

## Context

QuantStrategyLab consists of independently versioned strategy libraries,
platform applications, artifact producers, shared infrastructure and supporting
services. Shared contracts, platform composition modules, plugin specifications
and compatibility tooling already exist.

Maintenance becomes harder when request handling, configuration parsing,
strategy selection, persistence and presentation change in the same module.
Repeated helpers also increase the cost of consistent changes. Broad moves can
disrupt established imports, serialized artifacts, error classification and
side-effect order. Consumers may use different supported dependency revisions.

The [architecture overview](../architecture.md) distinguishes repository
ownership, package dependencies, artifact flow and optional integrations. These
are related boundaries, but a change to one does not require changing all of
them together.

## Decision

Evolve boundaries within the existing repositories through small, independently
reversible changes. Preserve trading, risk, accounting and execution behavior.

1. Characterize the affected public boundary before moving code. Record return
   values, serialized bytes where relevant, exception types and messages,
   dependency calls and their order.
2. Extract the smallest cohesive function or module. Prefer ordinary functions,
   explicit dependencies and existing extension registries. Reuse shared
   contracts and loaders before adding another abstraction.
3. Preserve existing imports and entrypoints through compatibility exports or
   thin delegation. Retain class identity and serialization names when consumers
   depend on them.
4. Keep shared domain contracts independent of broker implementations. QPK's
   broker and cloud adapters remain edge implementations inside the existing
   package unless a separate packaging decision justifies a split.
5. Keep formulas separate from broker I/O. Platform names may remain in
   compatibility metadata. Move existing monitoring or persistence effects only
   after their lifecycle and observable behavior are covered by tests.
6. Separate structural refactoring from dependency adoption, stricter input
   validation, configuration changes and behavior fixes. Each requires its own
   compatibility assessment.
7. Use the existing QRS bundle, repository-policy and matrix tooling for version
   governance. Record the tested consumer revisions and actual import sources.

The [architecture conventions](../architecture-conventions.md) describe the
implementation details. This proposal adds no automation, deployment behavior or
new organization-wide CI gate.

## Scope of each change

| Step | Scope | Acceptance |
| --- | --- | --- |
| Establish the boundary | Callers, inputs, outputs, dependency source and existing tests | A reproducible baseline and a stated compatibility surface. |
| Extract locally | One cohesive responsibility and compatibility forwarding | Matching behavior on representative success and failure cases. |
| Validate consumers | Materially affected import paths and interfaces | Contract tests against the candidate and the supported consumer versions. |
| Adopt a release | Intentional consumer pin or bundle update | Existing compatibility checks and separately authorized release procedures. |

A change that crosses repository boundaries should identify which consumer
needs it and how that consumer can continue using its existing dependency.
Runtime entrypoints with unresolved behavior or concurrent changes remain in
place until their baseline can be established.

## Alternatives considered

### Replace the trading engine

LEAN, NautilusTrader and Freqtrade provide useful examples of component and
adapter boundaries. Replacing an engine would also change runtime lifecycle,
data representation, execution integration and operational assumptions. No
engine replacement is needed to isolate a parser, remove equivalent duplication
or clarify dependency ownership. Such a migration would need a separate case
and validation plan.

### Introduce a common event bus or service framework

A new bus introduces delivery, ordering, retry and recovery contracts. Existing
direct calls and artifact interfaces should remain where they meet the required
interaction. Events are appropriate when independently owned consumers need a
defined delivery contract; they should not be added solely to reduce visible
imports.

### Consolidate all repeated code immediately

Some copies are deliberately versioned compatibility snapshots. Similar
implementations may differ in encoding, errors, timing or atomicity. Consolidate
only after equivalence is demonstrated. Preserve the source and update policy
for retained copies.

### Split repositories or packages first

Physical separation adds release coordination before it proves a useful
boundary. Establish module ownership and compatibility tests first. Package or
repository extraction can follow when it reduces a demonstrated dependency or
release constraint.

## Consequences

Existing consumers can retain their imports and dependency versions while
internal responsibilities become easier to test. Small changes expose a limited
review surface and can be reverted without a coordinated system migration.

Compatibility forwarding creates temporary duplication. Keep its ownership and
removal criteria in the owning repository; remove it through an explicit
interface change. A local improvement may also leave broader structural issues
for later work. Those limits should be visible in design documentation.

Behavior-preserving work does not establish that the baseline behavior is
correct. Report a discovered defect separately and keep its regression test and
fix distinct from a structural move when their acceptance differs.

## Verification

- Compare the baseline and candidate at the same boundary using fixed synthetic
  or appropriately sanitized fixtures.
- Cover missing, invalid and unknown inputs along with the successful path.
- Check public imports, callable signatures, serialization and exception
  behavior. Observe file, network and persistence call ordering when affected.
- Verify actual module paths as well as installed distribution metadata. Keep
  candidate-source testing explicit.
- Run the owning repository's required checks and the relevant consumer tests.
  Record skips, environment limits and missing results separately.
- Verify that dependency pins, runtime configuration, schemas and operational
  policy remain unchanged unless explicitly part of the change.

## Rollback

Revert the independent refactoring commit and retain the previous public
entrypoints. A local extraction should require no data migration. If a consumer
has adopted a new library version, revert that adoption through its normal
compatibility procedure as a separate change. Keep historical contracts and
test fixtures available for comparison; do not rewrite published history.

## References

- [QPK platform boundaries](https://github.com/QuantStrategyLab/QuantPlatformKit/blob/main/docs/platform-repo-boundaries.md)
- [QPK shared loader decision](https://github.com/QuantStrategyLab/QuantPlatformKit/blob/main/docs/adr/0004-strategy-loader-unification.md)
- [QRS compatibility model](https://github.com/QuantStrategyLab/QuantRuntimeSettings/blob/main/docs/qsl-org-architecture.md)
- [LEAN system overview](https://www.quantconnect.com/docs/v2/lean-engine/getting-started)
- [NautilusTrader adapter guidance](https://nautilustrader.io/docs/latest/developer_guide/adapters/)
- [Freqtrade contributor guide](https://www.freqtrade.io/en/stable/developer/)
