#!/usr/bin/env python3
"""Tests for automations/32_pull_push.sh. Run: python3 tests/test_32_pull_push.py

Two clones of one bare repository play the ingest and the m-parse-manuscript
pipeline: the second pushes manuscript_parsed/ while the first still has to push.
"""
import os
import shutil
import subprocess
import tempfile
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(REPO, 'automations', '32_pull_push.sh')


class TestPullPush(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp()
        self.remote = os.path.join(self.root, 'remote.git')
        subprocess.run(['git', 'init', '-q', '--bare', '-b', 'master', self.remote], check=True)
        self.ingest = self.clone('ingest')
        self.write(self.ingest, 'README.md', 'x')
        self.commit(self.ingest, 'init')
        self.git(self.ingest, 'push', '-q', 'origin', 'master')
        self.parse = self.clone('parse')

    def tearDown(self):
        shutil.rmtree(self.root)

    def git(self, cwd, *args):
        return subprocess.run(['git', *args], cwd=cwd, check=True, capture_output=True, text=True).stdout

    def clone(self, name):
        path = os.path.join(self.root, name)
        subprocess.run(['git', 'clone', '-q', self.remote, path], check=True, capture_output=True)
        self.git(path, 'config', 'user.email', 'test@example.com')
        self.git(path, 'config', 'user.name', 'Test')
        return path

    def write(self, cwd, path, text):
        full = os.path.join(cwd, path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, 'w') as f:
            f.write(text)

    def commit(self, cwd, msg):
        self.git(cwd, 'add', '.')
        self.git(cwd, 'commit', '-q', '-m', msg)

    def run_script(self, cwd, *args):
        env = {k: v for k, v in os.environ.items() if k != 'BITBUCKET_BRANCH'}
        return subprocess.run(['bash', SCRIPT, *args], cwd=cwd, env=env, capture_output=True, text=True)

    def parse_pushes_first(self):
        self.write(self.parse, 'manuscript_parsed/PDF_Proof/PDF_Proof.md', '# paper\n')
        self.commit(self.parse, 'Adding code from manuscript_parsed')
        self.git(self.parse, 'push', '-q', 'origin', 'master')

    def test_merge_keeps_the_ingest_commit_and_its_tag(self):
        self.write(self.ingest, '12345/code.do', 'x')
        self.commit(self.ingest, 'Adding code from 12345')
        ingest_commit = self.git(self.ingest, 'rev-parse', 'HEAD').strip()
        self.git(self.ingest, 'tag', 'update1')
        self.parse_pushes_first()
        result = self.run_script(self.ingest)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.git(self.ingest, 'rev-parse', 'update1^{commit}').strip(), ingest_commit)
        self.git(self.ingest, 'push', '-q', '--tags')
        remote_files = self.git(self.remote, 'ls-tree', '-r', '--name-only', 'master').split()
        self.assertIn('manuscript_parsed/PDF_Proof/PDF_Proof.md', remote_files)
        self.assertIn('12345/code.do', remote_files)

    def test_rebase_mode(self):
        self.parse_pushes_first()
        self.write(self.ingest, '12345/code.do', 'x')
        self.commit(self.ingest, 'Adding code from 12345')
        result = self.run_script(self.ingest, 'rebase')
        self.assertEqual(result.returncode, 0, result.stderr)
        remote_files = self.git(self.remote, 'ls-tree', '-r', '--name-only', 'master').split()
        self.assertIn('manuscript_parsed/PDF_Proof/PDF_Proof.md', remote_files)
        self.assertIn('12345/code.do', remote_files)

    def test_nothing_new_on_the_remote(self):
        self.write(self.ingest, '12345/code.do', 'x')
        self.commit(self.ingest, 'Adding code from 12345')
        self.assertEqual(self.run_script(self.ingest).returncode, 0)
        self.assertEqual(self.git(self.remote, 'rev-parse', 'master').strip(),
                         self.git(self.ingest, 'rev-parse', 'HEAD').strip())

    def test_bad_mode(self):
        self.assertEqual(self.run_script(self.ingest, 'squash').returncode, 2)


if __name__ == '__main__':
    unittest.main()
