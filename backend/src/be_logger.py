import os
import os.path
from logging.config import dictConfig


class BE_LOGGER:

    def __init__(self, app) -> None:
        self.app = app

    def implement_logging_for_BE(self):
        print("LOGGER specific")
        level = self.app.config['LOGGING_LEVEL']
        max_bytes = int(self.app.config['LOGGING_MAX_BYTES'])
        backup_count = int(self.app.config['LOGGING_BACKUP_COUNT'])
        log_folder = '../logs'
        if not os.path.exists(log_folder):
            os.makedirs(log_folder)

        logging_config = dict(
            version=1,
            formatters={
                'f': {'format': '%(asctime)s %(name)-12s %(levelname)-8s %(message)s'}},
            handlers={'rotatingFile': {'class': 'logging.handlers.RotatingFileHandler', 'formatter': 'f',
                            'level': level,
                            'filename': '../logs/logs.log',
                            'mode': 'a',
                            'maxBytes': max_bytes,
                            'backupCount': backup_count},
                    'stream': {'class': 'logging.StreamHandler', 'formatter': 'f', 'level': level}},
            root={'handlers': ['rotatingFile', 'stream'], 'level': level, })
        dictConfig(logging_config)
        self.app.logger.info(self.app.config)
        print("end LOGGER specific")
