import os


CLIENT_ID = os.environ.get("CLIENT_ID", default="0oa164ptl0ySnZSb50h8")
ISSUER = os.environ.get("ISSUER", default="https://tecnics-demo.oktapreview.com")
CLAIM_NAME = os.environ.get("AUTHORIZE_CLAIM_NAME", default="Admin")
AUTHORIZE_TOKEN_TYPE = os.environ.get("AUTHORIZE_TOKEN_TYPE", default="accessToken")
# These are for introspect API call.
if AUTHORIZE_TOKEN_TYPE.lower() == "idtoken":
    TOKEN_TYPE_HINT = "id_token" # If we pass idToken then token_type_hint should be id_token
elif AUTHORIZE_TOKEN_TYPE.lower() == "accesstoken":
    TOKEN_TYPE_HINT = "token" # If we pass accessToken then token_type_hint should be token
ENCRYPTED_API_KEY = os.environ.get("ENCRYPTED_API_KEY")
# ENCRYPTED_API_KEY = os.environ.get("ENCRYPTED_API_KEY", default = "b'94\\xc8\\xeezJt\\x1a-\\xe7\\x0c\\xb5\\x95i\\xe0\\xde\\xb9\\x8bFI=\\xa9|\\xb29\\xab]-E\\x08\\x01e\\x95\\x92\\x14\\x1e\\xae\\x12\\x80\\xc3|\\x80\\x00\\x96\\xfe\\abc\'")
API_KEY_SALT = os.environ.get("API_KEY_SALT", default="12345678")


DATABASE_TYPE = os.environ.get("DATABASE_TYPE", default="json")
if DATABASE_TYPE.lower() == "json":
    DATABASE_TYPE = "json"
elif DATABASE_TYPE.lower() == "mssql":
    DATABASE_TYPE = "mssql"

# server is running in src folder. Below path is from src folder.
SECRETS_FILE = os.environ.get("SECRETS_FILE", default="./database_operations/json_db/secrets.json")

MS_SQL_SERVER = os.environ.get("MS_SQL_SERVER", default="localhost")
MS_SQL_USERNAME = os.environ.get("MS_SQL_USERNAME", default="NaveenMasuna")
MS_SQL_PASSWORD = os.environ.get("MS_SQL_PASSWORD", default="Welcome@123")
DATABASE_NAME = os.environ.get("DATABASE_NAME", default="TecVerify")
TABLE_NAME = os.environ.get("TABLE_NAME", default="SecretsTecVerify")
AUTOSAVED_SECRET_USERNAME_HEAD = os.environ.get("AUTOSAVED_SECRET_USERNAME_HEAD", default="TecVerify")

SECRET_NAME = os.environ.get("SECRET_NAME", default="sctName")
SECRET_KEY = os.environ.get("SECRET_KEY", default="sctKey")
OKTA_USER_ID = os.environ.get("OKTA_USER_ID", default="oktUserId")
SECRET_ID = os.environ.get("SECRET_ID", default="sctId")
SECRET_UPDATED_AT = os.environ.get("SECRET_UPDATED_AT", default="sctUpdatedAt")
OKTA_FACTOR_ID = os.environ.get("OKTA_FACTOR_ID", default="oktFactorId")

SALT = os.environ.get("SALT", default="DES;?SED")


LOGGING_LEVEL = os.environ.get("LOGGING_LEVEL", default="DEBUG")
LOGGING_MAX_BYTES = os.environ.get("LOGGING_MAX_BYTES", default=104857600)
LOGGING_BACKUP_COUNT = os.environ.get("LOGGING_BACKUP_COUNT", default=20)


# These limits apply for each individual API. These are not applied collectively.
ENABLE_API_RATE_LIMITS = os.environ.get("ENABLE_API_RATE_LIMITS", default=False)
API_RATE_LIMITS_PER_HOUR = os.environ.get("API_RATE_LIMITS_PER_HOUR", default="300")
API_RATE_LIMITS_PER_MINUTE = os.environ.get("API_RATE_LIMITS_PER_MINUTE", default="20")
WHITELISTED_IPS = os.environ.get("WHITELISTED_IPS", default="[]")


SHOW_LOGS = os.environ.get("SHOW_LOGS", default=False)
DUMMY_ENV_VAR = os.environ.get("DUMMY_ENV_VAR", default="Dummy Environment Variable")



