/* Template config.do */
/* Copy this file to your replication directory if using Stata, e.g.,
    cp template-config.do 12345/codes/config.do

   or similar, and then add

   include "config.do"

   in the author's main Stata program

   */

/* Structure of the code, two scenarios:
   - Code looks like this (simplified, Scenario A)
         directory/
              code/
                 main.do
                 01_dosomething.do
              data/
                 data.dta
                 otherdata.dta
   - Code looks like this (simplified, Scenario B)
         directory/
               main.do
               scripts/
                   01_dosomething.do
                data/
                   data.dta
                   otherdata.dta
    For the variable "scenario" below, choose "A" or "B". It defaults to "A".

    NOTE: you should always put "config.do" in the same directory as "main.do"
*/

local scenario "A" 
* *** Add required packages from SSC to this list ***
local ssc_packages ""
    // Example:
    // local ssc_packages "estout boottest"
    // If you need to "net install" packages, go to the very end of this program, and add them there.

/* This works on all OS when running in batch mode, but may not work in interactive mode */


local pwd : pwd                     // This always captures the current directory

if "`scenario'" == "A" {             // If in Scenario A, we need to change directory first
    cd ..
}
global rootdir : pwd                // Now capture the directory to use as rootdir


/*================================================================================================================*/
/*                            You normally need to make no further changes below this                             */
/*                             unless you need to "net install" packages                                          */

set more off
cd "`pwd'"                            // Return to where we were before and never again use cd
global logdir "${rootdir}/logs"
cap mkdir "$logdir"

/* check if the author creates a log file. If not, adjust the following code fragment */

local c_date = c(current_date)
local cdate = subinstr("`c_date'", " ", "_", .)
local c_time = c(current_time)
local ctime = subinstr("`c_time'", ":", "_", .)

log using "$logdir/logfile_`cdate'-`ctime'-`c(username)'.log", name(ldi) replace text

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
capture mkdir "$rootdir/ado"
sysdir set PERSONAL "$rootdir/ado/personal"
sysdir set PLUS     "$rootdir/ado/plus"
sysdir set SITE     "$rootdir/ado/site"
sysdir

/* add packages to the macro */

    
    if !missing("`ssc_packages'") {
        foreach pkg in `ssc_packages' {
            capture which `pkg'
            if _rc == 111 {                 
               dis "Installing `pkg'"
                ssc install `pkg', replace
            }
            which `pkg'
        }
    }

/*==============================================================================================*/
/* If you need to "net install" packages, add lines to this section                             */
    * Install packages using net
    *  net install yaml, from("https://raw.githubusercontent.com/gslab-econ/stata-misc/master/")
    
/* other commands, rarely used, uncomment as needed */

/* if needing egenmore, uncomment next line. egenmore cannot be verified by "which" */

// ssc install egenmore

/*==============================================================================================*/
/* after installing all packages, it may be necessary to issue the mata mlib index command */
/* This should always be the LAST command after installing all packages                    */

	mata: mata mlib index

/*==============================================================================================*/
/* This is specific to AEA replication environment. May not be needed if no confidential data   */
/* are used in the reproducibility check.                                                       */
/* Replicator should check the JIRA field "Working location of restricted data" for right path  */

global sdrive ""


