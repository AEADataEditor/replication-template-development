> INSTRUCTIONS: ==>  Workflow stage: You are starting *PartB*. Move the *PartB* sub-task to *In Progress*.


## All data files provided

The full list of data files is listed in the Appendix.

> INSTRUCTIONS: Please verify that the list in the appendix was created and is complete. If not, create the list by hand (instructions in the appendix)


### File checks

{{ file-paths-summary.md }}

{{ duplicate-files-report.md }}

{{ zero-byte-files-report.md }}

{{ large-file-report.md }}

### PII Checks


{{ pii-summary.md }}


> [NOTE] As a reminder, no data with PII that **needs to remain private** should be published in the main replication package. If you have such PII in your dataset, and are allowed to publish it with restrictions, please contact us for the best solution, but do not include it in the main replication package. If you are allowed to publish the PII data as-is, please clearly document or explain that permission, to avoid future misunderstandings.

We recommend using the J-PAL maintained [PII-Scan for R](https://github.com/J-PAL/PII-Scan) or [PII-Scan for Stata](https://github.com/J-PAL/stata_PII_scan) to get an idea of potential PII in your dataset.

> ⚠️ 📢 You remain ultimately responsible for ensuring that no **unauthorized** PII is included in the published replication package.


## Stated Requirements

> INSTRUCTIONS: The authors may have specified specific requirements in terms of software, computer hardware, etc. Please list them here. This is **different** from the Computing Environment of the Replicator. You have the option to amend these with unstated requirements later. If all requirements are listed, check the box "Requirements are complete".

- [ ] No requirements specified
- [ ] Operating system used:
  - [ ] Windows 10/11
  - [ ] MacOS
  - [ ] Linux
  - [ ] Windows Server
  - [ ] Not specified
- [ ] Software Requirements specified as follows:
  - Software 1
  - Software 2
- [ ] Computational Requirements specified as follows:
  - Memory (RAM), number of nodes in a cluster, use of parallel processing, disk space, etc.
- [ ] Time Requirements specified as follows:
  - Length of necessary computation (hours, weeks, etc.)

- [ ] Requirements are complete.

> INSTRUCTIONS: If the requirements are NOT complete, please leave this line in. If UNSURE, leave this line in:

For missing requirements, see the list of required changes in the **[FINDINGS](#findings)** section.

> INSTRUCTIONS: If easier, simply copy-and-paste the authors' stated requirements here:

---

## Code description

> INSTRUCTIONS: Review the code (but do not run it yet). Identify programs that create "analysis files" ("data preparation code"). Identify programs that create tables and figures. Not every deposit will have separate programs for this.

> INSTRUCTIONS: Identify all **Figure, Table, and any in-text numbers**. Create a list, mapping each of them to a particular program and line number within the program (use [this template](code-check.xlsx)). Commit that list. You will come back to the list in your findings. IN THIS SECTION, point out only a summary description, including of shortcomings. E.g.

> INSTRUCTIONS: For example, you could write "There are four provided Stata do files, three Matlab .m files, including a "master.do"."
> INSTRUCTIONS: And you could list the issues you encounter:
> INSTRUCTIONS: - Table 5: could not identify code that produces Table 5
> INSTRUCTIONS: - Neither the program codes, nor the README, identify which tables are produced by what program.

{{ programs-summary.txt }}

The full list of programs provided can be found in the Appendix.

> INSTRUCTIONS: Verify the appendix, the repository. If the list is missing, generate it by hand (instructions in the appendix).

- [ ] The replication package contains a "main" or "master" file(s) which calls all other auxiliary programs.

> INSTRUCTIONS: If the above checkbox for "main" file is NOT checked, leave the following SUGGESTION in the report!

> [SUGGESTED] We strongly advise the use of a single (or a small number of) main control file(s) to automatically reproduce all figures and tables in the paper, without manual interaction.

> NOTE: In-text numbers that reference numbers in tables do not need to be listed. Only in-text numbers that correspond to no table or figure need to be listed.


### Experimental/Survey instructions

> INSTRUCTIONS: This section is only relevant if the authors conducted a survey themselves, or ran an experiment themselves. If not, please delete this entire section (including the section title).

> INSTRUCTIONS: Check if the deposit contains the software/scripts to implement the experiment/survey. The README should point you at such steps. Sometimes, there may be an appendix that describes the survey. That is sufficient IF it also describes the actual computer files. Do check the manifest (`generated/manifest.txt`) for any such files. Qualtrics files end with `qsf`, other survey or experiment files may be specific types of Excel files, or Python code. Primarily, this should be OBVIOUS from the README.

> INSTRUCTIONS: We do not attempt to run such code or scripts ourselves, we only ensure that they are present. 

> INSTRUCTIONS: If none are present, then leave the following text in the report.

The deposit does not seem to contain the required software/scripts to implement the experiment/survey, though the appendix provides a complete verbose description thereof. As per the AEA's [Policy for Papers Conducting Experiments and Collecting Primary Data](https://www.aeaweb.org/journals/data/policy-experimental), please

> [REQUIRED] Provide any computer programs, configuration files, or scripts used to run the experiment or develop the survey instrument, e.g., z-Tree code, Qualtrics, SurveyCTO, and LimeSurvey.

> INSTRUCTIONS: If such files ARE present, then leave the following text in the report, and describe the files that are present.

The deposit contains the following software/scripts to implement the experiment/survey:

```
List the files here, with a brief description of each.
```

## Computing Environment of the Replicator

{{ sivacor-partb-computing-environment.md }}

## Replication steps

{{ sivacor-partb-replication-steps.md }}

> INSTRUCTIONS: provide details about your process of accessing the code and data.
> 
> - Do NOT detail things like "I save them on my Desktop".
> - DO describe actions that you did as per instructions ("I added a config.do")
> - DO describe any other actions you needed to do ("I had to make changes in multiple programs"), without going into TOO much detail. (Link to the log file in the JIRA comments of this case!)
> 
> BUT:
> 
> - DO provide ENOUGH detail so that an author, without access to the logs, can understand what needed to be fixed, including a copy-paste of the error message.
> - DO commit to git before EACH new run with corrected code.
> - DO (after all debugging is completed) a full run through the data, top-to-bottom, once all bugs are fixed, using the approriate method (command line or right-click).

> INSTRUCTIONS: ==>  Workflow stage: You are now going to *Writing Report*. Verify that both PartA and PartB have been completed.

## Findings

> INSTRUCTIONS: Describe your findings both positive and negative in some detail, for each **Data Preparation Code, Figure, Table, and any in-text numbers**. You can re-use the Excel file created under *Code Description*. When errors happen, be as precise as possible. For differences in figures, provide both a screenshot of what the manuscript contains, as well as the figure produced by the code you ran. For differences in numbers, provide both the number as reported in the manuscript, as well as the number replicated. If too many numbers, contact your supervisor.

> INSTRUCTIONS: Even when there is an external reproducibility report, summarize the findings here. 

{{ sivacor-partb-findings.md }}

### Missing Requirements

> INSTRUCTIONS: If the replication package contains Stata programs run `tools/Stata_scan_code/scan_packages.do`, ensuring that you update the global `codedir` first. If the data is accessible, add any packages not mentioned in the README to the `config.do` and paste the excel output as a table below. If the data is restricted-access and not obtainable in a reasonable amount of time, paste the excel output as a table below.

> INSTRUCTIONS: If it turns out that some requirements were not stated/ are incomplete (software, packages, operating system), please list (check) the *missing* list of requirements here. Remove lines that are not necessary. If the stated requirements are complete, delete this entire section, including the [REQUIRED] tag at the end, and replace with "None"

- [ ] Software Requirements 
  - [ ] Stata
    - [ ] Version
    - Packages go here
  - [ ] Matlab
    - [ ] Version
  - [ ] R
    - [ ] Version
    - R packages go here
  - [ ] Python
    - [ ] Version
    - Python package go here
  - [ ] REPLACE ME WITH OTHER
- [ ] Computational Requirements specified as follows:
  - Cluster size, disk size, memory size, etc.
- [ ] Time Requirements 
  - Length of necessary computation (hours, weeks, etc.)

> [REQUIRED] Please amend README to contain complete requirements. 

You can copy the section above, amended if necessary.


### Data Preparation Code

Examples:

- Program `1-create-data.do` ran without error, output expected data
- Program `2-create-appendix-data.do` failed to produce any output.

### Tables and Figures

> INSTRUCTIONS: Insert the filled-out `code-check.xlsx` here (complete the column `Reproduced?`), using the VS Code Plugins [Excel to Markdown table](https://marketplace.visualstudio.com/items?itemName=csholmq.excel-to-markdown-table). Then describe in more detail the issues that may have arisen.

Examples:

- Table 1: Looks the same
- Table 2: (contains no data)
- Table 3: Minor differences in row 5, column 3, 0.003 instead of 0.3

> INSTRUCTIONS: For tables, simple comparisons can be listed out as above. More complex differences can be described by using screenshots of the original table and the reproduced table, highlighting the differences.
 
> INSTRUCTIONS: Please provide a comparison with the paper when describing that figures look different. Use a screenshot for the paper, and the graph generated by the programs for the comparison. Reference the graph generated by the programs as a local file within the repository.

Example:

- Figure 1: Looks the same
- Figure 2: no program provided
- Figure 3: Paper version looks different from the one generated by programs:

Paper version:
![Paper version](template/dog.jpg)

Figure 3 generated by programs:

![Replicated version](template/odie.jpg)

### In-Text Numbers

> INSTRUCTIONS: list page and line number of in-text numbers. If ambiguous, cite the surrounding text, i.e., "the rate fell to 52% of all jobs: verified".

[ ] In-text numbers not verified.

[ ] There are no in-text numbers, or all in-text numbers stem from tables and figures.

[ ] There are in-text numbers, but they are not identified in the code

- Page 21, line 5: Same


## Classification

> INSTRUCTIONS: Make an assessment here.
>
> Full reproduction can include a small number of apparently insignificant changes in the numbers in the table. Full reproduction also applies when changes to the programs needed to be made, but were successfully implemented.
>
> Partial reproduction means that a significant number (>25%) of programs and/or numbers are different.
>
> Note that if some data is confidential and not available, then a partial reproduction applies. This should be noted in the Reasons.
>
> Note that when all data is confidential, it is unlikely that this exercise should have been attempted.
>
> Failure to reproduce: only a small number of programs ran successfully, or only a small number of numbers were successfully generated (<25%). This also applies when all data is restricted-access and none of the **main** tables/figures are run.

- [ ] full reproduction
- [ ] full reproduction with minor issues
- [ ] partial reproduction (see above)
- [ ] not able to reproduce most or all of the results (reasons see above)

### Reason for incomplete reproducibility

> INSTRUCTIONS: mark the reasons here why full reproduciblity was not achieved, and enter this information in JIRA. When results are fully reproduced, leave this section here, and mark "None".

- [ ] None.
- [ ] `Discrepancy in output` (either figures or numbers in tables or text differ)
- [ ] `Bugs in code` that were fixable by the replicator (but should be fixed in the final deposit)
- [ ] `Code missing`, in particular if it prevented the replicator from completing the reproducibility check
  - [ ] `Data preparation code missing` should be checked if the code missing seems to be data preparation code
- [ ] `Code not functional` is more severe than a simple bug: it prevented the replicator from completing the reproducibility check
- [ ] `Software not available to replicator` may happen for a variety of reasons, but in particular (a) when the software is commercial, and the replicator does not have access to a licensed copy, or (b) the software is open-source, but a specific version required to conduct the reproducibility check is not available.
- [ ] `Insufficient time available to replicator` is applicable when (a) running the code would take weeks or more, even on the best of computers (b)  the replication package is very complex, and following all (manual and scripted) steps would take too long.
- [ ] `Insufficient computing resources available to replicator` is applicable when (a)  running the code might take less time if sufficient compute resources were to be brought to bear, but no such resources can be accessed in a timely fashion (b) running the code is not possible on any of the accessible computing resources, or would take more than a trivial amount of money to procure (i.e., AWS or Google Cloud).
- [ ] `Data missing` is marked when data *should* be available, but was erroneously not provided, or is not accessible via the procedures described in the replication package
- [ ] `Data not available` is marked when data requires additional access steps, for instance purchase or application procedure. 
- [ ] `Missing README` is marked if there is no README to guide the replicator, or the README is not in compliance with AEA requirements



> INSTRUCTIONS: ==>  Workflow stage: You are now going from *Writing Report* to *Submitting Report*!

---
