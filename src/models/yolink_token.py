import requests
import time

from logger import Logger
log = Logger.getInstance(name='yolink_utils',
                         fname='/tmp/yolink_utils.log').getLogger()

EXPIRES_IN_BUFFER = 60 * 10


class YoLinkToken(object):
    """
    http://doc.yosmart.com/docs/protocol/openAPIV2

    Args:
        object (_type_): _description_
    """

    def __init__(self, url: str, ua_id: str, sec_id: str) -> None:
        self.url = url
        self.ua_id = ua_id
        self.sec_id = sec_id

        self.access_token = None
        self.token_type = None
        self.expires_in = 0
        self.refresh_token = None
        self.scope = None
        self.access_token_t = None

    def renew_token(self) -> str:
        """

        Returns:
            str: _description_
        """

        if not self.is_token_expired():
            log.info("Access token is not expired")
            return self.access_token

        data = {
            'grant_type': 'refresh_token',
            'client_id': self.ua_id,
            'refresh_token': self.refresh_token
        }

        response = requests.post(
            self.url,
            data=data
        )

        if response.status_code != 200:
            log.error(("Failed to get access token! Status code {}").format(
                response.status_code
            ))

        self.set_yolink_token(response=response)
        return self.access_token

    def get_access_token(self) -> str:
        """

        Returns:
            str: _description_
        """
        data = {
            'grant_type': 'client_credentials'
        }

        response = requests.post(
            self.url,
            data=data,
            auth=(self.ua_id, self.sec_id)
        )

        if response.status_code != 200:
            log.error(("Failed to get access token! Status code {}").format(
                response.status_code
            ))

        self.set_yolink_token(response=response)
        return self.access_token

    def set_yolink_token(self, response) -> None:
        self.access_token = response.json()['access_token']
        self.token_type = response.json()['token_type']
        self.expires_in = response.json()['expires_in'] - EXPIRES_IN_BUFFER
        self.refresh_token = response.json()['refresh_token']
        self.scope = response.json()['scope']

        self.access_token_t = time.time()
        log.info("Successfully got yolink access_token!")

    def is_token_expired(self) -> bool:
        if self.access_token_t is None:
            log.error("Must get a token first!")
            return True

        return ((time.time() - self.access_token_t) > self.expires_in)

    def __str__(self) -> str:
        """_summary_

        Returns:
            str: _description_
        """
        return ("access_token: {}\n"
                "expires_in: {}\n"
                "refresh_token: {}\n").format(
                    self.access_token,
                    self.expires_in,
                    self.refresh_token
                )
