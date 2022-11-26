#!/bin/bash

IMAGE_TAG=yolinkv2ha
IMAGE_ID=$(docker images -q $IMAGE_TAG)

docker run -d --network=host --name yolinkv2 --restart=on-failure ${IMAGE_ID}
