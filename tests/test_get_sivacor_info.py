#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2026 Lars Vilhuber and contributors.
# Author(s): Lars Vilhuber
# Licensed under the BSD 3-Clause License; see the LICENSE file at the repository root.

"""Tests for get_sivacor_info.py. Run: python3 tests/test_get_sivacor_info.py"""
import os
import sys
import unittest
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools"))
import get_sivacor_info as gsi

VERIFICATION_BOX = "- [x] The reproducibility check was conducted by a trusted verification system"
THIRD_PARTY = "trusted third-party"


class BoxWordingTest(unittest.TestCase):
    def setUp(self):
        patcher = mock.patch.object(gsi, "extract_tro_summary", return_value={})
        patcher.start()
        self.addCleanup(patcher.stop)
        for name in ("format_sivacor_steps", "format_sivacor_environment"):
            p = mock.patch.object(gsi, name, return_value="body")
            p.start()
            self.addCleanup(p.stop)

    def test_replication_steps_checks_verification_system_box(self):
        out = gsi.format_sivacor_replication_steps_insert({})
        self.assertIn(VERIFICATION_BOX, out)
        self.assertNotIn(THIRD_PARTY, out)

    def test_computing_environment_checks_verification_system_box(self):
        out = gsi.format_sivacor_computing_environment_insert({})
        self.assertIn(VERIFICATION_BOX, out)
        self.assertNotIn(THIRD_PARTY, out)


def artifact(i, h):
    return {"@id": f"composition/1/artifact/{i}", "trov:hash": {"trov:hashAlgorithm": "sha256", "trov:hashValue": h}}


def arrangement(n, comment, files):
    """files: list of (path, artifact index)."""
    return {
        "@id": f"arrangement/{n}",
        "rdfs:comment": comment,
        "trov:hasArtifactLocation": [
            {"trov:path": p, "trov:artifact": {"@id": f"composition/1/artifact/{a}"}} for p, a in files
        ],
    }


def performance(n, comment, before, after, **extra):
    perf = {
        "@id": f"trp/{n}",
        "rdfs:comment": comment,
        "trov:accessedArrangement": {"trov:arrangement": {"@id": f"arrangement/{before}"}},
        "trov:contributedToArrangement": {"trov:arrangement": {"@id": f"arrangement/{after}"}},
    }
    perf.update(extra)
    return perf


def make_tro():
    """Nested package dir, a run step that modifies a file, then a pruning step."""
    artifacts = [artifact(i, f"h{i}") for i in range(9)]
    a0 = [("pkg/main.do", 0), ("pkg/data/in.csv", 1), ("pkg/results/old.tex", 2), ("pkg/data/big.zip", 3)]
    a1 = [("pkg/main.do", 0), ("pkg/data/in.csv", 1), ("pkg/results/old.tex", 4),  # modified
          ("pkg/data/big.zip", 3), ("pkg/data/extracted.dat", 5),
          ("pkg/results/fig1.PNG", 6), ("pkg/results/t1.tex", 7), ("pkg/main.log", 8)]
    a2 = [p for p in a1 if p[0] not in {"pkg/data/extracted.dat", "pkg/data/in.csv"}]
    root = {
        "@id": "tro",
        "@type": ["trov:TransparentResearchObject"],
        "trov:hasComposition": {"trov:hasArtifact": artifacts},
        "trov:hasArrangement": [
            arrangement(0, "Before executing workflow", a0),
            arrangement(1, "After executing workflow step 1", a1),
            arrangement(2, "After executing workflow step 2", a2),
        ],
        "trov:hasPerformance": [
            performance(0, "SIVACOR workflow execution (main.do) step 1", 0, 1,
                        **{"sivacor:DockerRunArgs": ["stata", "main.do"]}),
            performance(1, "SIVACOR Workspace pruning step", 1, 2),
        ],
    }
    return {"@graph": [root]}


