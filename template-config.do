/* Template config.do */
/* Copy this file to your replication directory if using Stata, e.g.,
    cp template-config.do replication-(netid)/config.do

   or similar, and then add

   include "config.do"

   in the author's main Stata program

   */

local pwd : pwd

/* check if the author creates a log file. If not, adjust the following code fragment */

local c_date = c(current_date)
local cdate = subinstr("`c_date'", " ", "_", .)
log using "`pwd'/logfile_`cdate'.log", replace text

/* keep this line in the config file */
di "=== SYSTEM DIAGNOSTICS ==="
di "Stata version: `c(stata_version)'"
di "Updated as of: `c(born_date)'"
di "Flavor:        `c(flavor)'"
di "Processors:    `c(processors)'"
di "OS:            `c(os)' `c(osdtl)'"
di "Machine type:  `c(machine_type)'"
di "Max matsize:   `c(max_matsize)'"
di "Max memory:    `c(max_memory)'"
di "=========================="

/* install any packages locally */
capture mkdir "`pwd'/ado"
sysdir set PERSONAL "`pwd'/ado/personal"
sysdir set PLUS     "`pwd'/ado/plus"
sysdir set SITE     "`pwd'/ado/site"
