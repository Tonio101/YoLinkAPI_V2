# YoLinkAPI_V2

## Description

YoLink client using the Version 2 of the API.

## Install required python packages.

```bash
python3 -m pip install -r requirements.txt
```

## YoLink Devices MQTT

First ensure that you can run the standalone YoLink script.
If that succeeds, proceed to docker if you want.

You will need YoLink account secrets:
    - UA ID
    - SEC ID

Populate the `yolink_config.json` with your credentials.

```bash
cd <your_path>/YoLinkAPI_V2/src
python3 main.py --config yolink_config.json --debug
```

## Run in Docker Container

Assuming that you already have Docker setup.

Build the docker image
```bash
./build_docker_image.sh
```

Like previously mentioned, you will need to provide
UA ID and SEC ID to your config file.

Start docker container
```bash
./start_docker_container.sh <PATH_TO_YOUR_CONFIG_FILE>
```

## Systemd Service

Modify the paths `start_yolinkv2.sh` script to match your environment.

```bash
sudo cp yolinkv2ha.service /etc/systemd/system/
sudo systemctl enable yolinkv2ha.service
sudo systemctl start yolinkv2ha.service
sudo systemctl status yolinkv2ha.service
```

## (Optional) Obtain Managed Device Info and Home ID

Utility script to obtain all the devices linked
to your account as well as the home id.
This step can be completely ignored.

Only if you are interested in seeing what devices
are linked to your YoLink account.

```bash
cd <your_path>/YoLinkAPI_V2/src/utils
PYTHONPATH=<path_to>/YoLinkAPI_V2/src \
    python3 yolink_utils.py \
    --config yolink_config.json \
    --devices
```