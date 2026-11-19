#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2026 Lars Vilhuber and contributors.
# Author(s): Lars Vilhuber
# Licensed under the BSD 3-Clause License; see the LICENSE file at the repository root.

"""Tests for tools/csv2md.py. Run: python3 tests/test_csv2md.py"""
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools"))
import csv2md


class TestCsv2md(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.dir.cleanup)
        self.csv = os.path.join(self.dir.name, 'in.csv')
        self.md = os.path.join(self.dir.name, 'out.md')

    def _convert(self, content):
        with open(self.csv, 'w', encoding='utf-8') as f:
            f.write(content)
        csv2md.csv_to_markdown(self.csv, self.md)
        with open(self.md, encoding='utf-8') as f:
            return f.read().splitlines()

    def test_plain(self):
        self.assertEqual(self._convert('A,B\n1,2\n'),
                         ['| A | B |', '| --- | --- |', '| 1 | 2 |'])

    def test_overflow_in_first_row_does_not_crash(self):
        # Unquoted comma in a one-column file: the extra field must be rejoined.
        lines = self._convert('Packages\nnumpy>=1.20,<2.0\npandas\n')
        self.assertEqual(lines, ['| Packages |', '| --- |',
                                 '| numpy>=1.20,<2.0 |', '| pandas |'])

    def test_overflow_in_later_row_is_rejoined(self):
        lines = self._convert('Packages\npandas\nnumpy>=1.20,<2.0\n')
        self.assertEqual(lines[-1], '| numpy>=1.20,<2.0 |')

    def test_short_row_is_padded(self):
        lines = self._convert('A,B\n1\n')
        self.assertEqual(lines[-1], '| 1 |  |')


if __name__ == '__main__':
    unittest.main()
