#!/bin/bash

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
\rm -rf replication-template-master tmp.tar master.zip
