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
local c_time = c(current_time)
local ctime = subinstr("`c_time'", ":", "_", .)

log using "`pwd'/logfile_`cdate'-`ctime'.log", replace text

/* It will provide some info about how and when the program was run */
/* See https://www.stata.com/manuals13/pcreturn.pdf#pcreturn */
local variant = cond(c(MP),"MP",cond(c(SE),"SE",c(flavor)) )  
// alternatively, you could use 
// local variant = cond(c(stata_version)>13,c(real_flavor),"NA")  

di "=== SYSTEM DIAGNOSTICS ==="
di "Stata version: `c(stata_version)'"
di "Updated as of: `c(born_date)'"
di "Variant:       `variant'"
di "Processors:    `c(processors)'"
di "OS:            `c(os)' `c(osdtl)'"
di "Machine type:  `c(machine_type)'"
di "=========================="


/* install any packages locally */
capture mkdir "`pwd'/ado"
sysdir set PERSONAL "`pwd'/ado/personal"
sysdir set PLUS     "`pwd'/ado/plus"
sysdir set SITE     "`pwd'/ado/site"
sysdir

/* add packages to the macro, then execute the program */

program install_packages
    * *** Add required packages from SSC to this list ***
    local ssc_packages ""
    
    if !missing("`ssc_packages'") {
        foreach pkg in "`ssc_packages'" {
            dis "Installing `pkg'"
            ssc install `pkg', replace
        }
    }

    * Install packages using net
    *  net install yaml, from("https://raw.githubusercontent.com/gslab-econ/stata-misc/master/")
    
end
install_packages

/* other commands */

global rootdir "`pwd'"

set more off


