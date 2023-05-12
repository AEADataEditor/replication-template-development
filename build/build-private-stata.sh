#!/bin/bash

[[ -z $1 ]] && TAG=$(date +%F) || TAG=$1
MYHUBID=larsvilhuber
MYIMG=bitbucket-stata

[ -f /usr/local/stata17/stata.lic ] && cp /usr/local/stata17/stata.lic .
[ -f ./stata.lic ] || echo "$STATA_LIC_BASE64" | base64 -d > ./stata.lic

cp ../requirements.txt .

DOCKER_BUILDKIT=1 docker build  . \
  -t $MYHUBID/${MYIMG}:$TAG \
  -f Dockerfile.stata

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
