# Get config values from file and assign

from flask import Flask

class EnvVars:
    app = Flask(__name__)
    app.config.from_pyfile('config.py')


    # Okta 
    CLIENT_ID = app.config['CLIENT_ID']
    ISSUER = app.config['ISSUER']
    AUTHORIZE_CLAIM_NAME = app.config['CLAIM_NAME']
    AUTHORIZE_TOKEN_TYPE = app.config['AUTHORIZE_TOKEN_TYPE']
    TOKEN_TYPE_HINT = app.config['TOKEN_TYPE_HINT']
    ENCRYPTED_API_KEY = app.config['ENCRYPTED_API_KEY']
    API_KEY_SALT = app.config['API_KEY_SALT']

    # Database 
    DATABASE_TYPE = app.config['DATABASE_TYPE']
    SECRETS_FILE = app.config['SECRETS_FILE']
    MS_SQL_SERVER = app.config['MS_SQL_SERVER']
    MS_SQL_USERNAME = app.config['MS_SQL_USERNAME']
    MS_SQL_PASSWORD = app.config['MS_SQL_PASSWORD']
    DATABASE_NAME = app.config['DATABASE_NAME']
    TABLE_NAME = app.config['TABLE_NAME']
    AUTOSAVED_SECRET_USERNAME_HEAD = app.config['AUTOSAVED_SECRET_USERNAME_HEAD']
    SECRET_NAME = app.config['SECRET_NAME']
    SECRET_KEY = app.config['SECRET_KEY']
    OKTA_USER_ID = app.config['OKTA_USER_ID']
    SECRET_ID = app.config['SECRET_ID']
    SECRET_UPDATED_AT = app.config['SECRET_UPDATED_AT']
    OKTA_FACTOR_ID = app.config['OKTA_FACTOR_ID']


    SALT = app.config['SALT']


    ENABLE_API_RATE_LIMITS = app.config['ENABLE_API_RATE_LIMITS']
    WHITELISTED_IPS = app.config['WHITELISTED_IPS']


    SHOW_LOGS = app.config['SHOW_LOGS']

    