#!/bin/bash
#set -ev

# Get some functions

. ./tools/parse_yaml.sh

# read parameters
eval $(parse_yaml config.yml)

# from environment
#          - name: openICPSRID   
#          - name: ZenodoID
#          - name: DataverseID
#          - name: OSFID

# environment overwrite config

openICPSRID="${openICPSRID:-$openicpsr}"
ZenodoID="${ZenodoID:-$zenodo}"
DataverseID="${DataverseID:-$dataverse}"
OSFID="${OSFID:-$osf}"
MainFile="${MainFile:-$main}"

# write it back
config=config.yml

sed -i "s/openicpsr: \(.*\)/openicpsr: $openICPSRID/" $config
sed -i "s/osf: \(.*\)/osf: $OSFID/" $config
sed -i "s/dataverse: \(.*\)/dataverse: $DataverseID/" $config
sed -i "s/zenodo: \(.*\)/zenodo: $ZenodoID/" $config
sed -i "s/main: \(.*\)/main: $MainFile/" $config  

cat $config
