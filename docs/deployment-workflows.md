# Reusable container release

Call `.github/workflows/deploy-job.yml` at an immutable commit from a manual
workflow. The caller grants only `id-token: write`. For each target, create a GitHub
Environment that allows releases from its reviewed branch and bind the cloud
trust to that repository, environment, caller workflow and the pinned reusable
workflow. For Google Cloud, match the immutable repository and owner IDs and the
manual event. For Azure, bind the immutable repository subject, environment and
reusable workflow in the federated subject, and restrict the allowed caller
branch in the GitHub Environment.

Set the following variables in that environment. Use one environment per target.

| Variable | Purpose |
| --- | --- |
| `DEPLOY_RESOURCE` | Full Container Apps Job resource ID, Cloud Run Job name, or Cloud Run Service name |
| `DEPLOY_PREVIOUS_IMAGE`, `DEPLOY_CANDIDATE_IMAGE` | Previous and candidate images from the same registry repository, each pinned by digest |
| `DEPLOY_CLIENT_ID`, `DEPLOY_TENANT_ID`, `DEPLOY_SUBSCRIPTION_ID` | Azure federation identifiers |
| `DEPLOY_WIF_PROVIDER`, `DEPLOY_SERVICE_ACCOUNT` | Google federation identifiers |

To keep resource identifiers and image digests out of public run logs, store
the resource, images, and Google federation identifiers as protected Environment
secrets. Pass the corresponding names explicitly in the caller's `secrets`
map. Do not set same-named variables for a target that uses masked values.
Existing variable-based callers remain supported.

Use the `verify` operation to check OIDC and the expected current image
without changing the resource. Set `DEPLOY_PREVIOUS_IMAGE` to the expected
current image. On a Service, verify checks the serving revision, including
when the template already holds a zero-traffic candidate. A Service deploy
requires both the serving revision and the configured template to match the
expected source image. A candidate image is required only for deploy or rollback.
Verify checks access to read the target. Test image updates on a separate
isolated environment before enabling production releases.

## Jobs

Select `azure` or `gcp` as the provider, and `deploy` or `rollback` as the
operation. An update requires one container and the expected current digest.
The workflow reads back the new digest and the job settings after the update.
If the update result is uncertain, inspect the cloud job before dispatching a
second operation. The caller checks any external schedule or state binding
separately. Provisioning, schedule changes, smoke execution and registry access
are managed outside this workflow. Keep the job's runtime identity separate
from the GitHub release identity.

## Cloud Run Services

Select `gcp-service` as the provider and `verify` or `deploy` as the operation. Use a resource
name of the form `projects/<project>/locations/<region>/services/<service>`. The
service must have internal ingress, invoker IAM enabled, one container with the
expected image, and one revision serving 100% of traffic without tags.

The workflow pins 100% traffic to the currently serving revision and updates
the image in the same request. It checks the new revision's digest and image
import directly, since a revision without traffic or a tag may be retired
without becoming the service's latest ready revision. The result verifies
staging and routing, with HTTP acceptance handled separately. Traffic promotion
and routing rollback are outside this workflow.

Scope the release identity to the target service and its revisions with
`run.services.get`, `run.services.update`, and `run.revisions.get`. Grant
permission to act as its runtime identity and to read the specified image
repository where required. If a run reports an uncertain result, inspect the
service and candidate revision before dispatching another release.

## Azure Blob packages

Call `.github/workflows/deploy-azure-blob.yml` at an immutable commit from a
manual workflow. Use a protected Environment with its own OIDC identity.
Scope it to read and write blobs in the package container and keep the runtime
identity separate. The workflow does not require a Storage account key.

Set these masked configuration values as Environment secrets so public logs
keep storage identifiers and package digests private. They do not authenticate
requests. Configure `DEPLOY_CLIENT_ID`, `DEPLOY_TENANT_ID`, `DEPLOY_STORAGE_ACCOUNT`,
`DEPLOY_CONTAINER`, `DEPLOY_BLOB`, and `DEPLOY_PREVIOUS_SHA256`.
Pass these names and the optional candidate digest explicitly in the caller's
`secrets` map. The protected Environment supplies the values at runtime.
Use `verify` to check the active package. To deploy, stage the approved ZIP
at `releases/<sha256>.zip` in the same private container, set
`DEPLOY_CANDIDATE_SHA256`, then dispatch `deploy`.

