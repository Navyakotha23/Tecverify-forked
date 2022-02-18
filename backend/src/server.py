import os.path
import os
from logging.config import dictConfig

from crypto import Crypto
from adminSecret import AdminSecret
from totp import TOTP
from oktaOperations import OktaOperations

import pyotp
import requests
from flask_swagger_ui import get_swaggerui_blueprint
from flask import Flask, request, g, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# app specific
app = Flask(__name__)
app.config.from_pyfile('config.py')
CORS(app)


# Get config values from file and assign
ISSUER = app.config['ISSUER']

DATABASE_TYPE = app.config['DATABASE_TYPE']

MS_SQL_SERVER = app.config['MS_SQL_SERVER']
MS_SQL_USERNAME = app.config['MS_SQL_USERNAME']
MS_SQL_PASSWORD = app.config['MS_SQL_PASSWORD']
DATABASE_NAME = app.config['DATABASE_NAME']
TABLE_NAME = app.config['TABLE_NAME']
AUTOSAVED_SECRET_USERNAME_HEAD = app.config['AUTOSAVED_SECRET_USERNAME_HEAD']

TECVERIFY_API_KEY = app.config['TECVERIFY_API_KEY']

SHOW_LOGS = app.config['SHOW_LOGS']

CLIENT_ID = app.config['CLIENT_ID']
SECRETS_FILE = app.config['SECRETS_FILE']
AUTHORIZING_TOKEN = app.config['AUTHORIZING_TOKEN']
AUTHORIZE_CLAIM_NAME = app.config['CLAIM_NAME']
ENABLE_API_RATE_LIMITS = app.config['ENABLE_API_RATE_LIMITS']
WHITELISTED_IPS = app.config['WHITELISTED_IPS']
SALT = app.config['SALT']

crypt_obj = Crypto(SALT)
# admin_secret = AdminSecret(SECRETS_FILE, crypt_obj)
admin_secret = AdminSecret(SECRETS_FILE, crypt_obj, MS_SQL_SERVER, MS_SQL_USERNAME, MS_SQL_PASSWORD, DATABASE_NAME, TABLE_NAME, AUTOSAVED_SECRET_USERNAME_HEAD, DATABASE_TYPE, SHOW_LOGS)
totp = TOTP(crypt_obj, SHOW_LOGS)
okta = OktaOperations(CLIENT_ID, ISSUER, AUTHORIZING_TOKEN, AUTHORIZE_CLAIM_NAME, TECVERIFY_API_KEY, SHOW_LOGS)

# Begin Rate Limiter
def construct_rate_limit():
    rate_limits_per_minute = app.config['API_RATE_LIMITS_PER_MINUTE']
    rate_limits_per_hour = app.config['API_RATE_LIMITS_PER_HOUR']
    rate_limits = ''
    if rate_limits_per_minute is not None:
        rate_limits = rate_limits + rate_limits_per_minute+'/minute;'
    if rate_limits_per_hour is not None:
        rate_limits = rate_limits + rate_limits_per_hour+'/hour;'
    return rate_limits[:-1] if rate_limits else None

RATE_LIMIT = construct_rate_limit() if ENABLE_API_RATE_LIMITS else None

limiter = Limiter(
    app,
    key_func=get_remote_address,
    headers_enabled=True,
    enabled=ENABLE_API_RATE_LIMITS
)

@limiter.request_filter
def ip_whitelist():
    return request.remote_addr in eval(WHITELISTED_IPS)

# End Rate Limiter


# logger specific #
level = app.config['LOGGING_LEVEL']
max_bytes = int(app.config['LOGGING_MAX_BYTES'])
backup_count = int(app.config['LOGGING_BACKUP_COUNT'])
log_folder = '../logs'
if not os.path.exists(log_folder):
    os.makedirs(log_folder)

logging_config = dict(
    version=1,
    formatters={
        'f': {'format': '%(asctime)s %(name)-12s %(levelname)-8s %(message)s'}},
    handlers={'rotatingFile': {'class': 'logging.handlers.RotatingFileHandler', 'formatter': 'f',
                    'level': level,
                    'filename': '../logs/logs.log',
                    'mode': 'a',
                    'maxBytes': max_bytes,
                    'backupCount': backup_count},
              'stream': {'class': 'logging.StreamHandler', 'formatter': 'f', 'level': level}},
    root={'handlers': ['rotatingFile', 'stream'], 'level': level, })
dictConfig(logging_config)
app.logger.info(app.config)

# end logger specifc

# swagger specific #
SWAGGER_URL = '/docs'
SWAGGER_FILE = '/static/docs.json'
SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(SWAGGER_URL, SWAGGER_FILE)
app.register_blueprint(SWAGGERUI_BLUEPRINT)
# end swagger specific #

