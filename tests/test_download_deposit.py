#!/usr/bin/env python3
"""Tests for tools/download_deposit.sh. Run: python3 tests/test_download_deposit.py

The script is sourced by bash in a temporary directory whose tools/ holds the
real script plus stub downloaders (each prints a fixed directory name, or
exits 2 when told to) and a stub update_config.sh that logs its calls.
"""
import os
import shutil
import subprocess
import tempfile
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

STUB = """#!/usr/bin/env python3
import os, sys
print("ARGS", " ".join(sys.argv[1:]), file=open(os.environ["CALLS"], "a"))
if os.environ.get("EMPTY_{name}"):
    sys.exit(2)
print("{prefix}-found")
"""


class TestDownloadDeposit(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        tools = os.path.join(self.dir, 'tools')
        os.mkdir(tools)
        shutil.copy(os.path.join(REPO, 'tools', 'download_deposit.sh'), tools)
        for name, prefix in (('WB', 'wb'), ('DV', 'dv'), ('ZEN', 'zenodo')):
            script = {'WB': 'download_worldbank.py', 'DV': 'download_dv.py', 'ZEN': 'download_zenodo.py'}[name]
            with open(os.path.join(tools, script), 'w') as f:
                f.write(STUB.format(name=name, prefix=prefix))
        with open(os.path.join(tools, 'jira_get_info.py'), 'w') as f:
            f.write('#!/usr/bin/env python3\nprint("https://dv.example/jira-url")\n')
        upd = os.path.join(tools, 'update_config.sh')
        with open(upd, 'w') as f:
            f.write('#!/bin/bash\necho "update_config" >> "$CALLS"\n')
        os.chmod(upd, 0o755)
        self.calls = os.path.join(self.dir, 'calls.log')

    def tearDown(self):
        shutil.rmtree(self.dir)

    def run_script(self, **env):
        names = ('projectID', 'wb_dir', 'dv_dir', 'zenodo_dir', 'WorldBankID', 'DataverseID', 'ZenodoID')
        script = ('projectID="${projectID:-}"; WorldBankID="${WorldBankID:-}"; DataverseID="${DataverseID:-}"; '
                  'ZenodoID="${ZenodoID:-}"; jiraticket="${jiraticket:-}"\n'
                  '. ./tools/download_deposit.sh || echo "SOURCE_FAILED"\n' +
                  ''.join(f'echo "{n}=${{{n}:-}}"\n' for n in names))
        base = {k: v for k, v in os.environ.items()
                if k not in names + ('jiraticket',) and not k.startswith('EMPTY_')}
        result = subprocess.run(['bash', '-c', script], cwd=self.dir, capture_output=True, text=True,
                                env={**base, 'CALLS': self.calls, **env}, check=True)
        out = dict(line.split('=', 1) for line in result.stdout.splitlines() if '=' in line)
        out['failed'] = 'SOURCE_FAILED' in result.stdout
        out['calls'] = open(self.calls).read().splitlines() if os.path.exists(self.calls) else []
        return out

    def test_nothing_set(self):
        r = self.run_script()
        self.assertEqual(r['projectID'], '')
        self.assertEqual(r['calls'], [])

    def test_worldbank_id(self):
        r = self.run_script(WorldBankID='abc')
        self.assertEqual(r['projectID'], 'wb-found')
        self.assertEqual(r['calls'], ['ARGS abc --print-id', 'update_config'])

    def test_worldbank_from_jira_fills_id(self):
        r = self.run_script(jiraticket='AEAREP-1')
        self.assertEqual(r['projectID'], 'wb-found')
        self.assertEqual(r['WorldBankID'], 'found')
        self.assertEqual(r['calls'], ['ARGS --jira-ticket AEAREP-1 --print-id', 'update_config'])

    def test_falls_through_to_dataverse(self):
        r = self.run_script(jiraticket='AEAREP-1', EMPTY_WB='1')
        self.assertEqual(r['projectID'], 'dv-found')
        self.assertEqual(r['DataverseID'], 'https://dv.example/jira-url')
        self.assertEqual(r['wb_dir'], '')
        self.assertFalse(r['failed'])

    def test_falls_through_to_zenodo(self):
        r = self.run_script(jiraticket='AEAREP-1', EMPTY_WB='1', EMPTY_DV='1')
        self.assertEqual(r['projectID'], 'zenodo-found')
        self.assertEqual(r['ZenodoID'], 'found')
        self.assertEqual(r['zenodo_dir'], 'zenodo-found')

    def test_zenodo_id_passed(self):
        r = self.run_script(ZenodoID='555', EMPTY_WB='1', EMPTY_DV='1')
        self.assertIn('ARGS --zenodo-id 555 --print-id', r['calls'])

    def test_all_empty_is_not_an_error(self):
        r = self.run_script(jiraticket='AEAREP-1', EMPTY_WB='1', EMPTY_DV='1', EMPTY_ZEN='1')
        self.assertEqual(r['projectID'], '')
        self.assertFalse(r['failed'])

    def test_existing_projectid_skips_downloads(self):
        r = self.run_script(projectID='123456', jiraticket='AEAREP-1')
        self.assertEqual(r['projectID'], '123456')
        self.assertEqual(r['calls'], [])


if __name__ == '__main__':
    unittest.main()
