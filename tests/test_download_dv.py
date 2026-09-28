#!/usr/bin/env python3
"""Tests for download_dv.py. Run: python3 tests/test_download_dv.py"""
import io
import os
import sys
import unittest
from contextlib import redirect_stderr, redirect_stdout
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools"))
import download_dv as dv


class TestParseIdentifier(unittest.TestCase):
    def test_doi_forms(self):
        for s in ('doi:10.7910/DVN/T81OHQ', '10.7910/DVN/T81OHQ',
                  'https://doi.org/10.7910/DVN/T81OHQ', 'https://doi.org/10.7910/DVN/T81OHQ/'):
            self.assertEqual(dv.parse_identifier(s), ('10.7910/DVN/T81OHQ', None), s)

    def test_landing_page_url(self):
        url = 'https://dataverse.example.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/T81OHQ&version=3.1'
        self.assertEqual(dv.parse_identifier(url), ('10.7910/DVN/T81OHQ', 'https://dataverse.example.edu'))

    def test_url_encoded_landing_page(self):
        url = 'https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi%3A10.7910%2FDVN%2FT81OHQ'
        self.assertEqual(dv.parse_identifier(url)[0], '10.7910/DVN/T81OHQ')

    def test_garbage(self):
        with self.assertRaises(ValueError):
            dv.parse_identifier('not a doi')


class TestDirName(unittest.TestCase):
    def test_harvard(self):
        self.assertEqual(dv.dir_name('10.7910/DVN/ABC123'), 'dv-DVN-ABC123')

    def test_two_part_doi(self):
        self.assertEqual(dv.dir_name('10.5064/F6ABCD'), 'dv-10.5064-F6ABCD')


class TestIsDataverseUrl(unittest.TestCase):
    def test_obvious_dataverse(self):
        with mock.patch.object(dv, 'resolve_doi_landing') as resolve:
            self.assertTrue(dv.is_dataverse_url('https://doi.org/10.7910/DVN/T81OHQ'))
            self.assertTrue(dv.is_dataverse_url('https://dataverse.nl/dataset.xhtml?persistentId=doi:10.34894/X'))
            resolve.assert_not_called()

    def test_other_repositories_not_resolved(self):
        with mock.patch.object(dv, 'resolve_doi_landing') as resolve:
            self.assertFalse(dv.is_dataverse_url('https://zenodo.org/records/1234567'))
            self.assertFalse(dv.is_dataverse_url('https://doi.org/10.3886/E123456V1'))
            self.assertFalse(dv.is_dataverse_url('https://doi.org/10.60572/101y-vn15'))
            resolve.assert_not_called()

    def test_generic_doi_resolved(self):
        with mock.patch.object(dv, 'resolve_doi_landing',
                               return_value='https://data.qdr.syr.edu/dataset.xhtml?persistentId=doi:10.5064/F6ABCD'):
            self.assertTrue(dv.is_dataverse_url('https://doi.org/10.5064/F6ABCD'))
        with mock.patch.object(dv, 'resolve_doi_landing', return_value='https://example.org/paper'):
            self.assertFalse(dv.is_dataverse_url('https://doi.org/10.1257/aer.1'))


class TestFilePlan(unittest.TestCase):
    def test_plan(self):
        files = [
            {'restricted': False, 'directoryLabel': 'Data/raw',
             'dataFile': {'id': 1, 'filename': 'cpi.tab', 'originalFileName': 'cpi.csv',
                          'filesize': 300, 'originalFileSize': 277,
                          'checksum': {'type': 'MD5', 'value': 'abc'}}},
            {'restricted': False,
             'dataFile': {'id': 2, 'filename': 'Code.zip', 'filesize': 10,
                          'checksum': {'type': 'SHA-1', 'value': 'def'}}},
            {'restricted': True,
             'dataFile': {'id': 3, 'filename': 'secret.dta', 'filesize': 5}},
        ]
        entries, restricted = dv.file_plan(files)
        self.assertEqual(restricted, ['secret.dta'])
        self.assertEqual([(e['relpath'], e['query'], e['size'], e['algo']) for e in entries],
                         [(os.path.join('Data', 'raw', 'cpi.csv'), '?format=original', 277, 'md5'),
                          ('Code.zip', '', 10, 'sha1')])

    def test_unsafe_path(self):
        files = [{'restricted': False, 'directoryLabel': '../..',
                  'dataFile': {'id': 1, 'filename': 'x', 'filesize': 1}}]
        with self.assertRaises(RuntimeError):
            dv.file_plan(files)


def run_main(argv):
    """Run main() with argv; return (exit_code, stdout, stderr)."""
    out, err = io.StringIO(), io.StringIO()
    code = 0
    with mock.patch.object(sys, 'argv', ['download_dv.py'] + argv), \
            redirect_stdout(out), redirect_stderr(err):
        try:
            dv.main()
        except SystemExit as e:
            code = e.code
    return code, out.getvalue(), err.getvalue()


class TestMain(unittest.TestCase):
    def test_dir_name_mode(self):
        code, out, _ = run_main(['https://doi.org/10.7910/DVN/T81OHQ', '--dir-name'])
        self.assertEqual((code, out), (0, 'dv-DVN-T81OHQ\n'))

    def test_legacy_doi_flag(self):
        code, out, _ = run_main(['--doi', 'doi:10.7910/DVN/ABC123', '--dir-name'])
        self.assertEqual((code, out), (0, 'dv-DVN-ABC123\n'))

    def test_no_identifier_no_jira_is_error(self):
        code, _, _ = run_main([])
        self.assertEqual(code, 1)

    def test_jira_no_url_exits_2(self):
        with mock.patch.object(dv, 'get_replication_url_from_jira', return_value=''):
            code, out, _ = run_main(['--jira-ticket', 'AEAREP-1', '--print-id'])
        self.assertEqual((code, out), (2, ''))

    def test_jira_url_not_dataverse_exits_2(self):
        with mock.patch.object(dv, 'get_replication_url_from_jira',
                               return_value='https://zenodo.org/records/1234567'):
            code, out, _ = run_main(['--jira-ticket', 'AEAREP-1', '--print-id'])
        self.assertEqual((code, out), (2, ''))

    def test_print_id_dry_run_prints_only_dir(self):
        data = {'latestVersion': {'versionNumber': 1, 'versionMinorNumber': 0, 'versionState': 'RELEASED',
                                  'files': [{'restricted': False,
                                             'dataFile': {'id': 1, 'filename': 'a.do', 'filesize': 3}}]}}
        with mock.patch.object(dv, 'get_replication_url_from_jira',
                               return_value='https://doi.org/10.7910/DVN/T81OHQ'), \
                mock.patch.object(dv, 'find_server', return_value=dv.SERVER_URL), \
                mock.patch.object(dv, 'get_dataset', return_value=data):
            code, out, err = run_main(['--jira-ticket', 'AEAREP-1', '--print-id', '--dry-run'])
        self.assertEqual((code, out), (0, 'dv-DVN-T81OHQ\n'))
        self.assertIn('a.do', err)

    def test_api_error_exits_1(self):
        with mock.patch.object(dv, 'find_server', return_value=dv.SERVER_URL), \
                mock.patch.object(dv, 'get_dataset', side_effect=RuntimeError('boom')):
            code, out, _ = run_main(['doi:10.7910/DVN/X', '--print-id'])
        self.assertEqual((code, out), (1, ''))


if __name__ == '__main__':
    unittest.main()
