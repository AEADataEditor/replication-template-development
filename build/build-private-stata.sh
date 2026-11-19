#!/bin/bash
# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022-2026 Lars Vilhuber and contributors.
# Author(s): Lars Vilhuber
# Licensed under the BSD 3-Clause License; see the LICENSE file at the repository root.

[[ -z $1 ]] && TAG=$(date +%F) || TAG=$1
MYHUBID=larsvilhuber
MYIMG=bitbucket-stata
STATAVERSION=now19

[ -f /usr/local/stata$STATAVERSION/stata.lic ] && cp /usr/local/stata$STATAVERSION/stata.lic .
[ -f ./stata.lic ] || echo "$STATA_LIC_BASE64" | base64 -d > ./stata.lic

cp ../requirements.txt .

DOCKER_BUILDKIT=1 docker build  . \
  --build-arg PYTHON_VERSION=3 \
  -t $MYHUBID/${MYIMG}:$TAG \
  -f Dockerfile.stata \
  --no-cache

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
