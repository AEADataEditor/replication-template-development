#!/bin/bash

# Tested on openSUSE

cat /etc/*release | grep PRETTY_NAME
cat /proc/cpuinfo | grep "model name" | awk -F: ' { sum+=1; model=$2 } END { print $2 ", " sum " cores" }
free -g | grep Mem | awk ' { print $2 "GB memory" } '