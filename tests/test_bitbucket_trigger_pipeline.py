#!/usr/bin/env python3
"""Tests for bitbucket_trigger_pipeline.py. Run: python3 tests/test_bitbucket_trigger_pipeline.py"""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools"))
import bitbucket_trigger_pipeline as btp

ENV = {
    "BITBUCKET_WORKSPACE": "ws", "BITBUCKET_REPO_SLUG": "aearep-1", "BITBUCKET_BRANCH": "master",
    "JIRA_USERNAME": "me@example.org", "P_BITBUCKET_PAT": "secret",
}


class FakeResponse:
    def __init__(self, status, body=None):
        self.status_code, self._body, self.text = status, body or {}, str(body)

    def json(self):
        return self._body


class TestBuildRequest(unittest.TestCase):
    def test_payload(self):
        url, payload = btp.build_request("m-parse", {"jiraticket": "AEAREP-1"}, ENV)
        self.assertEqual(url, "https://api.bitbucket.org/2.0/repositories/ws/aearep-1/pipelines/")
        self.assertEqual(payload["target"]["ref_name"], "master")
        self.assertEqual(payload["target"]["selector"], {"type": "custom", "pattern": "m-parse"})
        self.assertEqual(payload["variables"], [{"key": "jiraticket", "value": "AEAREP-1"}])

    def test_empty_variables_are_not_sent(self):
        _, payload = btp.build_request("m-parse", {"jiraticket": ""}, ENV)
        self.assertNotIn("variables", payload)

    def test_outside_bitbucket(self):
        with self.assertRaises(ValueError):
            btp.build_request("m-parse", {}, {})


class TestParseVars(unittest.TestCase):
    def test_pairs(self):
        self.assertEqual(btp.parse_vars(["a=1", "b=x=y", "c="]), {"a": "1", "b": "x=y", "c": ""})

    def test_bad(self):
        with self.assertRaises(ValueError):
            btp.parse_vars(["novalue"])


class TestTrigger(unittest.TestCase):
    def test_success(self):
        seen = {}

        def post(url, json, auth, timeout):
            seen.update(url=url, json=json, auth=auth)
            return FakeResponse(201, {"build_number": 7})

        link = btp.trigger("m-parse", {"jiraticket": "AEAREP-1"}, ENV, post=post)
        self.assertEqual(link, "https://bitbucket.org/ws/aearep-1/pipelines/results/7")
        self.assertEqual(seen["auth"], ("me@example.org", "secret"))

    def test_http_error(self):
        with self.assertRaises(RuntimeError):
            btp.trigger("m-parse", {}, ENV, post=lambda *a, **k: FakeResponse(403, {"error": "no"}))

    def test_missing_credentials(self):
        env = {k: v for k, v in ENV.items() if k != "P_BITBUCKET_PAT"}
        with self.assertRaises(RuntimeError):
            btp.trigger("m-parse", {}, env, post=lambda *a, **k: FakeResponse(201))


if __name__ == "__main__":
    unittest.main()
