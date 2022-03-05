import argparse
import json
import logging
import os
import requests
import sys
import time

from models.yolink_token import YoLinkToken

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger()


def parse_config_file(fname) -> dict:
    """

    Args:
        fname (_type_): _description_

    Returns:
        dict: _description_
    """
    with open(os.path.abspath(fname), 'r') as fp:
        data = json.load(fp)
        return data


def get_all_devices(apiUrl: str, access_token: str) -> dict:
    """_summary_

    Args:
        apiUrl (str): _description_
        access_token (str): _description_

    Returns:
        dict: _description_
    """
    data = dict()
    headers = dict()

    headers['Content-type'] = 'application/json'
    headers['Authorization'] = 'Bearer ' + access_token

    data['method'] = 'Home.getDeviceList'
    data['time'] = str(int(time.time()*1000))

    r = requests.post(apiUrl, data=json.dumps(data), headers=headers)

    if r.status_code != 200:
        log.error("Failed to get device list")
        return {}

    info = r.json()

    if info['data'] and 'devices' in info['data']:
        return info['data']['devices']

    return {}


def get_home_id(apiUrl: str, access_token: str) -> str:
    """_summary_

    Args:
        apiUrl (str): _description_
        access_token (str): _description_

    Returns:
        str: _description_
    """
    data = dict()
    headers = dict()

    headers['Content-type'] = 'application/json'
    headers['Authorization'] = 'Bearer ' + access_token

    data['method'] = 'Home.getGeneralInfo'
    data['time'] = str(int(time.time()*1000))

    r = requests.post(apiUrl, data=json.dumps(data), headers=headers)
    if r.status_code != 200:
        log.error("Failed to get device list")
        return ""

    info = r.json()
    if ('code' in info and info['code'] != '000000'):
        log.error("Failed to get device list")
        return ""

    log.info(info)
    return info['data']['id']


def main(args):
    usage = ("{FILE} --config --devices --debug").format(FILE=__file__)
    description = 'YoLink API utility script'
    parser = argparse.ArgumentParser(usage=usage, description=description)

    parser.add_argument("-c", "--config", help="Configuration file",
                        required=True)
    parser.add_argument("--devices", help="List managed devices",
                        action='store_true', required=False)

    parser.set_defaults(devices=False, debug=False)

    args = parser.parse_args()
    log.debug("{0}\n".format(args))
    config = parse_config_file(args.config)
    log.debug(config)

    if args.devices:
        yolink_token = \
            YoLinkToken(url=config['yoLink']['apiv2']['tokenUrl'],
                        ua_id=config['yoLink']['apiv2']['uaId'],
                        sec_id=config['yoLink']['apiv2']['secId'])
        token = yolink_token.get_access_token()
        log.debug(yolink_token)

        devices = get_all_devices(apiUrl=config['yoLink']['apiv2']['apiUrl'],
                                  access_token=token)
        for device in devices:
            log.info(device)

        home_id = get_home_id(apiUrl=config['yoLink']['apiv2']['apiUrl'],
                              access_token=token)
        log.info("Home ID: {}".format(home_id))


if __name__ == '__main__':
    main(sys.argv)
