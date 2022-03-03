import argparse
import json
import os
import sys

from logging import DEBUG
from logger import Logger
from models.yolink_token import YoLinkToken

log = Logger.getInstance(name='yolink_utils',
                         fname='/tmp/yolink_utils.log').getLogger()


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


def main(args):
    usage = ("{FILE} --config --devices --debug").format(FILE=__file__)
    description = 'YoLink API utility script'
    parser = argparse.ArgumentParser(usage=usage, description=description)

    parser.add_argument("-c", "--config", help="Configuration file",
                        required=True)
    parser.add_argument("--devices", help="List managed devices",
                        action='store_true', required=False)
    parser.add_argument("-d", "--debug", help="Debug",
                        action='store_true', required=False)

    parser.set_defaults(devices=False, debug=False)

    args = parser.parse_args()

    if args.debug:
        log.setLevel(DEBUG)

    log.debug("{0}\n".format(args))

    config = parse_config_file(args.config)
    log.debug(config)
    yolink_token = \
        YoLinkToken(url=config['yoLink']['apiv2']['tokenUrl'],
                    ua_id=config['yoLink']['apiv2']['uaId'],
                    sec_id=config['yoLink']['apiv2']['secId'])
    token = yolink_token.get_access_token()
    log.debug(yolink_token)
    log.debug(token)
    token = yolink_token.renew_token()
    log.debug(yolink_token)
    log.debug(token)


if __name__ == '__main__':
    main(sys.argv)
