# Testing plan: jira_auth.py (Atlassian API gateway)

Automated unit tests (no Jira access needed):

```bash
python3 tests/test_jira_auth.py
python3 tests/test_jira_add_comment.py
```

The manual checks below need real credentials. Run each one twice: once with an
unscoped (classic) API token and once with a scoped token in `JIRA_API_KEY`.
`TICKET` is a test issue that has at least one attachment.

## Read

```bash
python3 tools/jira_get_info.py TICKET doi            # prints the DOI
python3 tools/jira_find_task_by_icpsr.py ICPSR_ID    # prints an issue key
python3 tools/jira_download_attachments.py TICKET --list
```

## Attachments

Attachment `content` URLs come from the API response. They must be on
`https://api.atlassian.com/ex/jira/<cloudId>/...` and download with either token:

```bash
python3 tools/jira_download_attachments.py TICKET --output-dir /tmp/att --verbose
```

## Write (follows the issue's `self` link)

```bash
python3 tools/jira_add_comment.py TICKET "gateway test"
python3 tools/jira_add_comment.py --partb TICKET "gateway test (Part B)"
JIRA_API_KEY=wrong python3 tools/jira_add_comment.py TICKET "x"
#   -> "Warning: Jira rejected JIRA_USERNAME/JIRA_API_KEY (HTTP 401) ..."
```

Repeat the comment test without the `jira` package (stdlib REST client), e.g. in
a bare `python3 -m venv` environment.

`jira_update_software.py` and `jira_update_deposit_size.py` call `issue.update()`,
which the `jira` library sends to the issue's `self` URL; through the gateway that
URL is on the gateway host, so the path keeps `/ex/jira/<cloudId>`. Confirm by
running `jira_update_software.py TICKET METADATA --yes` on the test issue and
checking that the field changed.

## Pipelines

One run each of `70_publish_comment.sh`, `26_update_jira_software.sh`, and
`60_process_restricted_box.sh`, with a scoped token in the Bitbucket
`JIRA_API_KEY` variable.

## Scopes

Record which scopes the scoped token needed (expected: `read:jira-work` and
`write:jira-work`, or granular `read:attachment:jira` for attachments) so the
editor-scripts Authentication page can list them.
