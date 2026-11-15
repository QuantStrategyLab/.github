# Naming conventions

This repository organization uses one naming layout across GitHub repositories,
Google Cloud projects, Secret Manager secrets, Artifact Registry repositories,
and Cloudflare Workers so automation, access policies, and cleanup rules apply
uniformly without per-target special cases.

## GitHub repositories

Repository names use `PascalCase` without underscores or hyphens, grouped by
role:

- Shared libraries, runtime configuration, AI coordination, and internal
  operations use the `Quant` prefix (`QuantPlatformKit`, `QuantRuntimeSettings`,
  `QuantAIService`, `QuantInternalOps`).
- Broker integration repositories use `<Broker>Platform` (`BinancePlatform`,
  `CharlesSchwabPlatform`, `FirstradePlatform`, `InteractiveBrokersPlatform`,
  `LongBridgePlatform`).
- Market strategy and snapshot pipeline repositories use
  `<Market>Strategies` and `<Market>SnapshotPipelines` (`UsEquityStrategies`,
  `HkEquityStrategies`, `CnEquityStrategies`).
- Dedicated infrastructure and static site exceptions keep their established
  names (`IBKRGatewayManager`, `SchwabTokenAutoRefresher`,
  `.github`, `quantstrategylab.github.io`).

## Google Cloud projects

- Project IDs use lowercase `kebab-case`: `qsl-<platform>-<env>` for new
  projects, avoiding spaces in project display names.
- Every active quant project carries the canonical resource labels:
  - `owner`: `qsl`
  - `system`: `qsl`
  - `platform`: `binance`, `schwab`, `firstrade`, `ibkr`, `longbridge`, or `qsl`
  - `env`: `prod`, `paper`, or `shared`

## Google Cloud Secret Manager

- New and migrated secret IDs use lowercase `kebab-case` matching
  `^[a-z0-9]+(-[a-z0-9]+)*$`:
  `<platform>-<component>-<credential>[-<scope>]`
  (for example, `<platform>-oauth-token-<scope>`).
- Every secret carries at minimum `owner=qsl`, `platform=<platform>`, and
  `env=<prod|paper|shared>`. Add `account=<alias>` or `purpose=<role>` when
  scoping per-account or auxiliary credentials.
- Legacy `snake_case` secrets remain tagged with
  `naming_status=legacy-snake-case` until cut over cleanly inside a scheduled
  maintenance window; never maintain duplicate live values under both names.
- Only the active secret version stays `ENABLED`; rotated older versions are
  `DESTROY`ed once no Cloud Run template, active revision, or job pins them.

## Artifact Registry

- Docker repositories use lowercase `kebab-case` names.
- Releases deploy by immutable digest rather than mutable floating tags.
- Automated cleanup policies protect tags prefixed with `keep-`, `prod-`,
  `live-`, and `lkg-` alongside the most recent 5 versions.

## Cloudflare Workers and KV

- Worker script names use lowercase `kebab-case` (`qsl-<service>`).
- KV namespace titles use lowercase `kebab-case` (`qsl-<service>-<purpose>`),
  with Worker environment bindings written in `UPPER_SNAKE_CASE`
  (`STRATEGY_SWITCH_CONFIG`, `OAUTH_KV`).
