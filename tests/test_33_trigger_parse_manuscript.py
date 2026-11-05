#!/usr/bin/env python3
"""Tests for automations/33_trigger_parse_manuscript.sh. Run: python3 tests/test_33_trigger_parse_manuscript.py

Runs the real script and the real tools/manuscript_to_markdown.py. Only the Jira
download and the Bitbucket trigger are stubbed.
"""
import hashlib
import os
import shutil
import subprocess
import tempfile
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHECKSUMS = os.path.join('generated', 'manuscript.sha256')
STUB_DOWNLOAD = """import os, sys
out = sys.argv[sys.argv.index('--output-dir') + 1]
content = os.environ.get('FAKE_MANUSCRIPT', '')
if not content:
    sys.exit(1)
with open(os.path.join(out, 'PDF_Proof.pdf'), 'w') as f:
    f.write(content)
with open(os.path.join(out, 'form.pdf'), 'w') as f:
    f.write(os.environ.get('FAKE_FORM', 'form'))
"""
STUB_TRIGGER = """import sys
with open('triggered', 'w') as f:
    f.write(' '.join(sys.argv[1:]))
sys.exit(int(__import__('os').environ.get('FAKE_TRIGGER_RC', '0')))
"""


class TestTrigger(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp()
        os.makedirs(os.path.join(self.root, 'automations'))
        os.makedirs(os.path.join(self.root, 'tools'))
        shutil.copy(os.path.join(REPO, 'automations', '33_trigger_parse_manuscript.sh'),
                    os.path.join(self.root, 'automations'))
        shutil.copy(os.path.join(REPO, 'tools', 'manuscript_to_markdown.py'), os.path.join(self.root, 'tools'))
        self.write('tools/jira_download_attachments.py', STUB_DOWNLOAD)
        self.write('tools/bitbucket_trigger_pipeline.py', STUB_TRIGGER)

    def tearDown(self):
        shutil.rmtree(self.root)

    def write(self, path, text):
        full = os.path.join(self.root, path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, 'w') as f:
            f.write(text)

    def record(self, content):
        digest = hashlib.sha256(content.encode()).hexdigest()
        self.write(CHECKSUMS, f'{digest}  PDF_Proof.pdf\n')

    def run_script(self, jiraticket='AEAREP-1', **env_extra):
        env = {k: v for k, v in os.environ.items() if not k.startswith('FAKE_')}
        env.update(env_extra, jiraticket=jiraticket)
        result = subprocess.run(['bash', 'automations/33_trigger_parse_manuscript.sh'], cwd=self.root,
                                env=env, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result

    def triggered(self):
        return os.path.exists(os.path.join(self.root, 'triggered'))

    def test_no_checksum_starts_the_pipeline(self):
        self.run_script(FAKE_MANUSCRIPT='v1')
        self.assertTrue(self.triggered())
        with open(os.path.join(self.root, 'triggered')) as f:
            self.assertEqual(f.read(), 'm-parse-manuscript --var jiraticket=AEAREP-1')

    def test_empty_checksum_starts_the_pipeline(self):
        self.write(CHECKSUMS, '')
        self.run_script(FAKE_MANUSCRIPT='v1')
        self.assertTrue(self.triggered())

    def test_changed_manuscript_starts_the_pipeline(self):
        self.record('v1')
        self.run_script(FAKE_MANUSCRIPT='v2')
        self.assertTrue(self.triggered())

    def test_same_manuscript_does_not_start_the_pipeline(self):
        self.record('v1')
        result = self.run_script(FAKE_MANUSCRIPT='v1')
        self.assertFalse(self.triggered())
        self.assertIn('unchanged', result.stdout)

    def test_change_in_another_pdf_does_not_start_the_pipeline(self):
        self.record('v1')
        self.run_script(FAKE_MANUSCRIPT='v1', FAKE_FORM='a new form')
        self.assertFalse(self.triggered())

    def test_no_manuscript_does_not_start_the_pipeline(self):
        self.run_script()
        self.assertFalse(self.triggered())

    def test_a_broken_check_still_starts_the_pipeline(self):
        self.write('tools/manuscript_to_markdown.py', 'import sys\nsys.exit(1)\n')
        self.record('v1')
        self.run_script(FAKE_MANUSCRIPT='v1')
        self.assertTrue(self.triggered())

    def test_no_ticket_skips_the_check_and_starts_the_pipeline(self):
        self.record('v1')
        self.run_script(jiraticket='')
        self.assertTrue(self.triggered())

    def test_a_failed_trigger_does_not_fail_the_ingest(self):
        self.run_script(FAKE_MANUSCRIPT='v1', FAKE_TRIGGER_RC='1')
        self.assertTrue(self.triggered())


if __name__ == '__main__':
    unittest.main()
