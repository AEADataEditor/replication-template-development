#!/usr/bin/env python3
"""Tests for jira_update_deposit_size.py. Run: python3 tests/test_jira_update_deposit_size.py"""
import os
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
import io
import contextlib
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools"))
import jira_update_deposit_size as juds


def _make_zip(path, file_sizes):
    """Create a ZIP at path whose members have the given uncompressed sizes (bytes)."""
    with zipfile.ZipFile(path, "w") as zf:
        for name, size in file_sizes.items():
            zf.writestr(name, b"x" * size)


class TestComputeDepositSizeBytes(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)
        self.cwd = self.root / "cwd"
        self.project_dir = self.cwd / "12345"
        self.project_dir.mkdir(parents=True)

    def test_single_inner_zip_wins_over_envelope(self):
        _make_zip(self.cwd / "12345.zip", {"a.txt": 100})  # envelope, should be ignored
        _make_zip(self.project_dir / "data.zip", {"b.txt": 10, "c.txt": 20})

        size, source = juds.compute_deposit_size_bytes(str(self.project_dir), cwd=str(self.cwd))

        self.assertEqual(size, 30)
        self.assertIn("single inner ZIP", source)

    def test_envelope_zip_used_when_no_single_inner_zip(self):
        _make_zip(self.cwd / "12345.zip", {"a.txt": 100, "b.txt": 50})

        size, source = juds.compute_deposit_size_bytes(str(self.project_dir), cwd=str(self.cwd))

        self.assertEqual(size, 150)
        self.assertIn("envelope ZIP", source)

    def test_envelope_ignored_when_multiple_inner_zips(self):
        _make_zip(self.cwd / "12345.zip", {"a.txt": 999})
        _make_zip(self.project_dir / "part1.zip", {"x.txt": 5})
        _make_zip(self.project_dir / "part2.zip", {"y.txt": 7})

        size, source = juds.compute_deposit_size_bytes(str(self.project_dir), cwd=str(self.cwd))

        self.assertEqual(size, 999)
        self.assertIn("envelope ZIP", source)

    def test_on_disk_size_when_no_zip_anywhere(self):
        (self.project_dir / "data.csv").write_bytes(b"x" * 42)
        sub = self.project_dir / "sub"
        sub.mkdir()
        (sub / "more.csv").write_bytes(b"y" * 8)

        size, source = juds.compute_deposit_size_bytes(str(self.project_dir), cwd=str(self.cwd))

        self.assertEqual(size, 50)
        self.assertIn("on-disk size", source)


class TestNormalizeIssueKey(unittest.TestCase):
    def test_bare_number_gets_prefixed(self):
        self.assertEqual(juds.normalize_issue_key("9603"), "AEAREP-9603")

    def test_prefixed_key_is_uppercased(self):
        self.assertEqual(juds.normalize_issue_key("train-2000"), "TRAIN-2000")


class TestResolveFieldId(unittest.TestCase):
    def test_finds_field_by_name(self):
        jira = MagicMock()
        jira.fields.return_value = [
            {"id": "customfield_10028", "name": "Software used"},
            {"id": "customfield_10099", "name": "Deposit size"},
        ]

        self.assertEqual(juds.resolve_field_id(jira, "Deposit size"), "customfield_10099")

    def test_returns_none_when_not_found(self):
        jira = MagicMock()
        jira.fields.return_value = [{"id": "customfield_10028", "name": "Software used"}]

        self.assertIsNone(juds.resolve_field_id(jira, "Deposit size"))


