from datetime import datetime

from enum import Enum
from logger import Logger
log = Logger.getInstance().getLogger()


class DeviceType(Enum):
    DOOR = 1
    TEMPERATURE = 2
    LEAK = 3
    VIBRATION = 4


class TempType(Enum):
    CELSIUS = 1
    FAHRENHEIT = 2


class DoorEvent(Enum):
    UNKNOWN = -1
    OPEN = 1
    CLOSE = 2


class LeakEvent(Enum):
    UNKNOWN = -1
    DRY = 1
    FULL = 2


class VibrateEvent(Enum):
    UNKNOWN = -1
    NO_VIBRATE = 1
    VIBRATE = 2


DEVICE_TYPE = {
    "DoorSensor": DeviceType.DOOR,
    "THSensor": DeviceType.TEMPERATURE,
    "LeakSensor": DeviceType.LEAK,
    "VibrationSensor": DeviceType.VIBRATION
}

EVENT_STATE = {
    "normal": -1,
    "error": -1,
    "alert": -1,
    "open": DoorEvent.OPEN,
    "closed": DoorEvent.CLOSE,
    "dry": LeakEvent.DRY,
    "full": LeakEvent.FULL,
    "vibrate": VibrateEvent.VIBRATE
}

DEVICE_TYPE_TO_STR = {
    DeviceType.DOOR: "Door Sensor",
    DeviceType.TEMPERATURE: "Temperature Sensor",
    DeviceType.LEAK: "Leak Sensor",
    DeviceType.VIBRATION: "Vibration Sensor"
}


