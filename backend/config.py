ISSUER = "https://tecnics-dev.oktapreview.com/oauth2/ausuvcipegUUQa9Bk0h7"
CLIENT_ID = "0oauvb74ocd6zt1Yh0h7"
CLAIM_NAME = "Admin"
AUTHORIZING_TOKEN = "id_token"
FILE = "secrets.json"

LOGGING_CONFIG = dict(
    version = 1,
    formatters = { 'f': {'format': '%(asctime)s %(name)-12s %(levelname)-8s %(message)s'}},
    handlers = {'h': {'class': 'logging.handlers.RotatingFileHandler', 'formatter': 'f',
            'level': 'DEBUG',
            'filename': './logs/logs.log',
            'mode': 'a',
            'maxBytes': 1048576,
            'backupCount': 10}},
    root = {'handlers': ['h'], 'level': 'DEBUG',}
)
