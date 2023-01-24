#!/bin/bash

# This script is part of replication-template/tools.
# It can also be manually invoked by running
#   wget -O - https://raw.githubusercontent.com/AEADataEditor/replication-template/master/tools/update_tools.sh | bash -x
# NOTE: in order to do that, you have to trust what I've put together here!

wget -O master.zip https://github.com/AEADataEditor/replication-template/archive/refs/heads/master.zip
unzip master.zip 
cd replication-template-master
[[ -f config.yml ]] && mv config.yml config-template.yml
tar cvf ../tmp.tar tools/ automations/ *.yml template-* requirements.txt
cd ..
tar xvf tmp.tar
git add tools/ automations/ *.yml template-* 
git add -f requirements.txt
git commit -m '[skip ci] Update of tools'
case $? in
     0)
     echo "Code added"
     ;;
     1)
     echo "No changes detected"
     ;;
     *)
     echo "Not sure how we got here"
     ;;
  esac
\rm -rf replication-template-master tmp.tar master.zip
exit 0

