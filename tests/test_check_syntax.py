#!/usr/bin/env python3
"""Tests for tools/check_syntax.py. Run: python3 tests/test_check_syntax.py"""
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools"))
import check_syntax  # noqa: E402


def write(root, rel, text):
    path = os.path.join(root, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as handle:
        handle.write(text)


class CheckSyntaxTest(unittest.TestCase):
    def test_clean_tree_passes(self):
        with tempfile.TemporaryDirectory() as root:
            write(root, "automations/ok.sh", "#!/bin/bash\nif true; then echo hi; fi\n")
            write(root, "pipelines.yml", "a:\n  - b\n")
            self.assertEqual(check_syntax.main(["--root", root]), 0)

    def test_stray_fi_fails(self):
        with tempfile.TemporaryDirectory() as root:
            write(root, "automations/bad.sh", "#!/bin/bash\necho hi\nfi\n")
            self.assertEqual(check_syntax.main(["--root", root]), 1)

    def test_bad_yaml_fails(self):
        with tempfile.TemporaryDirectory() as root:
            write(root, "docs/myst.yml", "a: [unclosed\n")
            self.assertEqual(check_syntax.main(["--root", root]), 1)


if __name__ == "__main__":
    unittest.main()
