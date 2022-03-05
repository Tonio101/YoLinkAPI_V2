import logging

from logging.handlers import RotatingFileHandler

FILE = '/tmp/yolink_default.log'
FILE_MAXSIZE = 10 * 1024 * 1024  # 10MB
FILE_BACKUP_CNT = 2
LOG_FORMAT = '%(asctime)s:%(module)s:%(levelname)s - %(message)s'
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


class SingletonType(type):
    _instances = {}

    def getInstance(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = \
                    super(SingletonType, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Logger(object, metaclass=SingletonType):
    """_summary_

    Args:
        object (_type_): _description_
        metaclass (_type_, optional): _description_. Defaults to SingletonType.
    """

    def __init__(self, name='YoLink', fname=FILE,
                 maxBytes=FILE_MAXSIZE, backupCount=FILE_BACKUP_CNT):

        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)

        # String format log
        handler = logging.StreamHandler()

        formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
        handler.setFormatter(formatter)

        self.logger.addHandler(handler)
        rotate_file_handler = RotatingFileHandler(fname, maxBytes, backupCount)

        self.logger.addHandler(rotate_file_handler)

    def getLogger(self):
        return self.logger
