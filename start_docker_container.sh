#!/bin/bash

IMAGE_TAG=yolinkv2ha
IMAGE_ID=$(docker images -q $IMAGE_TAG)


docker run -d --network=host --restart=on-failure:5 ${IMAGE_ID}
