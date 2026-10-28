#!/usr/bin/env python3
"""Tests for big_ingest.py. Run: python3 tests/test_big_ingest.py"""
import csv
import os
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools"))
import big_ingest as bi

YML = """pipelines:
  custom:
    1-regular:
      - step:
          name: Download
          size: 2x
    w-big:   # the big one
      - step:
          name: Download and commit
          size: 2x
          image: python:3.12
    z-other:
      - step:
          size: 8x
"""


class TestRecordSize(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.cwd = os.getcwd()
        os.chdir(self._tmp.name)
        self.addCleanup(os.chdir, self.cwd)

    def test_zip_and_dir(self):
        os.makedirs("123")
        Path("123/a.txt").write_bytes(b"x" * 1000)
        with zipfile.ZipFile("123.zip", "w") as zf:
            zf.writestr("a.txt", b"x" * 1000)
        data = bi.record_size("123", "cache", "generated/s.csv", 100)
        self.assertEqual(data["unzipped_bytes"], 1000)
        self.assertEqual(data["small_bytes"], 1000)
        self.assertGreater(data["zip_bytes"], 0)
        with open("generated/s.csv", newline="") as fh:
            row = next(csv.DictReader(fh))
        self.assertEqual({k: (v if k == "project" else int(v)) for k, v in row.items()}, data)

    def test_zip_only_uses_central_directory_and_cache(self):
        os.makedirs("cache")
        with zipfile.ZipFile("cache/123.zip", "w") as zf:
            zf.writestr("a.txt", b"x" * 500)
        data = bi.record_size("123", "cache", "generated/s.csv", 100)
        self.assertEqual(data["unzipped_bytes"], 500)

    def test_small_bytes_excludes_files_over_the_limit(self):
        os.makedirs("123")
        Path("123/small.txt").write_bytes(b"x" * 1000)
        Path("123/big.dat").write_bytes(b"x" * (2 * bi.BYTES_PER_MB))
        data = bi.record_size("123", "cache", "generated/s.csv", 1)  # limit 1 MB
        self.assertEqual(data["small_bytes"], 1000)
        self.assertEqual(data["unzipped_bytes"], 1000 + 2 * bi.BYTES_PER_MB)

    def test_small_bytes_from_zip_directory(self):
        with zipfile.ZipFile("123.zip", "w") as zf:
            zf.writestr("small.txt", b"x" * 1000)
            zf.writestr("big.dat", b"x" * (2 * bi.BYTES_PER_MB))
        data = bi.record_size("123", "cache", "generated/s.csv", 1)
        self.assertEqual(data["small_bytes"], 1000)

    def test_nothing_found(self):
        with self.assertRaises(SystemExit):
            bi.record_size("123", "cache", "generated/s.csv", 100)


class TestExceeds(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.path = os.path.join(self._tmp.name, "s.csv")

    def _write(self, zip_mb, unzipped_mb, small_mb=None):
        mb = bi.BYTES_PER_MB
        small = "" if small_mb is None else small_mb * mb
        Path(self.path).write_text(
            "project,zip_bytes,unzipped_bytes,small_bytes\n"
            f"123,{zip_mb * mb},{unzipped_mb * mb},{small}\n")

    def test_below(self):
        self._write(100, 300, 0)
        self.assertFalse(bi.exceeds(self.path, 1000, 100))  # max(400, 300) + 100 = 500

    def test_unpacking_is_the_peak_when_few_small_files(self):
        self._write(400, 500, 0)
        self.assertFalse(bi.exceeds(self.path, 1000, 100))  # max(900, 500) + 100 = 1000
        self.assertTrue(bi.exceeds(self.path, 999, 100))

    def test_committing_is_the_peak_when_many_small_files(self):
        self._write(100, 500, 500)
        self.assertFalse(bi.exceeds(self.path, 1100, 100))  # max(600, 1000) + 100 = 1100
        self.assertTrue(bi.exceeds(self.path, 1099, 100))

    def test_unknown_small_bytes_assumes_git_copies_everything(self):
        self._write(100, 500)
        self.assertTrue(bi.exceeds(self.path, 1099, 100))   # unzipped + unzipped + margin = 1100
        self.assertFalse(bi.exceeds(self.path, 1100, 100))

    def test_missing_file_counts_as_exceeding(self):
        self.assertTrue(bi.exceeds(self.path, 1000, 100))


class TestSetVmSize(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.path = os.path.join(self._tmp.name, "p.yml")
        Path(self.path).write_text(YML)

    def test_changes_only_target_pipeline(self):
        self.assertTrue(bi.set_vm_size(self.path, "w-big", "4x"))
        self.assertEqual(Path(self.path).read_text(), YML.replace(
            "Download and commit\n          size: 2x", "Download and commit\n          size: 4x"))

    def test_idempotent(self):
        bi.set_vm_size(self.path, "w-big", "4x")
        self.assertFalse(bi.set_vm_size(self.path, "w-big", "4x"))

    def test_unknown_pipeline(self):
        with self.assertRaises(SystemExit):
            bi.set_vm_size(self.path, "nope", "4x")


class TestReadConfig(unittest.TestCase):
    def test_inline_comment_is_stripped(self):
        with tempfile.TemporaryDirectory() as d:
            cfg = os.path.join(d, "config.yml")
            Path(cfg).write_text("bigingest_threshold_mb: 6144   # why\nmain: a#b\n# note\n")
            out = bi.read_config(cfg)
        self.assertEqual(out["bigingest_threshold_mb"], "6144")
        self.assertEqual(out["main"], "a#b")


class TestNeeds4xCli(unittest.TestCase):
    def test_non_numeric_config_value_is_an_error_not_no(self):
        with tempfile.TemporaryDirectory() as d:
            cfg = os.path.join(d, "config.yml")
            Path(cfg).write_text("bigingest_threshold_mb: lots\nbigingest_margin_mb: 25\n")
            self.assertEqual(bi.main(["needs-4x", "--config", cfg]), 2)


class TestPipelineVariables(unittest.TestCase):
    def test_env_wins_over_config(self):
        with tempfile.TemporaryDirectory() as d:
            cfg = os.path.join(d, "config.yml")
            Path(cfg).write_text("openicpsr: 111\nzenodo:\njiraticket: AEAREP-1\n")
            out = bi.pipeline_variables(cfg, {"jiraticket": "AEAREP-2"})
        self.assertEqual(out, [{"key": "jiraticket", "value": "AEAREP-2"},
                               {"key": "openICPSRID", "value": "111"}])


if __name__ == "__main__":
    unittest.main()
