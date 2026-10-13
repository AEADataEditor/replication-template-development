#!/usr/bin/env python3
"""Tests for get_sivacor_info.py. Run: python3 tests/test_get_sivacor_info.py"""
import os
import sys
import unittest
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools"))
import get_sivacor_info as gsi

VERIFICATION_BOX = "- [x] The reproducibility check was conducted by a trusted verification system"
THIRD_PARTY = "trusted third-party"


class BoxWordingTest(unittest.TestCase):
    def setUp(self):
        patcher = mock.patch.object(gsi, "extract_tro_summary", return_value={})
        patcher.start()
        self.addCleanup(patcher.stop)
        for name in ("format_sivacor_steps", "format_sivacor_environment"):
            p = mock.patch.object(gsi, name, return_value="body")
            p.start()
            self.addCleanup(p.stop)

    def test_replication_steps_checks_verification_system_box(self):
        out = gsi.format_sivacor_replication_steps_insert({})
        self.assertIn(VERIFICATION_BOX, out)
        self.assertNotIn(THIRD_PARTY, out)

    def test_computing_environment_checks_verification_system_box(self):
        out = gsi.format_sivacor_computing_environment_insert({})
        self.assertIn(VERIFICATION_BOX, out)
        self.assertNotIn(THIRD_PARTY, out)


if __name__ == "__main__":
    unittest.main()