class FindingsTest(unittest.TestCase):
    def setUp(self):
        self.summary = gsi.extract_tro_summary(make_tro())
        self.findings = gsi.format_sivacor_findings(self.summary)

    def test_counts_use_files_not_paths(self):
        self.assertIn("- Initial arrangement: 4 files. Final arrangement: 6 files.", self.findings)
        self.assertIn("SIVACOR recorded 3 new files, 1 removed file, and 1 modified file", self.findings)
        self.assertNotIn(" path", self.findings)

    def test_suffix_classification_is_not_path_based(self):
        # nested under pkg/ and upper-case suffix: fig1.PNG counts as png
        self.assertIn("- Figures created or modified (based on file suffixes):\n  - 1 `png` file", self.findings)
        # created t1.tex + modified old.tex
        self.assertIn("- Tables created or modified (based on file suffixes):\n  - 2 `tex` files", self.findings)
        self.assertIn("- Other new files: 1 file.", self.findings)  # main.log

    def test_per_step_breakdown_lists_modified_files(self):
        self.assertIn("#### Changes by step", self.findings)
        self.assertIn("A detailed breakdown by step follows.", self.findings)
        self.assertIn(
            "- Step 1 (`main.do`; `Before executing workflow` to `After executing workflow step 1`):\n"
            "  - 4 files added\n  - 0 files removed\n  - 1 file modified\n    - `pkg/results/old.tex`",
            self.findings,
        )
        self.assertIn(
            "- Step 2 (SIVACOR Workspace pruning step; `After executing workflow step 1` to `After executing workflow step 2`):\n"
            "  - 0 files added\n  - 2 files removed\n  - 0 files modified",
            self.findings,
        )

    def test_caveat_is_separate_paragraph(self):
        self.assertTrue(self.findings.endswith(
            "\n\nSIVACOR is used here to document execution and generated files. "
            "It is not designed to compare figures and tables against the manuscript."))
        self.assertNotIn("concentrated in", self.findings)

    def test_single_step_has_no_breakdown(self):
        tro = make_tro()
        root = tro["@graph"][0]
        root["trov:hasArrangement"] = root["trov:hasArrangement"][:2]
        root["trov:hasPerformance"] = root["trov:hasPerformance"][:1]
        findings = gsi.format_sivacor_findings(gsi.extract_tro_summary(tro))
        self.assertNotIn("Changes by step", findings)
        self.assertNotIn("A detailed breakdown by step follows.", findings)

    def test_breakdown_falls_back_to_consecutive_arrangements(self):
        tro = make_tro()
        for perf in tro["@graph"][0]["trov:hasPerformance"]:
            del perf["trov:accessedArrangement"], perf["trov:contributedToArrangement"]
        findings = gsi.format_sivacor_findings(gsi.extract_tro_summary(tro))
        self.assertIn("- Step 2 (SIVACOR Workspace pruning step; `After executing workflow step 1`", findings)

    def test_appendix_groups(self):
        appendix = gsi.format_sivacor_appendix(self.summary)
        self.assertIn("#### Figures created or modified (based on file suffixes)\n\n- `pkg/results/fig1.PNG`", appendix)
        self.assertIn("#### Tables created or modified (based on file suffixes)\n\n- `pkg/results/old.tex`\n- `pkg/results/t1.tex`", appendix)
        self.assertIn("#### Other new files\n\n- `pkg/main.log`", appendix)
        self.assertIn("#### Modified files\n\n- `pkg/results/old.tex`", appendix)
        self.assertIn("#### Removed files\n\n- `pkg/data/in.csv`", appendix)
        self.assertNotIn(" path", appendix)


class StepWordingTest(unittest.TestCase):
    def test_pruning_step_is_not_a_run(self):
        steps = gsi.format_sivacor_steps(gsi.extract_tro_summary(make_tro()))
        self.assertIn("- Step 1: SIVACOR ran `main.do` (step 1).", steps)
        self.assertIn("- Step 2: SIVACOR Workspace pruning step.", steps)
        self.assertNotIn("ran `SIVACOR Workspace pruning step`", steps)


class PartbSummaryTest(unittest.TestCase):
    def setUp(self):
        self.out = gsi.format_partb_summary(make_tro())

    def test_uses_files_and_per_step_changes(self):
        self.assertIn(
            "- Step 1 ran `main.do` (step 1), reading the `Before executing workflow` arrangement (4 files) "
            "and producing the `After executing workflow step 1` arrangement (8 files).\n"
            "  - 4 files added\n  - 0 files removed\n  - 1 file modified\n    - `pkg/results/old.tex`",
            self.out,
        )
        self.assertIn(
            "- Step 2 (SIVACOR Workspace pruning step) read the `After executing workflow step 1` arrangement (8 files) "
            "and produced the `After executing workflow step 2` arrangement (6 files).\n"
            "  - 0 files added\n  - 2 files removed\n  - 0 files modified",
            self.out,
        )

    def test_drops_paths_and_concentrated_in(self):
        self.assertNotIn(" path", self.out)
        self.assertNotIn("concentrated in", self.out)


if __name__ == "__main__":
    unittest.main()
