#Template config.R

# If the author uses R, use this template, 
# copy it to config.R and call all required R scripts through the 
# source() function (i.e. source("DataPrep.R", echo = TRUE)).

install.packages('TeachingDemos')   
library(TeachingDemos)

# Set path to root directory
basepath <- "path/to/root/directory"
setwd(basepath)

# Start the markdown log file
mdtxtStart("Log", file = 'logfile.md', commands = TRUE, results = TRUE, visible.only = TRUE)
Sys.info()
R.version

####################################
# global libraries used everywhere #
####################################

mran.date <- "2019-09-01"
options(repos=paste0("https://cran.microsoft.com/snapshot/",mran.date,"/"))



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

global.libraries <- c("foreign","devtools","rprojroot")

results <- sapply(as.list(global.libraries), pkgTest)


# keep this line in the config file
print(sessionInfo())
print(paste0("MRAN date was set to: ",mran.date))

# Call provided R scripts using 'source(".", echo = TRUE)'


# Close log file
mdtxtStop()
