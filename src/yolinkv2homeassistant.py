#!/usr/bin/env python3
import argparse
import json
import logging
import os
import queue
import sys

from time import sleep
from models.yolink_token import YoLinkToken
from models.yolink_devices import YoLinkFactory
from models.yolink_consumer import YoLinkConsumer
from models.influxdb_interface import InfluxDbClient
from models.yolink_mqtt_client import YoLinkMQTTClient, MQTTClient
from models.logger import Logger
log = Logger.getInstance().getLogger()

Q_SIZE = 32


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
                InfluxDbClient(url=influxdb_info['url'],
                               auth=(influxdb_info['auth']['user'],
                                     influxdb_info['auth']['pasw']),
                               db_name=influxdb_info['dbName'],
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
        MQTTClient(username=config['mqttProducer']['user'],
                   password=config['mqttProducer']['pasw'],
                   mqtt_host=config['mqttProducer']['host'],
                   mqtt_port=config['mqttProducer']['port'])
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
    log.debug(config)
    yolinkconf = config['yoLink']
    localMqttEnabled = config['features']['localMQTT']
    influxDbEnabled = config['features']['influxDB']

    yolink_token = \
        YoLinkToken(url=yolinkconf['apiv2']['tokenUrl'],
                    ua_id=yolinkconf['apiv2']['uaId'],
                    sec_id=yolinkconf['apiv2']['secId'])
    acces_token = yolink_token.get_access_token()
    log.debug(acces_token)

    device_hash = dict()
    yolink_device = None

    for device in yolinkconf['deviceInfo']:
        log.debug("{} {}".format(
            device['type'],
            device['name']
        ))
        yolink_device = YoLinkFactory(device['type'], device)
        device_hash[yolink_device.get_id()] = yolink_device

    if influxDbEnabled:
        configure_influxdb_devices(device_hash, config)
    if localMqttEnabled:
        configure_local_mqtt_server(device_hash, config)

    log.debug(device_hash)
    output_q = queue.Queue(maxsize=Q_SIZE)
    consumer = YoLinkConsumer(name='consumer',
                              args=(output_q, device_hash,))
    consumer.start()
    sleep(1)

    mqtt_topic = yolinkconf['apiv2']['mqtt']['topic'].format(
        yolinkconf['yolinkHomeId']
    )
    yolink_mqtt_server = \
        YoLinkMQTTClient(username=acces_token,
                         passwd=None,
                         topic=mqtt_topic,
                         mqtt_url=yolinkconf['apiv2']['mqtt']['url'],
                         mqtt_port=yolinkconf['apiv2']['mqtt']['port'],
                         device_hash=device_hash,
                         output_q=output_q,
                         yolink_token=yolink_token)
    yolink_mqtt_server.connect_to_broker()


if __name__ == '__main__':
    main(sys.argv)
