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

Use the `verify` operation to check OIDC and the expected current image
without changing the resource. Set `DEPLOY_PREVIOUS_IMAGE` to the expected
current image. A candidate image is required only for deploy or rollback.
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
