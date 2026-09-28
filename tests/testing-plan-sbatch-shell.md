# Testing plan: sbatch-shell.sh

Manual QA plan for `tools/sbatch-shell.sh` (see [sbatch-shell.sh docs](../docs/tools/repository/96-90-sbatch-shell.md) for usage). This must be run **on the cluster**, since SLURM does not exist elsewhere. Prepare two throwaway Jira tickets first:

- **Ticket A** (`TICKET-A` below) - a Task with a Part B sub-task (`PARTB-SUBTASK-OF-A`). Give the sub-task a summary that does **not** contain "Part B" (e.g. "Test for notifications") - that forces the tool to match on the sub-task's **issue type**, which is the intended path, rather than on the summary fallback.
- **Ticket B** (`TICKET-B` below) - a Task with **no** sub-tasks, to exercise the no-Part-B fallback.

Post test comments **only** to these two throwaway tickets, and delete them (or their comments) once testing is done.

## 1. Environment (no Jira writes)

```bash
python3 --version                                     # the native interpreter the template uses
python3 -c "import jira" ; echo "jira lib: $?"        # either result is fine
```

`sbatch-shell.sh` no longer loads any Python module (see [Python on the compute node](../docs/tools/repository/96-90-sbatch-shell.md#python-on-the-compute-node)); this just confirms the native interpreter is >= 3.6.

## 2. Credentials

```bash
grep JIRA_API_KEY ~/.envvars               # expect at least one line; create the file if missing
env -u JIRA_API_KEY python3 tools/jira_add_comment.py --dry-run TICKET-A "x"
```

Do not count lines: a file that both assigns and later `export`s the variable matches twice, which is fine. The second command must still print a "Would post to ..." line - proving the file lookup works without the variable being exported.

## 3. Part B resolution (`--dry-run`, still no Jira writes)

```bash
python3 tools/jira_add_comment.py --partb --dry-run TICKET-A "test"
python3 tools/jira_add_comment.py --partb --dry-run TICKET-B "test"
python3 tools/jira_add_comment.py --partb --dry-run PARTB-SUBTASK-OF-A "test"
```

Expect, in order:

- `Would post to PARTB-SUBTASK-OF-A` - resolved from the parent by issue type
- a `no Part B sub-task found for TICKET-B` warning, then `Would post to TICKET-B` - the fallback
- `Would post to PARTB-SUBTASK-OF-A` - handed the sub-task itself, used as-is

## 4. Real comments, outside SLURM

```bash
python3 tools/jira_add_comment.py --partb --status started --label "smoke test" TICKET-A
python3 tools/jira_add_comment.py --partb --status completed --exit-code 0 --label "smoke test" TICKET-A
python3 tools/jira_add_comment.py --partb --status completed --exit-code 3 --label "smoke test" TICKET-A
```

Each should print `Jira comment posted to PARTB-SUBTASK-OF-A`. Check on PARTB-SUBTASK-OF-A that three comments appeared: 🚀 smoke test started, ✅ smoke test completed, ❌ smoke test failed (exit code 3). No SLURM job ID/directory suffix, since these did not run in a job.

## 5. A real SLURM job - success

Copy the template, set `--time=00:02:00`, replace the payload with `sleep 30`, comment out the Stata/R lines, and set `JIRATICKET=TICKET-A`. Then `sbatch` it. Expect two comments on PARTB-SUBTASK-OF-A, both reading e.g. `SLURM job <jobid> RunStata started (directory: ...)`, and the second one ✅. Cross-check the job ID against `scontrol show job <jobid>`. Prefer `scontrol` over `sacct` for this: on BioHPC/ECCO `sacct` has been observed returning stale, unrelated records for current job IDs (an accounting-database artifact), while `scontrol` was correct throughout.

## 6. A real SLURM job - failure

Same, with the payload replaced by `exit 7`. Expect ❌ **failed (exit code 7)**, and `scontrol show job <jobid>` to report `ExitCode=7:0`.

## 7. A real SLURM job - wall clock kill

Same, with `--time=00:01:00` and a payload of `sleep 600`. Expect ❌ **failed (exit code 143)** shortly after SLURM sends SIGTERM. (If SLURM's `KillWait` is too short for the payload to die first, the stop comment may be lost to SIGKILL - note it rather than treating it as a bug in the script.)

## 8. Auto ticket resolution

Repeat step 5 with `JIRATICKET=auto` and no `jiraticket` in the environment, submitted from a directory whose `config.yml` has `jiraticket: TICKET-A`. Expect the same two comments on PARTB-SUBTASK-OF-A.

## 9. Fallback in a real job

Repeat step 5 with `JIRATICKET=TICKET-B`. Expect both comments on TICKET-B itself, each preceded by a `no Part B sub-task found` warning in the SLURM log, and the job unaffected.

## 10. Degradation

Unsetting the two variables is **not** enough if your own `~/.envvars` holds valid credentials - the documented file fallback will find them and the job will post normally. Point `HOME` at an empty directory as well, so that no credential file is reachable:

```bash
mkdir -p /tmp/no-creds
env -u JIRA_USERNAME -u JIRA_API_KEY HOME=/tmp/no-creds bash run-replication.sh   # outside SLURM
```

Expect the payload to run, a `Jira credentials not available` warning on both the start and the stop call, and the script's exit code unchanged.

## Unit tests (anywhere, no cluster needed)

```bash
python3 tests/test_jira_add_comment.py
```
