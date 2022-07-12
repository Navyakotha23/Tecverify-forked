import os
import os.path
from logging.config import dictConfig


class BE_LOGGER:

    def __init__(self, app) -> None:
        self.app = app

    def implement_logging_for_BE(self):
        """
        This method implements logging for TecVerify backend.
        """
        level = self.app.config['LOGGING_LEVEL']
        max_bytes = int(self.app.config['LOGGING_MAX_BYTES'])
        backup_count = int(self.app.config['LOGGING_BACKUP_COUNT'])

        # server is running in src folder. Below paths are from src folder.
        log_folder = './tecverify_logging/logs'
        log_file = './tecverify_logging/logs/logs.log'
        try:
            if not os.path.exists(log_folder):
                os.makedirs(log_folder)
        except Exception as e:
            print("\nException in creating a folder for logs: ", e)
            return False
        # 

        logging_config = dict(
            version=1,
            formatters={
                        'tecverify-log-format': {
                                                 'format': '%(asctime)s %(name)-12s %(levelname)-8s %(message)s'
                                                }
                       },
            handlers={
                        'rotatingFile': {
                                            'class': 'logging.handlers.RotatingFileHandler', 
                                            'formatter': 'tecverify-log-format',
                                            'level': level,
                                            'filename': log_file,
                                            'mode': 'a',
                                            'maxBytes': max_bytes,
                                            'backupCount': backup_count
                                        },
                        'stream': {
                                    'class': 'logging.StreamHandler', 
                                    'formatter': 'tecverify-log-format', 
                                    'level': level
                                  }
                     },
            root={
                    'handlers': ['rotatingFile', 'stream'], 
                    'level': level, 
                 }
            )

        dictConfig(logging_config)
        self.app.logger.info(self.app.config)
        # self.app.logger.info("Config: %s" % self.app.config)
        # self.app.logger.info("level: %s,  myName: %s" % (level, "MasunaNaveenKumar"))
        # self.app.logger.info("level: '%s',  myName: '%s'" % (level, "MasunaNaveenKumar"))
        # self.app.logger.info("level: {0},  myName: {1}".format(level, "MasunaNaveenKumar"))
        # self.app.logger.info("level: '{0}',  myName: '{1}'".format(level, "MasunaNaveenKumar"))

