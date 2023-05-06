# YoLinkAPI_V2

## Description

YoLink client using the Version 2 of the API.

## Install required python packages.

```bash
python3 -m pip install -r requirements.txt
```

## YoLink Devices MQTT

Run the following command to start YoLink MQTT subscriber.

```bash
cd <your_path>/YoLinkAPI_V2
python3 src/main.py --config src/yolink_data.json --debug
```

## Create Docker Image

Assuming that you already have Docker setup.
Modify the Dockerfile to match your config file.

Build the docker image
```bash
./build_docker_image.sh
```

Start docker container
```bash
./start_docker_container.sh
```

## Obtain Managed Device Info and Home ID

Utility script to obtain all the devices linked
to your account as well as the home id

```bash
cd <your_path>/YoLinkAPI_V2/src/utils
PYTHONPATH=<path_to>/YoLinkAPI_V2/src python3 yolink_utils.py \
    --config yolink_data.json --devices
```