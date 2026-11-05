#!/usr/bin/env python3
"""Tests for automations/04_list_program_files.sh. Run: python3 tests/test_04_list_program_files.py

The replicator's main/master file choice lives in the REPLICATION.md template,
outside the generated block, so that re-filling the report does not overwrite it.
"""
import os
import re
import subprocess
import sys
import tempfile
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "tools"))
import replace_placeholders as rp

SCRIPT = os.path.join(REPO, "automations", "04_list_program_files.sh")
CHOICE = "> [ONE, NONE] is a main/master file."


class ProgramsSummaryTest(unittest.TestCase):
    def summary(self, *files):
        with tempfile.TemporaryDirectory() as tmp:
            deposit = os.path.join(tmp, "deposit")
            os.mkdir(deposit)
            for name in files:
                with open(os.path.join(deposit, name), "w") as f:
                    f.write("x\n")
            subprocess.run(["bash", SCRIPT, "deposit"], cwd=tmp, check=True, capture_output=True)
            with open(os.path.join(tmp, "generated", "programs-summary.txt")) as f:
                return f.read()

    def test_summary_does_not_contain_the_replicator_choice(self):
        out = self.summary("main.do")
        self.assertNotIn("ONE, NONE", out)
        self.assertNotIn("main/master", out)

    def test_summary_is_a_complete_sentence(self):
        out = self.summary("main.do", "a.do", "fig.R")
        self.assertIn("The deposit contains", out)
        self.assertRegex(out, r"2\s+do files,\s+1\s+r files\.\s*$")

    def test_summary_without_programs_says_so(self):
        self.assertIn("The deposit contains no program files.", self.summary("data.csv"))

    def test_summary_starts_with_a_timestamp_comment(self):
        first = self.summary("main.do").splitlines()[0]
        self.assertRegex(first, r"^<!-- Generated on .*\d{4}.* -->$")


class TemplateTest(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(REPO, "REPLICATION.md"), encoding="utf-8") as f:
            self.template = f.read()

    def test_choice_is_on_its_own_paragraph_after_the_placeholder(self):
        self.assertIn("{{ programs-summary.txt }}\n\n" + CHOICE + "\n\n", self.template)

    def test_replicator_choice_survives_a_refill(self):
        edited = self.template.replace(CHOICE, "> ONE is a main/master file.")
        once = rp.replace_content(edited, "<!-- Generated on A -->\nThe deposit contains 1 do files.\n",
                                  "programs-summary.txt")
        twice = rp.replace_content(once, "<!-- Generated on B -->\nThe deposit contains 2 do files.\n",
                                   "programs-summary.txt")
        self.assertIn("2 do files.", twice)
        self.assertNotIn("1 do files.", twice)
        self.assertIsNotNone(re.search(
            r"<!-- END GENERATED: programs-summary.txt -->\n\n> ONE is a main/master file\.\n", twice))


if __name__ == "__main__":
    unittest.main()
