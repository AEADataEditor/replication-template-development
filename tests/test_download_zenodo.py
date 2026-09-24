#!/usr/bin/env python3
"""Tests for download_zenodo.py. Run: python3 tests/test_download_zenodo.py"""
import io
import os
import sys
import unittest
from contextlib import redirect_stderr, redirect_stdout
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools"))
import download_zenodo as dz


class TestClassifyUrl(unittest.TestCase):
    def test_community_request_url(self):
        kind, ident = dz.classify_url(
            'https://zenodo.org/communities/foo/requests/61cff0cb-b3ca-48aa-bfe6-5b17dc8eb665'
        )
        self.assertEqual(kind, 'request')
        self.assertEqual(ident, '61cff0cb-b3ca-48aa-bfe6-5b17dc8eb665')

    def test_me_requests_url(self):
        kind, ident = dz.classify_url(
            'https://zenodo.org/me/requests/61cff0cb-b3ca-48aa-bfe6-5b17dc8eb665.zip'
        )
        self.assertEqual(kind, 'request')
        self.assertEqual(ident, '61cff0cb-b3ca-48aa-bfe6-5b17dc8eb665')

    def test_deposit_url(self):
        kind, ident = dz.classify_url('https://zenodo.org/deposit/1234567')
        self.assertEqual(kind, 'draft')
        self.assertEqual(ident, '1234567')

    def test_record_url(self):
        kind, ident = dz.classify_url('https://zenodo.org/records/1234567')
        self.assertEqual(kind, 'public')
        self.assertEqual(ident, '1234567')

    def test_bare_id(self):
        kind, ident = dz.classify_url('1234567')
        self.assertEqual(kind, 'public')
        self.assertEqual(ident, '1234567')

    def test_unparseable_raises(self):
        with self.assertRaises(SystemExit):
            dz.classify_url('https://zenodo.org/nonsense/path')


def run_main(argv):
    """Run main() with argv; return (exit_code, stdout, stderr)."""
    out, err = io.StringIO(), io.StringIO()
    code = 0
    with mock.patch.object(sys, 'argv', ['download_zenodo.py'] + argv), \
            redirect_stdout(out), redirect_stderr(err):
        try:
            dz.main()
        except SystemExit as e:
            code = e.code
    return code, out.getvalue(), err.getvalue()


class TestPrintId(unittest.TestCase):
    def test_success_prints_only_dir(self):
        with mock.patch.object(dz, 'run_public', return_value=0) as run:
            code, out, err = run_main(['--zenodo-id', 'https://zenodo.org/records/1234567', '--print-id'])
        self.assertEqual(code, 0)
        self.assertEqual(out, 'zenodo-1234567\n')
        self.assertIn('Identifier', err)
        # sub-script output is routed to stderr
        self.assertIsNotNone(run.call_args.args[2])

    def test_failure_prints_nothing(self):
        with mock.patch.object(dz, 'run_public', return_value=1):
            code, out, _ = run_main(['--zenodo-id', '1234567', '--print-id'])
        self.assertEqual(code, 1)
        self.assertEqual(out, '')

    def test_jira_url_not_zenodo_exits_2_silently(self):
        with mock.patch.object(dz, 'get_replication_url_from_jira',
                               return_value='https://doi.org/10.60572/101y-vn15'):
            code, out, _ = run_main(['--jira-ticket', 'AEAREP-8815', '--print-id'])
        self.assertEqual(code, 2)
        self.assertEqual(out, '')


if __name__ == '__main__':
    unittest.main()