class TestUpdateDepositSizeField(unittest.TestCase):
    def _mock_jira(self, field_id="customfield_10099"):
        jira = MagicMock()
        jira.fields.return_value = [{"id": field_id, "name": "Deposit size"}]
        issue = MagicMock()
        jira.issue.return_value = issue
        return jira, issue

    def test_overwrites_unconditionally(self):
        jira, issue = self._mock_jira()

        recorded = juds.update_deposit_size_field(jira, "AEAREP-1", 12.34)

        self.assertTrue(recorded)
        issue.update.assert_called_once_with(fields={"customfield_10099": 12.34})

    def test_raises_when_field_missing(self):
        jira = MagicMock()
        jira.fields.return_value = []

        with self.assertRaises(RuntimeError):
            juds.update_deposit_size_field(jira, "AEAREP-1", 12.34)

    def test_retries_on_transient_screen_error_then_succeeds(self):
        from jira.exceptions import JIRAError

        jira, issue = self._mock_jira()
        transient = JIRAError(
            text="Field 'customfield_10099' cannot be set. It is not on the appropriate screen, or unknown.",
            status_code=400,
        )
        issue.update.side_effect = [transient, transient, None]
        sleeps = []

        recorded = juds.update_deposit_size_field(
            jira, "AEAREP-1", 12.34, retry_delays=(2, 5, 10), sleep=sleeps.append
        )

        self.assertTrue(recorded)
        self.assertEqual(issue.update.call_count, 3)
        self.assertEqual(sleeps, [2, 5])
        jira.add_comment.assert_not_called()

    def test_falls_back_to_comment_after_exhausting_retries(self):
        # Regression: customfield_10552 "cannot be set. It is not on the
        # appropriate screen" for the pipeline's API user even though the
        # field is on-screen interactively - preserve the value as a comment
        # instead of losing it, mirroring jira_update_software.py's fallback
        # for the "Software used (other)" field.
        from jira.exceptions import JIRAError

        jira, issue = self._mock_jira()
        transient = JIRAError(
            text="Field 'customfield_10099' cannot be set. It is not on the appropriate screen, or unknown.",
            status_code=400,
        )
        issue.update.side_effect = transient
        sleeps = []

        recorded = juds.update_deposit_size_field(
            jira, "AEAREP-1", 12.34, retry_delays=(2, 5), sleep=sleeps.append
        )

        self.assertFalse(recorded)
        self.assertEqual(issue.update.call_count, 3)
        self.assertEqual(sleeps, [2, 5])
        jira.add_comment.assert_called_once()
        comment_text = jira.add_comment.call_args[0][1]
        self.assertIn("12.34", comment_text)
        self.assertIn("Deposit size", comment_text)

    def test_does_not_retry_unrelated_error(self):
        from jira.exceptions import JIRAError

        jira, issue = self._mock_jira()
        unrelated = JIRAError(text="Some other failure entirely", status_code=500)
        issue.update.side_effect = unrelated
        sleeps = []

        with self.assertRaises(JIRAError):
            juds.update_deposit_size_field(jira, "AEAREP-1", 12.34, retry_delays=(2, 5), sleep=sleeps.append)

        self.assertEqual(issue.update.call_count, 1)
        self.assertEqual(sleeps, [])
        jira.add_comment.assert_not_called()


class TestMain(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.project_dir = Path(self._tmp.name) / "12345"
        self.project_dir.mkdir()
        (self.project_dir / "data.csv").write_bytes(b"x" * (2 * juds.BYTES_PER_MB))

    def test_dry_run_without_yes_returns_0_and_makes_no_jira_call(self):
        rc = juds.main([str(1), str(self.project_dir)])
        self.assertEqual(rc, 0)

    def test_missing_project_dir_returns_1(self):
        rc = juds.main(["1", str(self.project_dir / "does-not-exist")])
        self.assertEqual(rc, 1)

    def test_yes_without_credentials_returns_1(self):
        env = dict(os.environ)
        os.environ.pop("JIRA_USERNAME", None)
        os.environ.pop("JIRA_API_KEY", None)
        try:
            rc = juds.main(["1", str(self.project_dir), "--yes"])
        finally:
            os.environ.clear()
            os.environ.update(env)
        self.assertEqual(rc, 1)

    def test_comment_fallback_still_returns_0(self):
        # The field write is unrecoverable for the pipeline's API user, but
        # the value was preserved as a comment - that counts as success.
        with patch.object(juds, "get_jira_client", return_value=MagicMock()):
            with patch.object(juds, "update_deposit_size_field", return_value=False):
                buf = io.StringIO()
                with contextlib.redirect_stdout(buf):
                    rc = juds.main(["1", str(self.project_dir), "--yes"])

        self.assertEqual(rc, 0)
        self.assertIn("comment", buf.getvalue().lower())


if __name__ == "__main__":
    unittest.main()
