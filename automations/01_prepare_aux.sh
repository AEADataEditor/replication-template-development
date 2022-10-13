#!/bin/bash
set -ev
if [ ! -d aux ] 
then 
  mkdir aux
fi

if [ ! -f aux/README.txt ]
then
    echo "This directory contains information generated automatically" > aux/README.txt
    echo "-- Do not modify --" >> aux/README.txt
fi
ls -lR