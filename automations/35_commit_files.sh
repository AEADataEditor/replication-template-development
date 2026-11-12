#!/bin/bash
# 35_commit_files.sh
# Commit exactly the given files on top of the remote branch and push.
# For steps that add their own files to a repository others push to as well
# (e.g. p-pii-checker). Nothing else in the working tree is committed, and the
# working tree is neither merged nor rebased: the commit is built in a
# separate index from the remote tip, so other changes in the checkout (logs,
# modes, the deposit) cannot block or leak into it. If someone pushes in the
# meantime, the commit is rebuilt on the new tip.
#
# Usage: 35_commit_files.sh "message" file [file ...]
#
# Environment:
#   jiraticket       prefixes the message with "<ticket> #comment [skip ci]"
#   BITBUCKET_BRANCH branch to push to (default: the current branch)

if [ $# -lt 2 ]
then
  echo "Usage: $0 \"message\" file [file ...]"
  exit 2
fi
msg=$1
shift
for f in "$@"
do
  [ -f "$f" ] || { echo "35_commit_files: $f not found"; exit 1; }
done
if [ -n "$jiraticket" ]; then msg="$jiraticket #comment [skip ci] $msg"; else msg="[skip ci] $msg"; fi

branch="${BITBUCKET_BRANCH:-$(git rev-parse --abbrev-ref HEAD)}"
index=$(mktemp)
trap 'rm -f "$index"' EXIT

for attempt in 1 2 3 4 5
do
  git fetch --quiet origin "$branch" || { sleep $((attempt * 5)); continue; }
  base=$(git rev-parse FETCH_HEAD)
  GIT_INDEX_FILE=$index git read-tree "$base"
  GIT_INDEX_FILE=$index git add -f -- "$@"
  tree=$(GIT_INDEX_FILE=$index git write-tree)
  if [ "$tree" = "$(git rev-parse "$base^{tree}")" ]
  then
    echo "35_commit_files: no changes to commit"
    exit 0
  fi
  commit=$(git commit-tree "$tree" -p "$base" -m "$msg")
  if git push origin "$commit:refs/heads/$branch"
  then
    echo "35_commit_files: pushed $(git rev-parse --short "$commit") to $branch:"
    git diff-tree --no-commit-id --name-status -r "$commit"
    exit 0
  fi
  echo "Push attempt $attempt failed; retrying on the new tip"
  sleep $((attempt * 5))
done
echo "35_commit_files: could not push to $branch" >&2
exit 1