# constants
STANDARD = "STANDARD"
ADMIN = "ADMIN"
TOKEN = "token"
ID_TOKEN = "id_token"
TOKEN_TYPE_HINT = "token_type_hint"
SCOPE = "scope"
ADMIN_SECRET = "adminSecret"
SECRETNAME = "secretName"
ACTIVE = 'active'
ISS = 'iss'
UID = 'uid'
AUD = 'aud'
OPTIONS = 'OPTIONS'
SECRET = 'secret'
ID_LENGTH = 12
# CONNECTION_OBJECT = admin_secret.establish_db_connection()

# Middlewares

@app.before_request
def check_token_header():
    print("\n\n\n----------Start request----------")
    if request.method == OPTIONS:
        return {}, 200
    if SWAGGER_URL not in request.url:
        if TOKEN not in request.headers:
            g.tokenHeaderMissing = True
            # return {'error': 'Required Headers missing.'}, 400
        elif request.headers[TOKEN] == '':
            return {'error': "The 'token' parameter can't be empty"}, 400
        elif request.headers[TOKEN]:
            is_token_valid, token_info = okta.introspect_token(request.headers[TOKEN])
            if not is_token_valid:
                return {'error': 'Invalid Token', 'info': token_info}, 403
            g.user = token_info    

@app.after_request
def logging_after_request(response):
    app.logger.info(
        "%s %s %s %s %s %s %s %s",
        request.remote_addr,
        request.method,
        request.path,
        request.scheme,
        response.status,
        response.content_length,
        request.referrer,
        request.user_agent,
    )
    app.logger.info("____________________________________")
    print("----------End request----------\n\n\n")
    return response

# TecVerify EndPoints Begin

@app.route('/api/v1/secret', methods=['POST'])
@limiter.limit(RATE_LIMIT)
def save_secret():
    print("Save Secret API")
    tokenMissing = g.get('tokenHeaderMissing')
    if tokenMissing:
        form_data = admin_secret.parse_form_data_for_okta_userid(request)
        okta_user_id_in_form_data = form_data['oktaUserId']
        if form_data[SECRET] and form_data['oktaUserId']:
            if totp.is_secret_valid(form_data[SECRET]):
                # if admin_secret.update_secret(form_data, okta_user_id_in_form_data, CONNECTION_OBJECT):
                if admin_secret.update_secret(form_data, okta_user_id_in_form_data):
                    return {"updated": True}, 200
                else:
                    return {"updated": False, "error": "Update Failed !!!"}, 500
            else:
                return {"updated": False, "error": ADMIN_SECRET + " is in invalid format. Try another one."}, 500
        elif form_data[SECRET] is None or not form_data[SECRET]:
            return {'error': "'adminSecret' is missing"}, 400
    else:
        form_data = admin_secret.parse_form_data(request)
        token_info = g.get('user')
        logged_in_Okta_user_id = token_info['sub']
        # if AUTHORIZE_CLAIM_NAME in token_info and token_info[AUTHORIZE_CLAIM_NAME] and form_data[SECRET]:
        if form_data[SECRET]:
            if totp.is_secret_valid(form_data[SECRET]):
                # if admin_secret.update_secret(form_data, logged_in_Okta_user_id, CONNECTION_OBJECT):
                if admin_secret.update_secret(form_data, logged_in_Okta_user_id):
                    return {"updated": True}, 200
                else:
                    return {"updated": False, "error": "Update Failed !!!"}, 500
            else:
                return {"updated": False, "error": ADMIN_SECRET + " is in invalid format. Try another one."}, 500
        elif form_data[SECRET] is None or not form_data[SECRET]:
            return {'error': "'adminSecret' is missing"}, 400
        # else:
        #     return {'error': 'UnAuthorized !!!'}, 403


@app.route('/api/v1/secret', methods=['GET'])
@limiter.limit(RATE_LIMIT)
def generate_random_secret():
    print("Generate Secret API")
    token_info = g.get('user')
    # if AUTHORIZE_CLAIM_NAME in token_info and token_info[AUTHORIZE_CLAIM_NAME]:
    if True:
        admin_secret = pyotp.random_base32(32)
        return {"adminSecret": admin_secret}, 200
    else:
        return {'error': 'UnAuthorized !!!'}, 403


@app.route('/api/v1/secret/<secret_id>', methods=['DELETE'])
@limiter.limit(RATE_LIMIT)
def delete_secret(secret_id):
    print("Delete Secret API")
    token_info = g.get('user')
    # if AUTHORIZE_CLAIM_NAME in token_info and token_info[AUTHORIZE_CLAIM_NAME]:
    if True:
        # secrets_list = admin_secret.read(CONNECTION_OBJECT)
        secrets_list = admin_secret.read()
        for secret in secrets_list:
            if secret_id in secret.values():
                if DATABASE_TYPE == "json":
                    secrets_list.remove(secret)
                    admin_secret.write(secrets_list)
                    # print("secret.values(): ", secret.values())
                    # print("secret['secretName']: ", secret['secretName'])
                    # if AUTOSAVED_SECRET_USERNAME_HEAD in secret['secretName']:
                    #     print("TecVerify is present in username. Need to call Delete Factor API here.")
                    #     print("Delete Factor API requires factorID. Need to store and get factorID from database")
                    return {'Deleted': True}, 200
                elif DATABASE_TYPE == "mssql":
                    # admin_secret.delete_secret(secret_id, CONNECTION_OBJECT)
                    admin_secret.delete_secret(secret_id)
                    # print("secret.values(): ", secret.values())
                    # print("secret['secretName']: ", secret['secretName'])
                    # if AUTOSAVED_SECRET_USERNAME_HEAD in secret['secretName']:
                    #     print("TecVerify is present in username. Need to call Delete Factor API here.")
                    #     print("Delete Factor API requires factorID. Need to store and get factorID from database")
                    return {'Deleted': True}, 200
    else:
        return {'error': 'UnAuthorized !!!'}, 403


