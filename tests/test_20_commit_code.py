#!/usr/bin/env python3
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


if __name__ == '__main__':
    unittest.main()
