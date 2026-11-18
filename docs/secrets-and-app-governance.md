# Secrets and GitHub App governance

This guide defines how repositories in the QuantStrategyLab organization
separate GitHub Actions Secrets from Variables, authenticate unattended
automation, and retire unused credentials and branches.

## Secrets vs. Variables

Store credentials and sensitive material in **Secrets** (masked in logs and
encrypted at rest) and non-sensitive configuration in **Variables**.

| Kind | Storage | Naming pattern | Examples |
| --- | --- | --- | --- |
| Credentials and keys | Secrets | `*_TOKEN`, `*_API_KEY`, `*_PRIVATE_KEY`, `*_SECRET` | `QSL_GITHUB_APP_PRIVATE_KEY`, `BROKER_API_KEY` |
| Non-sensitive config | Variables | `UPPER_SNAKE_CASE` without credential suffixes | URLs, project or target IDs, feature flags, `QSL_GITHUB_APP_ID` |

Rules for organization and repository configuration:

- Never store plaintext credentials, private keys, or bearer tokens in
  Variables, workflow files, or committed configuration.
- Keep organization-wide Variables (such as `RISK_GATE_OWNER` and
  `RISK_GATE_OWNER_ID`) defined at the organization level. Do not create
  same-named repository-level Variables that shadow the organization value
  unless an explicit exception is documented for that repository.
- When a reusable deployment workflow masks resource identifiers or federation
  values, follow [Reusable deployment workflows](deployment-workflows.md) and
  avoid setting same-named Variables alongside Secrets for the same target.

## Long-lived unattended authentication

Prefer short-lived, scoped tokens minted at runtime over static long-lived
credentials:

1. **GitHub automation**: Prefer a GitHub App (`QSL_GITHUB_APP_ID` in
   Variables and `QSL_GITHUB_APP_PRIVATE_KEY` in Secrets) with
   `actions/create-github-app-token` pinned to a full commit SHA. GitHub App
   installation tokens expire automatically after one hour and do not depend on
   a user account's expiring personal access token (PAT) such as
   `QSL_REPO_SYNC_TOKEN` or `SNAPSHOT_REPOSITORY_TOKEN`. By default, the
   minted token inherits all permissions granted to the App installation; the
   workflow `permissions:` block restricts only `GITHUB_TOKEN`. Always pass
   explicit `permission-*` inputs (and `repositories` when narrowing target
   scope) to `actions/create-github-app-token` so the minted token receives
   only the permissions that job needs.
2. **Cloud authentication**: Prefer OpenID Connect (OIDC) federation over
   static service account keys. For Google Cloud, configure Workload Identity
   Federation (`GCP_WORKLOAD_IDENTITY_PROVIDER`) bound to the repository,
   environment, or workflow instead of storing a static `GCP_SA_KEY`. For
   Azure, use federated OIDC credentials as described in
   [Reusable deployment workflows](deployment-workflows.md).
3. **Existing PATs**: Retain legacy PATs only where a GitHub App cannot
   perform the required cross-organization or user-scoped action. Track their
   expiration and migrate remaining callers to GitHub Apps or OIDC when
   supported.

## Lifecycle cleanup

- **Secrets and Variables**: Remove unused Secrets and Variables from
  repository and environment settings when a workflow, integration, or legacy
  PAT is retired. Rotate and destroy superseded cloud secret versions per
  [Naming conventions](naming-conventions.md).
- **Branches**: Delete merged or closed pull request branches promptly
  (including Dependabot and automation branches) so stale heads do not
  accumulate or trigger unnecessary checks.