The workflow validates both digests, creates a backup at
`rollback/<previous-sha256>.zip`, and updates the live object only if its
original ETag still matches. It reads back the package using the returned
ETag. Dispatch `rollback` with the same digest pair to restore the backup
only when the expected candidate is live. A failed conditional write
requires readback before another operation.

The digest caller may pass `source-artifact`, a same-run artifact containing
exactly `python/scripts/account_daily_digest.py`, `python/scripts/account_daily_facts.py`,
`python/scripts/azure_timer_digest.py`, and `python/scripts/cloud_run_daily_digest.py`
from its reviewed main commit.
Grant that caller `actions: read`. The shared workflow replaces only those
existing ZIP members and retains the other package contents and entry metadata.
It uses uncompressed ZIP entries so the protected candidate digest is stable
across runner platforms. Set both fixed digests before dispatching a release.
With this artifact, `verify` rebuilds and checks the candidate without writes;
`deploy` stages it with create-only semantics, reads it back, then uses the
same backup and ETag checks. `rollback` uses the saved package without an overlay.
The caller must check main CI before uploading the source artifact. Updating
the reusable workflow pin also requires updating the existing federated trust
to that reviewed immutable commit; it does not require broader storage access.

## Check CI before artifact publication

Call `QuantStrategyLab/.github/actions/verify-main-ci` at an immutable commit
before a publish step. Grant the job `actions: read` and provide its GitHub
token as `GH_TOKEN`. The action requires the latest run of `ci.yml` on
`main` to have completed successfully. Set `CI_WORKFLOW` or `VERIFY_BRANCH`
when the repository uses a different CI workflow or branch.

The caller selects when to run the check and owns the market-specific
validation, storage credentials and write plan.

## Cloudflare Workers

Call `.github/workflows/deploy-cloudflare-worker.yml` at an immutable commit from a
manual workflow (`workflow_dispatch` on `refs/heads/main`). Use a protected GitHub
Environment whose scoped Cloudflare API token only permits Worker Scripts and
Deployments on the target account (`<account-id>`).

Store target identifiers and pinned version UUIDs as protected Environment secrets
and pass them explicitly in the caller's `secrets` map so public workflow logs do
not disclose account or script names (`example-worker`):

| Secret | Purpose |
| --- | --- |
| `CF_API_TOKEN` | Scoped Cloudflare Workers edit token |
| `CF_ACCOUNT_ID` | 32-character hex Cloudflare account identifier |
| `CF_WORKER_SCRIPT_NAME` | Target Worker script name |
| `CF_EXPECTED_VERSION_ID` | Expected baseline Worker version UUID |
| `CF_CANDIDATE_VERSION_ID` | Candidate Worker version UUID (`deploy` and `rollback`) |

Use `verify` to check that a single version serves 100% traffic and matches
`CF_EXPECTED_VERSION_ID` with no writes. Use `deploy` to confirm the baseline,
verify that `CF_CANDIDATE_VERSION_ID` exists, promote it to 100% traffic, and read
back `/deployments`. Use `rollback` with the same pair of UUIDs to restore
`CF_EXPECTED_VERSION_ID` when the candidate is live.

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

## Cloudflare Isolation and Credential Hygiene

- Keep `QuantStrategyLab` edge Workers, KV namespaces, and R2 archive buckets in a
  dedicated Cloudflare Account isolated from personal or campus projects.
- Scope Cloudflare API tokens strictly to the target account and required resources
  (avoid account-wide or global keys), and enforce a 90-180 day expiration.
- Never create non-expiring Google Cloud service account JSON keys; use Workload
  Identity Federation (WIF) for CI/CD and short-lived impersonation for local ops.
- Keep smoke-test Workers ephemeral: delete temporary smoke Workers and KV
  namespaces immediately after validation.
