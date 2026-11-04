"""Regression tests for the cross-repository link checker.

Pins the distinction behind issue #28: a `tree/` link names a directory and a
`blob/` link names a file, so each must be resolved against the right set.

Run with `python3 scripts/test_cross_repo_links.py`.
"""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "check_cross_repo_links", Path(__file__).with_name("check_cross_repo_links.py")
)
links = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(links)

FILES = {"compat/bundles/a.json", "docs/guide.md", "README.md"}
DIRS = links.tree_dirs(FILES)
URL = "https://github.com/QuantStrategyLab/Sibling/{mode}/main/{path}"


def check(mode: str, path: str) -> bool:
    hit = links.classify(URL.format(mode=mode, path=path), "Here", "x.md", {}, {"Sibling": "main"})
    assert hit is not None
    _, target_path, kind, note = hit
    assert note == ""
    return links.target_exists(kind, target_path, FILES, DIRS)


class TreeVersusBlob(unittest.TestCase):
    def test_tree_link_to_existing_directory_resolves(self):
        self.assertTrue(check("tree", "compat/bundles"))
        self.assertTrue(check("tree", "compat/bundles/"))
        self.assertTrue(check("tree", "compat"))

    def test_tree_link_to_missing_directory_is_broken(self):
        self.assertFalse(check("tree", "compat/missing"))

    def test_tree_link_to_a_file_is_broken(self):
        self.assertFalse(check("tree", "docs/guide.md"))

    def test_blob_link_to_existing_file_resolves(self):
        self.assertTrue(check("blob", "docs/guide.md"))
        self.assertTrue(check("blob", "docs/guide.md#section"))

    def test_blob_link_to_a_directory_is_broken(self):
        self.assertFalse(check("blob", "compat/bundles"))

    def test_blob_link_to_missing_file_is_broken(self):
        self.assertFalse(check("blob", "docs/missing.md"))

    def test_relative_link_accepts_file_or_directory(self):
        self.assertTrue(links.target_exists("relative", "compat/bundles", FILES, DIRS))
        self.assertTrue(links.target_exists("relative", "README.md", FILES, DIRS))
        self.assertFalse(links.target_exists("relative", "nope", FILES, DIRS))


if __name__ == "__main__":
    unittest.main()
