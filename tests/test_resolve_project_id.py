#!/usr/bin/env python3
"""Tests for tools/resolve_project_id.sh. Run: python3 tests/test_resolve_project_id.py

The script is sourced by bash in a temporary directory that mirrors the
repository layout (config.yml plus the tools it calls).
"""
import os
import shutil
import subprocess
import tempfile
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS = ('parse_yaml.sh', 'resolve_project_id.sh', 'download_dv.py', 'download_zenodo.py')
CONFIG = """openicpsr: {openicpsr}
osf: {osf}
dataverse: {dataverse}
zenodo: {zenodo}
worldbank: {worldbank}
jiraticket: {jiraticket}
main:
"""


class TestResolveProjectId(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        os.mkdir(os.path.join(self.dir, 'tools'))
        for t in TOOLS:
            shutil.copy(os.path.join(REPO, 'tools', t), os.path.join(self.dir, 'tools', t))

    def tearDown(self):
        shutil.rmtree(self.dir)

    def resolve(self, env=None, **config):
        """Source the script; return a dict of the variables it sets."""
        values = {k: '' for k in ('openicpsr', 'osf', 'dataverse', 'zenodo', 'worldbank', 'jiraticket')}
        values.update(config)
        with open(os.path.join(self.dir, 'config.yml'), 'w') as f:
            f.write(CONFIG.format(**values))
        names = ('projectID', 'openICPSRID', 'WorldBankID', 'DataverseID', 'ZenodoID', 'OSFID', 'jiraticket')
        script = '. ./tools/resolve_project_id.sh >/dev/null\n' + \
                 ''.join(f'echo "{n}=${n}"\n' for n in names)
        base_env = {k: v for k, v in os.environ.items()
                    if k not in ('openICPSRID', 'WorldBankID', 'DataverseID', 'ZenodoID', 'OSFID', 'jiraticket',
                                 'BITBUCKET_REPO_SLUG')}
        result = subprocess.run(['bash', '-c', script], cwd=self.dir, capture_output=True, text=True,
                                env={**base_env, **(env or {})}, check=True)
        return dict(line.split('=', 1) for line in result.stdout.splitlines())

    def test_nothing_set(self):
        self.assertEqual(self.resolve()['projectID'], '')

    def test_openicpsr(self):
        self.assertEqual(self.resolve(openicpsr='123456', zenodo='999')['projectID'], '123456')

    def test_worldbank(self):
        self.assertEqual(self.resolve(worldbank='https://doi.org/10.60572/101y-vn15')['projectID'], 'wb-101y-vn15')
        self.assertEqual(self.resolve(worldbank='https://reproducibility.worldbank.org/index.php/catalog/400/')['projectID'],
                         'wb-400')

    def test_dataverse(self):
        self.assertEqual(self.resolve(dataverse='https://doi.org/10.7910/DVN/T81OHQ')['projectID'], 'dv-DVN-T81OHQ')

    def test_zenodo(self):
        v = self.resolve(zenodo='https://zenodo.org/records/1234567')
        self.assertEqual(v['projectID'], 'zenodo-1234567')
        self.assertEqual(v['ZenodoID'], 'https://zenodo.org/records/1234567')

    def test_osf(self):
        self.assertEqual(self.resolve(osf='https://osf.io/abc12/')['projectID'], 'osf-abc12')

    def test_environment_wins_over_config(self):
        v = self.resolve(env={'DataverseID': 'doi:10.7910/DVN/ENVENV'}, dataverse='doi:10.7910/DVN/CONFIG')
        self.assertEqual(v['projectID'], 'dv-DVN-ENVENV')
        self.assertEqual(v['DataverseID'], 'doi:10.7910/DVN/ENVENV')

    def test_order_worldbank_before_dataverse_before_zenodo(self):
        self.assertEqual(self.resolve(worldbank='400', dataverse='doi:10.7910/DVN/X', zenodo='1')['projectID'], 'wb-400')
        self.assertEqual(self.resolve(dataverse='doi:10.7910/DVN/X', zenodo='1')['projectID'], 'dv-DVN-X')

    def test_jiraticket_from_environment_preserved(self):
        self.assertEqual(self.resolve(env={'jiraticket': 'AEAREP-1'}, jiraticket='AEAREP-2')['jiraticket'], 'AEAREP-1')
        self.assertEqual(self.resolve(jiraticket='AEAREP-2')['jiraticket'], 'AEAREP-2')

    def test_jiraticket_from_repo_slug(self):
        self.assertEqual(self.resolve(env={'BITBUCKET_REPO_SLUG': 'aearep-9261'})['jiraticket'], 'AEAREP-9261')

    def test_repo_slug_does_not_override(self):
        self.assertEqual(self.resolve(env={'BITBUCKET_REPO_SLUG': 'aearep-9261', 'jiraticket': 'AEAREP-1'})['jiraticket'],
                         'AEAREP-1')
        self.assertEqual(self.resolve(env={'BITBUCKET_REPO_SLUG': 'aearep-9261'}, jiraticket='AEAREP-2')['jiraticket'],
                         'AEAREP-2')

    def test_other_repo_slug_ignored(self):
        self.assertEqual(self.resolve(env={'BITBUCKET_REPO_SLUG': 'replication-template'})['jiraticket'], '')


if __name__ == '__main__':
    unittest.main()
