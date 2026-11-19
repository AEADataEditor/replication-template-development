# Documentation deployment & PR previews

The MyST documentation in `docs/` is built by
[.github/workflows/docs-deploy.yml](../.github/workflows/docs-deploy.yml),
which mirrors the setup of the AEA Data Editor website
(`AEADataEditor/aeadataeditor.github.io`, `.github/workflows/main.yml` and
`README-DEPLOYMENT.md` there). It has three jobs:

- **build** - always runs. Builds the site and uploads it as a workflow
  artifact named `docs-html` (downloadable from the run page for 14 days).
- **deploy** - runs on pushes to `master` and on manual runs. In practice
  this happens in the deployed `AEADataEditor/replication-template` repo,
  whose GitHub Pages site (`/replication-template`) is the live
  documentation.
- **preview** - runs on pull requests opened from a branch of the same
  repository (not a fork). Deploys the site to the Cloudflare Pages project
  `replication-template-docs` under the alias `pr-<number>`
  (`https://pr-<number>.replication-template-docs.pages.dev`), and posts or
  updates a PR comment with the link. Forked PRs never get a preview: forks
  cannot read secrets.

## Credentials (shared with the website)

The preview job uses the same two secrets as the website:
`CLOUDFLARE_API_TOKEN` and `CLOUDFLARE_ACCOUNT_ID`. If neither is visible to
the repository, the job logs a notice and skips the deploy instead of
failing.

Keep them as **organization** secrets, scoped to the repositories that
deploy previews, rather than as copies on each repository. GitHub never
reveals a secret's value, so they are set from 1Password, where both live in
the `cloudflare.com` login entry for `lars.vilhuber@cornell.edu` (fields
`API token: aea-previews` and `Account ID`). The values are piped through
stdin, so they never appear in shell history, the process list, or on screen:

```bash
# Locate the cloudflare.com login for this username (for Login items,
# `op item list` reports the username as additional_information).
ITEM=$(op item list --categories Login --format json \
  | jq -r '.[] | select((.title == "cloudflare.com" or any(.urls[]?; .href | test("cloudflare\\.com")))
                        and .additional_information == "lars.vilhuber@cornell.edu") | .id')
[ "$(printf '%s\n' "$ITEM" | grep -c .)" -eq 1 ] || { echo "Expected exactly 1 item, got: $ITEM" >&2; return 1 2>/dev/null || exit 1; }

REPOS=aeadataeditor.github.io,replication-template-development,editor-scripts

op item get "$ITEM" --fields 'label=API token: aea-previews' --reveal | tr -d '\n' \
  | gh secret set CLOUDFLARE_API_TOKEN  --org AEADataEditor --visibility selected --repos "$REPOS"

op item get "$ITEM" --fields 'label=Account ID' --reveal | tr -d '\n' \
  | gh secret set CLOUDFLARE_ACCOUNT_ID --org AEADataEditor --visibility selected --repos "$REPOS"

# Check
gh api repos/AEADataEditor/replication-template-development/actions/organization-secrets --jq '.secrets[].name' | grep CLOUDFLARE
```

Notes: `--reveal` is required by `op` 2.25+ for concealed fields (drop it on
older versions); `tr -d '\n'` keeps `op`'s trailing newline out of the
secret; setting organization secrets needs org admin and the `admin:org`
scope on `gh` (`gh auth refresh -s admin:org`). If several `cloudflare.com`
logins match, pick the ID from `op item list --categories Login | grep -i cloudflare`.
To add another repository later, rerun the `gh secret set` lines with it
added to `REPOS` (the `--repos` list replaces the previous selection).

Once the organization secrets exist, the repository-level copies on
`aeadataeditor.github.io` can be deleted (a repository secret takes
precedence over an organization secret of the same name):

```bash
gh secret delete CLOUDFLARE_API_TOKEN  -R AEADataEditor/aeadataeditor.github.io
gh secret delete CLOUDFLARE_ACCOUNT_ID -R AEADataEditor/aeadataeditor.github.io
```

The token needs `Account > Cloudflare Pages: Edit` on the account (the
"Edit Cloudflare Workers" template includes it). The Cloudflare Pages
project is created by the workflow on first use; to rename it, change
`CF_PAGES_PROJECT` in the workflow.
