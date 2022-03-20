# YoLinkAPI_V2

## Install required python packages.

```bash
python3 -m pip install -r requirements.txt
```

## Obtain Managed Device Info and Home ID

This is a one time deal or whenever new device is added.<br>
Once you have optain your device info, note the Home ID<br>
and copy the list of JSON objects with all the device data<br>
into yolink_data.json config file.

```bash
PYTHONPATH=<path_to/YoLinkAPI_V2/src> python3 yolink_utils.py \
    --config YoLinkAPI_V2/src/utils/yolink_data.json --devices
```

## YoLink Devices MQTT

Run the following command to start yolink MQTT subscriber.


```bash
python3 src/yolinkv2.py --config src/yolink_data.local.json --debug
```
