#!/bin/bash

LOCAL_CONFIG_FILE=$1

# Check if the argument is not null or empty
if [[ -n "$LOCAL_CONFIG_FILE" ]]; then
    if [[ -f "$LOCAL_CONFIG_FILE" ]]; then
        echo "Config file: $LOCAL_CONFIG_FILE"
    else
        echo "$LOCAL_CONFIG_FILE does not exist."
        exit 1
    fi
else
    echo "Must provide config file"
    exit 2
fi

IMAGE_TAG=yolinkv2ha
IMAGE_ID=$(docker images -q $IMAGE_TAG)

docker run -d \
    -v $LOCAL_CONFIG_FILE:/app/yolink_config.json \
    --network=host --name yolinkv2 \
    --restart=on-failure ${IMAGE_ID}
