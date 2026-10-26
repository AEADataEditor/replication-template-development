#!/usr/bin/env python3
"""
Helpers for handing a deposit that is too big for the regular ingest pipeline
over to the "big" ingest pipeline.

Usage:
    big_ingest.py record-size <project-dir> [--cache-dir cache] [--out generated/deposit-size.json]
    big_ingest.py needs-4x [--size-file generated/deposit-size.json]
                           [--threshold-mb N] [--overhead-pct N]
    big_ingest.py set-vm-size <pipelines-yml> <pipeline-name> <size>
    big_ingest.py pipeline-variables [--config config.yml]
    big_ingest.py -h|--help

Subcommands:
    record-size          Write the ZIP size and the unzipped size of the deposit
                         to a JSON file in generated/ (so later steps and the
                         final commit can reuse it). The ZIP is looked for as
                         <project-dir>.zip, then <cache-dir>/<project-dir>.zip.
                         Without a ZIP, only the unzipped size is recorded.
                         Without an unpacked directory, the unzipped size is
                         read from the ZIP's central directory.
    needs-4x             Exit 0 if (zip + unzipped) * (1 + overhead) exceeds the
                         threshold, 1 if not. A missing or unreadable size file
                         counts as "exceeds" (the ZIP did not even fit into the
                         cache). Defaults come from config.yml keys
                         bigingest_threshold_mb and bigingest_overhead_pct.
    set-vm-size          Set `size:` of the first step of the given custom
                         pipeline in bitbucket-pipelines.yml, in place, leaving
                         the rest of the file byte-identical. Exit 0 if changed,
                         1 if it already had that size.
    pipeline-variables   Print the PIPELINE_VARIABLES JSON for
                         atlassian/trigger-pipeline, from config.yml and the
                         environment (jiraticket, openICPSRID, ZenodoID, ...).
"""

import argparse
import json
import os
import re
import sys
import zipfile

BYTES_PER_MB = 1024 * 1024
DEFAULT_SIZE_FILE = os.path.join("generated", "deposit-size.json")

# pipeline variable -> (environment variable, config.yml key)
PIPELINE_VARIABLES = (
    ("jiraticket", "jiraticket", "jiraticket"),
    ("openICPSRID", "openICPSRID", "openicpsr"),
    ("ZenodoID", "ZenodoID", "zenodo"),
    ("WorldBankID", "WorldBankID", "worldbank"),
    ("DataverseID", "DataverseID", "dataverse"),
)


def read_config(path):
    """Top-level `key: value` pairs of config.yml (keys lower-cased)."""
    values = {}
    if not os.path.isfile(path):
        return values
    with open(path) as fh:
        for line in fh:
            m = re.match(r"^([A-Za-z_][\w]*):[ \t]*(.*?)[ \t]*$", line)
            if m and not m.group(2).startswith("#"):
                values[m.group(1).lower()] = m.group(2).strip("\"'")
    return values


def on_disk_size(directory):
    total = 0
    for root, _dirs, files in os.walk(directory):
        for name in files:
            path = os.path.join(root, name)
            if not os.path.islink(path):
                total += os.path.getsize(path)
    return total


def zip_uncompressed_size(zip_path):
    with zipfile.ZipFile(zip_path) as zf:
        return sum(info.file_size for info in zf.infolist())


def record_size(project_dir, cache_dir, out):
    name = os.path.basename(os.path.normpath(project_dir))
    zip_path = next((p for p in (f"{name}.zip", os.path.join(cache_dir, f"{name}.zip"))
                     if os.path.isfile(p)), None)
    zip_bytes = os.path.getsize(zip_path) if zip_path else 0
    if os.path.isdir(project_dir):
        unzipped_bytes = on_disk_size(project_dir)
    elif zip_path:
        unzipped_bytes = zip_uncompressed_size(zip_path)
    else:
        raise SystemExit(f"Neither {project_dir}/ nor {name}.zip found")
    data = {"project": name, "zip_bytes": zip_bytes, "unzipped_bytes": unzipped_bytes}
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    with open(out, "w") as fh:
        json.dump(data, fh, indent=2)
        fh.write("\n")
    return data


