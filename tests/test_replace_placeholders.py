#!/usr/bin/env python3
"""Tests for replace_placeholders.py. Run: python3 tests/test_replace_placeholders.py"""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools"))
import replace_placeholders as rp


class ReplaceContentTest(unittest.TestCase):
    def test_plain_placeholder_is_wrapped_in_markers(self):
        template = "before\n\n{{ frag.md }}\n\nafter\n"
        out = rp.replace_content(template, "generated line\n", "frag.md")
        self.assertIn("<!-- BEGIN GENERATED: frag.md -->", out)
        self.assertIn("<!-- END GENERATED: frag.md -->", out)
        self.assertIn("generated line", out)
        self.assertNotIn("{{ frag.md }}", out)

    def test_rerun_with_unchanged_content_is_idempotent(self):
        template = "x\n{{ frag.md }}\ny\n"
        once = rp.replace_content(template, "content\n", "frag.md")
        twice = rp.replace_content(once, "content\n", "frag.md")
        self.assertEqual(once, twice)

    def test_marker_stays_outside_a_code_fence_around_the_placeholder(self):
        template = "intro\n\n```\n{{ list.txt }}\n```\n\noutro\n"
        out = rp.replace_content(template, "a\nb\nc\n", "list.txt")
        lines = out.splitlines()
        begin = lines.index("<!-- BEGIN GENERATED: list.txt -->")
        end = lines.index("<!-- END GENERATED: list.txt -->")
        fences = [i for i, l in enumerate(lines) if l.strip() == "```"]
        # both fences must be strictly between the two markers
        self.assertTrue(all(begin < f < end for f in fences),
                        f"fences {fences} not inside markers ({begin}, {end}):\n{out}")
        self.assertEqual(len(fences), 2)
        # the generated content is still fenced
        self.assertIn("```\na\nb\nc\n```", out)

    def test_rerun_preserves_a_fence_that_wraps_the_generated_content(self):
        template = "intro\n\n```\n{{ list.txt }}\n```\n\noutro\n"
        once = rp.replace_content(template, "a\nb\n", "list.txt")
        twice = rp.replace_content(once, "a\nb\n", "list.txt")
        self.assertEqual(once, twice)
        self.assertIn("```\na\nb\n```", twice)

    def test_rerun_hoists_markers_that_were_left_inside_a_fence(self):
        # simulate a file produced by the older, non-fence-aware script
        stale = ("intro\n\n```\n"
                 "<!-- BEGIN GENERATED: list.txt -->\n"
                 "<!-- Auto-generated content; do not edit by hand, changes will be overwritten -->\n"
                 "old\n"
                 "<!-- END GENERATED: list.txt -->\n"
                 "```\n\noutro\n")
        out = rp.replace_content(stale, "new\n", "list.txt")
        lines = out.splitlines()
        begin = lines.index("<!-- BEGIN GENERATED: list.txt -->")
        end = lines.index("<!-- END GENERATED: list.txt -->")
        fences = [i for i, l in enumerate(lines) if l.strip() == "```"]
        self.assertTrue(all(begin < f < end for f in fences),
                        f"fences {fences} not inside markers ({begin}, {end}):\n{out}")
        self.assertIn("new", out)
        self.assertNotIn("old", out)


    def test_placeholder_hidden_in_html_comment_is_unwrapped_on_fill(self):
        # An optional fragment: the template hides it in an HTML comment so an
        # unfilled placeholder renders as nothing. On fill, the comment
        # delimiters must go away and the markers must sit on their own lines.
        template = "before\n\n<!-- {{ frag.md }} -->\n\nafter\n"
        out = rp.replace_content(template, "real content\n", "frag.md")
        self.assertIn("\n<!-- BEGIN GENERATED: frag.md -->\n", out)
        self.assertIn("\nreal content\n", out)
        self.assertNotIn("<!-- {{ frag.md }} -->", out)
        self.assertNotIn("-->\n<!-- BEGIN", out)  # no leftover comment close

    def test_commented_placeholder_rerun_is_idempotent(self):
        template = "x\n<!-- {{ frag.md }} -->\ny\n"
        once = rp.replace_content(template, "c\n", "frag.md")
        twice = rp.replace_content(once, "c\n", "frag.md")
        self.assertEqual(once, twice)


if __name__ == "__main__":
    unittest.main()
