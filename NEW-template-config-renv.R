#Template master.R

# INSTRUCTIONS:
#
# Step 0: Bash setup
# 
#In bash, set your working directory to the root directory (probably 123456/code
#or similar) and type
# "touch .here"

# If for some reason that does not work (and it always should)
# manually override in line XXX of this file.


# Step 1: Script Order
#
#At the end of this file, add R scripts to author.programs in the order specified 
#in the README. If the author provides a main or master file, likely only that 
#file must be added.

#Step 2: Packages
#
# If the README specifies packages that need to be manually installed, add them 
# to readme.libraries further down.

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

# Note: if any package in an renv lockfile is missing a recorded repository, renv::restore()
# will use the PPM date from options("repos"), meaning it will use _your_ PPM date,
# not the author's


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

# In order to make config.R run smoothly, turn off prompts asking if we want to
# install packages

options(renv.config.autoloader.enabled = TRUE)
options(renv.config.install.prompt = FALSE)

# Bulky renv.lock checks

# How many directory levels to search for an author-provided renv.lock,
# relative to rootdir. Increase either if the author's renv.lock is more than 1
# directory level up or down from rootdir
lockfile.search.up   <- 1
lockfile.search.down <- 1

find_author_lockfile <- function(rootdir, up = 1, down = 1) {
  
  candidates <- data.frame(path = character(0), distance = integer(0))
  
  # rootdir itself
  self_check <- file.path(rootdir, "renv.lock")
  if (file.exists(self_check)) {
    candidates <- rbind(candidates, data.frame(path = self_check, distance = 0))
  }
  
  # check upwards from rootdir
  current <- rootdir
  for (i in seq_len(up)) {
    parent <- dirname(current)
    if (parent == current) break  # hit filesystem root
    candidate <- file.path(parent, "renv.lock")
    if (file.exists(candidate)) {
      candidates <- rbind(candidates, data.frame(path = candidate, distance = i))
    }
    current <- parent
  }
  
  # check downwards from rootdir
  if (down > 0) {
    subdirs <- list.dirs(rootdir, recursive = TRUE, full.names = TRUE)
    for (d in subdirs) {
      depth <- length(strsplit(sub(paste0("^", rootdir), "", d), .Platform$file.sep)[[1]]) - 1
      if (depth >= 1 && depth <= down) {
        candidate <- file.path(d, "renv.lock")
        if (file.exists(candidate)) {
          candidates <- rbind(candidates, data.frame(path = candidate, distance = depth))
        }
      }
    }
  }
  
  if (nrow(candidates) == 0) return(NULL)
  candidates <- candidates[order(candidates$distance), ]
  candidates$path[1]
}

lockfile_path <- find_author_lockfile(rootdir, up = lockfile.search.up, down = lockfile.search.down)

#if the author's renv.lock file was found, load their setup and switch rootdir to
#what their code will likely expect
if (!is.null(lockfile_path)) {
  author_root <- dirname(lockfile_path)
  message("Detected renv.lock at: ", lockfile_path)
  rootdir <- author_root
  setwd(rootdir)
  if (!requireNamespace("renv", quietly = TRUE)) install.packages("renv")
  renv::restore(project = author_root, prompt = FALSE)
  renv::load(project = author_root) #uses load not activate to prevent a popup asking to switch projects, which breaks the code

#if no author renv.lock file was found, create a new blank renv project
} else {
  message("No renv.lock found within ", lockfile.search.up, " level(s) up / ",
          lockfile.search.down, " level(s) down. Initializing project-local renv.")
  if (!requireNamespace("renv", quietly = TRUE)) install.packages("renv")
  if (!file.exists(file.path(rootdir, "renv"))) renv::init(project = rootdir, bare = TRUE, restart = FALSE)
  renv::load(project = rootdir) #uses load not activate to prevent a popup asking to switch projects, which breaks the code
}

#If you've run the setup and then the author's code breaks because they didn't
#install some packages, or if the README specifies additional packages that need 
#to be installed, add them here to install them into the project's renv library
#(not base R library) and will be picked up correctly by renv::snapshot() below.

readme.libraries <- c("paletteer", "viridis") #these are color packages for testing, delete 

# Install packages from readme.libraries

  pkgTest <- function(x)
  {
    if (!require(x,character.only = TRUE))
    {
      renv::install(x,prompt = FALSE)
      if(!require(x,character.only = TRUE)) stop("Package not found")
    }
    return("OK")
  }
  
invisible(lapply(readme.libraries,pkgTest))

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

#Final snapshot preserves the packages from a successful run but won't overwrite
#the author's original. Not forced, may change later. Select option 1 so you don't
#include `here` in the snapshot, but make sure no other packages are listed.
renv::snapshot(
  project  = rootdir,
  lockfile = file.path(rootdir, "renv.lock.replicator_snapshot"),
  packages = c(renv::dependencies(rootdir)$Package, readme.libraries),
  prompt   = FALSE
)

