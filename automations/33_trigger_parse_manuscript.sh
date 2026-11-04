#!/bin/bash
# 33_trigger_parse_manuscript.sh
# Start the m-parse-manuscript pipeline for the current Jira ticket, so that the
# manuscript is converted to Markdown while the ingest runs. It never fails: the
# ingest does not depend on the result, and a failed trigger is only reported.
#
# Usage: 33_trigger_parse_manuscript.sh
#
# Environment:
#   jiraticket - Jira ticket (set by `. ./tools/resolve_jiraticket.sh`)
#   BITBUCKET_*, JIRA_USERNAME, P_BITBUCKET_PAT - see tools/bitbucket_trigger_pipeline.py

python3 tools/bitbucket_trigger_pipeline.py m-parse-manuscript --var "jiraticket=${jiraticket:-}" \
    || echo "33_trigger_parse_manuscript: Warning - m-parse-manuscript was not started"
exit 0
