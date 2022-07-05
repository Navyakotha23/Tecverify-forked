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
        log_folder = '../logs'
        log_file = '../logs/logs.log'
        if not os.path.exists(log_folder):
            os.makedirs(log_folder)

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
