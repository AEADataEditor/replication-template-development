#!/usr/bin/env python3
"""Tests for manuscript_to_markdown.py. Run: python3 tests/test_manuscript_to_markdown.py"""
import hashlib
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools"))
import manuscript_to_markdown as m2m


def fake_runner(images=()):
    """A runner that writes <stem>/<stem>.md (and the given images) like marker does."""
    def run(pdf, out_dir):
        stem = Path(pdf).stem
        target = Path(out_dir) / stem
        target.mkdir()
        (target / f"{stem}.md").write_text("# text\n")
        for img in images:
            (target / img).write_bytes(b"\xff\xd8")
    return run


def failing_runner(pdf, out_dir):
    raise RuntimeError("boom")


class TestFindManuscripts(unittest.TestCase):
    def test_selection(self):
        with tempfile.TemporaryDirectory() as d:
            for name in ("PDF_Proof.PDF", "pdf_proof.pdf", "AEJApp-2025-0453.R1_Proof_hi.pdf",
                         "AER-2025-0473_AO.pdf", "13071-2.pdf", "Data and Code Availability.pdf",
                         "EXTERNAL-REPORT.docx", "README.pdf"):
                Path(d, name).write_text("x")
            Path(d, "AER-2025-9999.pdf").mkdir()  # a directory, not a file
            self.assertEqual(m2m.find_manuscripts(d),
                             ["AEJApp-2025-0453.R1_Proof_hi.pdf", "AER-2025-0473_AO.pdf",
                              "PDF_Proof.PDF", "pdf_proof.pdf"])

    def test_none(self):
        with tempfile.TemporaryDirectory() as d:
            Path(d, "13071-2.pdf").write_text("x")
            self.assertEqual(m2m.find_manuscripts(d), [])


class TestConvert(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.pdf = os.path.join(self.tmp.name, "PDF_Proof.PDF")
        Path(self.pdf).write_text("x")
        self.out = os.path.join(self.tmp.name, "manuscript_parsed")

    def tearDown(self):
        self.tmp.cleanup()

    def test_marker_result_lands_in_output(self):
        runners = {"marker": fake_runner(("fig.jpeg",)), "markitdown": failing_runner}
        self.assertEqual(m2m.convert(self.pdf, self.out, "auto", runners), "marker")
        self.assertTrue(os.path.isfile(os.path.join(self.out, "PDF_Proof", "PDF_Proof.md")))
        self.assertTrue(os.path.isfile(os.path.join(self.out, "PDF_Proof", "fig.jpeg")))

    def test_auto_falls_back_to_markitdown(self):
        runners = {"marker": failing_runner, "markitdown": fake_runner()}
        self.assertEqual(m2m.convert(self.pdf, self.out, "auto", runners), "markitdown")
        self.assertTrue(os.path.isfile(os.path.join(self.out, "PDF_Proof", "PDF_Proof.md")))

    def test_explicit_engine_does_not_fall_back(self):
        runners = {"marker": failing_runner, "markitdown": fake_runner()}
        with self.assertRaises(RuntimeError):
            m2m.convert(self.pdf, self.out, "marker", runners)
        self.assertFalse(os.path.exists(os.path.join(self.out, "PDF_Proof")))

    def test_rerun_replaces_old_result(self):
        m2m.convert(self.pdf, self.out, "marker", {"marker": fake_runner(("old.jpeg",))})
        m2m.convert(self.pdf, self.out, "marker", {"marker": fake_runner(("new.jpeg",))})
        files = sorted(os.listdir(os.path.join(self.out, "PDF_Proof")))
        self.assertEqual(files, ["PDF_Proof.md", "new.jpeg"])

    def test_missing_md_counts_as_failure(self):
        def empty(pdf, out_dir):
            os.mkdir(os.path.join(out_dir, Path(pdf).stem))
        with self.assertRaises(RuntimeError):
            m2m.convert(self.pdf, self.out, "marker", {"marker": empty})


class TestMain(unittest.TestCase):
    def test_no_manuscript_is_not_an_error(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(m2m.main(["--source-dir", d, "--output-dir", os.path.join(d, "o")]), 0)

    def test_list(self):
        with tempfile.TemporaryDirectory() as d:
            Path(d, "PDF_Proof.PDF").write_text("x")
            self.assertEqual(m2m.main(["--source-dir", d, "--list"]), 0)
            self.assertFalse(os.path.exists("manuscript_parsed"))


class TestChecksums(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.source = Path(tmp.name, "source")
        self.source.mkdir()
        self.file = Path(tmp.name, "generated", "manuscript.sha256")
        (self.source / "PDF_Proof.PDF").write_text("v1")
        (self.source / "form.pdf").write_text("form")

    def check(self):
        return m2m.main(["--source-dir", str(self.source), "--checksum-file", str(self.file), "--needs-conversion"])

    def record(self):
        return m2m.main(["--source-dir", str(self.source), "--checksum-file", str(self.file), "--record-checksums"])

    def test_format_is_that_of_sha256sum_and_covers_only_manuscripts(self):
        self.assertEqual(self.record(), 0)
        self.assertEqual(self.file.read_text(), f"{hashlib.sha256(b'v1').hexdigest()}  PDF_Proof.PDF\n")

    def test_no_file_needs_conversion(self):
        self.assertEqual(self.check(), 0)

    def test_empty_file_needs_conversion(self):
        self.file.parent.mkdir()
        self.file.write_text("")
        self.assertEqual(self.check(), 0)

    def test_same_manuscript_does_not(self):
        self.record()
        self.assertEqual(self.check(), m2m.EXIT_NO_CONVERSION)

    def test_changed_manuscript_does(self):
        self.record()
        (self.source / "PDF_Proof.PDF").write_text("v2")
        self.assertEqual(self.check(), 0)

    def test_renamed_manuscript_does(self):
        self.record()
        (self.source / "PDF_Proof.PDF").rename(self.source / "AER-2025-0473_AO.pdf")
        self.assertEqual(self.check(), 0)

    def test_added_manuscript_does(self):
        self.record()
        (self.source / "AER-2025-0473_AO.pdf").write_text("v1")
        self.assertEqual(self.check(), 0)

    def test_other_pdf_changing_does_not(self):
        self.record()
        (self.source / "form.pdf").write_text("new form")
        self.assertEqual(self.check(), m2m.EXIT_NO_CONVERSION)

    def test_no_manuscript_does_not(self):
        (self.source / "PDF_Proof.PDF").unlink()
        self.assertEqual(self.check(), m2m.EXIT_NO_CONVERSION)

    def test_no_manuscript_records_nothing(self):
        (self.source / "PDF_Proof.PDF").unlink()
        self.assertEqual(self.record(), 0)
        self.assertFalse(self.file.exists())


if __name__ == "__main__":
    unittest.main()
