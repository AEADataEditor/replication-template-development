#!/usr/bin/env python3
"""Tests for tools/compare_manifests.py and automations/22_compare_manifests.sh.

Run: python3 tests/test_compare_manifests.py
"""
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "tools"))

import compare_manifests as cm  # noqa: E402

A, B, C, D, E = ("a" * 64, "b" * 64, "c" * 64, "d" * 64, "e" * 64)


class TestCompare(unittest.TestCase):
    def test_identical(self):
        r = cm.compare({"x/a.do": A, "b.do": B}, {"x/a.do": A, "b.do": B})
        self.assertEqual(r["unchanged"], 2)
        self.assertEqual(cm.n_meaningful(r), 0)
        self.assertEqual(r["moved"], [])

    def test_content_changed(self):
        r = cm.compare({"a.do": A, "b.do": B}, {"a.do": C, "b.do": B})
        self.assertEqual(r["content_changed"], ["a.do"])
        self.assertEqual(r["unchanged"], 1)

    def test_move_is_not_meaningful(self):
        r = cm.compare({"old/a.do": A}, {"new/a.do": A})
        self.assertEqual(r["moved"], [("old/a.do", "new/a.do")])
        self.assertEqual(cm.n_meaningful(r), 0)

    def test_rename(self):
        r = cm.compare({"code/a.do": A}, {"code/b.do": A})
        self.assertEqual(r["renamed"], [("code/a.do", "code/b.do")])
        self.assertEqual(r["moved"], [])

    def test_rename_and_move(self):
        r = cm.compare({"old/a.do": A}, {"new/b.do": A})
        self.assertEqual(r["renamed"], [("old/a.do", "new/b.do")])

    def test_moved_and_changed(self):
        r = cm.compare({"old/a.do": A}, {"new/a.do": B})
        self.assertEqual(r["moved_changed"], [("old/a.do", "new/a.do")])
        self.assertEqual(r["added"], [])
        self.assertEqual(r["removed"], [])

    def test_ambiguous_name_is_added_and_removed(self):
        # Two candidates with the same name: don't guess a move.
        r = cm.compare({"x/f.txt": A, "y/f.txt": B}, {"z/f.txt": C})
        self.assertEqual(r["moved_changed"], [])
        self.assertEqual(sorted(r["removed"]), ["x/f.txt", "y/f.txt"])
        self.assertEqual(r["added"], [("z/f.txt", [])])

    def test_added_removed(self):
        r = cm.compare({"a.do": A, "gone.do": B}, {"a.do": A, "new.do": C})
        self.assertEqual(r["added"], [("new.do", [])])
        self.assertEqual(r["removed"], ["gone.do"])

    def test_added_copy_is_flagged(self):
        r = cm.compare({"a.do": A}, {"a.do": A, "copy/a2.do": A})
        self.assertEqual(r["added"], [("copy/a2.do", ["a.do"])])

    def test_repeated_names_do_not_inflate_counts(self):
        # Regression: the old tool cross-joined files sharing a basename.
        old = {f"NDC {y}/firms.txt": c for y, c in zip(range(2000, 2004), (A, B, C, D))}
        new = dict(old)
        new["NDC 2003/firms.txt"] = E
        r = cm.compare(old, new)
        self.assertEqual(r["unchanged"], 3)
        self.assertEqual(r["content_changed"], ["NDC 2003/firms.txt"])
        self.assertEqual(cm.n_meaningful(r), 1)

    def test_duplicate_contents_moved_together(self):
        old = {"old/a.txt": A, "old/b.txt": A}
        new = {"new/a.txt": A, "new/b.txt": A}
        r = cm.compare(old, new)
        self.assertEqual(r["moved"], [("old/a.txt", "new/a.txt"), ("old/b.txt", "new/b.txt")])
        self.assertEqual(cm.group_moves(r["moved"]), [(("old", "new"), 2)])

    def test_dot_slash_normalized(self):
        with tempfile.TemporaryDirectory() as d:
            p1, p2 = os.path.join(d, "m1"), os.path.join(d, "m2")
            open(p1, "w").write(f"{A}  ./x/a.do\n")
            open(p2, "w").write(f"{A}  x/a.do\n")
            r = cm.compare(cm.parse_manifest(p1), cm.parse_manifest(p2))
            self.assertEqual(r["unchanged"], 1)

    def test_paths_with_spaces(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "m")
            open(p, "w").write(f"{A}  ./NDC 2001 (12-31-2001)/firms.txt\n")
            self.assertEqual(cm.parse_manifest(p), {"NDC 2001 (12-31-2001)/firms.txt": A})


