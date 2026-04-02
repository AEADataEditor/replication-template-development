(helpful-scripts)=
# Various helpful scripts

All of the following scripts are either made available in `bash` when you run the [bash setup](setup-bash) in the `$HOME/bin` directory, or are available in the `tools/` folder in each repository. 

:::{note}

If you do not see a script referenced here, or the script does not behave as intended, 

1. `git commit` all changes, and `git push` them
2. Run the `Refresh repository` script in Bitbucket.

:::


## Data Download and Synchronization Tools

### download_box_private.py
Python script for downloading files from private Box folders using JWT authentication.

**Links:** [Source](https://github.com/aeaDataEditor/replication-template/blob/master/tools/download_box_private.py) | [Help](help-download_box_private)

### download_dv.py
Python script for downloading complete datasets from Dataverse repositories as ZIP archives using DOI.

**Links:** [Source](https://github.com/aeaDataEditor/replication-template/blob/master/tools/download_dv.py) | [Help](help-download_dv)

### download_openicpsr-private.py
Python script for downloading files from private (unpublished) openICPSR deposits with authentication.

**Links:** [Source](https://github.com/aeaDataEditor/replication-template/blob/master/tools/download_openicpsr-private.py) | [Help](help-download_openicpsr-private)

### download_osf.sh
Bash script for downloading all files and directories from Open Science Framework (OSF) projects.

**Links:** [Source](https://github.com/aeaDataEditor/replication-template/blob/master/tools/download_osf.sh) | [Help](help-download_osf)

### download_zenodo_draft.py
Python script for downloading files from Zenodo draft deposits that require authentication.

**Links:** [Source](https://github.com/aeaDataEditor/replication-template/blob/master/tools/download_zenodo_draft.py) | [Help](help-download_zenodo_draft)

### download_zenodo_public.sh
Bash script for downloading files from public Zenodo repositories using zenodo_get tool.

**Links:** [Source](https://github.com/aeaDataEditor/replication-template/blob/master/tools/download_zenodo_public.sh) | [Help](help-download_zenodo_public)

### list_box_files.py
Lists files from a private Box folder using JWT authentication and outputs results to a text file.

**Links:** [Source](https://github.com/aeaDataEditor/replication-template/blob/master/tools/list_box_files.py) | [Help](help-list_box_files)

### sync-codeocean.sh
Synchronizes CodeOcean capsules with local repositories, maintaining both live Git clones and static copies.

**Links:** [Source](https://github.com/aeaDataEditor/replication-template/blob/master/tools/sync-codeocean.sh) | [Help](help-sync-codeocean)

## File Format Conversion Tools

### convert_eps.sh
Bash script that recursively converts EPS (Encapsulated PostScript) files to PNG format using ImageMagick. 

**Links:** [Source](https://github.com/aeaDataEditor/replication-template/blob/master/tools/convert_eps.sh) | [Help](help-convert_eps)

### convert_graphs.do
Stata script that converts GPH graph files to PDF and PNG formats.

**Links:** [Source](https://github.com/aeaDataEditor/replication-template/blob/master/tools/convert_graphs.do) | [Help](help-convert_graphs)

### csv2md.py
Python tool for converting arbitrary CSV files to Markdown format.

**Links:** [Source](https://github.com/aeaDataEditor/replication-template/blob/master/tools/csv2md.py) | [Help](help-csv2md)

### matlab_convert_fig.m
MATLAB script that converts .fig files to PNG format, processing all figure files in the current directory.

**Links:** [Source](https://github.com/aeaDataEditor/replication-template/blob/master/tools/matlab_convert_fig.m) | [Help](help-matlab_convert_fig)

### matlab_convert_mat2csv.m
MATLAB script that converts .mat files to CSV format, extracting all variables as separate CSV files.

**Links:** [Source](https://github.com/aeaDataEditor/replication-template/blob/master/tools/matlab_convert_mat2csv.m) | [Help](help-matlab_convert_mat2csv)

### mk_tex_table.sh
Converts standalone LaTeX table files to complete PDF documents with comprehensive formatting packages.

**Links:** [Source](https://github.com/aeaDataEditor/replication-template/blob/master/tools/mk_tex_table.sh) | [Help](help-mk_tex_table)

## Tools to check for various things

These are usually not used directly, but run by the Pipelines.

### Stata_scan_code/
Directory containing Stata code scanning tools and packages for analyzing Stata scripts and dependencies.

**Links:** [Source](https://github.com/aeaDataEditor/replication-template/tree/master/tools/Stata_scan_code) | [Help](help-Stata_scan_code)



### scan_pkg.jl
Julia package scanner that identifies and lists packages used in Julia files via `using` and `import` statements.

**Links:** [Source](https://github.com/aeaDataEditor/replication-template/blob/master/tools/scan_pkg.jl) | [Help](help-scan_pkg)

### check_r_deps.R
R script that finds and outputs all R package dependencies as CSV from a project directory.

**Links:** [Source](https://github.com/aeaDataEditor/replication-template/blob/master/tools/check_r_deps.R) | [Help](help-check_r_deps)

### check_rds_files.R
R script for checking RDS (R data files), designed to run automatically without manual changes.

**Links:** [Source](https://github.com/aeaDataEditor/replication-template/blob/master/tools/check_rds_files.R) | [Help](help-check_rds_files)

### install.R
R package installation utility with version control; provides `pkgTest()` function to install and require packages.

**Links:** [Source](https://github.com/aeaDataEditor/replication-template/blob/master/tools/install.R) | [Help](help-install)

### summarize_data.py
Data summarization script that reads CSV metadata and calculates total bytes by directory level.

**Links:** [Source](https://github.com/aeaDataEditor/replication-template/blob/master/tools/summarize_data.py) | [Help](help-summarize_data)

## Ad-hoc Data Analysis and Comparison Tools

### compare_manifests.py
Python script that compares two SHA256 manifest files to identify overlaps in filenames, checksums, and complete records.

**Links:** [Source](https://github.com/aeaDataEditor/replication-template/blob/master/tools/compare_manifests.py) | [Help](help-compare_manifests)

### generate_png_diff.sh
Generates visual diffs for modified PNG images by comparing them against their git repository versions.

**Links:** [Source](https://github.com/aeaDataEditor/replication-template/blob/master/tools/generate_png_diff.sh) | [Help](help-generate_png_diff)


### summarize_diff_stats.py
Parses and summarizes statistical differences from files, extracting numerical values and filenames.

**Links:** [Source](https://github.com/aeaDataEditor/replication-template/blob/master/tools/summarize_diff_stats.py) | [Help](help-summarize_diff_stats)


## Pipeline and Workflow Tools


### pipeline-steps1-4.sh
Combined pipeline script that handles multiple steps of the openICPSR download process.

**Links:** [Source](https://github.com/aeaDataEditor/replication-template/blob/master/tools/pipeline-steps1-4.sh) | [Help](help-pipeline-steps1-4)

### run_scanner.sh
Runs Stata code scanner on ICPSR directory, reads configuration and executes scanning operations.

**Links:** [Source](https://github.com/aeaDataEditor/replication-template/blob/master/tools/run_scanner.sh) | [Help](help-run_scanner)

### sbatch-shell.sh
SLURM batch job script template for running Stata jobs on HPC clusters with resource specifications.

**Links:** [Source](https://github.com/aeaDataEditor/replication-template/blob/master/tools/sbatch-shell.sh) | [Help](help-sbatch-shell)

## Configuration and Setup Tools


### linux-system-info.sh
System information collector that displays OS details, processor info, and memory availability.

**Links:** [Source](https://github.com/aeaDataEditor/replication-template/blob/master/tools/linux-system-info.sh) | [Help](help-linux-system-info)


### update_tools.sh
Tool updater that downloads latest replication template files from GitHub and copies them to template directory.

**Links:** [Source](https://github.com/aeaDataEditor/replication-template/blob/master/tools/update_tools.sh) | [Help](help-update_tools)

## Document Processing Tools

### prepare-revision.py (inactive)

Processes Markdown files by replacing code block content in Appendix sections while maintaining headers.

**Links:** [Source](https://github.com/aeaDataEditor/replication-template/blob/master/tools/prepare-revision.py) | [Help](help-prepare-revision)


## Configuration Files

### requirements-scanner.txt
Python requirements file for scanner tools.

**Links:** [Source](https://github.com/aeaDataEditor/replication-template/blob/master/tools/requirements-scanner.txt)

### requirements.txt
Python requirements file for general tools.

**Links:** [Source](https://github.com/aeaDataEditor/replication-template/blob/master/tools/requirements.txt)

### template.tex
LaTeX template file for document generation.

**Links:** [Source](https://github.com/aeaDataEditor/replication-template/blob/master/tools/template.tex)
