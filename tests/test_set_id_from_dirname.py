#!/usr/bin/env python3
"""Tests for tools/set_id_from_dirname.sh. Run: python3 tests/test_set_id_from_dirname.py"""
import os
import subprocess
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NAMES = ('openICPSRID', 'DataverseID', 'ZenodoID', 'OSFID', 'WorldBankID')


class TestSetIdFromDirname(unittest.TestCase):
    def run_script(self, name):
        script = f'. ./tools/set_id_from_dirname.sh "{name}"\n' + ''.join(f'echo "{n}=${n}"\n' for n in NAMES)
        env = {k: v for k, v in os.environ.items() if k not in NAMES}
        out = subprocess.run(['bash', '-c', script], cwd=REPO, capture_output=True, text=True,
                             env=env, check=True).stdout
        return dict(line.split('=', 1) for line in out.splitlines())

    def only(self, name, var, value):
        got = self.run_script(name)
        self.assertEqual(got[var], value)
        for n in NAMES:
            if n != var:
                self.assertEqual(got[n], '', f'{n} should be unset for {name}')

    def test_openicpsr(self):
        self.only('123456', 'openICPSRID', '123456')

    def test_dataverse(self):
        self.only('dv-DVN-PTBWZT', 'DataverseID', 'dv-DVN-PTBWZT')

    def test_zenodo(self):
        self.only('zenodo-12345', 'ZenodoID', '12345')

    def test_osf(self):
        self.only('osf-abcde', 'OSFID', 'abcde')

    def test_worldbank(self):
        self.only('wb-400', 'WorldBankID', '400')


if __name__ == '__main__':
    unittest.main()
