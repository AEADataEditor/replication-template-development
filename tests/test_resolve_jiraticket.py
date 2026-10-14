#!/usr/bin/env python3
"""Tests for tools/resolve_jiraticket.sh. Run: python3 tests/test_resolve_jiraticket.py

The script is sourced by bash in a temporary directory that mirrors the
repository layout; the Jira lookup is replaced by a stub that prints
$FAKE_JIRA_RESULT (as the real one prints nothing without credentials or a match).
"""
import os
import shutil
import subprocess
import tempfile
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STUB = '#!/usr/bin/env python3\nimport os\nprint(os.environ.get("FAKE_JIRA_RESULT", ""))\n'


class TestResolveJiraticket(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        os.mkdir(os.path.join(self.dir, 'tools'))
        for t in ('parse_yaml.sh', 'resolve_jiraticket.sh', 'resolve_project_id.sh', 'update_config.sh'):
            shutil.copy(os.path.join(REPO, 'tools', t), os.path.join(self.dir, 'tools', t))
        with open(os.path.join(self.dir, 'tools', 'jira_find_task_by_icpsr.py'), 'w') as f:
            f.write(STUB)

    def tearDown(self):
        shutil.rmtree(self.dir)

    def run_script(self, script, var=None, config=None, lookup='', slug='aearep-1435'):
        """Run bash `script` in the fixture; return (stdout lines, config.yml text)."""
        with open(os.path.join(self.dir, 'config.yml'), 'w') as f:
            f.write(f'openicpsr: 122661\njiraticket: {config or ""}\nmain:\nmcid:\n')
        base = {k: v for k, v in os.environ.items()
                if k not in ('jiraticket', 'openICPSRID', 'BITBUCKET_REPO_SLUG', 'FAKE_JIRA_RESULT')}
        env = {**base, 'FAKE_JIRA_RESULT': lookup}
        if slug:
            env['BITBUCKET_REPO_SLUG'] = slug
        if var:
            env['jiraticket'] = var
        out = subprocess.run(['bash', '-c', script], cwd=self.dir, capture_output=True, text=True,
                             env=env, check=True).stdout.splitlines()
        with open(os.path.join(self.dir, 'config.yml')) as f:
            return out, f.read()

    def resolve(self, **kw):
        out, _ = self.run_script('. ./tools/resolve_jiraticket.sh >/dev/null\necho "jiraticket=$jiraticket"', **kw)
        return out[-1].split('=', 1)[1]

    def test_newest_ticket_beats_slug(self):
        self.assertEqual(self.resolve(lookup='AEAREP-10313'), 'AEAREP-10313')

    def test_newest_ticket_beats_stale_config_and_rewrites_it(self):
        script = ('. ./tools/resolve_jiraticket.sh >/dev/null\n. ./tools/resolve_project_id.sh >/dev/null\n'
                  './tools/update_config.sh >/dev/null\necho "jiraticket=$jiraticket"')
        out, config = self.run_script(script, config='AEAREP-1435', lookup='AEAREP-10313')
        self.assertEqual(out[-1], 'jiraticket=AEAREP-10313')
        self.assertIn('jiraticket: AEAREP-10313', config)

    def test_pipeline_variable_wins(self):
        self.assertEqual(self.resolve(var='AEAREP-1673', config='AEAREP-1435', lookup='AEAREP-10313'), 'AEAREP-1673')

    def test_lookup_unavailable_uses_config(self):
        self.assertEqual(self.resolve(config='AEAREP-1673'), 'AEAREP-1673')

    def test_lookup_unavailable_uses_slug(self):
        self.assertEqual(self.resolve(), 'AEAREP-1435')

    def test_no_source_stays_empty(self):
        self.assertEqual(self.resolve(slug=None), '')

    def test_other_repo_slug_ignored(self):
        self.assertEqual(self.resolve(slug='replication-template'), '')

    def test_exported_and_preserved_by_later_steps(self):
        script = ('. ./tools/resolve_jiraticket.sh >/dev/null\n. ./tools/resolve_project_id.sh >/dev/null\n'
                  'bash -c \'echo "child=$jiraticket"\'\necho "jiraticket=$jiraticket"')
        out, _ = self.run_script(script, config='AEAREP-1435', lookup='AEAREP-10313')
        self.assertIn('child=AEAREP-10313', out)
        self.assertEqual(out[-1], 'jiraticket=AEAREP-10313')

    def test_logs_the_source(self):
        out, _ = self.run_script('. ./tools/resolve_jiraticket.sh', lookup='AEAREP-10313')
        self.assertEqual(out[-1], 'Jira ticket: AEAREP-10313 (from the newest ticket for openICPSR ID 122661)')


if __name__ == '__main__':
    unittest.main()
