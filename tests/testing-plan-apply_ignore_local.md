# Testing plan: tools/apply_ignore_local.sh

Automated: `python3 tests/test_apply_ignore_local.py` (script), `python3 tests/test_01_check_file_sizes.py` (the producer), `python3 tests/test_update_tools.py` (the refresh).

Manual, in a copy of a real `aearep-NNNN` repository that still has an old-style `generated/dot-gitignore`:

1. Run `tools/update_tools.sh` (or the `4-refresh-tools` pipeline). Check that `generated/dot-gitignore` is gone, `generated/dot-ignore-local` lists the former large files, and `.gitignore` ends with `# local additions - auto-generated on <date>` and those files.
2. Run it again: `.gitignore` must not change.
3. Run `1-populate-from-icpsr` on a deposit with a file over the limit: three separate commits (`generated/dot-ignore-local`, `.gitignore`, deposit), and the large file is not committed.
