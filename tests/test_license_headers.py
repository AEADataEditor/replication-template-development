#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2026 Lars Vilhuber and contributors.
# Author(s): Lars Vilhuber
# Licensed under the BSD 3-Clause License; see the LICENSE file at the repository root.

"""Every script must carry the SPDX license/copyright/author header."""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import license_headers  # noqa: E402


def test_style_for():
    assert license_headers.style_for("x.do") == ("* ", "")
    assert license_headers.style_for("x.m") == ("% ", "")
    assert license_headers.style_for("x.R") == ("# ", "")
    assert license_headers.style_for("x.txt") is None


def test_complete_header():
    good = ("#!/bin/bash\n# SPDX-License-Identifier: BSD-3-Clause\n"
            "# Copyright (c) 2020-2026 Lars Vilhuber and contributors.\n"
            "# Author(s): Lars Vilhuber\n# Licensed under ...\n")
    assert license_headers.has_complete_header(good)
    assert not license_headers.has_complete_header("#!/bin/bash\necho hi\n")
    assert license_headers.foreign_spdx("# SPDX-License-Identifier: MIT\n")
    assert not license_headers.foreign_spdx(good)


def test_year_span():
    assert license_headers.year_span([2020, 2026, 2021]) == "2020-2026"
    assert license_headers.year_span([2024]) == "2024"


def test_scripts_have_headers():
    r = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "license_headers.py"), "--check"],
                       capture_output=True, text=True, cwd=ROOT)
    assert r.returncode == 0, r.stderr


if __name__ == "__main__":
    test_style_for()
    test_complete_header()
    test_year_span()
    test_scripts_have_headers()
    print("ok")
