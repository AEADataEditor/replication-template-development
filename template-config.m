%%% This template file should be copied to the root of the Matlab 
%%% codes of the author, and renamed to "config.m"
%%%

%%% This captures the version of Matlab and its installed toolboxes.

ver

%%% this dynamically captures the rootdir

[rootdir, thisFileName, ~ ] = fileparts(mfilename('fullpath'))

%%% Any mention elsewhere of hard-coded paths should now be replaced by fullfile(rootdir,'name of file')

