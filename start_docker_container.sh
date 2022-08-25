#!/bin/bash

IMAGE_ID=$1
docker run -d --network=host --restart on-failure:5 ${IMAGE_ID}
