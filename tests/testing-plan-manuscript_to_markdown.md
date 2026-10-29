# Testing plan: manuscript_to_markdown.py and the m-parse-manuscript pipeline

See [manuscript_to_markdown.py docs](../docs/tools/analysis/96-90-manuscript_to_markdown.md), [31_parse_manuscript.sh docs](../docs/automations/96-92-31_parse_manuscript.md), [32_pull_push.sh docs](../docs/automations/96-92-32_pull_push.md), [33_trigger_parse_manuscript.sh docs](../docs/automations/96-92-33_trigger_parse_manuscript.md) and [bitbucket_trigger_pipeline.py docs](../docs/tools/repository/96-90-bitbucket_trigger_pipeline.md) for usage. Automated unit tests (no converter, Jira or Bitbucket access needed; the converters and the API are replaced by fakes, the pushes use local bare repositories):

```bash
python3 tests/test_manuscript_to_markdown.py
python3 tests/test_bitbucket_trigger_pipeline.py
python3 tests/test_32_pull_push.py
```

## Converter, by hand

Needs `pip install -r requirements-manuscript.txt`. Use one proof with the plain name and one with a journal-acronym name.

1. `python3 tools/manuscript_to_markdown.py --source-dir <dir> --list` lists only the manuscript (not forms, not `Data and Code Availability.pdf`).
2. `python3 tools/manuscript_to_markdown.py --source-dir <dir> --output-dir out` gives `out/<stem>/<stem>.md` and the figure images; every `![](...)` in the Markdown names a file in that folder.
3. `--engine markitdown` gives the text only. With `marker_single` off the `PATH`, the default `auto` falls back to markitdown and says so on stderr.
4. CPU-only, to match the Bitbucket workers: `CUDA_VISIBLE_DEVICES="" TORCH_DEVICE=cpu OMP_NUM_THREADS=8 taskset -c 0-7 ...`. With marker 1.10.2 do not run it on all cores of a shared machine; one such run took a node down.

Sample results, 90-page proofs: marker 2.0.0, 8 CPU threads, 30-34 s and 2.3 GB, identical to its GPU output; marker 1.10.2, 16-33 min and 12.5 GB.

## Pipeline, on a scratch repository

1. Create a scratch `aearep-NNNN` repository with `aeagit-create`, populated from the branch under test (`DEBUG_REPO=<git URL>#<branch>`), and enable Pipelines on it. Use the test ticket (AEAREP-10400) with a manuscript PDF attached.
2. Run `m-parse-manuscript` from the Bitbucket UI on the ingest branch, with the `jiraticket` variable set.
3. Check: the Jira ticket gets "started" and "completed" comments; the branch has one new commit adding only `manuscript_parsed/`; no `update<N>` tag was added; the PDFs were not committed by this pipeline.
4. Ticket without a manuscript attachment: the pipeline completes, nothing is committed.
5. Run `1-populate-from-icpsr` (and `w-big-populate-from-icpsr`) on the scratch repository: right after its "started" comment a second pipeline, `m-parse-manuscript`, starts by itself and receives the ticket.
6. When both have finished, the branch holds the ingest's commits and tags (`update<N>` still on the ingest's commits) and `manuscript_parsed/`, whichever pushed first.
7. Without `P_BITBUCKET_PAT`, the trigger prints a warning and the ingest carries on.
8. The first conversion downloads the models; the log of the second run should show the `marker-models` cache restored with more than a few KiB, and the run should be shorter. A second run on an unchanged manuscript reports "No changes detected" and adds no commit.
