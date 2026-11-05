#!/usr/bin/env python3
"""Tests for automations/31_parse_manuscript.sh. Run: python3 tests/test_31_parse_manuscript.py

Two clones of one bare repository play the ingest and the m-parse-manuscript
pipeline. The clones hold the real 20_commit_code.sh, 31_parse_manuscript.sh,
32_pull_push.sh and tools/manuscript_to_markdown.py; only the Jira download and
the converters (marker_single, markitdown) are stubbed.
"""
import hashlib
import os
import shutil
import stat
import subprocess
import tempfile
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = ('20_commit_code.sh', '31_parse_manuscript.sh', '32_pull_push.sh')
LOG = 'generated/git-commit.log'
CHECKSUMS = 'generated/manuscript.sha256'
RESULT = 'manuscript_parsed/PDF_Proof/PDF_Proof.md'
MANUSCRIPT = 'the manuscript'
STUB_DOWNLOAD = f"""import os, sys
out = sys.argv[sys.argv.index('--output-dir') + 1]
if os.environ.get('FAKE_NO_MANUSCRIPT'):
    sys.exit(1)
with open(os.path.join(out, 'PDF_Proof.pdf'), 'w') as f:
    f.write({MANUSCRIPT!r})
"""
OLD_RESULT = 'manuscript_parsed/AER-2025-0001_old/_page_1_Figure_1.jpeg'
STUB_MARKER = """#!/bin/bash
[ -n "$FAKE_CONVERT_FAILS" ] && exit 1
stem=$(basename "$1" .pdf)
mkdir -p "$3/$stem"
echo '# paper' > "$3/$stem/$stem.md"
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
        shutil.copy(os.path.join(REPO, 'tools', 'manuscript_to_markdown.py'),
                    os.path.join(self.ingest, 'tools', 'manuscript_to_markdown.py'))
        self.bin = os.path.join(self.root, 'bin')
        self.write(self.root, 'bin/marker_single', STUB_MARKER)
        self.write(self.root, 'bin/markitdown', '#!/bin/bash\nexit 1\n')
        for name in ('marker_single', 'markitdown'):
            os.chmod(os.path.join(self.bin, name), 0o755)
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

    def run_script(self, cwd, **env_extra):
        env = {k: v for k, v in os.environ.items() if k not in ('BITBUCKET_BRANCH', 'SkipProcessing')}
        env.update(env_extra, jiraticket='AEAREP-1', PATH=self.bin + os.pathsep + os.environ['PATH'])
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

    def test_checksum_of_the_converted_manuscript_is_pushed(self):
        parse = self.clone('parse')
        self.ingest_pushes_its_log()
        self.assertEqual(self.run_script(parse).returncode, 0)
        digest = hashlib.sha256(MANUSCRIPT.encode()).hexdigest()
        self.assertEqual(self.git(self.remote, 'show', f'master:{CHECKSUMS}'), f'{digest}  PDF_Proof.pdf\n')

    def earlier_conversion(self, checksum_content):
        """Push an earlier result, recorded with the checksum of checksum_content (None: no checksum)."""
        self.write(self.ingest, OLD_RESULT, 'old figure')
        if checksum_content is not None:
            digest = hashlib.sha256(checksum_content.encode()).hexdigest()
            self.write(self.ingest, CHECKSUMS, f'{digest}  PDF_Proof.pdf\n')
        self.commit(self.ingest, 'earlier conversion')
        self.git(self.ingest, 'push', '-q', 'origin', 'master')
        return self.clone('parse')

    def test_changed_checksum_removes_the_earlier_result(self):
        parse = self.earlier_conversion('an older manuscript')
        result = self.run_script(parse)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn(OLD_RESULT, self.remote_files())
        self.assertIn(RESULT, self.remote_files())

    def test_no_checksum_removes_the_earlier_result(self):
        parse = self.earlier_conversion(None)
        result = self.run_script(parse)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn(OLD_RESULT, self.remote_files())
        self.assertIn(RESULT, self.remote_files())

    def test_same_checksum_keeps_the_earlier_result(self):
        parse = self.earlier_conversion(MANUSCRIPT)
        result = self.run_script(parse)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(OLD_RESULT, self.remote_files())
        self.assertIn(RESULT, self.remote_files())

    def test_failed_conversion_keeps_the_earlier_result(self):
        parse = self.earlier_conversion('an older manuscript')
        self.assertEqual(self.run_script(parse, FAKE_CONVERT_FAILS='1').returncode, 1)
        self.assertIn(OLD_RESULT, self.remote_files())

    def test_no_manuscript_keeps_the_earlier_result(self):
        parse = self.earlier_conversion('an older manuscript')
        result = self.run_script(parse, FAKE_NO_MANUSCRIPT='1')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(OLD_RESULT, self.remote_files())

    def test_failed_conversion_records_no_checksum(self):
        parse = self.clone('parse')
        self.assertEqual(self.run_script(parse, FAKE_CONVERT_FAILS='1').returncode, 1)
        self.assertNotIn(CHECKSUMS, self.remote_files())
        self.assertFalse(os.path.exists(os.path.join(parse, CHECKSUMS)))


if __name__ == '__main__':
    unittest.main()
