#Template config.R

# If the author uses R, use this template, copy it to config.R and
# include in the authors' program(s) with
#     source("config.R", echo=TRUE)

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

# check if the author creates a log file. If not, adjust the following code fragment
# the easiest way is from the command line:
# R --vanilla < program.R > program.log

# keep this line in the config file
print(sessionInfo())
print(paste0("MRAN date was set to: ",mran.date))
