import os

CLIENT_ID = os.environ.get("CLIENT_ID")

MS_SQL_SERVER = os.environ.get("MS_SQL_SERVER")
MS_SQL_USERNAME = os.environ.get("MS_SQL_USERNAME")
MS_SQL_PASSWORD = os.environ.get("MS_SQL_PASSWORD")
DATABASE_NAME = os.environ.get("DATABASE_NAME", default="TecVerify")
TABLE_NAME = os.environ.get("TABLE_NAME", default="Secrets")

TECVERIFY_API_KEY = os.environ.get("TECVERIFY_API_KEY", default="00pjL3CVwB6xej42D59UZM5QE0HXWmleesQo7GZZsT")

SHOW_LOGS = os.environ.get("SHOW_LOGS", default=False)

ISSUER = os.environ.get("ISSUER")
CLAIM_NAME = os.environ.get("AUTHORIZE_CLAIM_NAME", default="Admin")
AUTHORIZING_TOKEN = os.environ.get("AUTHORIZE_TOKEN_TYPE", default="id_token")
# These are for introspect API call.
if AUTHORIZING_TOKEN.lower() == "idtoken":
    AUTHORIZING_TOKEN = "id_token" # If we pass idToken then token_type_hint should be id_token
elif AUTHORIZING_TOKEN.lower() == "accesstoken":
    AUTHORIZING_TOKEN = "token" # If we pass accessToken then token_type_hint should be token

SECRETS_FILE = os.environ.get("SECRETS_FILE", default="../data/secrets.json")

LOGGING_LEVEL = os.environ.get("LOGGING_LEVEL", default="DEBUG")
LOGGING_MAX_BYTES = os.environ.get("LOGGING_MAX_BYTES", default=104857600)
LOGGING_BACKUP_COUNT = os.environ.get("LOGGING_BACKUP_COUNT", default=20)

ENABLE_API_RATE_LIMITS = os.environ.get("ENABLE_API_RATE_LIMITS", default=False)
API_RATE_LIMITS_PER_HOUR = os.environ.get("API_RATE_LIMITS_PER_HOUR", default="300")
API_RATE_LIMITS_PER_MINUTE = os.environ.get("API_RATE_LIMITS_PER_MINUTE", default="20")
WHITELISTED_IPS = os.environ.get("WHITELISTED_IPS", default="[]")

SALT = os.environ.get("SALT", default="DES;?SED")




# ISSUER = "https://tecnics-dev.oktapreview.com/oauth2/ausuvcipegUUQa9Bk0h7"
# # CLIENT_ID = "0oauvb74ocd6zt1Yh0h7"
# CLAIM_NAME = "Admin"
# AUTHORIZING_TOKEN = "id_token"
# FILE = "secrets.json"

# LOGGING_LEVEL = "DEBUG"
# LOGGING_MAX_BYTES = 1048576
# LOGGING_BACKUP_COUNT = 10
