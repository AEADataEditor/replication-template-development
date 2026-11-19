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
reveals a secret's value, so they must be set from the original values (or a
freshly rolled Cloudflare token):

```bash
gh secret set CLOUDFLARE_API_TOKEN  --org AEADataEditor --visibility selected \
  --repos aeadataeditor.github.io,replication-template-development
gh secret set CLOUDFLARE_ACCOUNT_ID --org AEADataEditor --visibility selected \
  --repos aeadataeditor.github.io,replication-template-development
gh api repos/AEADataEditor/replication-template-development/actions/organization-secrets --jq '.secrets[].name'
```

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
