import os


CLIENT_ID = os.environ.get("CLIENT_ID", default="0oa164ptl0ySnZSb50h8")
ISSUER = os.environ.get("ISSUER", default="https://tecnics-demo.oktapreview.com")
CLAIM_NAME = os.environ.get("AUTHORIZE_CLAIM_NAME", default="Admin")
AUTHORIZING_TOKEN = os.environ.get("AUTHORIZE_TOKEN_TYPE", default="id_token")
# These are for introspect API call.
if AUTHORIZING_TOKEN.lower() == "idtoken":
    AUTHORIZING_TOKEN = "id_token" # If we pass idToken then token_type_hint should be id_token
elif AUTHORIZING_TOKEN.lower() == "accesstoken":
    AUTHORIZING_TOKEN = "token" # If we pass accessToken then token_type_hint should be token
# ENCRYPTED_API_KEY = os.environ.get("ENCRYPTED_API_KEY")
ENCRYPTED_API_KEY = os.environ.get("ENCRYPTED_API_KEY", default = 'b\'C\\xb5\\x02M\\x10N\\x80\\xd0O\\xc8z\\xabV>\\x9aW\\xb5\\x17c&N\\x95\\x92\\xb7&t@Y\\xa9\\xf5"]\\xa0\\xd4]\\x9f\\xc6\\xfct\\xb9\\xefYWy\\x86_^\\xac\'')
API_KEY_SALT = os.environ.get("API_KEY_SALT", default="12345678")


DATABASE_TYPE = os.environ.get("DATABASE_TYPE", default="mssql")
if DATABASE_TYPE.lower() == "json":
    DATABASE_TYPE = "json"
elif DATABASE_TYPE.lower() == "mssql":
    DATABASE_TYPE = "mssql"

SECRETS_FILE = os.environ.get("SECRETS_FILE", default="../data/secrets.json")

MS_SQL_SERVER = os.environ.get("MS_SQL_SERVER", default="localhost")
MS_SQL_USERNAME = os.environ.get("MS_SQL_USERNAME", default="NaveenMasuna")
MS_SQL_PASSWORD = os.environ.get("MS_SQL_PASSWORD", default="Welcome@123")
DATABASE_NAME = os.environ.get("DATABASE_NAME", default="TecVerify")
TABLE_NAME = os.environ.get("TABLE_NAME", default="SecretsTecVerify")
AUTOSAVED_SECRET_USERNAME_HEAD = os.environ.get("AUTOSAVED_SECRET_USERNAME_HEAD", default="TecVerify")

SECRET_NAME = os.environ.get("SECRET_NAME", default="sName")
SECRET_KEY = os.environ.get("SECRET_KEY", default="sKey")
OKTA_USER_ID = os.environ.get("OKTA_USER_ID", default="oUserId")
SECRET_ID = os.environ.get("SECRET_ID", default="sId")
SECRET_UPDATED_AT = os.environ.get("SECRET_UPDATED_AT", default="sUpdatedAt")
OKTA_FACTOR_ID = os.environ.get("OKTA_FACTOR_ID", default="oFactorId")

SALT = os.environ.get("SALT", default="DES;?SED")


LOGGING_LEVEL = os.environ.get("LOGGING_LEVEL", default="DEBUG")
LOGGING_MAX_BYTES = os.environ.get("LOGGING_MAX_BYTES", default=104857600)
LOGGING_BACKUP_COUNT = os.environ.get("LOGGING_BACKUP_COUNT", default=20)

ENABLE_API_RATE_LIMITS = os.environ.get("ENABLE_API_RATE_LIMITS", default=False)
API_RATE_LIMITS_PER_HOUR = os.environ.get("API_RATE_LIMITS_PER_HOUR", default="300")
API_RATE_LIMITS_PER_MINUTE = os.environ.get("API_RATE_LIMITS_PER_MINUTE", default="20")
WHITELISTED_IPS = os.environ.get("WHITELISTED_IPS", default="[]")


SHOW_LOGS = os.environ.get("SHOW_LOGS", default=False)


