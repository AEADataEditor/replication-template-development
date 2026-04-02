#!/bin/bash
#set -ev

# Get some functions

. ./tools/parse_yaml.sh

# Check for config.yml

if [ ! -f config.yml ]; then
    # see if the template is there
    if [ -f template/new-config.yml ]; then
        cp template/new-config.yml config.yml
    else
      echo "config.yml not found!"
      exit 1
    fi
fi

# Save pipeline-provided values before eval overwrites them.
# config.yml and pipeline vars share the same key name for jiraticket, so
# eval $(parse_yaml ...) silently clobbers the pipeline/environment variable.
_env_jiraticket="${jiraticket:-}"

# read parameters
eval $(parse_yaml config.yml)

# from environment
#          - name: openICPSRID
#          - name: jiraticket
#          - name: ZenodoID
#          - name: DataverseID
#          - name: OSFID
#          - name: main
#          - name: mcid

# environment overwrite config

openICPSRID="${openICPSRID:-$openicpsr}"
ZenodoID="${ZenodoID:-$zenodo}"
DataverseID="${DataverseID:-$dataverse}"
OSFID="${OSFID:-$osf}"
MainFile="${MainFile:-$main}"
# Restore pipeline/environment value if it was set; otherwise keep config.yml value
jiraticket="${_env_jiraticket:-$jiraticket}"
mcid="${mcid:-$mcid}"

# write it back
config=config.yml

sed -i "s/openicpsr: \(.*\)/openicpsr: $openICPSRID/" $config
sed -i "s/osf: \(.*\)/osf: $OSFID/" $config
sed -i "s/dataverse: \(.*\)/dataverse: $DataverseID/" $config
sed -i "s/zenodo: \(.*\)/zenodo: $ZenodoID/" $config
sed -i "s/main: \(.*\)/main: $MainFile/" $config
sed -i "s/jiraticket: \(.*\)/jiraticket: $jiraticket/" $config
sed -i "s/mcid: \(.*\)/mcid: $mcid/" $config  

cat $config
