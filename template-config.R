#Template config.R

# INSTRUCTIONS:
# 
# In order to generate log files with R, use one of two methods:
# 1. If running on Linux or macOS, do not use this program, 
#    and run the author's program from the terminal:
#     R --vanilla < program.R > program.log
# 2. Alternatively, or if the setup is more complex, use this template.
#    Either integrate pieces of it into the author's main program
#    or call the author's R programs from this program, using 
#    this program as the "main" program:
#    - copy this program to main.R
#    - call all required R scripts through the source() function:
#      source("DataPrep.R", echo = TRUE)

####################################
# global libraries used everywhere #
####################################




####################################
# Set path to root directory       #
#                                  #
#  --->>   MODIFY THIS  <<---      #
####################################

# Preferred:
# in bash, go to the root directory and type
# "touch .here". Then the following code will work cleanly.

install.packages("here")
rootdir <- here::here()
setwd(rootdir)

# Alternatively, you might want to set the path manually:
#rootdir <- "path/to/root/directory"

# Get information on the system we are running on
Sys.info()
R.version



#*==============================================================================================*/
#* This is specific to AEA replication environment. May not be needed if no confidential data   */
#* are used in the reproducibility check.                                                       */
#* Replicator should check the JIRA field "Working location of restricted data" for right path  */

sdrive <- ""

#*================================================
#* This lists the libraries that are to be installed.
global.libraries <- c("foreign","devtools","rprojroot")


# Function to install libraries

pkgTest <- function(x)
{
	if (!require(x,character.only = TRUE))
	{
		install.packages(x,dep=TRUE)
		if(!require(x,character.only = TRUE)) stop("Package not found")
	}
	return("OK")
}

## Add any libraries to this line, and uncomment it.


results <- sapply(as.list(global.libraries), pkgTest)


# keep this line in the config file
print(sessionInfo())

# Add this file to the directory where the main file is and
# add the following line to the main file:
# source("config.R", echo = TRUE)
#
# Then run the main file as per instructions in the manual,
# e.g. R CMD BATCH main.R 

# If the authors' code needs additional directories, create them here. Adjust accordingly.
#


# Main directories
rawdata <- file.path(basepath, "data","raw")
interwrk <- file.path(basepath, "data","interwrk")
generated <- file.path(basepath, "data","generated")
results <- file.path(basepath, "results")

for ( dir in list(rawdata,interwrk,generated,results)){
	if (file.exists(dir)){
	} else {
	dir.create(file.path(dir))
	}
}