def exceeds(size_file, threshold_mb, overhead_pct):
    """True if the recorded size (plus overhead) is above the threshold."""
    try:
        with open(size_file) as fh:
            data = json.load(fh)
        needed = (data["zip_bytes"] + data["unzipped_bytes"]) * (1 + overhead_pct / 100)
    except (OSError, ValueError, KeyError):
        return True
    return needed > threshold_mb * BYTES_PER_MB


def set_vm_size(yml_path, pipeline, size):
    """Edit `size:` in the first step of custom pipeline `pipeline`. True if changed."""
    with open(yml_path) as fh:
        lines = fh.read().splitlines(keepends=True)
    start = next((i for i, l in enumerate(lines)
                  if re.match(rf"^\s+{re.escape(pipeline)}:\s*(#.*)?$", l)), None)
    if start is None:
        raise SystemExit(f"Pipeline {pipeline} not found in {yml_path}")
    indent = len(lines[start]) - len(lines[start].lstrip())
    for i in range(start + 1, len(lines)):
        line = lines[i]
        if line.strip() and not line.lstrip().startswith("#") and \
                len(line) - len(line.lstrip()) <= indent:
            break  # next pipeline
        m = re.match(r"^(\s+size:\s*)(\S+)(.*)$", line, re.S)
        if m:
            if m.group(2) == size:
                return False
            lines[i] = f"{m.group(1)}{size}{m.group(3)}"
            with open(yml_path, "w") as fh:
                fh.writelines(lines)
            return True
    raise SystemExit(f"No `size:` found in pipeline {pipeline}")


def pipeline_variables(config_path, environ):
    config = read_config(config_path)
    out = []
    for var, env_key, cfg_key in PIPELINE_VARIABLES:
        value = environ.get(env_key) or config.get(cfg_key)
        if value:
            out.append({"key": var, "value": value})
    return out


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("record-size")
    s.add_argument("project_dir")
    s.add_argument("--cache-dir", default="cache")
    s.add_argument("--out", default=DEFAULT_SIZE_FILE)

    s = sub.add_parser("needs-4x")
    s.add_argument("--size-file", default=DEFAULT_SIZE_FILE)
    s.add_argument("--config", default="config.yml")
    s.add_argument("--threshold-mb", type=float)
    s.add_argument("--overhead-pct", type=float)

    s = sub.add_parser("set-vm-size")
    s.add_argument("pipelines_yml")
    s.add_argument("pipeline")
    s.add_argument("size")

    s = sub.add_parser("pipeline-variables")
    s.add_argument("--config", default="config.yml")

    args = p.parse_args(argv)

    if args.cmd == "record-size":
        data = record_size(args.project_dir, args.cache_dir, args.out)
        print(f"Recorded in {args.out}: zip {data['zip_bytes'] / BYTES_PER_MB:.0f} MB, "
              f"unzipped {data['unzipped_bytes'] / BYTES_PER_MB:.0f} MB")
        return 0
    if args.cmd == "needs-4x":
        config = read_config(args.config)
        threshold = args.threshold_mb if args.threshold_mb is not None else config.get("bigingest_threshold_mb")
        overhead = args.overhead_pct if args.overhead_pct is not None else config.get("bigingest_overhead_pct")
        if threshold is None or overhead is None:
            print("bigingest_threshold_mb and bigingest_overhead_pct must be set in config.yml "
                  "(or passed as options)", file=sys.stderr)
            return 2
        return 0 if exceeds(args.size_file, float(threshold), float(overhead)) else 1
    if args.cmd == "set-vm-size":
        return 0 if set_vm_size(args.pipelines_yml, args.pipeline, args.size) else 1
    if args.cmd == "pipeline-variables":
        print(json.dumps(pipeline_variables(args.config, os.environ)))
        return 0


if __name__ == "__main__":
    sys.exit(main())
