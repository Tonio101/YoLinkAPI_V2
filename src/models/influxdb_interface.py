import requests

from models.logger import Logger
log = Logger.getInstance().getLogger()


class InfluxDbClient(object):
    """
        Object representation for influx db interface client.
    """
    def __init__(self, url, auth, db_name, measurement, tag_set):
        """

        Args:
            url ([type]): [description]
            auth ([type]): [description]
            db_name ([type]): [description]
            measurement ([type]): [description]
            tag_set ([type]): [description]
        """
        self.url = url
        self.auth = auth
        self.db = db_name
        self.params = (
            ('db', db_name),
        )
        self.headers = {'Content-Type': 'application/json'}
        self.measurement = measurement
        self.tag_set = tag_set

    def set_url(self, url):
        self.url = url

    def set_auth(self, auth):
        self.auth = auth

    def set_db(self, db_name):
        self.db = db_name
        self.params = (
            ('db', db_name),
        )

    def write_data(self, data):
        # measurment,tag_set field_set=<val>
        # Example:
        # weather,location=home temperature=55.5,humidity=70.2
        data = ("{0},{1} {2}").format(
            self.measurement,
            self.tag_set,
            data
        )
        log.debug(data)
        response = requests.post(url=self.url,
                                 params=self.params,
                                 data=data,
                                 auth=self.auth,
                                 headers=self.headers)
        log.debug(response)

        if response.status_code == 204:
            log.debug(("Successfully sent data to influx db "
                       "Elapsed time {0}").format(response.elapsed))
            return 0

        log.error("Error to send data to influx db {0}".format(
            response.status_code
        ))
        return response.status_code
