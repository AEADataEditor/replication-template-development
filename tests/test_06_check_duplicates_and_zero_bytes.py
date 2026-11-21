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

    def test_full_list_not_picked_up_as_summary(self):
        # 24_amend_report.sh globs duplicate-files-report*.md; the full list must not match
        self.write_manifest([4, 4, 4, 4])
        self.run_script()
        names = os.listdir(os.path.join(self.dir, 'generated'))
        self.assertEqual([n for n in names if n.startswith('duplicate-files-report')],
                         [f'duplicate-files-report.{DATE}.md'])


if __name__ == '__main__':
    unittest.main()
