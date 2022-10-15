#!/bin/bash

# will run the Stata code scanner on the ICPSR directory
# invoke from root of repository

rootdir=$(pwd)
icpsrdir=$1

[[ -z $icpsrdir ]] && icpsrdir=$(ls -1d *| grep -E "^[1-9][0-9][0-9][0-9][0-9][0-9]$")
if [[ -d $icpsrdir ]]
then 
   echo "Found $icpsrdir - processing."
else
   echo "$icpsrdir is not a directory - don't know what to do"
   exit 2
fi

SOFTWARE=stata
VERSION=17
TAG=2022-01-17
MYHUBID=dataeditors
MYNAME=${SOFTWARE}${VERSION}
MYIMG=$MYHUBID/${MYNAME}:${TAG}
# this probably only works for Lars
[[ -z $STATALIC && -z $CI ]] && STATALIC=$(find $HOME/Dropbox/ -name stata.lic.$VERSION| tail -1)


if [[ -z $STATALIC && -z $CI ]]
then
	echo "Could not find Stata license"
	grep STATALIC $0
	exit 2
fi

# modify the scan code

cd tools/Stata_scan_code
#sed -i "s+XXXCODEDIRXXX+../../$icpsrdir+" scan_packages.do

if [ "$CI" == "true" ]
then
# we run without Docker call, because we are inside Docker
  stata-mp -q -b scan_packages.do ../../$icpsrdir
else
  # now run it with the Docker Stata
  docker run -it --rm \
    -v "${STATALIC}":/usr/local/stata/stata.lic \
    -v "$rootdir":/project \
    -w /project/tools/Stata_scan_code \
    $MYIMG -q -b scan_packages.do ../../$icpsrdir

  cd $rootdir
  git add tools/Stata_scan_code/scan_packages.*
  [[ -f $icpsrdir/candidatepackages.xlsx ]] && git add $icpsrdir/candidatepackages.xlsx
fi
# clean up




