import os

CLIENT_ID = os.environ.get("CLIENT_ID")
ISSUER = os.environ.get("ISSUER")
CLAIM_NAME = os.environ.get("AUTHORIZE_CLAIM_NAME", default="Admin")
AUTHORIZING_TOKEN = os.environ.get("AUTHORIZE_TOKEN_TYPE", default="id_token")
if AUTHORIZING_TOKEN.lower() == "idtoken":
    AUTHORIZING_TOKEN = "id_token"

SECRETS_FILE = os.environ.get("SECRETS_FILE", default="secrets.json")

LOGGING_LEVEL = os.environ.get("LOGGING_LEVEL", default="DEBUG")
LOGGING_MAX_BYTES = os.environ.get("LOGGING_MAX_BYTES", default=1048576)
LOGGING_BACKUP_COUNT = os.environ.get("LOGGING_BACKUP_COUNT", default=20)
API_RATE_LIMITS = os.environ.get("API_RATE_LIMITS", default="20/minute;300/hour")
WHITELISTED_IPS = os.environ.get("WHITELISTED_IPS", default="[]")




# ISSUER = "https://tecnics-dev.oktapreview.com/oauth2/ausuvcipegUUQa9Bk0h7"
# # CLIENT_ID = "0oauvb74ocd6zt1Yh0h7"
# CLAIM_NAME = "Admin"
# AUTHORIZING_TOKEN = "id_token"
# FILE = "secrets.json"

# LOGGING_LEVEL = "DEBUG"
# LOGGING_MAX_BYTES = 1048576
# LOGGING_BACKUP_COUNT = 10
