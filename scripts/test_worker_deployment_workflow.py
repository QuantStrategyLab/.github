"""Regression tests for the shared Cloudflare Worker release contract."""

from pathlib import Path
from textwrap import dedent
import unittest
from unittest.mock import Mock, patch


WORKFLOW = Path(__file__).resolve().parents[1] / ".github/workflows/deploy-cloudflare-worker.yml"
PREVIOUS_ID = "11111111-1111-4111-8111-111111111111"
CANDIDATE_ID = "22222222-2222-4222-8222-222222222222"
OTHER_ID = "33333333-3333-4333-8333-333333333333"
ACCOUNT_ID = "0123456789abcdef0123456789abcdef"
SCRIPT_NAME = "example-worker"


class CloudflareWorkerReleaseTests(unittest.TestCase):
    def setUp(self):
        script = WORKFLOW.read_text(encoding="utf-8").split("python3 -u - <<'PY'\n", 1)[1].rsplit("\n          PY", 1)[0]
        self.module = {"__name__": "worker_release"}
        exec(compile(dedent(script), str(WORKFLOW), "exec"), self.module)
        self.deployer = Mock()

    def test_verify_reads_deployments_without_mutating(self):
        self.deployer.list_deployments.return_value = [
            {"versions": [{"version_id": PREVIOUS_ID, "percentage": 100}]}
        ]
        self.module["release"](self.deployer, PREVIOUS_ID, "", "verify")
        self.deployer.list_deployments.assert_called_once_with()
        self.deployer.get_version.assert_not_called()
        self.deployer.deploy_version.assert_not_called()

    def test_deploy_checks_baseline_and_candidate_then_reads_back(self):
        self.deployer.list_deployments.side_effect = [
            [{"versions": [{"version_id": PREVIOUS_ID, "percentage": 100}]}],
            [{"versions": [{"version_id": CANDIDATE_ID, "percentage": 100}]}],
        ]
        self.deployer.get_version.return_value = {"id": CANDIDATE_ID}
        self.module["release"](self.deployer, PREVIOUS_ID, CANDIDATE_ID, "deploy")
        self.deployer.get_version.assert_called_once_with(CANDIDATE_ID)
        self.deployer.deploy_version.assert_called_once_with(CANDIDATE_ID)
        self.assertEqual(self.deployer.list_deployments.call_count, 2)

    def test_rollback_checks_candidate_is_live_then_restores_previous(self):
        self.deployer.list_deployments.side_effect = [
            [{"versions": [{"version_id": CANDIDATE_ID, "percentage": 100}]}],
            [{"versions": [{"version_id": PREVIOUS_ID, "percentage": 100}]}],
        ]
        self.deployer.get_version.return_value = {"id": PREVIOUS_ID}
        self.module["release"](self.deployer, PREVIOUS_ID, CANDIDATE_ID, "rollback")
        self.deployer.get_version.assert_called_once_with(PREVIOUS_ID)
        self.deployer.deploy_version.assert_called_once_with(PREVIOUS_ID)

    def test_rejects_split_traffic_before_any_mutation(self):
        self.deployer.list_deployments.return_value = [
            {
                "versions": [
                    {"version_id": PREVIOUS_ID, "percentage": 50},
                    {"version_id": CANDIDATE_ID, "percentage": 50},
                ]
            }
        ]
        with self.assertRaisesRegex(RuntimeError, "one active Worker version"):
            self.module["release"](self.deployer, PREVIOUS_ID, CANDIDATE_ID, "deploy")
        self.deployer.get_version.assert_not_called()
        self.deployer.deploy_version.assert_not_called()

    def test_rejects_drifted_live_version_before_mutation(self):
        self.deployer.list_deployments.return_value = [
            {"versions": [{"version_id": OTHER_ID, "percentage": 100}]}
        ]
        with self.assertRaisesRegex(RuntimeError, "expected baseline"):
            self.module["release"](self.deployer, PREVIOUS_ID, CANDIDATE_ID, "deploy")
        self.deployer.deploy_version.assert_not_called()

    def test_rejects_unconfirmed_readback(self):
        self.deployer.list_deployments.side_effect = [
            [{"versions": [{"version_id": PREVIOUS_ID, "percentage": 100}]}],
            [{"versions": [{"version_id": PREVIOUS_ID, "percentage": 100}]}],
        ]
        self.deployer.get_version.return_value = {"id": CANDIDATE_ID}
        with self.assertRaisesRegex(RuntimeError, "readback"):
            self.module["release"](self.deployer, PREVIOUS_ID, CANDIDATE_ID, "deploy")

    def test_rejects_invalid_identifiers_without_leaking_values(self):
        with self.assertRaises(ValueError) as ctx_acct:
            self.module["WorkerDeployer"]("secret-acct-123", SCRIPT_NAME, "synthetic-token")
        self.assertNotIn("secret-acct-123", str(ctx_acct.exception))

        with self.assertRaises(ValueError) as ctx_script:
            self.module["WorkerDeployer"](ACCOUNT_ID, "Bad_Script_Name", "synthetic-token")
        self.assertNotIn("Bad_Script_Name", str(ctx_script.exception))

        with self.assertRaisesRegex(ValueError, "distinct UUID"):
            self.module["release"](self.deployer, PREVIOUS_ID, PREVIOUS_ID, "deploy")

    def test_deployer_http_error_suppresses_account_and_script(self):
        from io import BytesIO
        from urllib.error import HTTPError

        deployer = self.module["WorkerDeployer"](ACCOUNT_ID, SCRIPT_NAME, "synthetic-token")
        err = HTTPError("https://api.cloudflare.com/hidden", 403, "Forbidden", {}, BytesIO(b"secret detail"))
        with patch.object(deployer.opener, "open", side_effect=err):
            with self.assertRaises(RuntimeError) as ctx:
                deployer.list_deployments()
        self.assertNotIn(ACCOUNT_ID, str(ctx.exception))
        self.assertNotIn(SCRIPT_NAME, str(ctx.exception))
        self.assertNotIn("secret detail", str(ctx.exception))
        self.assertIn("HTTP 403", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
