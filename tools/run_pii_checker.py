#!/usr/bin/env python3
"""
Run pii-checker (https://github.com/AEADataEditor/pii-checker) on a deposit
and sort its results into what may be committed and what may not.

pii-checker writes two workbooks into the package directory (with
--strip-details):
  pii_checker_results.xlsx            includes the values shown to the model
  pii_checker_results-nodetails.xlsx  the same without those values
The first is moved to --full-dir (a build artifact, never committed), the
second to --output-dir. A one-paragraph summary of the counts goes to
--summary-file, for the Jira comment.

Ollama is reached at --endpoint, else $OLLAMA_ENDPOINTS, else port 11434 of
the default gateway: in a container started by a Bitbucket Docker runner, the
gateway is the host that also serves Ollama. The model is loaded before
pii-checker starts, because pii-checker's own test call gives up after 30
seconds, which loading a large model from disk can exceed.

Usage:
    python3 tools/run_pii_checker.py DIRECTORY --checker-dir PATH [--model NAME]
        [--endpoint URL] [--full-dir DIR] [--output-dir DIR] [--summary-file FILE]

Run it with a Python that has pii-checker's requirements installed (it runs
pii-checker with the same interpreter); automations/34_run_pii_checker.sh
sets that up.
"""

import argparse
import json
import os
import shutil
import socket
import struct
import subprocess
import sys
import urllib.request

RESULTS = 'pii_checker_results.xlsx'
NODETAILS = 'pii_checker_results-nodetails.xlsx'
OLLAMA_PORT = 11434
LOAD_TIMEOUT = 900  # seconds; a 25B model loads from a cold disk in a few minutes

# Overview sheet labels of pii-checker's results workbook
COUNTS = [
    ('Columns checked', 'columns checked'),
    ('Flagged: direct PII', 'direct PII'),
    ('Flagged: possible indirect PII', 'possible indirect PII'),
    ('Flagged: internal ID', 'internal IDs'),
]


def default_gateway(route_file='/proc/net/route'):
    """IPv4 address of the default gateway, or None."""
    try:
        with open(route_file) as f:
            next(f)  # header
            for line in f:
                fields = line.split()
                if len(fields) > 2 and fields[1] == '00000000':
                    return socket.inet_ntoa(struct.pack('<L', int(fields[2], 16)))
    except (OSError, ValueError, StopIteration):
        pass
    return None


def resolve_endpoint(endpoint=None, environ=os.environ, route_file='/proc/net/route'):
    if endpoint:
        return endpoint
    if environ.get('OLLAMA_ENDPOINTS'):
        return environ['OLLAMA_ENDPOINTS'].split(',')[0].strip()
    gateway = default_gateway(route_file)
    return f"http://{gateway or 'localhost'}:{OLLAMA_PORT}"


def load_model(endpoint, model, timeout=LOAD_TIMEOUT):
    """Asks Ollama to load the model (a generate call without a prompt)."""
    request = urllib.request.Request(
        endpoint.rstrip('/') + '/api/generate',
        data=json.dumps({'model': model, 'keep_alive': '15m'}).encode(),
        headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        response.read()


def read_overview(path):
    """{Metric: Value} from the Overview sheet of a results workbook."""
    from openpyxl import load_workbook
    workbook = load_workbook(path, read_only=True)
    try:
        if 'Overview' not in workbook.sheetnames:
            return {}
        rows = workbook['Overview'].iter_rows(min_row=2, values_only=True)
        return {row[0]: row[1] for row in rows if row and row[0] is not None}
    finally:
        workbook.close()


def summarize(overview, model, nodetails_path, full_path):
    counts = ', '.join(f"{overview.get(label, '?')} {text}" for label, text in COUNTS)
    return (f"pii-checker (model {model}): {counts}. "
            f"Results without the values observed in the data: {{{{{nodetails_path}}}}}. "
            f"The full results, with the values shown to the model, are not committed: "
            f"download {{{{{full_path}}}}} from the build's Artifacts tab within 14 days.")


def parse_args(argv):
    parser = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    parser.add_argument('directory', help='deposit directory to check')
    parser.add_argument('--checker-dir', required=True, help='pii-checker checkout')
    parser.add_argument('--model', default='gemma4:26b', help='Ollama model (default: %(default)s)')
    parser.add_argument('--endpoint', help='Ollama URL (default: $OLLAMA_ENDPOINTS, else the default gateway)')
    parser.add_argument('--full-dir', default='pii-checker-full',
                        help='where the full results go; must not be committed (default: %(default)s)')
    parser.add_argument('--output-dir', default='generated',
                        help='where the results without values go (default: %(default)s)')
    parser.add_argument('--summary-file', help='write the summary here as well as to stdout')
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    if not os.path.isdir(args.directory):
        print(f"run_pii_checker: not a directory: {args.directory}", file=sys.stderr)
        return 2

    endpoint = resolve_endpoint(args.endpoint)
    print(f"run_pii_checker: loading {args.model} on {endpoint}", file=sys.stderr)
    try:
        load_model(endpoint, args.model)
    except OSError as e:
        print(f"run_pii_checker: could not load {args.model} on {endpoint}: {e}", file=sys.stderr)
        return 1

    env = dict(os.environ, LLM_PROVIDER='ollama', OLLAMA_ENDPOINTS=endpoint)
    run = subprocess.run(
        [sys.executable, os.path.join(args.checker_dir, 'interface.py'),
         os.path.abspath(args.directory), '--strip-details', '--model', args.model],
        cwd=args.checker_dir, env=env)
    if run.returncode != 0:
        print(f"run_pii_checker: pii-checker exited with {run.returncode}", file=sys.stderr)
        return run.returncode

    # pii-checker logs a failed package and exits 0: the workbooks tell
    produced = {name: os.path.join(args.directory, name) for name in (RESULTS, NODETAILS)}
    missing = [name for name, path in produced.items() if not os.path.isfile(path)]
    if missing:
        print(f"run_pii_checker: pii-checker did not write {', '.join(missing)}", file=sys.stderr)
        return 1

    os.makedirs(args.full_dir, exist_ok=True)
    os.makedirs(args.output_dir, exist_ok=True)
    full_path = os.path.join(args.full_dir, RESULTS)
    nodetails_path = os.path.join(args.output_dir, NODETAILS)
    shutil.move(produced[RESULTS], full_path)
    shutil.move(produced[NODETAILS], nodetails_path)

    summary = summarize(read_overview(nodetails_path), args.model, nodetails_path, full_path)
    print(summary)
    if args.summary_file:
        with open(args.summary_file, 'w') as f:
            f.write(summary + '\n')
    return 0


if __name__ == '__main__':
    sys.exit(main())
