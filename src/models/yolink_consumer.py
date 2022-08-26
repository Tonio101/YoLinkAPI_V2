import threading
from time import sleep

from models.logger import Logger
log = Logger.getInstance().getLogger()


class YoLinkConsumer(threading.Thread):
    """
    YoLink MQTT Message Consumer.

    Args:
        threading (Thread): Spin a thread.
    """
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs=None, verbose=None):
        super(YoLinkConsumer, self).__init__()
        self.setDaemon(True)
        self.target = target
        self.name = name
        self.output_q = args[0]
        self.device_hash = args[1]

    def run(self):
        """
        Spin up a thread to dequeue and process device data.
        """
        while True:
            if not self.output_q.empty():
                payload = self.output_q.get()
                log.debug("Pulled from the output_q")
                log.debug(payload)
                rc = self.process_entry(payload)
                if rc == 0:
                    log.debug(
                        ("Successfully processed entry, number "
                         "of entries in the queue: {0}").format(
                             self.output_q.qsize()
                         ))
                else:
                    log.error("Failed to process entry {0}".format(
                        rc
                    ))
            sleep(0.5)

    def process_entry(self, payload) -> int:
        """
        Process the device info data.

        Args:
            payload (dict): Contains info about device data.

        Returns:
            int: 0 if successful else -1.
        """
        device_id = payload['deviceId']

        if device_id not in self.device_hash:
            log.debug(("Device ID:{0} is not "
                       "in device hash").format(device_id))
            return -1

        self.device_hash[device_id].refresh_device_data(payload)
        device = self.device_hash[device_id]
        log.debug("\n{0}\n".format(device))

        rc = 0
        try:
            rc = device.process()
        except Exception as e:
            log.error(e)
            rc = -1

        return rc
