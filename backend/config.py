import os

CLIENT_ID = os.environ.get("CLIENT_ID")
ISSUER = os.environ.get("ISSUER")
CLAIM_NAME = os.environ.get("AUTHORIZE_CLAIM_NAME", default="Admin")
AUTHORIZING_TOKEN = os.environ.get("AUTHORIZE_TOKEN_TYPE", default="id_token")
if AUTHORIZING_TOKEN.lower() == "idtoken":
    AUTHORIZING_TOKEN = "id_token"

SECRETS_FILE = os.environ.get("SECRETS_FILE", default="secrets.json")

LOGGING_LEVEL = os.environ.get("LOGGING_LEVEL", default="DEBUG")
LOGGING_MAX_BYTES = os.environ.get("LOGGING_MAX_BYTES", default="1048576")
LOGGING_BACKUP_COUNT = os.environ.get("LOGGING_BACKUP_COUNT", default="10")
RATE_LIMIT_CALLS = os.environ.get("RATE_LIMIT_CALLS", default=10)
RATE_LIMIT_PERIOD = os.environ.get("RATE_LIMIT_PERIOD", default=1)




# ISSUER = "https://tecnics-dev.oktapreview.com/oauth2/ausuvcipegUUQa9Bk0h7"
# # CLIENT_ID = "0oauvb74ocd6zt1Yh0h7"
# CLAIM_NAME = "Admin"
# AUTHORIZING_TOKEN = "id_token"
# FILE = "secrets.json"

# LOGGING_LEVEL = "DEBUG"
# LOGGING_MAX_BYTES = 1048576
# LOGGING_BACKUP_COUNT = 10
