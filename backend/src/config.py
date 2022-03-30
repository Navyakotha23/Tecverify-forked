import os

# tecnics-dev Tenant 
# CLIENT_ID = os.environ.get("CLIENT_ID", default="0oa13u4q28j1TtvEP0h8")
# tecnics-demo Tenant 
CLIENT_ID = os.environ.get("CLIENT_ID", default="0oa164ptl0ySnZSb50h8")

DATABASE_TYPE = os.environ.get("DATABASE_TYPE", default="json")
if DATABASE_TYPE.lower() == "json":
    DATABASE_TYPE = "json"
elif DATABASE_TYPE.lower() == "mssql":
    DATABASE_TYPE = "mssql"

MS_SQL_SERVER = os.environ.get("MS_SQL_SERVER", default="192.168.1.202")
MS_SQL_USERNAME = os.environ.get("MS_SQL_USERNAME", default="SA")
MS_SQL_PASSWORD = os.environ.get("MS_SQL_PASSWORD", default="Tecnics@123")
DATABASE_NAME = os.environ.get("DATABASE_NAME", default="TecVerify")
TABLE_NAME = os.environ.get("TABLE_NAME", default="Secrets")
AUTOSAVED_SECRET_USERNAME_HEAD = os.environ.get("AUTOSAVED_SECRET_USERNAME_HEAD", default="TecVerify")

# tecnics-dev Tenant 
# ENCRYPTED_API_KEY = os.environ.get("ENCRYPTED_API_KEY", default="b'\\xbd\\x9f\\xccD\\xf0\\x8d\\xb3\\xeati\\x8c\\x03\\x98\\x15\\x89A\\xde\\xdcx\\xf0\\x13r\\xa9(\\x11x\\xe7,\\xb19\\x16\\xba\\xe2*AT\\xa5\\x0c@K\\x9d&^\\xeeQ\\x86\\xf9\\x9d'")
# tecnics-demo Tenant 
# ENCRYPTED_API_KEY = os.environ.get("ENCRYPTED_API_KEY", default="b'\\x1c\\x9fX\\xd1\\xbean\\xe1\\xe3\\xb6}m\\xe1*\\xc0\\xf96\\xa7Nr\\x8e\\xae[\\xef<e\\x94\\xe1\\xa0\\x99\\x81\\x93\\xb7\\xc7\\x97\\x8a\\xce\\xa4\\x80\\x8d\\x82\\xc8\\x18o\\x1f1\\xa5'")
ENCRYPTED_API_KEY = os.environ.get("ENCRYPTED_API_KEY", default="DummyAPIKey")
API_KEY_SALT = os.environ.get("API_KEY_SALT", default="12345678")

SHOW_LOGS = os.environ.get("SHOW_LOGS", default=False)

# tecnics-dev Tenant 
# ISSUER = os.environ.get("ISSUER", default="https://tecnics-dev.oktapreview.com")
# tecnics-demo Tenant 
ISSUER = os.environ.get("ISSUER", default="https://tecnics-demo.oktapreview.com")
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

