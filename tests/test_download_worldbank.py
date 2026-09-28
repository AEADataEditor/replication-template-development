#!/usr/bin/env python3
"""Tests for download_worldbank.py. Run: python3 tests/test_download_worldbank.py"""
import io
import os
import sys
import unittest
from contextlib import redirect_stderr, redirect_stdout
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools"))
import download_worldbank as dw


class TestIsWorldbankUrl(unittest.TestCase):
    def test_doi_url(self):
        self.assertTrue(dw.is_worldbank_url('https://doi.org/10.60572/101y-vn15'))

    def test_catalog_url(self):
        self.assertTrue(dw.is_worldbank_url('https://reproducibility.worldbank.org/index.php/catalog/298'))

    def test_zenodo_url(self):
        self.assertFalse(dw.is_worldbank_url('https://zenodo.org/records/1234567'))


class TestParseInput(unittest.TestCase):
    def test_doi_url(self):
        kind, value = dw.parse_input('https://doi.org/10.60572/101y-vn15')
        self.assertEqual(kind, 'doi')
        self.assertEqual(dw.extract_doi_suffix(value), '101y-vn15')

    def test_catalog_url(self):
        self.assertEqual(dw.parse_input('https://reproducibility.worldbank.org/index.php/catalog/400/'),
                         ('catalog', '400'))

    def test_catalog_id(self):
        self.assertEqual(dw.parse_input('400'), ('catalog', '400'))


def run_main(argv):
    """Run main() with argv; return (exit_code, stdout, stderr)."""
    out, err = io.StringIO(), io.StringIO()
    code = 0
    with mock.patch.object(sys, 'argv', ['download_worldbank.py'] + argv), \
            redirect_stdout(out), redirect_stderr(err):
        try:
            dw.main()
        except SystemExit as e:
            code = e.code
    return code, out.getvalue(), err.getvalue()


class TestJiraFallback(unittest.TestCase):
    def test_no_identifier_no_jira_is_error(self):
        code, _, _ = run_main([])
        self.assertEqual(code, 1)

    def test_jira_url_not_worldbank_exits_2(self):
        with mock.patch.object(dw, 'get_replication_url_from_jira',
                               return_value='https://zenodo.org/records/1234567'):
            code, out, _ = run_main(['--jira-ticket', 'AEAREP-1', '--print-id'])
        self.assertEqual(code, 2)
        self.assertEqual(out, '')

    def test_jira_url_empty_exits_2(self):
        with mock.patch.object(dw, 'get_replication_url_from_jira', return_value=''):
            code, _, _ = run_main(['--jira-ticket', 'AEAREP-1'])
        self.assertEqual(code, 2)

    def test_jira_worldbank_print_id_only_on_stdout(self):
        with mock.patch.object(dw, 'get_replication_url_from_jira',
                               return_value='https://doi.org/10.60572/101y-vn15'), \
                mock.patch.object(dw, 'resolve_catalog_info', return_value=('298', [])) as resolve:
            code, out, err = run_main(['--jira-ticket', 'AEAREP-8815', '--print-id', '--dry-run'])
        self.assertEqual(code, 0)
        resolve.assert_called_once_with('101y-vn15')
        self.assertEqual(out, 'wb-101y-vn15\n')
        self.assertIn('Replication URL from Jira', err)

    def test_explicit_id_skips_jira(self):
        with mock.patch.object(dw, 'get_replication_url_from_jira') as jira, \
                mock.patch.object(dw, 'get_catalog_info_direct', return_value=('400', [])):
            code, out, _ = run_main(['400', '--jira-ticket', 'AEAREP-1', '--print-id', '--dry-run'])
        self.assertEqual(code, 0)
        jira.assert_not_called()
        self.assertEqual(out, 'wb-400\n')


if __name__ == '__main__':
    unittest.main()
