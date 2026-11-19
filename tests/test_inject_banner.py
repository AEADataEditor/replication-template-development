#!/usr/bin/env python3
"""Tests for tools/inject_banner.py (preview/announcement banner injection)."""
import os
import sys
import tempfile
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import inject_banner  # noqa: E402

PAGE = "<html><head><title>x</title></head><body><p>hi</p></body></html>"


def _site(tmp):
    html = Path(tmp) / "html"
    (html / "sub").mkdir(parents=True)
    (html / "index.html").write_text(PAGE)
    (html / "sub" / "page.html").write_text(PAGE)
    (html / "nohead.html").write_text("<p>fragment</p>")
    return html


def test_no_config_no_preview_is_noop():
    with tempfile.TemporaryDirectory() as tmp:
        html = _site(tmp)
        inject_banner.main(["--config", str(Path(tmp) / "missing.yml"), "--html-dir", str(html)])
        assert (html / "index.html").read_text() == PAGE


def test_preview_injects_once_with_live_link():
    with tempfile.TemporaryDirectory() as tmp:
        html = _site(tmp)
        args = ["--config", str(Path(tmp) / "missing.yml"), "--html-dir", str(html),
                "--preview", "PR #1, commit abc1234", "--live-url", "https://example.org/site/"]
        inject_banner.main(args)
        text = (html / "sub" / "page.html").read_text()
        assert inject_banner.MARKER in text
        assert text.index(inject_banner.MARKER) < text.index("</head>")
        assert "Preview build (PR #1, commit abc1234)" in text
        assert "https://example.org/site/" in text and "Go to the live site" in text
        assert (html / "nohead.html").read_text() == "<p>fragment</p>"
        inject_banner.main(args)  # idempotent
        assert (html / "sub" / "page.html").read_text().count(inject_banner.MARKER) == 1


def test_preview_merges_enabled_announcement():
    with tempfile.TemporaryDirectory() as tmp:
        cfg = Path(tmp) / "banner.yml"
        cfg.write_text("enabled: true\nlevel: critical\nmessage: Outage tonight.\n"
                       "expires: '2000-01-01T00:00:00Z'\n")
        ann = inject_banner.load_config(cfg)
        merged = inject_banner.preview_config("PR #2", ann, "https://example.org/")
        assert merged["level"] == "critical"
        assert merged["message"].startswith("Preview build (PR #2)")
        assert merged["message"].endswith("Outage tonight.")
        assert merged["link"] == "https://example.org/"
        assert merged["expires"] == ""


def test_disabled_config_and_script_safe_payload():
    with tempfile.TemporaryDirectory() as tmp:
        cfg = Path(tmp) / "banner.yml"
        cfg.write_text("enabled: false\nmessage: hidden\n")
        assert inject_banner.load_config(cfg) is None
    snippet = inject_banner.build_snippet(inject_banner.with_id(
        {"level": "info", "message": "</script><b>", "link": "", "link_text": "", "expires": ""}))
    assert "</script><b>" not in snippet


if __name__ == "__main__":
    test_no_config_no_preview_is_noop()
    test_preview_injects_once_with_live_link()
    test_preview_merges_enabled_announcement()
    test_disabled_config_and_script_safe_payload()
    print("ok")
