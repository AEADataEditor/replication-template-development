# Author: Andres Aradillas Fernandez
# (C) 2022
# Licensed under BSD-3 license
#
# Running instructions: Run all the code at once, no manual changes needed.

# Import necessary packages, install if necessary

pkgTest <- function(x,y="")
{
	if (!require(x,character.only = TRUE))
	{
		if ( y == "" ) 
			{
		        install.packages(x,dep=TRUE)
			} else {
			remotes::install_version(x, y)
			}
		if(!require(x,character.only = TRUE)) stop("Package not found")
	}
	return("OK")
}

global.libraries <- c("here")

results <- sapply(as.list(global.libraries), pkgTest)

# create basename
basename <- "r-data-checks"

# Finds current directory
root <- here()

# Create list of all RDS files in directory
datafiles_list <- list.files(root, pattern = "\\.rds", full.names = TRUE, recursive = TRUE, ignore.case = TRUE, include.dirs = FALSE)

# Create list denoting successes/failures
read_success <- list()

# Loop to read all RDS files, recording successes as "yes"
if ( length(datafiles_list) == 0 ) {
  message("No RDS files found, exiting")
} else {
  for(k in 1:length(datafiles_list)){
    filename <- datafiles_list[[k]]
    short.filename <- gsub(paste0(root,"/"),"",filename)
    message(paste0("Processing: ",short.filename))
    t <- try(readRDS(filename), silent = TRUE)
    if ("try-error" %in% class(t)){
      read_success[[k]] <- "No"
    } else{
      read_success[[k]] <- "Yes"
    }
  }

  # Convert list into data frame
  df <- data.frame(matrix(unlist(datafiles_list), nrow=length(datafiles_list),  byrow=TRUE))
  df$col2 <- read_success

  # Add column names to new data frame
  colnames(df) <- c("File name", "Successfully read")
  df <- as.matrix(df)

  # remove root from absolute pathnames
  df[,1] <- gsub(paste0(root,"/"),"",df[,1])


  # Export as text file - always

  txtfile = here(paste0(basename,".txt"))
  xlsxfile= here(paste0(basename,".xlsx"))

  message(paste0("Writing out results: ",gsub(paste0(root,"/"),"",txtfile)))
  write.table(df, file = txtfile, 
                sep = ",", 
                quote = FALSE, 
                row.names = FALSE)


  # Export results as Excel if xlsx package installed
  t <- try(library(xlsx), silent = TRUE)
  if ("try-error" %in% class(t)) {
    message("No xlsx library, skipping write-out of XLSX file.")

  } else{
    message(paste0("Writing out results: ",gsub(paste0(root,"/"),"",xlsxfile)))
    write.xlsx(df, file = xlsxfile, 
                sheetName = "Output", 
                append = FALSE)
  }
}