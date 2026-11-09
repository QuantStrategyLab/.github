# Reusable job release

Call `.github/workflows/deploy-job.yml` at an immutable commit from a manual
workflow. The caller grants only `id-token: write`. For each job, create a GitHub
Environment that allows releases from its reviewed branch and bind the cloud
trust to that repository, environment, caller workflow and the pinned reusable
workflow. For Google Cloud, match the immutable repository and owner IDs and the
manual event. For Azure, bind the immutable repository subject, environment and
reusable workflow in the federated subject, and restrict the allowed caller
branch in the GitHub Environment.

Set the following variables in that environment. Use one environment per target.

| Variable | Purpose |
| --- | --- |
| `DEPLOY_RESOURCE` | Full Container Apps Job resource ID or Cloud Run Job resource name |
| `DEPLOY_PREVIOUS_IMAGE`, `DEPLOY_CANDIDATE_IMAGE` | Previous and candidate images from the same registry repository, each pinned by digest |
| `DEPLOY_CLIENT_ID`, `DEPLOY_TENANT_ID`, `DEPLOY_SUBSCRIPTION_ID` | Azure federation identifiers |
| `DEPLOY_WIF_PROVIDER`, `DEPLOY_SERVICE_ACCOUNT` | Google federation identifiers |

Select `azure` or `gcp` as the provider, and `deploy` or `rollback` as the
operation. An update requires one container and the expected current digest.
The workflow reads back the new digest and the job settings after the update.
If the update result is uncertain, inspect the cloud job before dispatching a
second operation. The caller checks any external schedule or state binding
separately. Provisioning, schedule changes, smoke execution and registry access
are managed outside this workflow. Keep the job's runtime identity separate
from the GitHub release identity.
