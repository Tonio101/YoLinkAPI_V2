# YoLinkAPI_V2

Simple program to get data from YoLink sensors via APIv2.<br>
Extend and add whatever you need to do with the sensor data<br>
in the `process` function of each device type.<br>

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
cd <your_path>/YoLinkAPI_V2/src/utils
PYTHONPATH=<path_to/YoLinkAPI_V2/src> python3 yolink_utils.py \
    --config YoLinkAPI_V2/src/utils/yolink_data.json --devices
```

Example of data to copy in the `"deviceInfo": []` (`yolink_data.json`):<br>
```bash
"deviceInfo": [
    {
        "deviceId": "XXXXXXXXXXXXXXXX",
        "deviceUDID": "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
        "name": "Device Name",
        "token": "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
        "type": "DoorSensor"
    },
    {...},
    {...},
    ...
]
```

## YoLink Devices MQTT

Run the following command to start yolink MQTT subscriber.

```bash
cd <your_path>/YoLinkAPI_V2
python3 src/yolinkv2.py --config src/yolink_data.json --debug
```
