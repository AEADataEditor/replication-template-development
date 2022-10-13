#!/bin/bash

[[ -z $1 ]] && TAG=$(date +%F) || TAG=$1
MYHUBID=aeadataeditor
MYIMG=verification-r

cp ../tools/install.R .

DOCKER_BUILDKIT=1 docker build  . \
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
