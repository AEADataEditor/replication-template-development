#!/bin/bash
# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022-2024 Lars Vilhuber and contributors.
# Author(s): Lars Vilhuber
# Licensed under the BSD 3-Clause License; see the LICENSE file at the repository root.

[[ -z $1 ]] && TAG=$(date +%F) || TAG=$1
MYHUBID=aeadataeditor
MYIMG=verification-r

cp ../tools/install.R .
cp ../requirements.txt .

DOCKER_BUILDKIT=1 docker build  . \
  -f Dockerfile-r \
  -t $MYHUBID/${MYIMG}:$TAG

echo "Ready to push?"
echo "  docker push  $MYHUBID/${MYIMG}:$TAG"
read answer
case $answer in 
   y|Y)
   docker push  $MYHUBID/${MYIMG}:$TAG
   ;;
   *)
   exit 0
   ;;
esac

docker tag $MYHUBID/${MYIMG}:$TAG $MYHUBID/${MYIMG}:latest
docker push $MYHUBID/${MYIMG}:latest
