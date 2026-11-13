"""Regression tests for the shared Blob release contract."""
from io import BytesIO
from pathlib import Path
from textwrap import dedent
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import Mock
from zipfile import ZipFile


def archive(text):
    with BytesIO() as stream:
        with ZipFile(stream, "w") as package:
            package.writestr("fixture.txt", text)
        return stream.getvalue()


class BlobReleaseTests(unittest.TestCase):
    def setUp(self):
        workflow = Path(__file__).resolve().parents[1] / ".github/workflows/deploy-azure-blob.yml"
        script = workflow.read_text().split("python3 -u - <<'PY'\n", 1)[1].rsplit("\n          PY", 1)[0]
        self.module = {"__name__": "blob_release"}
        exec(compile(dedent(script), str(workflow), "exec"), self.module)
        self.old, self.new = archive("old"), archive("candidate")
        self.previous = self.module["digest"](self.old)
        self.candidate = self.module["digest"](self.new)
        self.headers = {"etag": '"before"', "x-ms-blob-type": "BlockBlob"}
        self.key = "package.zip"
        self.backup = f"rollback/{self.previous}.zip"
        self.source = f"releases/{self.candidate}.zip"
        self.store = Mock()

    def release(self, operation):
        self.module["release"](self.store, self.key, self.previous, self.candidate, operation)

    def test_verify_reads_live_package_only(self):
        self.store.get.return_value = self.old, self.headers
        self.module["release"](self.store, self.key, self.previous, "", "verify")
        self.store.get.assert_called_once_with(self.key)
        self.store.put.assert_not_called()

    def test_deploy_creates_backup_and_writes_live_with_etag(self):
        self.store.get.side_effect = [(self.old, self.headers), (self.new, {}), (self.old, {}), (self.new, {})]
        self.store.put.side_effect = ['"backup"', '"after"']
        self.release("deploy")
        first, second = (call.args for call in self.store.put.call_args_list)
        self.assertEqual(first, (self.backup, self.old, self.headers, {"If-None-Match": "*"}))
        self.assertEqual(second, (self.key, self.new, self.headers, {"If-Match": '"before"'}))
        self.store.get.assert_called_with(self.key, '"after"')

    def test_deploy_rejects_conflicting_backup_before_live_write(self):
        self.store.get.side_effect = [(self.old, self.headers), (self.new, {}), (self.new, {})]
        self.store.put.side_effect = self.module["Conflict"]()
        with self.assertRaisesRegex(RuntimeError, "Rollback backup"):
            self.release("deploy")
        self.store.put.assert_called_once()

    def test_etag_conflict_does_not_retry_live_write(self):
        self.store.get.side_effect = [(self.old, self.headers), (self.new, {}), (self.old, {})]
        self.store.put.side_effect = ['"backup"', self.module["Conflict"]()]
        with self.assertRaisesRegex(RuntimeError, "Read the target before retrying"):
            self.release("deploy")
        self.assertEqual(self.store.put.call_count, 2)
        self.assertEqual(self.store.get.call_count, 3)

    def test_rollback_restores_the_backup(self):
        self.store.get.side_effect = [(self.new, self.headers), (self.old, {}), (self.old, {})]
        self.store.put.return_value = '"restored"'
        self.release("rollback")
        self.store.put.assert_called_once_with(self.key, self.old, self.headers, {"If-Match": '"before"'})
        self.store.get.assert_called_with(self.key, '"restored"')

    def test_stale_live_digest_fails_before_any_write(self):
        self.store.get.return_value = self.new, self.headers
        with self.assertRaisesRegex(RuntimeError, "Live package does not match"):
            self.release("deploy")
        self.store.put.assert_not_called()

    def source_overlay(self):
        directory = TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        root = Path(directory.name)
        for name in self.module["DIGEST_SCRIPTS"]:
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("# reviewed source\n")
        with BytesIO() as stream:
            with ZipFile(stream, "w") as package:
                package.comment = b"retain package metadata"
                for name in sorted(self.module["DIGEST_SCRIPTS"]):
                    package.writestr(name, "# previous source\n")
                package.writestr("dependencies/unchanged.txt", "keep installed dependencies")
            self.old = stream.getvalue()
        self.previous = self.module["digest"](self.old)
        self.new = self.module["overlay_package"](self.old, root)
        self.candidate = self.module["digest"](self.new)
        self.source = f"releases/{self.candidate}.zip"
        return root

    def test_overlay_preserves_all_other_files_and_is_deterministic(self):
        root = self.source_overlay()
        self.assertEqual(self.module["overlay_package"](self.old, root), self.new)
        with ZipFile(BytesIO(self.old)) as old, ZipFile(BytesIO(self.new)) as new:
            self.assertEqual(old.namelist(), new.namelist())
            self.assertEqual(old.comment, new.comment)
            for name in old.namelist():
                expected = b"# reviewed source\n" if name in self.module["DIGEST_SCRIPTS"] else old.read(name)
                self.assertEqual(new.read(name), expected)
                self.assertEqual(old.getinfo(name).external_attr, new.getinfo(name).external_attr)
                self.assertEqual(old.getinfo(name).date_time, new.getinfo(name).date_time)

    def test_overlay_rejects_unexpected_or_missing_source_files(self):
        root = self.source_overlay()
        extra = root / "extra.py"
        extra.write_text("# not part of this release")
        with self.assertRaisesRegex(ValueError, "exactly the three"):
            self.module["overlay_package"](self.old, root)
        extra.unlink()
        (root / next(iter(self.module["DIGEST_SCRIPTS"]))).unlink()
        with self.assertRaisesRegex(ValueError, "exactly the three"):
            self.module["overlay_package"](self.old, root)

    def test_overlay_cannot_add_new_package_paths(self):
        root = self.source_overlay()
        with self.assertRaisesRegex(ValueError, "existing digest script paths"):
            self.module["overlay_package"](archive("no source files"), root)

    def test_verify_checks_overlay_without_staging_or_writing(self):
        root = self.source_overlay()
        self.store.get.return_value = self.old, self.headers
        self.module["release"](self.store, self.key, self.previous, self.candidate, "verify", root)
        self.store.get.assert_called_once_with(self.key)
        self.store.put.assert_not_called()

    def test_overlay_digest_mismatch_fails_before_any_write(self):
        root = self.source_overlay()
        self.store.get.return_value = self.old, self.headers
        with self.assertRaisesRegex(RuntimeError, "fixed candidate SHA-256"):
            self.module["release"](self.store, self.key, self.previous, "1" * 64, "deploy", root)
        self.store.put.assert_not_called()

    def test_overlay_deploy_stages_then_uses_existing_conditional_release(self):
        root = self.source_overlay()
        self.store.get.side_effect = [(self.old, self.headers), (self.new, {}), (self.old, {}), (self.new, {})]
        self.store.put.side_effect = ['"staged"', '"backup"', '"after"']
        self.module["release"](self.store, self.key, self.previous, self.candidate, "deploy", root)
        calls = self.store.put.call_args_list
        self.assertEqual(calls[0].args, (self.source, self.new, self.headers, {"If-None-Match": "*"}))
        self.assertEqual(calls[-1].args, (self.key, self.new, self.headers, {"If-Match": '"before"'}))
        self.store.get.assert_called_with(self.key, '"after"')

    def test_overlay_stage_conflict_reads_back_before_touching_live_or_backup(self):
        root = self.source_overlay()
        self.store.get.side_effect = [(self.old, self.headers), (archive("wrong"), {})]
        self.store.put.side_effect = self.module["Conflict"]()
        with self.assertRaisesRegex(RuntimeError, "Staged artifact differs"):
            self.module["release"](self.store, self.key, self.previous, self.candidate, "deploy", root)
        self.store.put.assert_called_once()


if __name__ == "__main__":
    unittest.main()
