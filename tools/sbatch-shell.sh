#!/bin/bash
# Job name:
#SBATCH --job-name=RunStata
#
# Memory
#SBATCH --mem=32G
#
# Request one node:
#SBATCH --nodes=1
#
# Specify number of tasks for use case (example):
#SBATCH --ntasks-per-node=1
#
# Processors per task: here, 8 bc we have Stata-MP/8
#SBATCH --cpus-per-task=8
#
# Wall clock limit: adjust accordingly. Format is HH:MM:SS or DD-HH:MM:SS where DD are days.
#SBATCH --time=00:00:30
#
# Email?
# Probably do not need "--mail-user=youremail@cornell.edu"
# Just add your email to the file "$HOME/.forward"
# 
#SBATCH --mail-type=ALL
#
#############################################################################
## Jira notifications
#############################################################################
#
# The main Jira ticket for this replication. Leave as "auto" to let
# jira_add_comment.py find it ($jiraticket in the environment, else the
# "jiraticket:" line of the nearest config.yml). Or hard-code it, e.g.
# JIRATICKET=AEAREP-1234
JIRATICKET=auto
#
# Where the replication-template tools are, as seen from the compute node.
TOOLS_DIR="${SLURM_SUBMIT_DIR:-$PWD}/tools"
#
# The cluster's native python3 is 3.9.x. Load a newer one; both module names
# are tried since not every cluster node has both. If neither is available,
# jira_add_comment.py still works on the native python3 (it falls back to the
# Jira REST API over the standard library), so failures here are not fatal.
if ! command -v module >/dev/null 2>&1; then
    for modinit in /etc/profile.d/lmod.sh /etc/profile.d/modules.sh /usr/share/lmod/lmod/init/bash; do
        [ -r "$modinit" ] && . "$modinit" && break
    done
fi
# On BioHPC/ECCO the python modulefiles live in /programs/modulefiles, which is
# not on the default MODULEPATH - without this the loads below silently fail.
[ -d /programs/modulefiles ] && module use /programs/modulefiles 2>/dev/null
module load python/3.10.6-r9 2>/dev/null || module load python/3.12.7 2>/dev/null || true
PYTHON_CMD=$(command -v python3 || command -v python || true)
#
# One entry point for both notifications. Credentials (JIRA_USERNAME,
# JIRA_API_KEY) are picked up by the script itself from the environment, from
# ./.env, or from ~/.envvars - nothing to set here. --partb redirects the
# comment from the main ticket to its "Part B ..." sub-task.
jira_notify() {
    [ -n "$PYTHON_CMD" ] || return 0
    [ -f "$TOOLS_DIR/jira_add_comment.py" ] || return 0
    "$PYTHON_CMD" "$TOOLS_DIR/jira_add_comment.py" --partb --slurm \
        --label "SLURM job ${SLURM_JOB_NAME:-$(basename "$0")}" \
        "$@" -- "$JIRATICKET" || true
}
#
# The stop notification runs from a trap, so it also fires when the job fails
# or is killed at the wall clock limit (SIGTERM, reported as exit code 143).
jira_notify_end() {
    rc=$?
    [ -z "$1" ] || rc=$1
    trap - EXIT TERM
    jira_notify --status completed --exit-code "$rc"
    exit "$rc"
}
trap 'jira_notify_end' EXIT
trap 'jira_notify_end 143' TERM
#
# Start notification.
jira_notify --status started
#
#############################################################################
## Command(s) to run (example):
#############################################################################
#
# Stata example
#
/usr/local/stata16/stata-mp -b main.do
#
## Matlab - will run "main.m", output to "main.log"
## Assumes you have done the setup at https://labordynamicsinstitute.github.io/ecco-notes/docs/biohpc/slurm-quick-start.html#one-time-setup
# module load matlab/2023a
# matlab -nodisplay -r "addpath(genpath('.')); main" -logfile main.$(date +%F_%H-%M-%S).log
#
# R example - caution with version and parallel processing
module load R/4.4.2
R CMD BATCH main.R main.$(date +%F_%H-%M-%S).log
#
# Exit with the status of the last command above, so that the stop
# notification reports "completed" or "failed" correctly.
exit $?
