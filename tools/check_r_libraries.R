# Author: Lars Vilhuber
# (C) 2023
# Licensed under BSD-3 license
#
# Running instructions: Run all the code at once, no manual changes needed.
# Run with the WD set in this directory.
# Example: cd tools; R CMD BATCH (THIS FILE)

# Import necessary packages, install if necessary

!require("renv",character.only = TRUE)
!require("knitr",character.only = TRUE)
!require("dplyr",character.only = TRUE)
!require("rmarkdown",character.only = TRUE)
!require("here",character.only = TRUE)
!require("readr",character.only = TRUE)

# create aux if doesn't exist, as we will be writing stuff there.

if ( ! file.exists(here("aux")) ) {
    dir.create(here("aux"))
}

output.md = here(file.path("aux","r-libraries.md"))
output.csv= here(file.path("aux","r-libraries.csv"))
  
# Capture arguments
# https://stackoverflow.com/questions/14167178/passing-command-line-arguments-to-r-cmd-batch

##First read in the arguments listed at the command line
args=(commandArgs(TRUE))

##args is now a list of character vectors
## First check to see if arguments are passed.
## Then cycle through each element of the list and evaluate the expressions.
if(length(args)==0){
    print("No arguments supplied.")
    ##supply default values
    root=getwd()
} else {
    for(i in 1:length(args)){
      eval(parse(text=args[[i]]))
    }
}

# find dependencies
# this does not fail if no libraries are found.

libraries <- renv::dependencies(path=root)


# Loop to read all RDS files, recording successes as "yes"
if ( nrow(libraries) == 0 ) {
  message("No R libraries found, exiting")
  cat("No R libraries found",file=output.md,
                   sep="\n")
} else {
 
  # write out CSV file
  write_csv(libraries,output.csv)
  # write out the compressed Markdown table
 
  libraries %>% distinct(Package,Require,Version) %>% 
                arrange(Package,Version) %>% 
                knitr::kable() %>% 
                cat(.,file=output.md,
                   sep="\n")
 }

