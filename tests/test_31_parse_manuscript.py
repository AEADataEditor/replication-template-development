#!/usr/bin/env python3
"""Tests for automations/31_parse_manuscript.sh. Run: python3 tests/test_31_parse_manuscript.py

Two clones of one bare repository play the ingest and the m-parse-manuscript
pipeline. The clones hold the real 20_commit_code.sh, 31_parse_manuscript.sh and
32_pull_push.sh; only the Jira download and the conversion are stubbed.
"""
import os
import shutil
import stat
import subprocess
import tempfile
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = ('20_commit_code.sh', '31_parse_manuscript.sh', '32_pull_push.sh')
LOG = 'generated/git-commit.log'
RESULT = 'manuscript_parsed/PDF_Proof/PDF_Proof.md'
STUB_DOWNLOAD = 'import sys\nsys.exit(0)\n'
STUB_CONVERT = """import os
os.makedirs('manuscript_parsed/PDF_Proof')
with open('manuscript_parsed/PDF_Proof/PDF_Proof.md', 'w') as f:
    f.write('# paper\\n')
"""


class TestParseManuscriptPush(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp()
        self.remote = os.path.join(self.root, 'remote.git')
        subprocess.run(['git', 'init', '-q', '--bare', '-b', 'master', self.remote], check=True)
        self.ingest = self.clone('ingest')
        for name in SCRIPTS:
            target = os.path.join(self.ingest, 'automations', name)
            os.makedirs(os.path.dirname(target), exist_ok=True)
            shutil.copy(os.path.join(REPO, 'automations', name), target)
            os.chmod(target, os.stat(target).st_mode | stat.S_IXUSR)
        self.write(self.ingest, 'tools/jira_download_attachments.py', STUB_DOWNLOAD)
        self.write(self.ingest, 'tools/manuscript_to_markdown.py', STUB_CONVERT)
        self.write(self.ingest, 'generated/README.txt', 'x')
        self.commit(self.ingest, 'init')
        self.git(self.ingest, 'push', '-q', 'origin', 'master')

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

    def ingest_pushes_its_log(self):
        self.write(self.ingest, LOG, 'from the ingest\n')
        self.commit(self.ingest, 'Adding generated files and logs')
        self.git(self.ingest, 'push', '-q', 'origin', 'master')

    def run_script(self, cwd):
        env = {k: v for k, v in os.environ.items() if k not in ('BITBUCKET_BRANCH', 'SkipProcessing')}
        env['jiraticket'] = 'AEAREP-1'
        return subprocess.run(['bash', 'automations/31_parse_manuscript.sh'], cwd=cwd, env=env,
                              capture_output=True, text=True)

    def remote_files(self):
        return self.git(self.remote, 'ls-tree', '-r', '--name-only', 'master').split()

    def remote_log(self):
        return self.git(self.remote, 'show', f'master:{LOG}')

    def test_ingest_pushes_its_log_while_parsing(self):
        parse = self.clone('parse')
        self.ingest_pushes_its_log()
        result = self.run_script(parse)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(RESULT, self.remote_files())
        self.assertEqual(self.remote_log(), 'from the ingest\n')

    def test_run_by_hand_after_the_ingest(self):
        self.ingest_pushes_its_log()
        parse = self.clone('parse')
        result = self.run_script(parse)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(RESULT, self.remote_files())
        self.assertEqual(self.remote_log(), 'from the ingest\n')

    def test_parse_pushes_first_and_the_ingest_merges(self):
        parse = self.clone('parse')
        result = self.run_script(parse)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(RESULT, self.remote_files())
        self.assertNotIn(LOG, self.remote_files())
        self.write(self.ingest, LOG, 'from the ingest\n')
        self.commit(self.ingest, 'Adding generated files and logs')
        self.git(self.ingest, 'pull', '-q', '--no-rebase', '--no-edit', 'origin', 'master')
        self.git(self.ingest, 'push', '-q', 'origin', 'master')
        self.assertIn(RESULT, self.remote_files())
        self.assertEqual(self.remote_log(), 'from the ingest\n')


if __name__ == '__main__':
    unittest.main()
