#!/usr/bin/env python3
"""
Convert the manuscript PDF(s) in a directory to Markdown, with the figures
extracted as images. The conversion is mechanical: nothing is interpreted,
summarized or corrected.

Usage:
    manuscript_to_markdown.py [--source-dir DIR] [--output-dir DIR]
                              [--engine auto|marker|markitdown] [--list]
    manuscript_to_markdown.py -h|--help

A file counts as the manuscript when its name is
    - PDF_Proof.PDF (any case), or
    - a journal acronym followed by the manuscript number, e.g.
      AEJApp-2025-0453.R1_Proof_hi.pdf or AER-2025-0473_AO.pdf
Other PDFs (forms, "Data and Code Availability.pdf", 13071-2.pdf) are ignored.

Options:
    --source-dir DIR   Directory with the PDFs (default: current directory)
    --output-dir DIR   Directory for the results (default: manuscript_parsed).
                       Each manuscript gets <output-dir>/<file stem>/, holding
                       <file stem>.md and the extracted images.
    --engine           marker:     marker_single, OCR disabled (layout, tables,
                                   equations and figures as images)
                       markitdown: text only, no images; fast
                       auto:       marker, then markitdown if marker is missing
                                   or fails (default)
    --list             Print the files that would be converted and stop

Exit code: 0 on success or when no manuscript is found, 1 if a manuscript could
not be converted by any engine.
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile

MANUSCRIPT_PATTERNS = (
    re.compile(r"^PDF_Proof.*\.pdf$", re.IGNORECASE),
    re.compile(r"^[A-Za-z]+-\d{4}-\d+.*\.pdf$"),
)
ENGINES = ("marker", "markitdown")


def find_manuscripts(directory):
    """Sorted names of the manuscript PDFs directly in directory."""
    names = []
    for name in sorted(os.listdir(directory)):
        if os.path.isfile(os.path.join(directory, name)) and any(p.match(name) for p in MANUSCRIPT_PATTERNS):
            names.append(name)
    return names


def run_marker(pdf, out_dir):
    """Convert with marker_single; its result lands in out_dir/<stem>/."""
    exe = shutil.which("marker_single")
    if not exe:
        raise RuntimeError("marker_single not found")
    subprocess.run([exe, pdf, "--output_dir", out_dir, "--disable_ocr", "--disable_tqdm"], check=True)


def run_markitdown(pdf, out_dir):
    """Convert with markitdown; its result lands in out_dir/<stem>/<stem>.md."""
    exe = shutil.which("markitdown")
    if not exe:
        raise RuntimeError("markitdown not found")
    stem = os.path.splitext(os.path.basename(pdf))[0]
    target = os.path.join(out_dir, stem)
    os.makedirs(target, exist_ok=True)
    subprocess.run([exe, pdf, "-o", os.path.join(target, stem + ".md")], check=True)


RUNNERS = {"marker": run_marker, "markitdown": run_markitdown}


def engine_order(engine):
    return ENGINES if engine == "auto" else (engine,)


def convert(pdf, output_dir, engine="auto", runners=None):
    """Convert one PDF into output_dir/<stem>/. Returns the engine used.

    The engine works in a scratch directory first, so a failed attempt never
    leaves a half-written result behind. Raises RuntimeError if all engines fail.
    """
    runners = runners or RUNNERS
    stem = os.path.splitext(os.path.basename(pdf))[0]
    errors = []
    for name in engine_order(engine):
        with tempfile.TemporaryDirectory() as scratch:
            try:
                runners[name](pdf, scratch)
                produced = os.path.join(scratch, stem)
                if not os.path.isfile(os.path.join(produced, stem + ".md")):
                    raise RuntimeError(f"no {stem}.md produced")
            except (RuntimeError, subprocess.CalledProcessError, OSError) as e:
                errors.append(f"{name}: {e}")
                print(f"{name} failed for {os.path.basename(pdf)}: {e}", file=sys.stderr)
                continue
            target = os.path.join(output_dir, stem)
            shutil.rmtree(target, ignore_errors=True)
            os.makedirs(output_dir, exist_ok=True)
            shutil.move(produced, target)
            return name
    raise RuntimeError("; ".join(errors))


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--source-dir", default=".")
    p.add_argument("--output-dir", default="manuscript_parsed")
    p.add_argument("--engine", choices=("auto",) + ENGINES, default="auto")
    p.add_argument("--list", action="store_true")
    args = p.parse_args(argv)

    manuscripts = find_manuscripts(args.source_dir)
    if not manuscripts:
        print(f"No manuscript PDF found in {args.source_dir}")
        return 0
    if args.list:
        print("\n".join(manuscripts))
        return 0

    failed = 0
    for name in manuscripts:
        try:
            used = convert(os.path.join(args.source_dir, name), args.output_dir, args.engine)
            print(f"Converted {name} with {used} -> {os.path.join(args.output_dir, os.path.splitext(name)[0])}")
        except RuntimeError as e:
            failed += 1
            print(f"Error: could not convert {name}: {e}", file=sys.stderr)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
