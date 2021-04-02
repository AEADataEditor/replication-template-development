<<<<<<< HEAD
options(warn=-1)

# Searches through Stata code to find the packages and dependent packages 
# necessary for running the code. Uses list of most common package names 
# to search through code. Does not include commented lines in the search.

##### User needs to fill in these file names
#-------------------------------------------------------------
working_dir = "U:/Documents/AEA_Workspace/Statapackagesearch" # your current working directory aka where .do files can be found
package_list = "U:/Documents/AEA_Workspace/Statapackagesearch/package_list.xlsx" # xlsx file containing the package names
#-------------------------------------------------------------

# Uncomment line 15 if package readxl is not installed 
#install.packages("readxl") 
library("readxl")

setwd(working_dir) # Choose your working directory here

packages = read_xlsx(package_list,sheet=1, col_names=TRUE)

# Imports and defines column A of package_list.xlsx (list of packages mined from SSC)
names = packages$Package

# Imports and defines column B (signal commands that indicate use of a certain package)
signals = packages$Signals[!is.na(packages$Signals)]
names_with_signal = packages$Package[!is.na(packages$Signals)]

# Imports and defines column C (dependencies- when a package/command relies on another to run)
dependencies = packages$Dependencies[!is.na(packages$Dependencies)]
names_with_dependency = packages$Package[!is.na(packages$Dependencies)]

all_code = c()
for (file in list.files(working_dir, full.names = TRUE)) {
  if (endsWith (file, '.do')) {
    code_lines = scan(file = file, what="", sep="\n",blank.lines.skip=TRUE)
    
    #removes lines which are comments (start with *, **, or //)
    code_lines_no_comments = code_lines[!startsWith(code_lines, '*') & !startsWith(code_lines, '//')]
    
    #combines the code into one string
    code = paste(code_lines_no_comments, collapse = ' ') 
    
    #takes combined string and returns vector of strings from the code to search through
    all_code = c(all_code, strsplit(code, " ")[[1]])
  }
  
}


#Prints list of missing packages- includes those found via direct search, signal commands, and required dependencies
# Outputs such that it can be directly copied into our config.do

packages_to_install = c( names[names %in% all_code],
                         names_with_signal[signals %in% all_code],
                         dependencies[names_with_dependency %in% all_code])

print(noquote(paste(packages_to_install, collapse=" ")))

=======
options(warn=-1)

# Searches through Stata code to find the packages and dependent packages 
# necessary for running the code. Uses list of most common package names 
# to search through code. Does not include commented lines in the search.

##### User needs to fill in these file names
#-------------------------------------------------------------
working_dir = "U:/Documents/AEA_Workspace/Statapackagesearch" # your current working directory aka where .do files can be found
package_list = "U:/Documents/AEA_Workspace/Statapackagesearch/package_list.xlsx" # xlsx file containing the package names
#-------------------------------------------------------------

# Uncomment line 15 if package readxl is not installed 
#install.packages("readxl") 
library("readxl")

setwd(working_dir) # Choose your working directory here

packages = read_xlsx(package_list,sheet=1, col_names=TRUE)

# Imports and defines column A of package_list.xlsx (list of packages mined from SSC)
names = packages$Package

# Imports and defines column B (signal commands that indicate use of a certain package)
signals = packages$Signals[!is.na(packages$Signals)]
names_with_signal = packages$Package[!is.na(packages$Signals)]

# Imports and defines column C (dependencies- when a package/command relies on another to run)
dependencies = packages$Dependencies[!is.na(packages$Dependencies)]
names_with_dependency = packages$Package[!is.na(packages$Dependencies)]

all_code = c()
for (file in list.files(working_dir, full.names = TRUE)) {
  if (endsWith (file, '.do')) {
    code_lines = scan(file = file, what="", sep="\n",blank.lines.skip=TRUE)
    
    #removes lines which are comments (start with *, **, or //)
    code_lines_no_comments = code_lines[!startsWith(code_lines, '*') & !startsWith(code_lines, '//')]
    
    #combines the code into one string
    code = paste(code_lines_no_comments, collapse = ' ') 
    
    #takes combined string and returns vector of strings from the code to search through
    all_code = c(all_code, strsplit(code, " ")[[1]])
  }
  
}


#Prints list of missing packages- includes those found via direct search, signal commands, and required dependencies
# Outputs such that it can be directly copied into our config.do

packages_to_install = c( names[names %in% all_code],
                         names_with_signal[signals %in% all_code],
                         dependencies[names_with_dependency %in% all_code])

print(noquote(paste(packages_to_install, collapse=" ")))

>>>>>>> 1c74262a85c64045860c2ca5e9b4d8d63136121b
