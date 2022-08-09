import json
import random
import sys

from time import sleep
import paho.mqtt.client as mqtt
from models.logger import Logger
log = Logger.getInstance().getLogger()


class YoLinkMQTTClient(object):
    """
    Object representation for YoLink MQTT Client
    """
    def __init__(self, username: str, passwd: str, topic: str,
                 mqtt_url: str, mqtt_port: str, device_hash: str,
                 output_q: str, yolink_token: str):
        self.username = username
        self.passwd = passwd
        self.topic = topic
        self.mqtt_url = mqtt_url
        self.mqtt_port = int(mqtt_port)
        self.device_hash = device_hash
        self.output_q = output_q
        self.yolink_token = yolink_token
        self.client = self.get_mqtt_client()

    def get_mqtt_client(self, client_id=random.randint(0, 1000)) -> mqtt:
        """
        Initialize MQTT client.

        Args:
            client_id (string or int, optional): MQTT subscribes require a
            unique client id. Defaults to random.randint(0, 1000).

        Returns:
            mqtt: MQTT Client object.
        """
        mqtt_c = mqtt.Client(client_id=str(__name__ + str(client_id)),
                             clean_session=True, userdata=None,
                             protocol=mqtt.MQTTv311, transport="tcp")
        mqtt_c.on_connect = self.on_connect
        mqtt_c.on_message = self.on_message
        return mqtt_c

    def connect_to_broker(self):
        """
        Connect to MQTT broker
        """
        log.info("Connecting to broker...")
        self.client.username_pw_set(username=self.username,
                                    password=self.passwd)

        self.client.connect(self.mqtt_url, self.mqtt_port, 10)
        # method blocks the program, handles reconnects, etc.
        # Since we are listening for published messages to the
        # YoLink broker topic, we need to run indefinitely.
        # If you need to do other things, than call loop_start()
        # instead.
        self.client.loop_forever()

    def on_message(self, client, userdata, msg):
        """
        Callback for broker published events

        Args:
            client (): MQTT client id.
            userdata (): MQTT client metadata.
            msg (json): JSON payload containing MQTT data.
        """
        payload = json.loads(msg.payload.decode("utf-8"))
        self.output_q.put(payload)

    def on_connect(self, client, userdata, flags, rc):
        """
        Callback for connection to broker.
        """
        log.info("Connected with result code %s" % rc)

        if (rc == 0):
            log.info("Successfully connected to broker %s" % self.mqtt_url)
        else:
            log.error("Connection with result code %s" % rc)
            self.restart_mqtt()

        self.client.subscribe(self.topic)

    def restart_mqtt(self):
        """
        Obtain a new refresh token and restart MQTT connection.
        """
        log.info("Attempting to reconnect with fresh token")
        self.client.loop_stop()
        self.client.disconnect()
        sleep(2)
        self.client = self.get_mqtt_client()
        self.username = self.yolink_token.renew_token()
        self.connect_to_broker()
        sleep(2)


class MQTTClient(object):
    """
    Object representation for a MQTT Client
    """

    def __init__(self, username, password, mqtt_host, mqtt_port):
        self.host = mqtt_host
        self.port = mqtt_port

        self.client = mqtt.Client(client_id=__name__, clean_session=True,
                                  userdata=None, protocol=mqtt.MQTTv311,
                                  transport="tcp")
        self.client.username_pw_set(username, password)
        self.client.on_connect = self.on_connect

    def connect_to_broker(self):
        """
        Connect to MQTT broker
        """
        log.info("Connecting to broker...")
        self.client.connect(self.host, self.port, 10)
        # Spins a thread that will call the loop method at
        # regualr intervals and handle re-connects.
        self.client.loop_start()

    def on_connect(self, client, userdata, flags, rc):
        """
        Callback for broker connection event
        """
        log.info("Connected with result code %s" % rc)

        if (rc == 0):
            log.info("Successfully connected to broker %s" % self.host)
        else:
            log.error("Connection with result code %s" % rc)
            sys.exit(2)

    def publish(self, topic, data):
        """
        Publish events to topic
        """
        rc = self.client.publish(str(topic), data)
        if rc[0] == 0:
            log.debug("Successfully published event to topic {0}".format(
                topic
            ))
        else:
            log.error("Failed to publish {0} to topic {1}".format(
                data, topic
            ))

        return rc[0]
