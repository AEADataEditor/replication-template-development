#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2026 Lars Vilhuber and contributors.
# Author(s): Lars Vilhuber
# Licensed under the BSD 3-Clause License; see the LICENSE file at the repository root.

"""Tests for automations/06_check_duplicates_and_zero_bytes.sh. Run: python3 tests/test_06_check_duplicates_and_zero_bytes.py"""
import os
import shutil
import subprocess
import tempfile
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(REPO, 'automations', '06_check_duplicates_and_zero_bytes.sh')
DATE = '2026-01-02'


class TestCheckDuplicates(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        os.makedirs(os.path.join(self.dir, 'generated'))

    def tearDown(self):
        shutil.rmtree(self.dir)

    def write_manifest(self, groups, singles=1):
        """groups: list of group sizes; each group shares one checksum."""
        lines, meta = [], ['filename,bytes']
        for g, size in enumerate(groups):
            checksum = f'{g:064x}'
            for i in range(size):
                path = f'./project/dir{i}/file{g}.m'
                lines.append(f'{checksum}  {path}')
                meta.append(f'{path},10')
        for s in range(singles):
            path = f'./project/single{s}.m'
            lines.append(f'{"f" * 63}{s}  {path}')
            meta.append(f'{path},10')
        with open(os.path.join(self.dir, 'generated', f'manifest.{DATE}.sha256'), 'w') as f:
            f.write('\n'.join(lines) + '\n')
        with open(os.path.join(self.dir, 'generated', 'metadata.txt'), 'w') as f:
            f.write('\n'.join(meta) + '\n')

    def run_script(self, env=None):
        result = subprocess.run(['bash', SCRIPT, '12345', '', DATE], cwd=self.dir,
                                capture_output=True, text=True,
                                env={**os.environ, **(env or {})})
        self.assertEqual(result.returncode, 0, result.stderr)

    def read(self, name):
        with open(os.path.join(self.dir, 'generated', f'{name}.{DATE}.md')) as f:
            return f.read()

    @staticmethod
    def rows(text):
        return [l for l in text.splitlines() if l.startswith('| ') and not l.startswith('| Checksum') and not l.startswith('| ---')]

    def test_many_duplicates_sampled_with_full_list_in_appendix(self):
        self.write_manifest([4, 4, 4, 4])  # 16 duplicate files, 4 groups
        self.run_script()
        summary = self.read('duplicate-files-report')
        full = self.read('duplicate-files-full')
        self.assertIn('- Files checked: 17', summary)
        self.assertIn('- Files that have at least one duplicate: 16', summary)
        self.assertIn('- Groups of identical files: 4', summary)
        self.assertIn('sample of 12 of the 16 duplicate files', summary)
        self.assertIn('Appendix', summary)
        self.assertEqual(len(self.rows(summary)), 12)
        self.assertEqual(len(self.rows(full)), 16)
        self.assertEqual(self.rows(summary), self.rows(full)[:12])

    def test_few_duplicates_listed_in_full_without_appendix_pointer(self):
        self.write_manifest([2, 3])
        self.run_script()
        summary = self.read('duplicate-files-report')
        self.assertEqual(len(self.rows(summary)), 5)
        self.assertNotIn('Appendix', summary)
        self.assertEqual(len(self.rows(self.read('duplicate-files-full'))), 5)

    def test_sample_size_configurable(self):
        self.write_manifest([4, 4])
        self.run_script({'DUPLICATES_SAMPLE_LINES': '3'})
        self.assertEqual(len(self.rows(self.read('duplicate-files-report'))), 3)

    def test_no_duplicates(self):
        self.write_manifest([], singles=3)
        self.run_script()
        self.assertIn('No duplicates found', self.read('duplicate-files-report'))
        self.assertIn('No duplicates found', self.read('duplicate-files-full'))

    def add_metadata(self, rows):
        """Append (path, bytes) rows to the metadata written by write_manifest."""
        with open(os.path.join(self.dir, 'generated', 'metadata.txt'), 'a') as f:
            f.write(''.join(f'{path},{size}\n' for path, size in rows))

    @staticmethod
    def table_rows(text):
        return [l for l in text.splitlines() if l.startswith('| ') and not l.startswith('| File') and not l.startswith('| ---')]

    def test_zero_byte_and_small_files_reported(self):
        self.write_manifest([], singles=1)
        self.add_metadata([('./p/empty.do', 0), ('./p/stub.dta', 130), ('./p/STUB.XLSX', 9),
                           ('./p/tiny.do', 5), ('./p/real.dta', 90000), ('./p/a, b.pdf', 40)])
        self.run_script()
        report = self.read('zero-byte-files-report')
        self.assertIn('| ./p/empty.do |', report)
        self.assertIn('| ./p/stub.dta | 130 |', report)
        self.assertIn('| ./p/STUB.XLSX | 9 |', report)
        self.assertIn('| ./p/a, b.pdf | 40 |', report)      # commas in names survive
        self.assertNotIn('tiny.do', report)                  # small, but not a binary type
        self.assertNotIn('real.dta', report)
        self.assertIn('this note by the Data Editor', report)
        self.assertEqual(len(self.table_rows(report)), 4)

    def test_many_small_files_sampled_with_full_list_in_appendix(self):
        self.write_manifest([], singles=1)
        self.add_metadata([(f'./p/s{i}.dta', 10) for i in range(15)] + [(f'./p/z{i}.do', 0) for i in range(14)])
        self.run_script()
        report = self.read('zero-byte-files-report')
        full = self.read('zero-byte-files-full')
        self.assertIn('- Files found: 14', report)
        self.assertIn('- Files found: 15', report)
        self.assertEqual(report.count('sample of 12 of the'), 2)
        self.assertEqual(len(self.table_rows(report)), 24)
        self.assertEqual(len(self.table_rows(full)), 29)

    def test_few_small_files_listed_without_appendix_pointer(self):
        self.write_manifest([], singles=1)
        self.add_metadata([('./p/s.dta', 10)])
        self.run_script()
        self.assertNotIn('Appendix', self.read('zero-byte-files-report'))
        self.assertIn('| ./p/s.dta | 10 |', self.read('zero-byte-files-full'))

    def test_small_file_threshold_and_extensions_configurable(self):
        self.write_manifest([], singles=1)
        self.add_metadata([('./p/a.dta', 600), ('./p/b.xyz', 10)])
        self.run_script({'SMALL_FILE_BYTES': '1000', 'SMALL_FILE_EXTENSIONS': 'dta xyz'})
        report = self.read('zero-byte-files-report')
        self.assertIn('a.dta', report)
        self.assertIn('b.xyz', report)

    def test_no_zero_or_small_files(self):
        self.write_manifest([], singles=2)
        self.run_script()
        for name in ('zero-byte-files-report', 'zero-byte-files-full'):
            text = self.read(name)
            self.assertIn('No zero byte files found', text)
            self.assertIn('No suspiciously small files found', text)
        self.assertNotIn('Data Editor', self.read('zero-byte-files-report'))

    def test_full_list_not_picked_up_as_summary(self):
        # 24_amend_report.sh globs duplicate-files-report*.md; the full list must not match
        self.write_manifest([4, 4, 4, 4])
        self.run_script()
        names = os.listdir(os.path.join(self.dir, 'generated'))
        self.assertEqual([n for n in names if n.startswith('duplicate-files-report')],
                         [f'duplicate-files-report.{DATE}.md'])


if __name__ == '__main__':
    unittest.main()
