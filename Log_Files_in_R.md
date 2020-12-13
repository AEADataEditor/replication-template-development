# Creating Log Files in R

For manuscripts which use STATA, our `template-config.do` contains code to write a log file that captures both program code and output by utilizing the "log using" command.

The purpose of the following instruction sheet is to show how we can convert the `template-config.R` into a master file to call all necessary R scripts and generate a log file for the replication.

## 'TeachingDemos' Package

Although there is no direct equivalent to the "log using" command in STATA, an R command which works in much the same way is the 'mdtxtStart()' function included in the 'TeachingDemos' package.

More detailed information on the 'TeachingDemos' package and 'mdtxtStart()' function can be found [here](https://cran.r-project.org/web/packages/TeachingDemos/TeachingDemos.pdf), or by searching for it using the "Help" dropdown in the Rstudio console. 

## Using 'mdtxtStart()'
The nature of the function is such that is must be place at the top of each script and 'mdtxtStop()' at the bottom to capture all commands and output written in between. 

Instead of going through each program in a replication package and including these lines of code, a simpler solution is to convert the `template-config.R` into a master file which will call each R script included in the replication package (in the order which is hopefully described in the README) and capture a log file, in Markdown format, of the complete analysis.

## Example of `config.R` 

```
#Template config.R

# If the author uses R, use this template, copy it to config.R and call all required R scripts through the source() function (i.e. source("DataPrep.R", echo = TRUE)).

install.packages('TeachingDemos')   
library(TeachingDemos)

basepath <- "path/to/root/directory"
setwd(basepath)

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

# Call provided R scripts
source("config.R", echo = TRUE)
source("DataPrep.R", echo = TRUE)
source("Tables.R", echo = TRUE)
source("Figures.R", echo = TRUE)

mdtxtStop()
```

In the sample program above we have: 
1. Installed the package and loaded the library needed create the log file. 
2. Set the base path to our root directory. 
3. Started the log file as `logfile.md` written to subdirectory "Log".
4. Generated system information of the replicator's computing environment and R version.
5. Called the data prep and analysis programs provided in the replication package.
6. Closed the log file.


