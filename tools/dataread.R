# Running instructions: Run all the code at once, no manual changes needed.

# Import necessary packages
require(xlsx)
require("stringi")
require("here")
require(tidyverse)

# Finds current directory
root <- here()

# Retrieve list of all folders
dir_list <- list.dirs(root)[-1]
folder_list <- gsub("\\./", "", dir_list)
folder_list
data_folder_list <- list()

# Find data/RDS folder(s)
for(k in 1:length(folder_list)){
  if (grepl("data", folder_list[[k]], fixed = TRUE) || grepl("rds", folder_list[[k]], fixed = TRUE) || grepl("Data", folder_list[[k]], fixed = TRUE) || grepl("Rds", folder_list[[k]], fixed = TRUE) || grepl("RDS", folder_list[[k]], fixed = TRUE)) {
    # If data/RDS folder exists, add it to new list
      data_folder_list <- append(data_folder_list, folder_list[[k]])
    }
}

# Create list of all RDS files in directory
datafiles_list <- list()
for(k in 1:length(data_folder_list)){
  setwd(data_folder_list[[k]])
  listrds <- dir(pattern = ".rds")
  listRds <- dir(pattern = ".Rds")
  listRDS <- dir(pattern = "RDS")
  datafiles_list <- append(datafiles_list, listrds)
  datafiles_list <- append(datafiles_list, listRds)
  datafiles_list <- append(datafiles_list, listRDS)
}

# Loop to read all RDS files, recording successes as "yes"
dataFiles <- list()
for(k in 1:length(datafiles_list)){
  t <- try(readRDS(datafiles_list[[k]]))
  if ("try-error" %in% class(t)){
    datafiles_list[[k]][2] <- "No"
  } else{
    datafiles_list[[k]][2] <- "Yes"
  }
  dataFiles[[k]] <- ""
}

# Convert list into data frame
df <- data.frame(matrix(unlist(datafiles_list), nrow=length(datafiles_list), byrow=TRUE))

# Add column names to new data frame
colnames(df) <- c("File name", "Successfully read?")

# Export list as Excel spreadsheet, will appear in AEAREP directory
setwd(root)
write.xlsx(df, file = "rdatareading.xlsx", sheetName = "Output", append = FALSE)
