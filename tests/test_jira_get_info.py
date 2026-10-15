#!/usr/bin/env python3
"""Tests for jira_get_info.py. Run: python3 tests/test_jira_get_info.py"""
import os
import sys
import unittest
from unittest.mock import MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools"))
import jira_get_info as jgi


class TestGetBoxFolderId(unittest.TestCase):
    FIELD_MAP = {"Restricted data Box Folder ID": "customfield_99999"}

    def _issue(self, value):
        issue = MagicMock()
        setattr(issue.fields, "customfield_99999", value)
        return issue

    def test_returns_stripped_value_when_present(self):
        issue = self._issue("  123456  ")
        self.assertEqual(jgi.get_box_folder_id(issue, self.FIELD_MAP), "123456")

    def test_returns_empty_string_when_none(self):
        issue = self._issue(None)
        self.assertEqual(jgi.get_box_folder_id(issue, self.FIELD_MAP), "")

    def test_returns_empty_string_when_blank(self):
        issue = self._issue("   ")
        self.assertEqual(jgi.get_box_folder_id(issue, self.FIELD_MAP), "")

    def test_returns_empty_string_when_field_unmapped(self):
        issue = self._issue("123456")
        self.assertEqual(jgi.get_box_folder_id(issue, {}), "")


class TestGetReasonForFailure(unittest.TestCase):
    FIELD_MAP = {"Reason for Failure to be Fully Reproduced": "customfield_88888"}

    def _option(self, value):
        opt = MagicMock()
        opt.value = value
        return opt

    def _issue(self, value):
        issue = MagicMock()
        setattr(issue.fields, "customfield_88888", value)
        return issue

    def test_returns_single_checked_option(self):
        issue = self._issue([self._option("Data not available")])
        self.assertEqual(
            jgi.get_reason_for_failure(issue, self.FIELD_MAP), "Data not available"
        )

    def test_returns_multiple_checked_options_newline_joined(self):
        issue = self._issue([self._option("Bugs in code"), self._option("Code missing")])
        self.assertEqual(
            jgi.get_reason_for_failure(issue, self.FIELD_MAP),
            "Bugs in code\nCode missing",
        )

    def test_returns_empty_string_when_none_checked(self):
        issue = self._issue([])
        self.assertEqual(jgi.get_reason_for_failure(issue, self.FIELD_MAP), "")

    def test_returns_empty_string_when_field_unmapped(self):
        issue = self._issue([self._option("Data missing")])
        self.assertEqual(jgi.get_reason_for_failure(issue, {}), "")


class TestKeywordRouting(unittest.TestCase):
    def test_boxfolderid_keyword_is_routed(self):
        field_map = TestGetBoxFolderId.FIELD_MAP
        issue = MagicMock()
        setattr(issue.fields, "customfield_99999", "654321")

        jira = MagicMock()
        jira.issue.return_value = issue
        jira.fields.return_value = [
            {"name": "Restricted data Box Folder ID", "id": "customfield_99999"}
        ]

        with unittest.mock.patch.object(jgi, "get_jira_client", return_value=jira):
            result = jgi.get_info_from_jira("AEAREP-1", "boxfolderid")

        self.assertEqual(result, "654321")


class TestGetMcstatus(unittest.TestCase):
    FIELD_MAP = {"MCStatus": "customfield_77777"}

    def _issue(self, value):
        issue = MagicMock()
        setattr(issue.fields, "customfield_77777", value)
        return issue

    def test_returns_plain_string_value(self):
        self.assertEqual(jgi.get_mcstatus(self._issue(" RR "), self.FIELD_MAP), "RR")

    def test_returns_option_value(self):
        option = MagicMock()
        option.value = "Accept"
        self.assertEqual(jgi.get_mcstatus(self._issue(option), self.FIELD_MAP), "Accept")

    def test_returns_empty_string_when_none(self):
        self.assertEqual(jgi.get_mcstatus(self._issue(None), self.FIELD_MAP), "")

    def test_returns_empty_string_when_field_unmapped(self):
        self.assertEqual(jgi.get_mcstatus(self._issue("RR"), {}), "")


class TestResolveLatestCase(unittest.TestCase):
    def test_explicit_key_is_kept(self):
        self.assertEqual(jgi.resolve_latest_case("aearep-12"), "aearep-12")

    def test_auto_uses_configured_ticket(self):
        with unittest.mock.patch.object(jgi, "resolve_configured_key", return_value="AEAREP-99"):
            self.assertEqual(jgi.resolve_latest_case("auto"), "AEAREP-99")

    def test_auto_falls_back_to_repository_number(self):
        with unittest.mock.patch.object(jgi, "resolve_configured_key", return_value=""), \
                unittest.mock.patch.object(jgi, "repository_name", return_value="aearep-1234"):
            self.assertEqual(jgi.resolve_latest_case("auto"), "AEAREP-1234")

    def test_auto_is_empty_when_nothing_resolves(self):
        with unittest.mock.patch.object(jgi, "resolve_configured_key", return_value=""), \
                unittest.mock.patch.object(jgi, "repository_name", return_value="some-other-repo"):
            self.assertEqual(jgi.resolve_latest_case("auto"), "")

    def test_mcstatus_keyword_routed_with_auto(self):
        issue = MagicMock()
        setattr(issue.fields, "customfield_77777", "RR")
        jira = MagicMock()
        jira.issue.return_value = issue
        jira.fields.return_value = [{"name": "MCStatus", "id": "customfield_77777"}]

        with unittest.mock.patch.object(jgi, "get_jira_client", return_value=jira), \
                unittest.mock.patch.object(jgi, "resolve_configured_key", return_value="aearep-5"):
            result = jgi.get_info_from_jira("auto", "mcstatus")

        jira.issue.assert_called_once_with("AEAREP-5")
        self.assertEqual(result, "RR")


if __name__ == "__main__":
    unittest.main()
