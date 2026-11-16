#!/usr/bin/env python3
"""Tests for tools/run_pii_checker.py. Run: python3 tests/test_run_pii_checker.py

pii-checker is replaced by a stub interface.py that writes the two workbooks;
the Ollama calls (loading, unloading, measuring the speed) are stubbed.
"""
import datetime
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

    def test_link_to_the_pipeline_run_and_expiry_date(self):
        environ = {'BITBUCKET_BUILD_NUMBER': '7', 'BITBUCKET_STEP_UUID': '{ab-12}',
                   'BITBUCKET_GIT_HTTP_ORIGIN': 'https://bitbucket.org/ws/aearep-1'}
        text = run_pii_checker.summarize({}, 'm', 'a', 'b', environ, datetime.date(2026, 11, 13))
        self.assertIn('Artifacts tab of pipeline run '
                      '[#7|https://bitbucket.org/ws/aearep-1/pipelines/results/7/steps/%7Bab-12%7D] '
                      'until November 27, 2026.', text)

    def test_pipeline_run_fallbacks(self):
        run = run_pii_checker.pipeline_run
        self.assertEqual(run({}), 'the pipeline run')
        self.assertEqual(run({'BITBUCKET_BUILD_NUMBER': '7'}), 'pipeline run #7')
        self.assertEqual(run({'BITBUCKET_BUILD_NUMBER': '7', 'BITBUCKET_WORKSPACE': 'ws',
                              'BITBUCKET_REPO_SLUG': 'r'}),
                         'pipeline run [#7|https://bitbucket.org/ws/r/pipelines/results/7]')

    def test_missing_counts_show_question_marks(self):
        self.assertIn('? direct PII', run_pii_checker.summarize({}, 'm', 'a', 'b'))


class FakeClock:
    def __init__(self):
        self.now = 0.0

    def __call__(self):
        return self.now

    def sleep(self, seconds):
        self.now += seconds


class TestSpeed(unittest.TestCase):
    def setUp(self):
        self.clock = FakeClock()
        self.patches = {name: mock.patch.object(run_pii_checker, name).start()
                        for name in ('measure_speed', 'load_model', 'unload_model', 'other_models')}
        self.addCleanup(mock.patch.stopall)
        self.patches['other_models'].return_value = []

    def wait(self, rates, wait=30, retry=5):
        self.patches['measure_speed'].side_effect = rates
        return run_pii_checker.wait_for_speed('http://h:1', 'm', 10, wait, retry,
                                              clock=self.clock, sleep=self.clock.sleep, log=lambda t: None)

    def test_fast_enough_at_once(self):
        ok, message = self.wait([42.0])
        self.assertTrue(ok)
        self.assertIn('42.0 tokens/s', message)
        self.patches['unload_model'].assert_not_called()

    def test_reloads_until_fast(self):
        ok, _ = self.wait([3.0, 4.0, 40.0])
        self.assertTrue(ok)
        self.assertEqual(self.patches['unload_model'].call_count, 2)
        self.assertEqual(self.patches['load_model'].call_count, 2)
        self.assertEqual(self.clock.now, 600)

    def test_gives_up_after_the_wait(self):
        self.patches['other_models'].return_value = ['llama3:70b']
        ok, message = self.wait([3.0] * 20)
        self.assertFalse(ok)
        # attempts at 0, 5, ..., 30 minutes: 7 measurements, 6 reloads
        self.assertEqual(self.patches['measure_speed'].call_count, 7)
        self.assertEqual(self.clock.now, 1800)
        self.assertIn('at most 3.0 tokens/s', message)
        self.assertIn('also loaded: llama3:70b', message)
        self.assertIn('PiiWaitMinutes', message)

    def test_no_wait_means_one_measurement(self):
        ok, _ = self.wait([3.0], wait=0)
        self.assertFalse(ok)
        self.patches['load_model'].assert_not_called()


class TestMeasureSpeed(unittest.TestCase):
    def test_rate_from_eval_counts(self):
        with mock.patch.object(run_pii_checker, 'ollama', return_value={'eval_count': 64, 'eval_duration': 2e9}) as call:
            self.assertEqual(run_pii_checker.measure_speed('http://h:1', 'm'), 32.0)
        payload = call.call_args.args[2]
        self.assertNotIn('num_ctx', payload['options'])  # would make Ollama reload the model

    def test_missing_counts(self):
        with mock.patch.object(run_pii_checker, 'ollama', return_value={}):
            self.assertEqual(run_pii_checker.measure_speed('http://h:1', 'm'), 0.0)

    def test_other_models(self):
        loaded = {'models': [{'name': 'm'}, {'name': 'x:7b'}]}
        with mock.patch.object(run_pii_checker, 'ollama', return_value=loaded):
            self.assertEqual(run_pii_checker.other_models('http://h:1', 'm'), ['x:7b'])
        with mock.patch.object(run_pii_checker, 'ollama', side_effect=OSError):
            self.assertEqual(run_pii_checker.other_models('http://h:1', 'm'), [])


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
        self.load_model = mock.patch.object(run_pii_checker, 'load_model').start()
        self.unload_model = mock.patch.object(run_pii_checker, 'unload_model').start()
        self.wait_for_speed = mock.patch.object(run_pii_checker, 'wait_for_speed',
                                                return_value=(True, 'fast')).start()
        self.addCleanup(mock.patch.stopall)

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

    def test_speed_options_are_passed(self):
        self.assertEqual(self.run_main('--min-tokens-per-sec', '20', '--wait-minutes', '10',
                                       '--retry-minutes', '2'), 0)
        self.wait_for_speed.assert_called_once_with('http://h:1', 'gemma4:26b', 20.0, 10.0, 2.0)

    def test_too_slow_writes_the_reason_and_skips_pii_checker(self):
        self.wait_for_speed.return_value = (False, 'pii-checker did not run: too slow')
        self.assertEqual(self.run_main(), run_pii_checker.SLOW)
        self.unload_model.assert_called_once()
        self.assertFalse(os.path.exists('generated'))
        with open('summary.txt') as f:
            self.assertIn('too slow', f.read())

    def test_zero_skips_the_check(self):
        self.assertEqual(self.run_main('--min-tokens-per-sec', '0'), 0)
        self.wait_for_speed.assert_not_called()

    def test_missing_directory(self):
        self.assertEqual(run_pii_checker.main(['nope', '--checker-dir', self.checker]), 2)


if __name__ == '__main__':
    unittest.main()
