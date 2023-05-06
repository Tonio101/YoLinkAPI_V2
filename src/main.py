import argparse
import json
import logging
import os
import queue
import sys

from time import sleep
from yolink_token import YoLinkToken
from yolink_devices import YoLinkFactory
from yolink_consumer import YoLinkConsumer, YoLinkApi
from influxdb_interface import InfluxDbClient
from yolink_mqtt_client import YoLinkMqttClient, MqttClient
from logger import Logger
log = Logger.getInstance().getLogger()

Q_SIZE = 64


def parse_config_file(fname: str) -> dict:
    """
    Parse Config File.

    Args:
        fname (string): yolink_data.json config file.

    Returns:
        dict: A dict with all the config data.
    """
    with open(os.path.abspath(fname), 'r') as fp:
        data = json.load(fp)
        return data


def configure_influxdb_devices(device_hash, config):
    """
    Configure influx db devices.

    Args:
        device_hash (map): Device hash map.
        config (map): Config hash map.
    """
    influxdb_info = config['influxdb']
    if len(influxdb_info['sensors']) == 0:
        log.debug("No sensors are configured for influx db")
        return

    for sensor in influxdb_info['sensors']:
        device_id = sensor['deviceId']
        if device_id in device_hash:
            client = \
                InfluxDbClient(config=influxdb_info,
                               measurement=sensor['measurement'],
                               tag_set=sensor['tagSet'])
            device_hash[device_id].set_influxdb_client(client)


def configure_local_mqtt_server(device_hash, config):
    """
    Need to publish to another broker to distinguish between
    each of the YoLink devices. All YoLink devices publish
    to the same topic (CSName/report)

    Args:
        device_hash (map): Device hash map.
        config (map): Config hash map.
    """
    mqtt_server = \
        MqttClient(config=config['mqttBroker'])

    mqtt_server.connect_to_broker()

    for deviceid in device_hash:
        device_hash[deviceid].set_mqtt_server(mqtt_server)


def main(argv):
    usage = ("{FILE} --config <config_file> --debug").format(FILE=__file__)
    description = 'YoLink Device API Sensor Data'
    parser = argparse.ArgumentParser(usage=usage, description=description)
    parser.add_argument("-c", "--config", help="Configuration file",
                        required=True)
    parser.add_argument("--debug", help="Enable verbose logging",
                        action='store_true', required=False)
    parser.set_defaults(debug=False)

    args = parser.parse_args()

    if args.debug:
        log.setLevel(logging.DEBUG)

    config = parse_config_file(args.config)
    yolinkv2_config = config['yoLink']['apiv2']
    localMqttEnabled = config['features']['localMQTT']
    influxDbEnabled = config['features']['influxDB']

    yolink_token = \
        YoLinkToken(url=yolinkv2_config['tokenUrl'],
                    ua_id=yolinkv2_config['uaId'],
                    sec_id=yolinkv2_config['secId'])
    access_token = yolink_token.get_access_token()
    log.debug(access_token)

    yolink_api = \
        YoLinkApi(api_url=yolinkv2_config['apiUrl'],
                  access_token=access_token)
    devices = yolink_api.get_all_devices()
    home_id = yolink_api.get_home_id()

    device_hash = dict()
    yolink_device = None

    for device in devices:
        device_type = device['type']
        device_name = device['name']
        log.debug("{} {}".format(
            device_type,
            device_name
        ))

        if (device_type == 'Hub' or device_type == 'Siren'):
            continue

        yolink_device = YoLinkFactory(device_type, device)
        device_hash[yolink_device.get_id()] = yolink_device

    if influxDbEnabled:
        log.info("Influx DB Enabled")
        configure_influxdb_devices(device_hash, config)
    if localMqttEnabled:
        log.info("MQTT Broker Enabled")
        configure_local_mqtt_server(device_hash, config)

    log.debug(device_hash)
    output_q = queue.Queue(maxsize=Q_SIZE)
    consumer = YoLinkConsumer(name='consumer',
                              args=(output_q, device_hash,))
    consumer.start()
    sleep(1)

    mqtt_topic = \
        yolinkv2_config['mqtt']['topic'].format(home_id)

    yolink_mqtt_server = \
        YoLinkMqttClient(username=access_token,
                         passwd=None,
                         topic=mqtt_topic,
                         mqtt_url=yolinkv2_config['mqtt']['url'],
                         mqtt_port=yolinkv2_config['mqtt']['port'],
                         device_hash=device_hash,
                         output_q=output_q,
                         yolink_token=yolink_token)
    yolink_mqtt_server.connect_to_broker()


if __name__ == '__main__':
    main(sys.argv)