class YoLinkDevice(object):
    """
    Object representation for YoLink Device
    """
    def __init__(self, device_info):
        self.id = device_info['deviceId']
        self.name = device_info['name']
        self.type = DEVICE_TYPE[device_info['type']]
        self.uuid = device_info['deviceUDID']
        self.token = device_info['token']
        self.raw_type = device_info['type']

        # Device data from each MQTT event received
        # from YoLink brokers
        self.event_payload = {}

    def get_id(self):
        return self.id

    def set_name(self, name):
        self.name = name

    def get_name(self):
        return self.name

    def get_type(self):
        return self.type

    def get_raw_type(self):
        return self.raw_type

    def get_uuid(self):
        return self.uuid

    def get_token(self):
        return self.token

    def refresh_device_data(self, data):
        self.event_payload = data

    def get_device_event(self):
        return self.event_payload['event']

    def get_device_event_time(self):
        return datetime.fromtimestamp(
                self.event_payload['time'] / 1000)\
                .strftime("%Y-%m-%d %H:%M:%S")

    def get_current_time(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def get_device_message_id(self):
        return self.event_payload['msgid']

    def get_device_data(self):
        return self.event_payload['data']

    def set_mqtt_server(self, mqtt_server):
        self.topic = "yolink/{0}/{1}/report".format(
            self.get_raw_type(),
            self.get_id()
        )
        log.debug(self.topic)
        log.debug(self.get_name())

        self.mqtt_server = mqtt_server

    def process(self):
        raise NotImplementedError

    def __str__(self):
        to_str = ("Id: {0}\nName: {1}\nType: {2}\n"
                  "Event: {3}\nToken: {4}\n"
                  "Event Time: {5}\nCurrent Time: {6}\n").format(
                      self.id,
                      self.name,
                      DEVICE_TYPE_TO_STR[self.type],
                      self.get_device_event(),
                      self.token,
                      self.get_device_event_time(),
                      self.get_current_time()
        )
        return to_str


class YoLinkDoorDevice(YoLinkDevice):
    """
    Object representation for YoLink Door Sensor
    """
    def __init__(self, device_info):
        super().__init__(device_info)

    def is_open(self):
        return EVENT_STATE[self.get_device_data()['state']] == DoorEvent.OPEN

    def is_close(self):
        return EVENT_STATE[self.get_device_data()['state']] == DoorEvent.CLOSE

    def get_event(self):
        if 'state' in self.get_device_data():
            return str(EVENT_STATE[self.get_device_data()['state']])
        return None

    def __str__(self):
        to_str = ("Event: {0} ({1}) \n").format(
            self.get_event(),
            self.get_device_data()['state']
        )
        return super().__str__() + to_str

    def process(self):
        event = self.get_event()
        log.debug("Process event: {}".format(
            self.get_event()
        ))

        if event:
            return self.mqtt_server.publish(self.topic, self.get_event())
        else:
            log.info("Not supported event: {}".format(
                self.get_device_data()
            ))

        return 0


class YoLinkTempDevice(YoLinkDevice):
    """
    Object representation for YoLink Temperature Sensor
    """
    def __init__(self, device_info):
        super().__init__(device_info)
        self.temp = 0.0
        self.influxdb_client = None

    def get_temperature(self, type=TempType.FAHRENHEIT):
        self.temp = float(self.get_device_data()['temperature'])

        if type == TempType.FAHRENHEIT:
            return round(((self.temp * 1.8) + 32), 2)

        return round(self.temp, 2)

    def get_humidity(self):
        return round(float(self.get_device_data()['humidity']), 2)

    def set_influxdb_client(self, influxdb_c):
        self.influxdb_client = influxdb_c

    def influxdb_write_data(self):
        if not self.influxdb_client:
            log.debug("InfluxDB client not configured")
            return -1

        return self.influxdb_client.write_data(
                    ("temperature={0},humidity={1}").format(
                        str(self.get_temperature()),
                        str(self.get_humidity())
                    ))

    def __str__(self):
        to_str = ("Temperature (F): {0}\nHumidity: {1}\n").format(
            self.get_temperature(),
            self.get_humidity()
        )
        return super().__str__() + to_str

    def process(self):
        log.debug(("{0} {1}").format(
            self.get_temperature(),
            self.get_humidity()
        ))

        if self.influxdb_client:
            return self.influxdb_write_data()

        return 0


class YoLinkLeakDevice(YoLinkDevice):
    """
    Object representation for a YoLink Leak Sensor
    """
    def __init__(self, device_info):
        super().__init__(device_info)
        self.curr_state = LeakEvent.FULL
        self.influxdb_client = None

    def is_water_exhausted(self):
        return EVENT_STATE[self.get_device_data()['state']] == LeakEvent.DRY

    def is_water_full(self):
        return EVENT_STATE[self.get_device_data()['state']] == LeakEvent.FULL

    def get_state(self):
        if 'state' in self.get_device_data():
            return EVENT_STATE[self.get_device_data()['state']]
        return ''

    def __str__(self):
        to_str = ("Current State: {0}\n").format(
            str(self.get_state())
        )

        return super().__str__() + to_str

    def process(self):
        ret = 0

        if self.get_device_event() == 'LeakSensor.setInterval':
            log.info("Alert interval event, discard")
            return ret
        elif 'state' not in self.get_device_data():
            log.info("State not in device data {0}".format(
                self.get_device_data()
            ))
            return ret

        sensor_state = self.get_state()
        log.info("{}: {}".format(self, sensor_state))
        return ret


class YoLinkVibrationDevice(YoLinkDevice):
    """
    Object representation for a YoLink Vibration Sensor
    """
    def __init__(self, device_info):
        super().__init__(device_info)
        self.curr_state = VibrateEvent.NO_VIBRATE

    def is_vibrating(self):
        return (self.get_device_data()['state'] == 'alert')

    def get_state(self):
        if 'state' in self.get_device_data():
            if self.is_vibrating():
                return VibrateEvent.VIBRATE
        return VibrateEvent.NO_VIBRATE

    def __str__(self):
        to_str = ("Current State: {0}\n").format(
            str(self.get_state())
        )

        return super().__str__() + to_str

    def process(self):
        ret = 0

        if 'state' not in self.get_device_data():
            log.info("State not in device data {0}".format(
                self.get_device_data()
            ))
            return ret

        vibrate_state = self.get_state()
        log.info("{}: {}".format(self, vibrate_state))
        return ret


def YoLinkFactory(type: str, device_info: dict) -> YoLinkDevice:
    """
    Factory Method

    Args:
        type (str): Device type.
        device_info (dict): Device info.

    Returns:
        YoLinkDevice: YoLink Device Object.
    """
    localizers = {
        "DoorSensor": YoLinkDoorDevice,
        "THSensor": YoLinkTempDevice,
        "LeakSensor": YoLinkLeakDevice,
        "VibrationSensor": YoLinkVibrationDevice,
    }

    return localizers[type](device_info=device_info)
