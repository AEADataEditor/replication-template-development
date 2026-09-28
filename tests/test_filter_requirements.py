#!/usr/bin/env python3
"""Tests for tools/filter_requirements.py. Run: python3 tests/test_filter_requirements.py"""
import os
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools"))
import filter_requirements as fr


class TestFilterRequirements(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.dir.cleanup)
        self.author = os.path.join(self.dir.name, 'requirements.txt')
        self.scanned = os.path.join(self.dir.name, 'requirements-generated.txt')
        self.deps_csv = os.path.join(self.dir.name, 'python-deps.csv')
        self.warnings = os.path.join(self.dir.name, 'software-warnings-python.md')

    def _write(self, path, content):
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)

    def _run(self):
        argv = [
            'filter_requirements.py',
            '--author', self.author,
            '--scanned', self.scanned,
            '--deps-csv', self.deps_csv,
            '--warnings', self.warnings,
        ]
        with patch.object(sys, 'argv', argv):
            fr.main()

    def test_empty_scan_no_author_writes_no_warning(self):
        # pipreqs emits a lone newline when it finds no Python files/imports.
        self._write(self.scanned, '\n')
        self._write(self.warnings, 'stale fragment from an earlier run\n')

        self._run()

        self.assertFalse(os.path.exists(self.warnings))

    def test_empty_scan_with_curated_author_file_reports_author_no_warning(self):
        self._write(self.scanned, '\n')
        self._write(self.author, 'pandas==1.5.0\nnumpy==1.24.0\n')

        self._run()

        with open(self.deps_csv) as f:
            csv_content = f.read()
        self.assertIn('pandas==1.5.0', csv_content)
        self.assertIn('numpy==1.24.0', csv_content)
        self.assertFalse(os.path.exists(self.warnings))

    def test_nonempty_scan_no_author_writes_nonescalated_warning(self):
        self._write(self.scanned, 'pandas==1.5.0\n')

        self._run()

        with open(self.warnings) as f:
            warning_content = f.read()
        self.assertIn('Python code was detected and scanned', warning_content)
        with open(self.deps_csv) as f:
            csv_content = f.read()
        self.assertIn('pandas==1.5.0', csv_content)

    def test_nonempty_scan_with_conda_dump_author_writes_escalated_warning(self):
        self._write(self.scanned, 'pandas==1.5.0\n')
        self._write(
            self.author,
            'conda==23.1.0\n'
            'conda-build==3.23.3\n'
            'pandas @ file:///tmp/build/pandas\n',
        )

        self._run()

        with open(self.warnings) as f:
            warning_content = f.read()
        self.assertIn('conda/Anaconda environment', warning_content)


if __name__ == '__main__':
    unittest.main()
