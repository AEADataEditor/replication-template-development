%%% This template file should be copied to the root of the Matlab 
%%% codes of the author, and renamed to "config.m"
%%%


%%% This sets the directory structure type
%%% /* Structure of the code, two scenarios:
%%%    - Code looks like this (simplified, Scenario A)
%%%          directory/
%%%               code/
%%%                  main.m
%%%                  01_dosomething.m
%%%               data/
%%%                  data.dta
%%%                  otherdata.dta
%%%    - Code looks like this (simplified, Scenario B)
%%%          directory/
%%%                main.m
%%%                scripts/
%%%                    01_dosomething.m
%%%                 data/
%%%                    data.dta
%%%                    otherdata.dta
%%%     For the variable "scenario" below, choose "A" or "B". It defaults to "A".
%%% 
%%%     NOTE: you should always put "config.do" in the same directory as "main.m"
%%% */

scenario = "A"

%%% this dynamically captures the rootdir

[mydir, thisFileName, ~ ] = fileparts(mfilename('fullpath'))

if ~exist('configdone','var')
% do initial config
    if scenario == "A"
        cd ..
        rootdir = pwd
        cd(mydir)
    else
        rootdir = mydir
    end
    configdone = 'TRUE'
end

%%% This captures the version of Matlab and its installed toolboxes.

ver

%%% Any mention elsewhere of hard-coded paths should now be replaced by fullfile(rootdir,'name of file')

% datadir = "../../empirics"
datadir = fullfile(rootdir,"data")

% results = "../results"
% results = "/results" %% if running on Codeocean
