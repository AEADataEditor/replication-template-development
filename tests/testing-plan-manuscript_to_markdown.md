# Testing plan: manuscript_to_markdown.py and the m-parse-manuscript pipeline

See [manuscript_to_markdown.py docs](../docs/tools/analysis/96-90-manuscript_to_markdown.md) and [31_parse_manuscript.sh docs](../docs/automations/96-92-31_parse_manuscript.md) for usage. Automated unit tests (no converter or Jira access needed; the converters are replaced by fakes):

```bash
python3 tests/test_manuscript_to_markdown.py
python3 tests/test_big_ingest.py     # pipeline-variables --only
```

## Converter, by hand

Needs `pip install -r requirements-manuscript.txt`. Use one proof with the plain name and one with a journal-acronym name.

1. `python3 tools/manuscript_to_markdown.py --source-dir <dir> --list` lists only the manuscript (not forms, not `Data and Code Availability.pdf`).
2. `python3 tools/manuscript_to_markdown.py --source-dir <dir> --output-dir out` gives `out/<stem>/<stem>.md` and the figure images; every `![](...)` in the Markdown names a file in that folder.
3. `--engine markitdown` gives the text only. With `marker_single` off the `PATH`, the default `auto` falls back to markitdown and says so on stderr.
4. CPU-only, to match the Bitbucket workers: `CUDA_VISIBLE_DEVICES="" TORCH_DEVICE=cpu OMP_NUM_THREADS=8 taskset -c 0-7 ...`. Do not run it on all cores of a shared machine; one such run took a node down.

Sample results (marker 1.10.2, 8 CPU threads): 90 pages in 16-33 min, 12.5 GB peak memory.

## Pipeline, on a scratch repository

1. Create a scratch `aearep-NNNN` repository with `aeagit-create` and set `jiraticket` in `config.yml` to the test ticket (AEAREP-10400), with a manuscript PDF attached to it.
2. Run `m-parse-manuscript` from the Bitbucket UI on the ingest branch, with the `jiraticket` variable set.
3. Check: the Jira ticket gets "started" and "completed" comments; the branch has one new commit adding only `manuscript_parsed/`; no `update<N>` tag was added; the PDFs were not committed by this pipeline.
4. Push to the branch while the pipeline runs: the retry in `31_parse_manuscript.sh` rebases and pushes anyway.
5. Ticket without a manuscript attachment: the pipeline completes, nothing is committed.
6. Run `1-populate-from-icpsr` (and `w-big-populate-from-icpsr`) on the scratch repository: after the final push a second pipeline, `m-parse-manuscript`, starts by itself and receives the ticket.
7. The first run downloads the models (about 1.5 GB); the second run should find them in the `marker-models` cache.
