# Testing plan: jira_add_comment.py

See [jira_add_comment.py docs](../docs/tools/jira/96-90-jira_add_comment.md) for usage. Automated unit tests (no Jira access needed):

```bash
python3 tests/test_jira_add_comment.py
```

For manual end-to-end testing of `--partb` resolution, SLURM notifications, and credential fallback against real Jira tickets, see [testing-plan-sbatch-shell.md](testing-plan-sbatch-shell.md), which exercises `jira_add_comment.py` through `sbatch-shell.sh`.
