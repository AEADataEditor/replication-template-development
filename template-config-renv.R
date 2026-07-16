#Template master.R

# INSTRUCTIONS:
#
# Step 0: Bash setup
# 
# In File Explorer, look for "name_of_project.Rproj" file in the root directory.
# If one exists, go to Step 1. If not, open Git Bash.
# In bash, set your working directory to the root directory (probably 123456/code
#or similar) and type
# "touch .here"

# If for some reason that does not work (and it always should)
# manually override in line XXX of this file.


# Step 1: Script Order
#
#At the end of this file, add "source("<filename>", echo = TRUE)" for each R script
#provided by the author, in the order specified in the README. If the author provides
#a main or master file, only that file must be added.

#Step 2: Packages
#
# If the README specifies packages that need to be manually installed, add them 
# to readme.libraries, NOT global.libraries to make sure they're part of the renv
# snapshot.

# Step 3: Generate log file
# 
# The following command works on Linux, MacOS, and on Windows
# from the "Terminal" within Rstudio:
#     R CMD BATCH master.R 
# For alternative ways to do that, see 
# https://github.com/labordynamicsinstitute/replicability-training/wiki/R-Tips

# Step 4: Make sure this script carries over
#
# Check any author scripts you're running for lines like rm(list = ls(all = TRUE))
# These will clear your environment and rootdir will no longer work. Comment these
# lines out

#*================================================
#* Let's do everything verbosely

options(verbose=TRUE)

#*================================================
#* Let's capture the current working directory, so we can return to it later
temphome <- getwd()

#*================================================
#* This lists the libraries that are to be installed to properly set up renv. Leave
#* devtools and rprojroot here; if the authors want you to install others, wait
#* until you've activated renv

# do we actually need devtools and rprojroot? testing but currently no
global.libraries <- c()

#global.libraries <- c("devtools","rprojroot")
#install.packages(global.libraries)

#*================================================
#* If you're running this script in terminal, you may get a mirror error. This 
#* line tells R where to install packages from to avoid this error

options(repos = c(CRAN = "https://cloud.r-project.org"))

#*==============================================================================================*/
#* This is specific to AEA replication environment. May not be needed if no confidential data   */
#* are used in the reproducibility check.                                                       */
#* Replicator should check the JIRA field "Working location of restricted data" for right path  */

sdrive <- ""

#*================================================
#* This lists any paths, relative to the root directory, that are to be created.

create.paths <- c("logs")
# for instance, the following paths might be necessary
#create.paths <- c("data/raw","data/interwrk","data/generated","results")

################################################
# Setup for automatic basepath detection       #
################################################

# Preferred:
# in bash, go to the root directory and type
# "touch .here". Then the following code will work cleanly.

# Alternative:
# There is already a "name_of_project.Rproj" file in the root directory.
# No further action needed

# If for some reason that does not work (and it always should)
# manually override:

# rootdir <- "path/to/root/directory"
rootdir <- ""

####################################
# global libraries used everywhere #
####################################

posit.date <- Sys.Date() - 31
# posit.date <- "2020-01-01" # uncomment and set manually if the above does not work

# PPM only snapshots on weekdays (not sure why...)
# Only check for weekday if posit.date is a Date object, not a string
if (!is.character(posit.date) && weekdays(posit.date) %in% c("Saturday","Sunday")) {
  posit.date <- posit.date - 2
}

