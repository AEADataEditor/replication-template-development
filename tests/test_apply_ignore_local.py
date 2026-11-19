#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) Lars Vilhuber and contributors.
# Licensed under the BSD 3-Clause License; see the LICENSE file at the repository root.

"""Tests for tools/apply_ignore_local.sh. Run: python3 tests/test_apply_ignore_local.py

The script runs in a temporary git repository.
"""
import os
import shutil
import subprocess
import tempfile
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(REPO, 'tools', 'apply_ignore_local.sh')
MARKER = '# local additions - auto-generated on'
LEGACY = ('*.dta\n*.parquet\n\n# Auto-generated on 2026-01-02 03:04:05\n'
          '# The following files exceed 100MB and should not be committed to Git\n'
          '12345/big.csv\n12345/sub/huge.bin\n')


class TestApplyIgnoreLocal(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.git('init', '-q')
        self.git('config', 'user.email', 'test@example.com')
        self.git('config', 'user.name', 'Test')
        self.write('.gitignore', '*.dta\n*.parquet\n')
        self.git('add', '.')
        self.git('commit', '-q', '-m', 'init')

    def tearDown(self):
        shutil.rmtree(self.dir)

    def git(self, *args):
        return subprocess.run(['git', *args], cwd=self.dir, check=True,
                              capture_output=True, text=True).stdout

    def write(self, path, text):
        full = os.path.join(self.dir, path)
        os.makedirs(os.path.dirname(full) or self.dir, exist_ok=True)
        with open(full, 'w') as f:
            f.write(text)

    def read(self, path):
        with open(os.path.join(self.dir, path)) as f:
            return f.read()

    def exists(self, path):
        return os.path.exists(os.path.join(self.dir, path))

    def run_script(self):
        result = subprocess.run(['bash', SCRIPT], cwd=self.dir, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result

    def staged(self):
        return self.git('diff', '--cached', '--name-status').split('\n')

    def test_nothing_to_apply_leaves_gitignore_alone(self):
        self.run_script()
        self.assertEqual(self.read('.gitignore'), '*.dta\n*.parquet\n')

    def test_local_additions_are_appended_with_a_dated_comment(self):
        self.write('generated/dot-ignore-local', '# Files larger\n12345/big.csv\n')
        self.run_script()
        text = self.read('.gitignore')
        self.assertTrue(text.startswith('*.dta\n*.parquet\n'))
        self.assertRegex(text, MARKER + r' \d{4}-\d\d-\d\d\n# Files larger\n12345/big.csv\n$')

    def test_running_twice_does_not_duplicate_the_block(self):
        self.write('generated/dot-ignore-local', '12345/big.csv\n')
        self.run_script()
        once = self.read('.gitignore')
        self.run_script()
        self.assertEqual(self.read('.gitignore'), once)
        self.assertEqual(once.count(MARKER), 1)

    def test_template_refresh_keeps_the_additions_but_not_a_stale_block(self):
        self.write('generated/dot-ignore-local', '12345/big.csv\n')
        self.run_script()
        # 4-refresh-tools: new template .gitignore (the old block is gone with it)
        self.write('.gitignore', '*.dta\n*.parquet\n*.new\n')
        self.run_script()
        text = self.read('.gitignore')
        self.assertTrue(text.startswith('*.dta\n*.parquet\n*.new\n'))
        self.assertEqual(text.count('12345/big.csv'), 1)

    def test_empty_local_file_adds_nothing(self):
        self.write('generated/dot-ignore-local', '# Files larger\n\n')
        self.run_script()
        self.assertEqual(self.read('.gitignore'), '*.dta\n*.parquet\n')

    def test_local_file_is_staged_even_when_generated_is_ignored(self):
        self.write('.gitignore', 'generated/\n')
        self.write('generated/dot-ignore-local', '12345/big.csv\n')
        self.run_script()
        self.assertIn('A\tgenerated/dot-ignore-local', self.staged())

    def test_legacy_dot_gitignore_is_converted(self):
        self.write('generated/dot-gitignore', LEGACY)
        self.write('generated/diff-dot-gitignore.txt', 'diff\n')
        result = self.run_script()
        self.assertIn('2 entries', result.stdout)
        self.assertFalse(self.exists('generated/dot-gitignore'))
        self.assertFalse(self.exists('generated/diff-dot-gitignore.txt'))
        local = self.read('generated/dot-ignore-local')
        self.assertIn('12345/big.csv\n12345/sub/huge.bin\n', local)
        self.assertNotIn('*.parquet', local)
        text = self.read('.gitignore')
        self.assertEqual(text.count('# Auto-generated'), 0)
        self.assertIn('12345/big.csv', text)
        self.assertTrue(text.startswith('*.dta\n*.parquet\n'))

    def test_tracked_legacy_file_is_removed_from_git(self):
        self.write('generated/dot-gitignore', LEGACY)
        self.git('add', '-f', 'generated/dot-gitignore')
        self.git('commit', '-q', '-m', 'old ingest')
        self.run_script()
        self.assertIn('D\tgenerated/dot-gitignore', self.staged())
        self.assertIn('A\tgenerated/dot-ignore-local', self.staged())

    def test_legacy_without_large_files_is_removed_and_adds_nothing(self):
        self.write('generated/dot-gitignore', '*.dta\n*.old\n')
        self.run_script()
        self.assertFalse(self.exists('generated/dot-gitignore'))
        self.assertFalse(self.exists('generated/dot-ignore-local'))
        self.assertEqual(self.read('.gitignore'), '*.dta\n*.parquet\n')

    def test_legacy_entries_are_merged_with_existing_local_file(self):
        self.write('generated/dot-ignore-local', '# Files larger\n12345/big.csv\nother/x.bin\n')
        self.write('generated/dot-gitignore', LEGACY)
        self.run_script()
        entries = [l for l in self.read('generated/dot-ignore-local').split('\n')
                   if l and not l.startswith('#')]
        self.assertEqual(entries, ['12345/big.csv', '12345/sub/huge.bin', 'other/x.bin'])

    def test_conversion_happens_once(self):
        self.write('generated/dot-gitignore', LEGACY)
        self.run_script()
        first = self.read('.gitignore')
        result = self.run_script()
        self.assertNotIn('Converted', result.stdout)
        self.assertEqual(self.read('.gitignore'), first)


if __name__ == '__main__':
    unittest.main()
