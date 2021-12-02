import os.path
import os
from logging.config import dictConfig

from crypto import Crypto
from adminSecret import AdminSecret
from totp import TOTP
from hotp import HOTP ###
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
CLIENT_ID = app.config['CLIENT_ID']
SECRETS_FILE = app.config['SECRETS_FILE']
AUTHORIZING_TOKEN = app.config['AUTHORIZING_TOKEN']
AUTHORIZE_CLAIM_NAME = app.config['CLAIM_NAME']
ENABLE_API_RATE_LIMITS = app.config['ENABLE_API_RATE_LIMITS']
WHITELISTED_IPS = app.config['WHITELISTED_IPS']
SALT = app.config['SALT']

crypt_obj = Crypto(SALT)
admin_secret = AdminSecret(SECRETS_FILE, crypt_obj)
totp = TOTP(crypt_obj)
hotp = HOTP(crypt_obj) ###
okta = OktaOperations(CLIENT_ID, ISSUER, AUTHORIZING_TOKEN, AUTHORIZE_CLAIM_NAME)

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

# Middlewares

@app.before_request
def check_token_header():
    print("\n\nSTART-----START-----START-----START-----START-----START-----START-----START-----START-----START")
    # app.logger.info("---before_request middleware---")
    print("-----In before_request middleware in check_token_header()-----")
    if request.method == OPTIONS:
        # Need to print token_info here and check
        return {}, 200
    if SWAGGER_URL not in request.url:
        if TOKEN not in request.headers:
            return {'error': 'Required Headers missing.'}, 400
        elif request.headers[TOKEN] == '':
            return {'error': "The 'token' parameter can't be empty"}, 400
        elif request.headers[TOKEN]:
            is_token_valid, token_info = okta.introspect_token(request.headers[TOKEN])
            if not is_token_valid:
                return {'error': 'Invalid Token', 'info': token_info}, 403
            print("-----token_info in before_request middleware at the bottom of check_token_header(): -----")
            print(token_info)
            print(token_info['sub'])
            g.user = token_info


@app.after_request
def logging_after_request(response):
    # app.logger.info("---after_request middleware---")
    print("-----In after_request middleware in logging_after_request(response)-----")
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
    print("END-----END-----END-----END-----END-----END-----END-----END-----END-----END-----END-----END\n\n")
    return response

# TecVerify EndPoints Begin

@app.route('/api/v1/secret', methods=['POST'])
@limiter.limit(RATE_LIMIT)
def save_secret():
    print("-----In Save Secret API in save_secret()-----")
    form_data = admin_secret.parse_form_data(request)
    token_info = g.get('user')
    logged_in_Okta_user_id = token_info['sub']
    print("logged_in_Okta_user_id: " + logged_in_Okta_user_id)
    if AUTHORIZE_CLAIM_NAME in token_info and token_info[AUTHORIZE_CLAIM_NAME] and form_data[SECRET]:
        if totp.is_secret_valid(form_data[SECRET]):
            if admin_secret.update_secret(form_data, logged_in_Okta_user_id):
                return {"updated": True}, 200
            else:
                return {"updated": False, "error": "Update Failed !!!"}, 500
        else:
            return {"updated": False, "error": ADMIN_SECRET + " is in invalid format. Try another one."}, 500
    elif form_data[SECRET] is None or not form_data[SECRET]:
        return {'error': "'adminSecret' is missing"}, 400
    else:
        return {'error': 'UnAuthorized !!!'}, 403


@app.route('/api/v1/secret', methods=['GET'])
@limiter.limit(RATE_LIMIT)
def generate_random_secret():
    token_info = g.get('user')
    if AUTHORIZE_CLAIM_NAME in token_info and token_info[AUTHORIZE_CLAIM_NAME]:
        admin_secret = pyotp.random_base32(32)
        return {"adminSecret": admin_secret}, 200
    else:
        return {'error': 'UnAuthorized !!!'}, 403


@app.route('/api/v1/secret/<secret_id>', methods=['DELETE'])
@limiter.limit(RATE_LIMIT)
def delete_secret(secret_id):
    token_info = g.get('user')
    if AUTHORIZE_CLAIM_NAME in token_info and token_info[AUTHORIZE_CLAIM_NAME]:
        secrets_list = admin_secret.read()
        for secret in secrets_list:
            if secret_id in secret.values():
                secrets_list.remove(secret)
                admin_secret.write(secrets_list)
                return {'Deleted': True}, 200
    else:
        return {'error': 'UnAuthorized !!!'}, 403


@app.route('/api/v1/totp', methods=['GET'])
@limiter.limit(RATE_LIMIT)
def get_totp():
    print("-----In TOTP API in get_totp()-----")
    token_info = g.get('user')
    print("-----token_info in get_totp() In TOTP API: -----")
    print(token_info)
    logged_in_Okta_user_id = token_info['sub']
    print("logged_in_Okta_user_id: " + logged_in_Okta_user_id)
    if AUTHORIZE_CLAIM_NAME in token_info:
        secrets_list = admin_secret.read()
        totp_list = totp.generate_totp_for_all_secrets(secrets_list, logged_in_Okta_user_id)
        return jsonify(totp_list), 200
    else:
        return {'error': 'UnAuthorized !!!'}, 403

############
@app.route('/api/v1/hotp/<int:counterParam>', methods=['GET'])
@limiter.limit(RATE_LIMIT)
def get_hotp(counterParam):
    print(counterParam)
    token_info = g.get('user')
    if AUTHORIZE_CLAIM_NAME in token_info:
        secrets_list = admin_secret.read()
        hotp_list = hotp.generate_hotp_for_all_secrets(secrets_list, counterParam)
        return jsonify(hotp_list), 200
    else:
        return {'error': 'UnAuthorized !!!'}, 403
############

if __name__ == '__main__':
    app.run(host="0.0.0.0")
