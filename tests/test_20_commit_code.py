#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2026 Lars Vilhuber and contributors.
# Author(s): Lars Vilhuber
# Licensed under the BSD 3-Clause License; see the LICENSE file at the repository root.

"""Tests for automations/20_commit_code.sh. Run: python3 tests/test_20_commit_code.py

The script runs in a temporary git repository. The tag is only created when the
script itself makes the commit, which is why the big pipeline
(w-big-populate-from-icpsr) resets the downloader's own commit first.
"""
import os
import shutil
import subprocess
import tempfile
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(REPO, 'automations', '20_commit_code.sh')


class TestCommitCode(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.git('init', '-q')
        self.git('config', 'user.email', 'test@example.com')
        self.git('config', 'user.name', 'Test')
        self.write('README.md', 'x')
        self.git('add', '.')
        self.git('commit', '-q', '-m', 'init')

    def tearDown(self):
        shutil.rmtree(self.dir)

    def git(self, *args):
        return subprocess.run(['git', *args], cwd=self.dir, check=True,
                              capture_output=True, text=True).stdout

    def write(self, path, text):
        full = os.path.join(self.dir, path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, 'w') as f:
            f.write(text)

    def run_script(self, *args):
        env = {k: v for k, v in os.environ.items()
               if k not in ('SkipProcessing', 'jiraticket')}
        return subprocess.run(['bash', SCRIPT, *args], cwd=self.dir, env=env,
                              capture_output=True, text=True)

    def tags(self):
        return self.git('tag').split()

    def test_new_files_are_committed_and_tagged(self):
        self.write('12345/code.do', 'x')
        self.run_script('12345')
        self.assertEqual(self.tags(), ['update1'])

    def test_deposit_committed_by_downloader_is_not_tagged(self):
        """Why the big pipeline must undo the downloader's commit."""
        self.write('12345/code.do', 'x')
        self.git('add', '12345')
        self.git('commit', '-q', '-m', 'Adding files from openICPSR project 12345')
        self.run_script('12345')
        self.assertEqual(self.tags(), [])

    def test_deposit_after_reset_of_downloader_commit_is_tagged(self):
        """What w-big-populate-from-icpsr does: git reset <pre-download commit>."""
        before = self.git('rev-parse', 'HEAD').strip()
        self.write('12345/code.do', 'x')
        self.git('add', '12345')
        self.git('commit', '-q', '-m', 'Adding files from openICPSR project 12345')
        self.git('reset', '-q', before)
        self.run_script('12345')
        self.assertEqual(self.tags(), ['update1'])
        self.assertIn('12345/code.do', self.git('ls-files').split())

    def test_notag_flag_never_tags(self):
        self.write('config.yml', 'x')
        self.run_script('config.yml', 'notag')
        self.assertEqual(self.tags(), [])

    def read(self, path):
        with open(os.path.join(self.dir, path)) as f:
            return f.read()

    def test_20_no_longer_touches_gitignore(self):
        """.gitignore is handled by tools/apply_ignore_local.sh, not by this script."""
        self.write('.gitignore', '*.dta\n')
        self.write('generated/dot-gitignore', '*.dta\n12345/big.csv\n')
        self.git('add', '.gitignore')
        self.git('commit', '-q', '-m', 'gitignore')
        self.write('12345/code.do', 'x')
        self.run_script('12345')
        self.assertEqual(self.read('.gitignore'), '*.dta\n')
        self.assertNotIn('generated/dot-gitignore', self.git('ls-files').split())

    def test_ignored_generated_file_is_committed_on_request(self):
        self.write('.gitignore', 'generated/\n')
        self.write('generated/dot-ignore-local', '12345/big.csv\n')
        self.run_script('generated/dot-ignore-local', 'notag')
        self.assertIn('generated/dot-ignore-local', self.git('ls-files').split())
        self.assertEqual(self.tags(), [])

    def test_gitignore_is_committed_separately(self):
        self.write('.gitignore', '*.dta\n12345/big.csv\n')
        self.run_script('.gitignore', 'notag')
        self.assertIn('Adding code from .gitignore', self.git('log', '--format=%s'))


if __name__ == '__main__':
    unittest.main()