# Check if running on Linux
if (Sys.info()['sysname'] == "Linux") {
  # Try to determine the Linux distribution and version using /etc/os-release
  if (file.exists("/etc/os-release")) {
    os_release <- system("grep -E '^(ID|VERSION_ID|VERSION_CODENAME|ID_LIKE)=' /etc/os-release", intern = TRUE)
    
    # Extract distribution ID (like ubuntu, debian, rocky)
    distro_id <- gsub("ID=", "", grep("^ID=", os_release, value = TRUE))
    distro_id <- gsub("[\"']", "", distro_id) # Remove quotes if present
    
    # Extract version ID (like 9.4 for Rocky Linux)
    version_id <- gsub("VERSION_ID=", "", grep("^VERSION_ID=", os_release, value = TRUE))
    version_id <- gsub("[\"']", "", version_id) # Remove quotes if present
    
    # Extract codename (like focal, jammy, bullseye)
    codename <- gsub("VERSION_CODENAME=", "", grep("^VERSION_CODENAME=", os_release, value = TRUE))
    
    # Extract ID_LIKE (like rhel, centos, fedora)
    id_like <- gsub("ID_LIKE=", "", grep("^ID_LIKE=", os_release, value = TRUE))
    id_like <- gsub("[\"']", "", id_like) # Remove quotes if present
    
    # If we found Ubuntu or Debian
    if (length(distro_id) > 0 && grepl("^(ubuntu|debian)$", distro_id)) {
      # Set CRAN to binary PPM for Ubuntu/Debian
      options(repos = c(CRAN = paste0("https://packagemanager.posit.co/cran/__linux__/", codename, "/", posit.date)))
      message(paste0("Using binary PPM for Linux distribution: ", distro_id, " (", codename, ")"))
    } else if (length(distro_id) > 0 && distro_id == "rocky" && grepl("^9", version_id)) {
      # Set CRAN to binary PPM for Rocky Linux 9
      options(repos = c(CRAN = paste0("https://packagemanager.posit.co/cran/__linux__/rhel9/", posit.date)))
      message(paste0("Using binary PPM for Linux distribution: ", distro_id, " (version ", version_id, ")"))
    } else if (length(distro_id) > 0 && distro_id == "opensuse-leap" && version_id == "15.6") {
      # Set CRAN to binary PPM for opensuse-leap 15.6
      options(repos = c(CRAN = paste0("https://packagemanager.posit.co/cran/__linux__/opensuse156/",posit.date)))
      message(paste0("Using binary PPM for Linux distribution: ", distro_id, " (version ", version_id, ")"))
    } else {
      # Use standard PPM with date-based snapshot for other Linux
      options(repos = c(CRAN = paste0("https://packagemanager.posit.co/cran/", posit.date)))
    }
  } else {
    # Use standard PPM with date-based snapshot if os-release not available
    options(repos = c(CRAN = paste0("https://packagemanager.posit.co/cran/", posit.date)))
  }
} else {
  # Use standard PPM with date-based snapshot for non-Linux systems
  options(repos = c(CRAN = paste0("https://packagemanager.posit.co/cran/", posit.date)))
}



# print option repos 
message(paste0("Setting Posit Package Manager snapshot to ",posit.date))
message("If this does not work, set the date manually in line 22")
getOption("repos")

# If any package in an renv lockfile is missing a recorded repository, renv::restore()
# will use the PPM date from options("repos") <- your PPM date, not the author's


####################################
# Set path to root directory       #
#                                  #
####################################
options(renv.consent = TRUE)

if (!requireNamespace("here", quietly = TRUE)) install.packages("here")
if ( rootdir == "" ) rootdir <- here::here()
setwd(rootdir)


# Main directories

for ( dir in create.paths){
	if (file.exists(file.path(rootdir,dir))){
	} else {
	dir.create(file.path(rootdir,dir))
	}
}


# Setting project-specific library


# In order to make config.R run smoothly, turn off prompts asking if we want to
# install packages

options(renv.config.autoloader.enabled = TRUE)
options(renv.config.install.prompt = FALSE)


# Package management using author's renv when available

if (file.exists(file.path(rootdir,"renv.lock"))) {
  message("Detected renv.lock. Restoring author's renv environment.")
  if (!requireNamespace("renv", quietly=TRUE)) install.packages("renv")
  renv::restore(prompt=FALSE)
} else {
  message("No renv.lock found. Initializing project-local renv.")
  if (!requireNamespace("renv", quietly=TRUE)) install.packages("renv")
  if (!file.exists(file.path(rootdir,"renv"))) renv::init(bare=TRUE, restart = FALSE)
  source(file.path(rootdir, "renv", "activate.R"))

#* If the README specifies additional packages that need to be installed,
#* add them here. This runs AFTER renv has been activated, so they will be
#* installed into the project-local renv library (not your base R library),
#* and will be picked up correctly by renv::snapshot() below.
  readme.libraries <- c()  # e.g. c("packagename1", "packagename2")
  global.libraries <- c(global.libraries, readme.libraries)
  
# dependencies = NA to prevent _all_ suggested packages from being downloaded
  pkgTest <- function(x){
    if(!requireNamespace(x, quietly=TRUE))
      install.packages(x, dependencies=NA)
    library(x, character.only=TRUE)
  }

  invisible(lapply(global.libraries,pkgTest))
  
  #Install any remaining dependencies renv::dependencies() finds in scripts across
  # the project.
  missing <- setdiff(renv::dependencies(rootdir)$Package, rownames(installed.packages()))
  if (length(missing) > 0) renv::install(missing, prompt=FALSE)
  
  renv::snapshot(prompt=FALSE)
}


# Get information on the system we are running on
Sys.info()
R.version

# Return to the directory we started in
setwd(temphome)

# keep these lines in the config file
message("======================================================================================================")
message(paste0(" Current working directory: ",getwd()))
print(sessionInfo())
message("Current libPaths:")
message(.libPaths())
message(print(list.files(.libPaths()[1])))

message("Done with configuration.")


####################################
# Run author code                  #
#                                  #
####################################

#* Add author's programs in the order listed in the README

author.programs <- c(
   "code/master.R"
)

for (prog in author.programs) {
  message(paste0("---- Sourcing: ", prog, " ----"))
  source(file.path(rootdir, prog), echo = TRUE)
}

#Final snapshot preserves the packages from a successful run
renv::snapshot(prompt=FALSE)

