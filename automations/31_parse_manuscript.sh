#!/bin/bash
# 31_parse_manuscript.sh
# Convert the manuscript PDF(s) attached to the Jira ticket to Markdown, with
# the figures extracted as images, and commit the result as manuscript_parsed/.
#
# The PDFs are downloaded into a scratch directory and are not committed here;
# 30_download_commit_jira_attachments.sh commits them. The conversion itself is
# tools/manuscript_to_markdown.py.
#
# Usage: 31_parse_manuscript.sh
#
# Environment:
#   jiraticket      - Jira ticket (set by `. ./tools/resolve_jiraticket.sh`)
#   JIRA_USERNAME, JIRA_API_KEY - for the attachment download
#   BITBUCKET_BRANCH - branch to push to (default: the current branch)

if [ -z "${jiraticket:-}" ]; then
    echo "31_parse_manuscript: no Jira ticket; source tools/resolve_jiraticket.sh first" >&2
    exit 1
fi

workdir=$(mktemp -d)
trap 'rm -rf "$workdir"' EXIT

python3 tools/jira_download_attachments.py "$jiraticket" --output-dir "$workdir" --filter .pdf || exit 1
python3 tools/manuscript_to_markdown.py --source-dir "$workdir" --output-dir manuscript_parsed || exit 1

if [ ! -d manuscript_parsed ]; then
    echo "31_parse_manuscript: no manuscript found for $jiraticket, nothing to commit"
    exit 0
fi

./automations/20_commit_code.sh manuscript_parsed notag

# The ingest may have pushed in the meantime; manuscript_parsed/ is disjoint from
# everything it touches, so rebase onto the branch and try again.
branch="${BITBUCKET_BRANCH:-$(git rev-parse --abbrev-ref HEAD)}"
for attempt in 1 2 3 4 5; do
    if git pull --rebase origin "$branch" && git push origin "HEAD:$branch"; then
        exit 0
    fi
    echo "Push attempt $attempt failed; retrying"
    sleep $((attempt * 5))
done
echo "31_parse_manuscript: could not push manuscript_parsed to $branch" >&2
exit 1
