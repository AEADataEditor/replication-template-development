#!/usr/bin/env python3
"""Tests for jira_update_software.py. Run: python3 tools/test_jira_update_software.py"""
import csv
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import jira_update_software as jus


class TestLoadCsvLookup(unittest.TestCase):
    def test_loads_real_extension_table(self):
        lookup = jus.load_csv_lookup(jus.DEFAULT_EXT_LOOKUP)
        self.assertEqual(lookup["do"], "Stata")
        self.assertEqual(lookup["ado"], "Stata")
        self.assertEqual(lookup["py"], "Python")
        self.assertNotIn("sh", lookup)
        self.assertNotIn("toml", lookup)

    def test_loads_real_filename_table(self):
        lookup = jus.load_csv_lookup(jus.DEFAULT_NAME_LOOKUP)
        self.assertEqual(lookup["project.toml"], "Julia")
        self.assertEqual(lookup["manifest.toml"], "Julia")


class TestDetectIpynbLanguage(unittest.TestCase):
    def _write_notebook(self, metadata):
        fd, path = tempfile.mkstemp(suffix=".ipynb")
        with os.fdopen(fd, "w") as f:
            json.dump({"metadata": metadata, "cells": []}, f)
        return path

    def test_kernelspec_language(self):
        path = self._write_notebook({"kernelspec": {"language": "python"}})
        try:
            self.assertEqual(jus.detect_ipynb_language(path), "Python")
        finally:
            os.remove(path)

    def test_language_info_fallback(self):
        path = self._write_notebook({"language_info": {"name": "julia"}})
        try:
            self.assertEqual(jus.detect_ipynb_language(path), "Julia")
        finally:
            os.remove(path)

    def test_r_kernel(self):
        path = self._write_notebook({"kernelspec": {"language": "R"}})
        try:
            self.assertEqual(jus.detect_ipynb_language(path), "R")
        finally:
            os.remove(path)

    def test_unrecognized_language_returns_none(self):
        path = self._write_notebook({"kernelspec": {"language": "brainfuck"}})
        try:
            self.assertIsNone(jus.detect_ipynb_language(path))
        finally:
            os.remove(path)

    def test_missing_file_returns_none(self):
        self.assertIsNone(jus.detect_ipynb_language("/nonexistent/path.ipynb"))

    def test_malformed_json_returns_none(self):
        fd, path = tempfile.mkstemp(suffix=".ipynb")
        with os.fdopen(fd, "w") as f:
            f.write("not valid json{")
        try:
            self.assertIsNone(jus.detect_ipynb_language(path))
        finally:
            os.remove(path)


class TestResolveSoftware(unittest.TestCase):
    def setUp(self):
        self.ext_lookup = {"do": "Stata", "ado": "Stata", "py": "Python", "r": "R"}
        self.name_lookup = {"project.toml": "Julia", "manifest.toml": "Julia"}

    def test_basic_extension_mapping(self):
        found, unmatched = jus.resolve_software(
            ["./code/main.do", "./code/clean.py"], None, self.ext_lookup, self.name_lookup
        )
        self.assertEqual(found, {"Stata", "Python"})
        self.assertEqual(unmatched, {})

    def test_filename_override_beats_extension(self):
        found, unmatched = jus.resolve_software(
            ["./Project.toml"], None, self.ext_lookup, self.name_lookup
        )
        self.assertEqual(found, {"Julia"})

    def test_excluded_extension_is_unmatched(self):
        found, unmatched = jus.resolve_software(
            ["./run.sh"], None, self.ext_lookup, self.name_lookup
        )
        self.assertEqual(found, set())
        self.assertEqual(unmatched, {"sh": 1})

    def test_dedup_across_files(self):
        found, unmatched = jus.resolve_software(
            ["./a.do", "./b.do", "./c.ado"], None, self.ext_lookup, self.name_lookup
        )
        self.assertEqual(found, {"Stata"})

    def test_ipynb_without_project_dir_is_unmatched(self):
        found, unmatched = jus.resolve_software(
            ["./notebook.ipynb"], None, self.ext_lookup, self.name_lookup
        )
        self.assertEqual(found, set())
        self.assertEqual(unmatched, {"ipynb": 1})

    def test_ipynb_with_project_dir_resolves_language(self):
        with tempfile.TemporaryDirectory() as tmp:
            nb_path = Path(tmp) / "notebook.ipynb"
            nb_path.write_text(json.dumps({"metadata": {"kernelspec": {"language": "python"}}}))
            found, unmatched = jus.resolve_software(
                ["notebook.ipynb"], tmp, self.ext_lookup, self.name_lookup
            )
            self.assertEqual(found, {"Python"})
            self.assertEqual(unmatched, {})

    def test_no_extension_uses_basename_as_unmatched_key(self):
        found, unmatched = jus.resolve_software(
            ["./makefile"], None, self.ext_lookup, self.name_lookup
        )
        self.assertEqual(found, set())
        self.assertEqual(unmatched, {"makefile": 1})


class TestReadMetadataFilenames(unittest.TestCase):
    def test_reads_filenames_skipping_header(self):
        fd, path = tempfile.mkstemp(suffix=".csv")
        with os.fdopen(fd, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["filename", "lines"])
            writer.writerow(["./code/main.do", "120"])
            writer.writerow(["./code/clean.py", "45"])
        try:
            self.assertEqual(
                jus.read_metadata_filenames(path),
                ["./code/main.do", "./code/clean.py"],
            )
        finally:
            os.remove(path)


if __name__ == "__main__":
    unittest.main()
