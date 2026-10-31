# Architecture conventions

These conventions support the proposed
[incremental architecture boundaries](adr/0001-incremental-architecture-boundaries.md).
They guide implementation and review alongside each repository's engineering
rules. They do not change existing automation, required checks or operating
policy. See the [architecture overview](architecture.md) for repository ownership.

## Module ownership

Name a module for the responsibility it owns. Keep parsing, pure computation,
I/O and presentation separate when their callers or failure modes differ.
Function and file length are review signals; extraction should follow a cohesive
responsibility rather than a fixed line count.

Use a shared module when its consumers share semantics. Compare accepted inputs,
outputs, exceptions, encoding, ordering and side effects before consolidating
similar code. Keep broker-specific behavior in an adapter even when it resembles
another broker's implementation.

QPK contains both shared contracts and edge implementations. Import the narrow
module needed by the caller. Core contracts should not initialize broker SDKs,
storage clients, notification publishers or model services. Platform composition
owns their construction and lifecycle.

## Configuration and constants

Configuration has an owner, a source and an interpretation. Document all three
before moving a value out of code.

| Kind | Preferred owner | Handling |
| --- | --- | --- |
| Deployment resource or endpoint | Deployment configuration | Read at the application boundary; use placeholders in public examples. |
| Runtime selection and binding | Existing runtime configuration model | Preserve its established precedence and validation. |
| Strategy or risk parameter | Owning domain contract and authorized configuration | Preserve value, units, default and meaning during structural changes. |
| Protocol code or schema identifier | Owning contract or adapter | Keep it named and versioned; avoid making invariant values arbitrary runtime options. |
| Parsing or transport option | Owning component | Use a named default with documented units and supported values. |

Parse external values once at their owning boundary and pass typed values inward.
Prefer small configuration groups over passing an entire environment mapping to
every function. An existing public settings object can remain unchanged while
its internal parsing functions are separated.

State the precedence among command-line arguments, environment variables,
configuration files and defaults. Preserve that order during extraction. Useful
diagnostics identify the source of an effective value without exposing secrets
or account identifiers.

Missing, explicit null, empty, zero, false and invalid values are distinct inputs.
Do not introduce truthiness-based fallback where the contract distinguishes
them. A stricter parser changes accepted behavior; propose and test that change
separately from moving the parser.

## Errors and state

Catch an exception where the caller can classify, recover from or report it.
Preserve the cause when translating to a domain-specific error. Avoid converting
unrelated failures into empty results or successful outcomes.

| Observation | Required treatment |
| --- | --- |
| Missing optional input | Apply only the documented optional behavior. |
| Invalid supplied input | Retain the contract's validation result or exception. |
| Unavailable dependency | Report unavailability with its original classification. |
| Ambiguous external result | Keep the unknown outcome and required recovery evidence. |
| Best-effort diagnostic failure | Preserve the documented warning and continuation policy. |

Error messages, return codes and logging are observable interfaces when callers
or operators depend on them. A refactor should not change retry classification,
retry count, timeout, ordering or persistence semantics. Broad exception
handling that is already part of an operational contract needs a dedicated
behavior change before it can be narrowed.

Keep state ownership explicit. Prefer an injected state store, clock or publisher
over process-global lookup. Migrate existing globals with tests for initialization,
reuse, shutdown and failure behavior; moving initialization can change behavior
even when function bodies remain identical.

## Interfaces and extension registration

Use existing protocols, catalogs, manifests, adapter factories and loader entrypoints.
A new interface should describe capabilities required by real consumers.
Avoid a base class that forces unrelated adapters to implement unsupported
operations.

| Change | Compatibility obligations |
| --- | --- |
| Move a function | Preserve its import path, signature, defaults and exceptions. |
| Move a class | Preserve public identity and serialized names where used. |
| Register a strategy or plugin | Update the existing catalog, manifest and capability declaration together. |
| Add an adapter capability | State supported modes and provide matching contract tests. |
| Change an artifact | Version the schema or demonstrate compatibility for existing consumers. |

Use explicit registration at the existing composition boundary. Preserve ordering,
duplicate handling, disabled behavior and unknown-identifier errors. Discovery
must not silently turn a recognized name into an enabled trading capability.

Compatibility aliases should stay small and delegate to one implementation.
Document the owning module and the criteria for eventually removing an alias.
Do not create a second general plugin loader beside an existing one.

## Tests and source identity

Test observable contracts. Use representative success cases and the failure
cases affected by the change. Avoid tests that only repeat an implementation's
private call structure.

For a structural extraction, compare baseline and candidate outputs with the
same fixture and configuration. Include exception type and message, return code,
serialized bytes, dependency arguments, call counts and ordering when those are
part of the affected boundary. Keep canonical serialization tests exact when
hashes or persisted artifacts depend on them.

Keep external services behind test doubles or controlled local fixtures.
Importing a pure module should not require credentials or create an external
session. Existing import-time initialization requires explicit characterization
before it moves.

Distinguish two test environments:

| Environment | Source selection | Evidence |
| --- | --- | --- |
| Consumer compatibility | Declared and locked package versions | Installed metadata and actual imported module paths. |
| Candidate integration | Explicitly selected local candidate sources | Candidate revisions, source paths and the exercised consumers. |

A sibling checkout should not silently replace an installed dependency. If a
repository supports that development mode, select it explicitly and identify it
in test results. A passing test of local sources does not establish compatibility
with a different installed wheel.

Group tests by owned contract or feature. Keep shared fixtures in test support,
with only the scope they need. Retain focused cross-component integration tests
where they prove an interaction that unit tests cannot. When moving tests, check
collection counts, parameter sets and assertions so that coverage is preserved.

Record a skipped test as skipped. Record unavailable dependencies or test
environments as limitations. Run additional checks to resolve a stated risk or a
required gate; test volume alone does not establish correctness.

## Dependency versions and retained copies

Use consumer manifests and locks as the installation record. Use QRS bundles and
repository policy for compatibility expectations. Regenerate the dependency
matrix from those sources instead of editing its derived entries manually. See
the [QRS governance guide](https://github.com/QuantStrategyLab/QuantRuntimeSettings/blob/main/docs/qsl-org-architecture.md)
for existing commands and release boundaries.

Keep package versions, interface versions, artifact schemas and deployment
versions distinct. A shared refactor does not require every consumer to upgrade.
Dependency adoption should identify the consumers affected and preserve their
existing compatibility procedures.

For a retained source snapshot, document its canonical source, license, local
differences and update procedure. An equality check can detect drift, but it
does not prove that the newest upstream implementation is appropriate for every
consumer. Keep test-only support out of production modules.

## Documentation ownership

Each contract or operating procedure has one owning document. Other repositories
link to it and describe only their local differences. Generated references are
updated through their generator inputs. The organization map links to detailed
specifications rather than reproducing their schemas or runtime parameters.

Use an ADR for a decision that affects multiple repositories, changes a public
interface or is costly to reverse. State context, status, decision, alternatives,
compatibility, validation and rollback. Keep repository rules and automated gates
in their existing owning files.

When replacing documentation, update links and identify the replacement. Retain
required research baselines, contracts and historical decisions. Temporary
progress notes and raw operational evidence belong outside public documentation.

Follow the [documentation style guide](STYLE_GUIDE.md). Keep existing translations
consistent with the changed content, and use synthetic resource names in examples.
