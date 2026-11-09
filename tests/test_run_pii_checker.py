#!/usr/bin/env python3
"""Tests for tools/run_pii_checker.py. Run: python3 tests/test_run_pii_checker.py

pii-checker is replaced by a stub interface.py that writes the two workbooks;
loading the model is stubbed.
"""
import os
import shutil
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools"))
import run_pii_checker  # noqa: E402

try:
    import openpyxl
except ImportError:
    openpyxl = None

# Writes the workbooks the way pii-checker --strip-details does (Overview sheet only)
STUB_INTERFACE = """import os, sys
from openpyxl import Workbook
assert '--strip-details' in sys.argv and os.environ['LLM_PROVIDER'] == 'ollama'
package = sys.argv[1]
if os.environ.get('STUB_FAIL'):
    sys.exit(0)  # pii-checker logs a failed package and exits 0
for name, extra in (('pii_checker_results.xlsx', 'Jane Doe'), ('pii_checker_results-nodetails.xlsx', None)):
    wb = Workbook()
    ws = wb.active
    ws.title = 'Overview'
    ws.append(['Metric', 'Value'])
    for row in (['Columns checked', 12], ['Flagged: direct PII', 2],
                ['Flagged: possible indirect PII', 3], ['Flagged: internal ID', 1]):
        ws.append(row)
    if extra:
        wb.create_sheet('Results').append([extra])
    wb.save(os.path.join(package, name))
"""


class TestEndpoint(unittest.TestCase):
    def route_file(self, lines):
        path = os.path.join(tempfile.mkdtemp(), 'route')
        self.addCleanup(shutil.rmtree, os.path.dirname(path))
        with open(path, 'w') as f:
            f.write("Iface\tDestination\tGateway\tFlags\n" + ''.join(l + '\n' for l in lines))
        return path

    def test_default_gateway_is_decoded(self):
        path = self.route_file(["eth0\t000011AC\t00000000\t0001", "eth0\t00000000\t010011AC\t0003"])
        self.assertEqual(run_pii_checker.default_gateway(path), '172.17.0.1')

    def test_no_default_route(self):
        path = self.route_file(["eth0\t000011AC\t00000000\t0001"])
        self.assertIsNone(run_pii_checker.default_gateway(path))
        self.assertIsNone(run_pii_checker.default_gateway('/nonexistent/route'))

    def test_precedence(self):
        path = self.route_file(["eth0\t00000000\t010011AC\t0003"])
        resolve = run_pii_checker.resolve_endpoint
        self.assertEqual(resolve('http://x:1', {'OLLAMA_ENDPOINTS': 'http://y:2'}, path), 'http://x:1')
        self.assertEqual(resolve(None, {'OLLAMA_ENDPOINTS': 'http://y:2, http://z:3'}, path), 'http://y:2')
        self.assertEqual(resolve(None, {}, path), 'http://172.17.0.1:11434')
        self.assertEqual(resolve(None, {}, '/nonexistent/route'), 'http://localhost:11434')


class TestSummary(unittest.TestCase):
    def test_counts_and_paths(self):
        text = run_pii_checker.summarize(
            {'Columns checked': 12, 'Flagged: direct PII': 2,
             'Flagged: possible indirect PII': 3, 'Flagged: internal ID': 1},
            'gemma4:26b', 'generated/n.xlsx', 'pii-checker-full/f.xlsx')
        self.assertIn('12 columns checked, 2 direct PII, 3 possible indirect PII, 1 internal IDs', text)
        self.assertIn('{{generated/n.xlsx}}', text)
        self.assertIn('{{pii-checker-full/f.xlsx}}', text)

    def test_missing_counts_show_question_marks(self):
        self.assertIn('? direct PII', run_pii_checker.summarize({}, 'm', 'a', 'b'))


@unittest.skipIf(openpyxl is None, "openpyxl not installed")
class TestMain(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.root)
        self.checker = os.path.join(self.root, 'pii-checker')
        os.makedirs(self.checker)
        with open(os.path.join(self.checker, 'interface.py'), 'w') as f:
            f.write(STUB_INTERFACE)
        self.deposit = os.path.join(self.root, '123456')
        os.makedirs(self.deposit)
        self.cwd = os.getcwd()
        os.chdir(self.root)
        self.addCleanup(os.chdir, self.cwd)
        patcher = mock.patch.object(run_pii_checker, 'load_model')
        self.load_model = patcher.start()
        self.addCleanup(patcher.stop)

    def run_main(self, *extra):
        return run_pii_checker.main(['123456', '--checker-dir', self.checker, '--endpoint', 'http://h:1',
                                     '--summary-file', 'summary.txt', *extra])

    def test_sorts_results_and_writes_summary(self):
        self.assertEqual(self.run_main(), 0)
        self.load_model.assert_called_once_with('http://h:1', 'gemma4:26b')
        self.assertTrue(os.path.isfile('pii-checker-full/pii_checker_results.xlsx'))
        self.assertTrue(os.path.isfile('generated/pii_checker_results-nodetails.xlsx'))
        self.assertEqual(os.listdir(self.deposit), [])  # nothing left in the deposit
        with open('summary.txt') as f:
            self.assertIn('12 columns checked, 2 direct PII', f.read())

    def test_missing_workbooks_fail(self):
        with mock.patch.dict(os.environ, {'STUB_FAIL': '1'}):
            self.assertEqual(self.run_main(), 1)
        self.assertFalse(os.path.exists('summary.txt'))

    def test_unreachable_ollama_fails_before_running(self):
        self.load_model.side_effect = OSError('connection refused')
        self.assertEqual(self.run_main(), 1)
        self.assertFalse(os.path.exists('generated'))

    def test_missing_directory(self):
        self.assertEqual(run_pii_checker.main(['nope', '--checker-dir', self.checker]), 2)


if __name__ == '__main__':
    unittest.main()
