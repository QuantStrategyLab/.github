"""Regression tests for the reusable workflow's inline release logic."""

from copy import deepcopy
from pathlib import Path
from textwrap import dedent
import unittest
from unittest.mock import Mock, patch


WORKFLOW = Path(__file__).resolve().parents[1] / ".github/workflows/deploy-job.yml"
RESOURCE = "projects/example-project/locations/example-region/services/example-service"
URL = "https://run.googleapis.com/v2/" + RESOURCE
PREVIOUS = "registry.example.com/example/image@sha256:" + "1" * 64
CANDIDATE = "registry.example.com/example/image@sha256:" + "2" * 64
BASELINE = "example-service-00001-base"
NEW_REVISION = "example-service-00002-next"
PINNED_TRAFFIC = [
    {"type": "TRAFFIC_TARGET_ALLOCATION_TYPE_REVISION", "revision": BASELINE, "percent": 100}
]


def service_before():
    return {
        "generation": "1",
        "observedGeneration": "1",
        "etag": "example-etag",
        "ingress": "INGRESS_TRAFFIC_INTERNAL_ONLY",
        "defaultUriDisabled": True,
        "terminalCondition": {"state": "CONDITION_SUCCEEDED"},
        "traffic": [{"type": "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST", "percent": 100}],
        "trafficStatuses": [{"revision": BASELINE, "percent": 100}],
        "latestCreatedRevision": RESOURCE + "/revisions/" + BASELINE,
        "latestReadyRevision": RESOURCE + "/revisions/" + BASELINE,
        "template": {"containers": [{"image": PREVIOUS, "command": ["serve"]}]},
    }


class CloudRunServiceReleaseTest(unittest.TestCase):
    def setUp(self):
        script = WORKFLOW.read_text().split("python3 -u - <<'PY'\n", 1)[1].rsplit("\n          PY", 1)[0]
        self.workflow = {"__name__": "release_workflow"}
        exec(compile(dedent(script), str(WORKFLOW), "exec"), self.workflow)
        self.before = service_before()
        self.serving = {"containers": [{"image": PREVIOUS}]}
        self.after = deepcopy(self.before)
        self.after.update(
            generation="2",
            observedGeneration="2",
            traffic=PINNED_TRAFFIC,
            latestCreatedRevision=RESOURCE + "/revisions/" + NEW_REVISION,
        )
        self.after["template"]["containers"][0]["image"] = CANDIDATE
        self.revision = {
            "containers": [{"image": "mirror.example.com/image@" + CANDIDATE.split("@")[1]}],
            "conditions": [
                {"type": "Ready", "state": "CONDITION_SUCCEEDED", "revisionReason": "RETIRED"},
                {"type": "ContainerReady", "state": "CONDITION_SUCCEEDED"},
            ],
        }

    def release(self, responses, operation="deploy"):
        api = Mock(side_effect=responses)
        self.workflow["request"] = api
        with patch.dict("os.environ", {"GOOGLE_ACCESS_TOKEN": "synthetic-test-token"}):
            self.workflow["release_service"](RESOURCE, PREVIOUS, CANDIDATE, operation)
        return api

    def test_reads_retired_revision_without_following_latest_ready(self):
        api = self.release([self.before, self.serving, {}, self.after, self.revision])
        self.assertEqual(api.call_args_list[1].args[0], URL + "/revisions/" + BASELINE)
        args = api.call_args_list[2].args
        self.assertEqual(args[0], URL + "?updateMask=template,traffic")
        self.assertEqual(args[2], "PATCH")
        self.assertEqual(args[3], {
            "name": RESOURCE,
            "etag": "example-etag",
            "template": self.after["template"],
            "traffic": PINNED_TRAFFIC,
        })
        self.assertEqual(api.call_args.args[0], URL + "/revisions/" + NEW_REVISION)
        self.assertEqual(self.before["template"]["containers"][0]["image"], PREVIOUS)

    def test_rejects_tagged_split_or_public_service_before_update(self):
        for field, value, reason in (
            ("traffic", [{"tag": "candidate"}], "without traffic tags"),
            ("trafficStatuses", [{"revision": BASELINE, "percent": 50}], "at 100%"),
            ("ingress", "INGRESS_TRAFFIC_ALL", "internal ingress"),
            ("invokerIamDisabled", True, "invoker IAM"),
        ):
            with self.subTest(field=field):
                with self.assertRaisesRegex(RuntimeError, reason):
                    self.release([{**self.before, field: value}])
                self.workflow["request"].assert_called_once()

    def test_rejects_candidate_that_receives_traffic(self):
        self.after["trafficStatuses"] = [{"revision": NEW_REVISION, "percent": 100}]
        with self.assertRaisesRegex(RuntimeError, "Serving revision changed"):
            self.release([self.before, self.serving, {}, self.after])

    def test_rejects_unconfirmed_image_import(self):
        self.revision["conditions"][1]["state"] = "CONDITION_FAILED"
        with self.assertRaisesRegex(RuntimeError, "revision condition"):
            self.release([self.before, self.serving, {}, self.after, self.revision])

    def test_rejects_routing_rollback(self):
        with self.assertRaisesRegex(ValueError, "only verify or zero-traffic deploy"):
            self.release([], operation="rollback")
        self.workflow["request"].assert_not_called()

    def test_service_verify_reads_without_updating(self):
        revision = {"containers": [{"image": PREVIOUS}]}
        api = self.release([self.before, revision], operation="verify")
        self.assertEqual([call.args[0] for call in api.call_args_list], [URL, URL + "/revisions/" + BASELINE])

    def test_service_verify_checks_serving_image_after_zero_traffic_stage(self):
        revision = {"containers": [{"image": PREVIOUS}]}
        api = self.release([self.after, revision], operation="verify")
        self.assertEqual([call.args[0] for call in api.call_args_list], [URL, URL + "/revisions/" + BASELINE])

    def test_service_verify_rejects_staged_image_when_different_image_serves(self):
        with self.assertRaisesRegex(RuntimeError, "Serving revision"):
            self.release([self.before, self.revision], operation="verify")

    def test_service_deploy_rejects_wrong_serving_image_even_if_template_matches(self):
        with self.assertRaisesRegex(RuntimeError, "Serving revision"):
            self.release([self.before, self.revision])
        calls = self.workflow["request"].call_args_list
        self.assertEqual([call.args[0] for call in calls], [URL, URL + "/revisions/" + BASELINE])
        self.assertTrue(all(len(call.args) == 2 for call in calls))

    def test_service_deploy_rejects_template_drift_even_if_serving_image_matches(self):
        with self.assertRaisesRegex(RuntimeError, "expected source image"):
            self.release([self.after, self.serving])
        calls = self.workflow["request"].call_args_list
        self.assertEqual([call.args[0] for call in calls], [URL, URL + "/revisions/" + BASELINE])
        self.assertTrue(all(len(call.args) == 2 for call in calls))

    def test_job_verify_requires_only_current_image_and_does_not_update(self):
        job = Mock()
        job.template.return_value = {"containers": [{"image": PREVIOUS}]}
        self.workflow["check_images"](PREVIOUS, "", "verify")
        self.workflow["release"](job, PREVIOUS, "", "verify")
        job.read.assert_called_once()
        job.update.assert_not_called()


if __name__ == "__main__":
    unittest.main()
