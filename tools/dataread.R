
# Running instructions: Run all the code at once, no manual changes needed.

# Import necessary packages, create basename
require("stringi")
require("here")
basename <- "r-data-checks.txt"

# Finds current directory
root <- here()

# Create list of all RDS files in directory
datafiles_list <- list.files(root, pattern = ".rds", full.names = TRUE, recursive = TRUE, ignore.case = TRUE, include.dirs = FALSE)

# Create list denoting successes/failures
read_success <- list()

# Loop to read all RDS files, recording successes as "yes"
for(k in 1:length(datafiles_list)){
  t <- try(readRDS(datafiles_list[[k]]))
  if ("try-error" %in% class(t)){
    read_success[[k]] <- "No"
  } else{
    read_success[[k]] <- "Yes"
  }
}

# Convert list into data frame
df <- data.frame(matrix(unlist(datafiles_list), nrow=length(datafiles_list), byrow=TRUE))
df$col2 <- read_success

# Add column names to new data frame
colnames(df) <- c("File name", "Successfully read?")

# Export results as Excel if xlsx package installed; if not, export as comma-separated .txt file
t <- try(library(xlsx))
if ("try-error" %in% class(t)) {
  write.table(df, file = here(basename), sep = ",", quote = FALSE, row.names = FALSE)
} else{
  write.xlsx(df, file = here("r-data-checks.xlsx"), sheetName = "Output", append = FALSE)
}