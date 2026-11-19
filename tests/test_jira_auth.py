#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2026 Lars Vilhuber and contributors.
# Author(s): Lars Vilhuber
# Licensed under the BSD 3-Clause License; see the LICENSE file at the repository root.

"""Tests for jira_auth.py and the Jira tools that connect through it.
Run: python3 tests/test_jira_auth.py"""
import contextlib
import importlib
import io
import os
import subprocess
import sys
import unittest
from unittest.mock import MagicMock, patch

TOOLS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools")
sys.path.insert(0, TOOLS)
import jira_auth as A
from jira.exceptions import JIRAError


class FakeClient:
    def __init__(self, result=None, error=None):
        self.result, self.error = result, error

    def myself(self):
        if self.error:
            raise self.error
        return self.result


class TestVerifyAuth(unittest.TestCase):
    def test_accepted_credentials_return_the_user_record(self):
        user = {"displayName": "Someone"}
        self.assertEqual(A.verify_auth(FakeClient(result=user)), user)

    def test_rejected_credentials_raise_an_auth_error(self):
        for status in A.REJECTED:
            with self.subTest(status=status):
                with self.assertRaisesRegex(A.JiraAuthError, "HTTP {0}".format(status)):
                    A.verify_auth(FakeClient(error=JIRAError(status_code=status)))

    def test_other_errors_pass_through_unchanged(self):
        error = JIRAError(status_code=503)
        with self.assertRaises(JIRAError) as caught:
            A.verify_auth(FakeClient(error=error))
        self.assertIs(caught.exception, error)

    def test_errors_without_a_status_pass_through(self):
        with self.assertRaises(OSError):
            A.verify_auth(FakeClient(error=OSError("network down")))

    def test_rejection_names_the_token_page(self):
        with self.assertRaisesRegex(A.JiraAuthError, A.TOKEN_URL):
            A.verify_auth(FakeClient(error=JIRAError(status_code=401)))


class TestUrls(unittest.TestCase):
    def test_gateway_url_carries_the_cloud_id(self):
        self.assertEqual(
            A.GATEWAY_URL, "https://api.atlassian.com/ex/jira/" + A.CLOUD_ID)

    def test_site_url_is_the_browse_host(self):
        self.assertEqual(A.SITE_URL, "https://aeadataeditors.atlassian.net")


class TestConnect(unittest.TestCase):
    def test_connects_through_the_gateway_and_verifies(self):
        with patch("jira.JIRA") as JIRA:
            JIRA.return_value.myself.return_value = {"accountId": "x"}
            jira, user = A.connect("me@example.com", "token")
        JIRA.assert_called_once_with(
            server=A.GATEWAY_URL, basic_auth=("me@example.com", "token"),
            options={"verify": True})
        self.assertIs(jira, JIRA.return_value)
        self.assertEqual(user, {"accountId": "x"})

    def test_rejected_credentials_raise(self):
        with patch("jira.JIRA") as JIRA:
            JIRA.return_value.myself.side_effect = JIRAError(status_code=401)
            with self.assertRaises(A.JiraAuthError):
                A.connect("me@example.com", "bad")


class TestStdlibOnly(unittest.TestCase):
    def test_importable_without_the_jira_package(self):
        # A None entry in sys.modules makes `import jira` fail.
        code = ("import sys; sys.modules['jira'] = None; sys.path.insert(0, {0!r}); "
                "import jira_auth, jira_add_comment; "
                "print(jira_add_comment._JIRA_LIB)").format(TOOLS)
        result = subprocess.run([sys.executable, "-c", code],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "False")


# Every tool built on the `jira` package, with whether it reports a rejected
# token on stderr. jira_find_task_by_icpsr.py stays silent: callers capture its
# stderr together with stdout as the issue key.
LIBRARY_TOOLS = {
    "jira_get_info": True,
    "jira_download_attachments": True,
    "jira_sync_fields": True,
    "jira_find_task_by_icpsr": False,
    "jira_update_software": True,
    "jira_update_deposit_size": True,
    "jira_software_field_report": True,
    "jira_migrate_software_field": True,
}


class TestToolsUseTheGateway(unittest.TestCase):
    def setUp(self):
        env = patch.dict(os.environ, {"JIRA_USERNAME": "me@example.com",
                                      "JIRA_API_KEY": "token"})
        env.start()
        self.addCleanup(env.stop)

    def _client(self, name, myself_error=None):
        module = importlib.import_module(name)
        stderr = io.StringIO()
        with patch("jira.JIRA") as JIRA, contextlib.redirect_stderr(stderr):
            if myself_error:
                JIRA.return_value.myself.side_effect = myself_error
            client = module.get_jira_client()
        return JIRA, client, stderr.getvalue()

    def test_every_tool_connects_through_the_gateway(self):
        for name in LIBRARY_TOOLS:
            with self.subTest(tool=name):
                JIRA, client, _ = self._client(name)
                self.assertIs(client, JIRA.return_value)
                self.assertEqual(JIRA.call_args.kwargs["server"], A.GATEWAY_URL)

    def test_rejected_token_yields_no_client(self):
        for name, reports in LIBRARY_TOOLS.items():
            with self.subTest(tool=name):
                _, client, stderr = self._client(name, JIRAError(status_code=401))
                self.assertIsNone(client)
                if reports:
                    self.assertIn("rejected JIRA_USERNAME/JIRA_API_KEY", stderr)
                else:
                    self.assertEqual(stderr, "")

    def test_no_tool_hard_codes_the_site_url(self):
        for name in list(LIBRARY_TOOLS) + ["jira_add_comment"]:
            with self.subTest(tool=name):
                with open(os.path.join(TOOLS, name + ".py")) as handle:
                    self.assertNotIn("aeadataeditors.atlassian.net", handle.read())


if __name__ == "__main__":
    unittest.main()
