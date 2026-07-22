#!/usr/bin/env python3
"""
Detect the software used in a deposit from a programs-metadata.csv (produced
by automations/04_list_program_files.sh) and update a Jira issue's
"Software used" field (customfield_10028) with any newly-identified names.

Usage:
    python3 jira_update_software.py <issue-key> <metadata-csv> [--project-dir DIR] [--yes]
    python3 jira_update_software.py -h|--help

Arguments:
    issue-key      Jira issue key (e.g., AEAREP-9354). Bare numbers are
                    expanded to AEAREP-<n>.
    metadata-csv    Path to generated/programs-metadata[.tag].csv.

Options:
    --project-dir DIR   Root directory the metadata CSV's paths are relative
                        to. Required to inspect .ipynb kernel language;
                        without it, notebooks are left unmatched.
    --lookup-ext CSV    Override the extension->software table (default:
                        software-extensions.csv next to this script).
    --lookup-name CSV   Override the filename->software table (default:
                        software-filenames.csv next to this script).
    --yes               Apply the update to Jira. Without this flag, the
                        script only prints what it would do (dry run).

Environment Variables Required (only when --yes is passed):
    JIRA_USERNAME - Your Jira email address
    JIRA_API_KEY  - API token from https://id.atlassian.com/manage-profile/security/api-tokens

Output:
    Prints detected software and any unmatched files (by extension) to
    stdout. Exit code 0 on success (including a no-op dry run), 1 on error.
"""

import argparse
import csv
import json
import os
import sys
from pathlib import Path

JIRA_SERVER = "https://aeadataeditors.atlassian.net"
SOFTWARE_FIELD = "customfield_10028"

DEFAULT_EXT_LOOKUP = Path(__file__).resolve().parent / "software-extensions.csv"
DEFAULT_NAME_LOOKUP = Path(__file__).resolve().parent / "software-filenames.csv"

IPYNB_LANGUAGE_MAP = {
    "python": "Python",
    "python3": "Python",
    "r": "R",
    "ir": "R",
    "julia": "Julia",
}


def load_csv_lookup(path):
    """Load a two-column CSV (key,value) into a dict keyed by lower-cased first column."""
    lookup = {}
    with open(path, newline="") as f:
        reader = csv.reader(f)
        next(reader, None)  # header
        for row in reader:
            if not row:
                continue
            key, value = row[0], row[1]
            lookup[key.strip().lower()] = value.strip()
    return lookup


def detect_ipynb_language(path):
    """Return the canonical software name for a notebook's kernel language, or None."""
    try:
        with open(path, encoding="utf-8") as f:
            notebook = json.load(f)
    except (OSError, ValueError):
        return None

    metadata = notebook.get("metadata", {}) if isinstance(notebook, dict) else {}
    lang = None
    kernelspec = metadata.get("kernelspec")
    if isinstance(kernelspec, dict):
        lang = kernelspec.get("language")
    if not lang:
        language_info = metadata.get("language_info")
        if isinstance(language_info, dict):
            lang = language_info.get("name")
    if not lang:
        return None
    return IPYNB_LANGUAGE_MAP.get(str(lang).strip().lower())


def resolve_software(filenames, project_dir, ext_lookup, name_lookup):
    """
    Resolve a list of relative file paths (as found in programs-metadata.csv)
    to canonical software names.

    Returns (found: set[str], unmatched: dict[str, int]) where unmatched
    counts files that could not be mapped, keyed by extension (or basename
    when there is no extension).
    """
    found = set()
    unmatched = {}

    def record_unmatched(key):
        unmatched[key] = unmatched.get(key, 0) + 1

    for rel_path in filenames:
        rel_path = rel_path.strip()
        if not rel_path:
            continue
        basename = os.path.basename(rel_path)
        base_lower = basename.lower()
        ext = Path(basename).suffix.lstrip(".").lower()

        if base_lower in name_lookup:
            found.add(name_lookup[base_lower])
            continue

        if ext == "ipynb":
            lang = detect_ipynb_language(Path(project_dir) / rel_path) if project_dir is not None else None
            if lang:
                found.add(lang)
            else:
                record_unmatched("ipynb")
            continue

        if ext in ext_lookup:
            found.add(ext_lookup[ext])
            continue

        record_unmatched(ext if ext else base_lower)

    return found, unmatched


def read_metadata_filenames(metadata_csv):
    """Read the filename column of a generated/programs-metadata.csv file."""
    filenames = []
    with open(metadata_csv, newline="") as f:
        reader = csv.reader(f)
        next(reader, None)  # header: filename,lines
        for row in reader:
            if row:
                filenames.append(row[0])
    return filenames