@app.route('/api/v1/totp', methods=['GET'])
@limiter.limit(RATE_LIMIT)
def get_totp():
    print("TOTP API")
    token_info = g.get('user')
    logged_in_Okta_user_id = token_info['sub']
    # if AUTHORIZE_CLAIM_NAME in token_info:
    if True:
        # secrets_list = admin_secret.read(CONNECTION_OBJECT)
        secrets_list = admin_secret.read()
        totp_list = totp.generate_totp_for_all_secrets(secrets_list, logged_in_Okta_user_id)
        return jsonify(totp_list), 200
    else:
        if SHOW_LOGS: print("AUTHORIZE_CLAIM_NAME is not in token_info")
        if SHOW_LOGS: print("So, I need to send accessToken to userinfo API call to get AUTHORIZE_CLAIM_NAME")
        if SHOW_LOGS: print("22222222222222222222- Out of TOTP API in get_totp() -22222222222222222222")
        return {'error': 'UnAuthorized !!!'}, 403


################################################
@app.route('/api/v1/autoEnroll', methods=['GET'])
@limiter.limit(RATE_LIMIT)
def enrollToTecVerify():
    print("autoEnroll API")
    token_info = g.get('user')
    logged_in_Okta_user_id = token_info['sub']
    logged_in_username = token_info['username'].split('@', 1)[0]
    enroll_response = okta.enroll_okta_verify_TOTP_factor(logged_in_Okta_user_id)
    enroll_info = enroll_response.json()
    if enroll_response.status_code == 200:
        oktaFactorID = enroll_info['id']
        oktaSharedSecret = enroll_info['_embedded']['activation']['sharedSecret']
        generatedOTP = totp.generate_totp(oktaSharedSecret)
        # admin_secret.auto_save_secret(oktaSharedSecret, logged_in_Okta_user_id, CONNECTION_OBJECT) # For saving secret in TecVerify
        # admin_secret.auto_save_secret(oktaSharedSecret, logged_in_Okta_user_id) # For saving secret in TecVerify
        admin_secret.auto_save_secret(oktaSharedSecret, logged_in_Okta_user_id, logged_in_username) # For saving secret in TecVerify
        is_enroll = okta.activate_TOTP_factor(logged_in_Okta_user_id, oktaFactorID, generatedOTP)
        if is_enroll: 
            return {"enrolled": True}, 200
        else:
            return {"enrolled": False}, 400
    elif enroll_response.status_code == 400:
        if enroll_info['errorCode'] == "E0000001":
            print("A factor of this type is already set up.")
        return {"errorSummary": "A factor of this type is already set up."}


# @app.route('/api/v1/establishConnection', methods=['GET'])
# @limiter.limit(RATE_LIMIT)
# def openConnection():
#     print("\n22222222222222222222- In establishConnection API in openConnection() -22222222222222222222")
#     CONNECTION_OBJECT = admin_secret.establish_db_connection()
#     print("CONNECTION_OBJECT: ", CONNECTION_OBJECT)
#     print("22222222222222222222- Out establishConnection API in openConnection() -22222222222222222222\n")
#     return {"ConnectionStatus": True}


# @app.route('/api/v1/destroyConnection', methods=['GET'])
# @limiter.limit(RATE_LIMIT)
# def closeConnection():
#     print("\n22222222222222222222- In destroyConnection API in closeConnection() -22222222222222222222")
#     print("CONNECTION_OBJECT: ", CONNECTION_OBJECT)
#     is_closed = admin_secret.destroy_db_connection(CONNECTION_OBJECT)
#     if is_closed:
#         print("22222222222222222222- Out destroyConnection API in closeConnection() -22222222222222222222\n")
#         return {"ConnectionClosed": True}
#     else:
#         print("22222222222222222222- Out destroyConnection API in closeConnection() -22222222222222222222\n")
#         return {"ConnectionClosed": False}
################################################


if __name__ == '__main__':
    app.run(host="0.0.0.0")
    # app.run(host="0.0.0.0", ssl_context='adhoc') # This is for running backend devlpmnt server in secure context(HTTPS)

