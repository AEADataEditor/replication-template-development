
# Running instructions: Run all the code at once, no manual changes needed.

# Import necessary packages, create basename
require("stringi")
require("here")
basename <- "r-data-checks.txt"

# Finds current directory
root <- here()

# Retrieve list of all folders
dir_list <- list.dirs(root)[-1]
folder_list <- gsub("\\./", "", dir_list)

# Create list of all RDS files in directory
datafiles_list <- list()
for(k in 1:length(folder_list)){
  setwd(folder_list[[k]])
  listrds <- dir(pattern = ".rds")
  listRds <- dir(pattern = ".Rds")
  listRDS <- dir(pattern = ".RDS")
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

# Export results as Excel if xlsx package installed; if not, export as comma-separated .txt file
t <- try(library(xlsx))
if ("try-error" %in% class(t)) {
  write.table(df, file = here(basename), sep = ",", quote = FALSE, row.names = FALSE)
} else{
  write.xlsx(df, file = here("r-data-checks.xlsx"), sheetName = "Output", append = FALSE)
}