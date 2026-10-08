#!/usr/bin/env python3
"""Tests for tools/automation_doc_links.py. Run: python3 tests/test_automation_doc_links.py"""
import io
import os
import shutil
import sys
import tempfile
import textwrap
import unittest
from contextlib import redirect_stderr, redirect_stdout

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "tools"))
import automation_doc_links as adl  # noqa: E402

PIPELINES = textwrap.dedent("""\
    image: python:3.12
    definitions:
      steps:
        - step: &shared-anchor
            name: Shared step
            script:
              - chmod a+rx ./automations/*.sh
              - ./automations/01_b.sh $projectID
    pipelines:
      custom:
        p-one: #name of this pipeline
          - variables:
              - name: jiraticket
          - step:
              name: First step
              image:
                name: some/image:latest
              script:
                - ./automations/00_a.sh $projectID
                # - ./automations/01_b.sh commented out
                - swDetected=$(./automations/00_a.sh again) || true
        p-two:
          - step:
              <<: *shared-anchor
              name: Overridden name
    """)


class TestAutomationDocLinks(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp()
        os.makedirs(os.path.join(self.root, "automations"))
        os.makedirs(os.path.join(self.root, "docs", "automations"))
        self.write("bitbucket-pipelines.yml", PIPELINES)
        self.write("automations/00_a.sh", "#!/bin/bash\necho hi\n")
        self.write("automations/01_b.sh",
                   "#!/bin/bash\n# ./automations/02_c.sh is only mentioned here\n"
                   "echo \"run ./automations/02_c.sh\"\nif ! ./automations/02_c.sh -x\nthen exit 1; fi\n")
        self.write("automations/02_c.sh", "#!/bin/bash\n")
        self.write("automations/03_d.sh", "#!/bin/bash\n")
        self.write("docs/automations/96-92-bitbucket-pipelines.md",
                   "# Pipelines\n\n(pipeline-p-one)=\n### p-one\n\n(pipeline-p-two)=\n### p-two\n")
        for stem in ("00_a", "01_b", "02_c", "03_d"):
            self.write(f"docs/automations/96-92-{stem}.md", f"(help-{stem})=\n\n# {stem}.sh - Title\n\nBody.\n")

    def tearDown(self):
        shutil.rmtree(self.root)

    def write(self, rel, text):
        with open(os.path.join(self.root, rel), "w", encoding="utf-8") as fh:
            fh.write(text)

    def read(self, rel):
        with open(os.path.join(self.root, rel), encoding="utf-8") as fh:
            return fh.read()

    def run_tool(self, *args):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            rc = adl.main(["--root", self.root, *args])
        return rc, out.getvalue(), err.getvalue()

    def test_scan_pipelines(self):
        calls = adl.scan_pipelines(os.path.join(self.root, "bitbucket-pipelines.yml"))
        self.assertEqual(calls["00_a.sh"], [("p-one", "First step", None, 19), ("p-one", "First step", None, 21)])
        # anchor calls are attributed to the pipeline using the anchor; the commented line is ignored
        self.assertEqual(calls["01_b.sh"], [("p-two", "Overridden name", "shared-anchor", 8)])

    def test_scan_scripts_ignores_comments_and_echo(self):
        calls = adl.scan_scripts(self.root)
        self.assertEqual(calls, {"02_c.sh": [("01_b.sh", 4)]})

    def test_write_then_check(self):
        rc, out, _ = self.run_tool("--check")
        self.assertEqual(rc, 1)
        self.assertIn("stale", out)
        rc, _, _ = self.run_tool()
        self.assertEqual(rc, 0)
        page = self.read("docs/automations/96-92-00_a.md")
        self.assertTrue(page.startswith(f"(help-00_a)=\n\n# 00_a.sh - Title\n\n{adl.BEGIN}\n"))
        self.assertIn(":::{attention} Usually run by a Bitbucket pipeline", page)
        self.assertIn("[`p-one`](#pipeline-p-one), step \"First step\": [line 19](", page)
        self.assertIn("bitbucket-pipelines.yml#L21)", page)
        self.assertIn(f"{adl.END}\n\nBody.\n", page)
        self.assertIn("Usually run by another automation script", self.read("docs/automations/96-92-02_c.md"))
        self.assertIn("[`01_b.sh`](#help-01_b): [line 4]", self.read("docs/automations/96-92-02_c.md"))
        self.assertIn("Not currently called by any pipeline", self.read("docs/automations/96-92-03_d.md"))
        rc, out, _ = self.run_tool("--check")
        self.assertEqual((rc, out), (0, ""))

    def test_block_is_replaced_when_lines_move(self):
        self.run_tool()
        self.write("bitbucket-pipelines.yml", "# new first line\n" + PIPELINES)
        rc, _, _ = self.run_tool("--check")
        self.assertEqual(rc, 1)
        self.run_tool()
        page = self.read("docs/automations/96-92-00_a.md")
        self.assertIn("#L20)", page)
        self.assertNotIn("#L19)", page)
        self.assertEqual(page.count(adl.BEGIN), 1)

    def test_missing_page_and_label_are_errors(self):
        os.remove(os.path.join(self.root, "docs/automations/96-92-03_d.md"))
        self.write("docs/automations/96-92-bitbucket-pipelines.md", "# Pipelines\n\n(pipeline-p-one)=\n")
        rc, _, err = self.run_tool()
        self.assertEqual(rc, 1)
        self.assertIn("automations/03_d.sh: no page", err)
        self.assertIn("(pipeline-p-two)=", err)

    def test_repository_docs_are_current(self):
        out_buf, err_buf = io.StringIO(), io.StringIO()
        with redirect_stdout(out_buf), redirect_stderr(err_buf):
            rc = adl.main(["--check"])
        self.assertEqual(rc, 0, "run python3 tools/automation_doc_links.py\n" + out_buf.getvalue() + err_buf.getvalue())


if __name__ == "__main__":
    unittest.main()