class TestRollUp(unittest.TestCase):
    def test_new_directory_rolls_up_to_topmost_new_dir(self):
        old = {"code/a.do": A}
        new = {"code/a.do": A, "ado/plus/x.ado": B, "ado/plus/y.ado": C, "ado/z.trk": D,
               "code/new.do": E}
        r = cm.compare(old, new)
        items = dict((h, i) for h, _, i in cm.category_items(r))["Added"]
        self.assertEqual(items, ["`ado/` (new directory, 3 files)", "`code/new.do`"])

    def test_removed_directory_and_single_file_dir(self):
        old = {"keep.do": A, "scratch/1.dta": B, "scratch/2.dta": C, "lonely/only.txt": D}
        new = {"keep.do": A}
        r = cm.compare(old, new)
        heading_n = {h: n for h, n, _ in cm.category_items(r)}
        items = dict((h, i) for h, _, i in cm.category_items(r))["Removed"]
        self.assertEqual(heading_n["Removed"], 3)
        self.assertEqual(items, ["`scratch/` (removed directory, 2 files)", "`lonely/only.txt`"])


class TestCli(unittest.TestCase):
    def test_summary_lists_and_truncates(self):
        old = {f"f{i:03d}.csv": A for i in range(30)}
        old["keep.do"] = B
        new = {"keep.do": C}
        with tempfile.TemporaryDirectory() as d:
            p1, p2, s = (os.path.join(d, n) for n in ("prev.sha256", "cur.sha256", "sum.md"))
            for path, entries in ((p1, old), (p2, new)):
                with open(path, "w") as f:
                    f.writelines(f"{c}  ./{p}\n" for p, c in entries.items())
            out = subprocess.run([sys.executable, os.path.join(REPO, "tools", "compare_manifests.py"),
                                  p1, p2, "--summary-file", s],
                                 capture_output=True, text=True, check=True).stdout
            summary = open(s).read()
        self.assertIn("**Content changed** (1):", summary)
        self.assertIn("- `keep.do`", summary)
        self.assertIn("**Removed** (30):", summary)
        self.assertIn("... and 5 more", summary)
        self.assertIn("`f029.csv`", out)  # full report lists everything


class TestSelectionScript(unittest.TestCase):
    """22_compare_manifests.sh must pick manifests by date in the name, not mtime."""

    def test_picks_latest_dated_public_manifests(self):
        with tempfile.TemporaryDirectory() as d:
            for sub in ("automations", "tools", "generated"):
                os.makedirs(os.path.join(d, sub))
            shutil.copy(os.path.join(REPO, "automations", "22_compare_manifests.sh"),
                        os.path.join(d, "automations"))
            shutil.copy(os.path.join(REPO, "tools", "compare_manifests.py"), os.path.join(d, "tools"))
            gen = os.path.join(d, "generated")
            files = {
                "manifest.2024-01-01.sha256": f"{A}  ./a.do\n",
                "manifest.2026-11-03.sha256": f"{A}  ./a.do\n",
                "manifest.2026-11-06.sha256": f"{B}  ./a.do\n",
                "manifest.restricted.2024-11-28.sha256": f"{C}  ./secret.dta\n",
            }
            for name, body in files.items():
                open(os.path.join(gen, name), "w").write(body)
            # Make mtimes misleading: oldest-named files newest on disk.
            for i, name in enumerate(["manifest.2026-11-06.sha256", "manifest.2026-11-03.sha256",
                                      "manifest.2024-01-01.sha256",
                                      "manifest.restricted.2024-11-28.sha256"]):
                os.utime(os.path.join(gen, name), (1_000_000 + i * 1000,) * 2)
            subprocess.run(["bash", os.path.join(d, "automations", "22_compare_manifests.sh")],
                           capture_output=True, text=True, check=True, env={**os.environ, "SkipProcessing": "no"})
            report = open(os.path.join(gen, "manifest-comparison.md")).read()
        self.assertIn("**Previous Manifest:** `manifest.2026-11-03.sha256`", report)
        self.assertIn("**Current Manifest:** `manifest.2026-11-06.sha256`", report)
        self.assertIn("- `a.do`", report)


if __name__ == "__main__":
    unittest.main()
