#!/usr/bin/env python3
"""Every help page must end with the generated GitHub source link."""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import doc_source_links  # noqa: E402


def test_make_block():
    b = doc_source_links.make_block(["tools/x.py"])
    assert ":::{seealso}" in b and "tools/x.py" in b


def test_pages_up_to_date():
    r = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "doc_source_links.py"), "--check"],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr


if __name__ == "__main__":
    test_make_block()
    test_pages_up_to_date()
    print("ok")
