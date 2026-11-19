#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) Lars Vilhuber and contributors.
# Licensed under the BSD 3-Clause License; see the LICENSE file at the repository root.

"""Tests for automations/01_check_file_sizes.sh. Run: python3 tests/test_01_check_file_sizes.py"""
import os
import shutil
import subprocess
import tempfile
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(REPO, 'automations', '01_check_file_sizes.sh')


class TestCheckFileSizes(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        os.makedirs(os.path.join(self.dir, 'tools'))
        os.makedirs(os.path.join(self.dir, 'generated'))
        shutil.copy(os.path.join(REPO, 'tools', 'parse_yaml.sh'), os.path.join(self.dir, 'tools'))
        self.write('config.yml', 'limitsize: 1\n')
        self.write('.gitignore', '*.dta\n')

    def tearDown(self):
        shutil.rmtree(self.dir)

    def write(self, path, text, size=None):
        full = os.path.join(self.dir, path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, 'w') as f:
            f.write(text if size is None else 'x' * size)

    def read(self, path):
        with open(os.path.join(self.dir, path)) as f:
            return f.read()

    def run_script(self, directory):
        result = subprocess.run(['bash', SCRIPT, directory], cwd=self.dir,
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_large_files_go_to_dot_ignore_local_only(self):
        self.write('12345/big.csv', '', size=2 * 1024 * 1024)
        self.write('12345/small.csv', 'x')
        self.run_script('12345')
        local = self.read('generated/dot-ignore-local')
        self.assertIn('12345/big.csv\n', local)
        self.assertNotIn('small.csv', local)
        self.assertNotIn('*.dta', local)
        self.assertFalse(os.path.exists(os.path.join(self.dir, 'generated/dot-gitignore')))
        self.assertEqual(self.read('.gitignore'), '*.dta\n')

    def test_entries_from_earlier_runs_are_kept(self):
        self.write('12345/big.csv', '', size=2 * 1024 * 1024)
        self.write('restricted/huge.bin', '', size=2 * 1024 * 1024)
        self.run_script('12345')
        self.run_script('restricted')
        self.run_script('restricted')
        entries = [l for l in self.read('generated/dot-ignore-local').split('\n')
                   if l and not l.startswith('#')]
        self.assertEqual(entries, ['12345/big.csv', 'restricted/huge.bin'])

    def test_no_large_files_writes_nothing(self):
        self.write('12345/small.csv', 'x')
        self.run_script('12345')
        self.assertFalse(os.path.exists(os.path.join(self.dir, 'generated/dot-ignore-local')))


if __name__ == '__main__':
    unittest.main()
