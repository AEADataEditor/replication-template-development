#!/usr/bin/env python3
"""Tests for tools/update_tools.sh. Run: python3 tests/test_update_tools.py

Runs the real script in a throwaway repository. Only the download is stubbed:
wget hands back an archive built here, using the real .gitignore.
"""
import os
import re
import shutil
import stat
import subprocess
import tempfile
import unittest
import zipfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PREFIX = "replication-template-master"
ARCHIVE_FILES = (
    "tools/x.sh", "tools/software-extensions.csv", "tools/software-filenames.csv",
    "automations/x.sh", "bitbucket-pipelines.yml", "template-x", "template/x",
    "docs/x.md", ".claude/x", "requirements.txt", "requirements-sivacor.txt",
    "requirements-manuscript.txt", "sample-language-report.md", "run.sh",
    "REPLICATION.md", "EXTERNAL-REPORT.md", "config.yml",
)
STUB_WGET = """#!/bin/sh
# usage: wget -O target url
cp "$ARCHIVE" "$2"
"""


def pipeline_requirement_files():
    """Requirements files at the top of the repository that pipelines install from."""
    with open(os.path.join(REPO, "bitbucket-pipelines.yml"), encoding="utf-8") as f:
        return set(re.findall(r"pip install -r (requirements[^\s;]*)", f.read()))


class UpdateToolsTest(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.root)
        archive = os.path.join(self.root, "archive.zip")
        with zipfile.ZipFile(archive, "w") as z:
            for name in ARCHIVE_FILES:
                z.writestr(f"{PREFIX}/{name}", "x\n")
            z.write(os.path.join(REPO, ".gitignore"), f"{PREFIX}/.gitignore")
        bindir = os.path.join(self.root, "bin")
        os.mkdir(bindir)
        wget = os.path.join(bindir, "wget")
        with open(wget, "w") as f:
            f.write(STUB_WGET)
        os.chmod(wget, os.stat(wget).st_mode | stat.S_IXUSR)
        self.work = os.path.join(self.root, "work")
        os.mkdir(self.work)
        self.env = dict(
            os.environ, PATH=bindir + os.pathsep + os.environ["PATH"], ARCHIVE=archive,
            GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1",
            GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@example.com",
            GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@example.com",
        )
        self.git("init", "-q")
        self.git("commit", "-q", "--allow-empty", "-m", "init")

    def git(self, *args):
        return subprocess.run(["git", *args], cwd=self.work, env=self.env, check=True,
                              capture_output=True, text=True).stdout

    def committed_after_refresh(self):
        subprocess.run(["bash", os.path.join(REPO, "tools", "update_tools.sh")], cwd=self.work,
                       env=self.env, check=True, capture_output=True)
        return set(self.git("ls-tree", "-r", "--name-only", "HEAD").splitlines())

    def test_manuscript_requirements_are_committed(self):
        self.assertIn("requirements-manuscript.txt", self.committed_after_refresh())

    def test_every_requirements_file_used_by_a_pipeline_is_committed(self):
        needed = pipeline_requirement_files()
        self.assertIn("requirements.txt", needed)
        self.assertEqual(needed - self.committed_after_refresh(), set())


if __name__ == "__main__":
    unittest.main()
