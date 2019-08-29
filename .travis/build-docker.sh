#!/bin/bash

TAG="${TRAVIS_BRANCH//\//_}"

ORG=`echo $DOCKER_PROJECT | tr '[:upper:]' '[:lower:]'`
ORG="${ORG:+${ORG}/}"
IMAGE="${ORG}influxdb"
TIMESTAMP=`date +'%y%m%d%H'`
GITHASH=`git log -1 --pretty=format:"%h"`

BUILD_VERSION="${TIMESTAMP}_${GITHASH}${TRAVIS_BRANCH:+:$TRAVIS_BRANCH}"
echo "BUILD_VERSION $BUILD_VERSION"

docker pull influxdb:latest

# Pass tag to docker-compose
docker build --build-arg TIMESTAMP="${BUILD_VERSION}" -t ${IMAGE}:build .
status=$?
if [ $status -ne 0 ]; then
  echo "Error: status $status"
  exit 1
fi

echo " "
echo "Running the build container to load the data"

# start influxdb with the proper conf file
#did=`docker run --rm -d -p 8086:8086 -v $( pwd )/timeseries:/tmp/timeseries ${IMAGE}:build`
did=`docker run --rm -d -p 8086:8086 ${IMAGE}:build`
status=$?

echo "$did $status"

if [ "$status" -gt 0 ]; then
  echo " "
  echo "Error starting container"
  echo "Exiting "
  exit 1
fi

#allow the database to come up
sleep 10

curl -sl -I http://localhost:8086/ping
status=$?
if [ $status -ne 0 ]; then
  echo "Error: influxdb ping status $status"
  exit 1
fi

echo " "
echo "Importing data"
docker exec -it $did /bin/bash -c "influx -import -path=/tmp/ghi_dhi_bulkload.txt -precision s"
status=$?
if [ $status -ne 0 ]; then
  echo "Error: influxdb ping status $status"
  exit 1
fi

echo " "
echo "Commiting changes to image ${IMAGE}:${TIMESTAMP}_${GITHASH}"
docker commit $did ${IMAGE}:${TIMESTAMP}_${GITHASH}
status=$?
if [ $status -ne 0 ]; then
  echo "Error: commit status $status"
  exit 1
fi

echo " "
echo "Stop build container"
docker stop $did
status=$?
if [ $status -ne 0 ]; then
  echo "Error: stop status $status"
  exit 1
fi

echo " "
echo "Remove the build container"
docker rmi ${IMAGE}:build
status=$?
if [ $status -ne 0 ]; then
  echo "Error: stop status $status"
  exit 1
fi


# To have `DOCKER_USERNAME` and `DOCKER_PASSWORD`
# filled you need to either use `travis`' cli
# (https://github.com/travis-ci/travis.rb)
# and then `travis set ..` or go to the travis
# page of your repository and then change the
# environment in the settings pannel.

if [ -n "$DOCKER_USERNAME" -a -n "$DOCKER_PASSWORD" ]; then

  echo " "
  echo "Connecting to docker"

  echo $DOCKER_PASSWORD | docker login -u $DOCKER_USERNAME --password-stdin
  status=$?
  if [ $status -ne 0 ]; then
    echo "Error: status $status"
    exit 1
  fi

  if [ -n "$TAG" -a -n "$ORG" ]; then
    # Get the built container name
    CONTAINER=`docker images --format "{{.Repository}}:{{.Tag}}" ${IMAGE}`

    echo "docker push ${CONTAINER}"
    docker push "${CONTAINER}"
    status=$?
    if [ $status -ne 0 ]; then
      echo "Error: status $status"
      exit 1
    fi

    echo "docker tag ${CONTAINER} ${IMAGE}:$TAG"
    docker tag ${CONTAINER} ${IMAGE}:$TAG
    status=$?
    if [ $status -ne 0 ]; then
      echo "Error: status $status"
      exit 1
    fi

    echo "docker push ${IMAGE}:$TAG"
    docker push ${IMAGE}:$TAG
    status=$?
    if [ $status -ne 0 ]; then
      echo "Error: status $status"
      exit 1
    fi
  fi

fi
