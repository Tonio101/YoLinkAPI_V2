import argparse
import json
import logging
import os
import sys

from yolink_token import YoLinkToken
from yolink_consumer import YoLinkApi

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger()


def parse_config_file(fname) -> dict:
    with open(os.path.abspath(fname), 'r') as fp:
        data = json.load(fp)
        return data


def main(args):
    usage = ("{FILE} --config <config_file> "
             "--devices").format(FILE=__file__)
    description = 'YoLink API utility script'
    parser = argparse.ArgumentParser(usage=usage, description=description)
    parser.add_argument("-c", "--config", help="Configuration file",
                        required=True)
    parser.add_argument("--devices", help="List managed devices",
                        action='store_true', required=False)

    parser.set_defaults(devices=False)

    args = parser.parse_args()
    config = parse_config_file(args.config)

    if args.devices:
        yolinkapi_config = config['yoLink']['apiv2']

        yolink_token = \
            YoLinkToken(url=yolinkapi_config['tokenUrl'],
                        ua_id=yolinkapi_config['uaId'],
                        sec_id=yolinkapi_config['secId'])
        token = yolink_token.get_access_token()
        log.info(yolink_token)

        yolink_api = YoLinkApi(api_url=yolinkapi_config['apiUrl'],
                               access_token=token)
        devices = yolink_api.get_all_devices()
        for device in devices:
            log.info("{}".format(json.dumps(device, indent=2)))

        home_id = yolink_api.get_home_id()
        log.info("Home ID: {}".format(home_id))


if __name__ == '__main__':
    main(sys.argv)
