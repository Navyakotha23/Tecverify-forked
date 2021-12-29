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
    print("\n\n\nSTART-----START-----START-----START-----START-----START-----START-----START-----START-----START")
    # app.logger.info("---before_request middleware---")
    print("11111111111111111111- In before_request middleware in check_token_header() -11111111111111111111")
    if request.method == OPTIONS:
        return {}, 200
    if SWAGGER_URL not in request.url:
        # print("request")
        # print(request)
        # print("request.method")
        # print(request.method)
        # print("request.url")
        # print(request.url)
        # print("request.headers")
        # print(request.headers)
        #
        # print("request.headers[TOKEN]: ")
        # print(request.headers[TOKEN])
        if TOKEN not in request.headers:
            print("TOKEN not in request.headers")
            g.tokenHeaderMissing = True
            # return {'error': 'Required Headers missing.'}, 400
        elif request.headers[TOKEN] == '':
            print("TOKEN parameter is empty")
            return {'error': "The 'token' parameter can't be empty"}, 400
        elif request.headers[TOKEN]:
            is_token_valid, token_info = okta.introspect_token(request.headers[TOKEN])
            # print("token_info: ")
            # print(token_info)
            print("Okta UserID in token_info: ")
            print(token_info['sub'])
            # print("Token Status: ")
            # print(is_token_valid)
            if not is_token_valid:
                print("Token is not valid")
                return {'error': 'Invalid Token', 'info': token_info}, 403
            else:
                print("Token is valid")
            g.user = token_info
    print("11111111111111111111- Out of before_request middleware in check_token_header() -11111111111111111111")
    

@app.after_request
def logging_after_request(response):
    # app.logger.info("---after_request middleware---")
    print("\n33333333333333333333- In after_request middleware in logging_after_request(response) -33333333333333333333")
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
    print("33333333333333333333- Out of after_request middleware in logging_after_request(response) -33333333333333333333")
    print("END-----END-----END-----END-----END-----END-----END-----END-----END-----END-----END-----END\n\n\n")
    return response

# TecVerify EndPoints Begin

@app.route('/api/v1/secret', methods=['POST'])
@limiter.limit(RATE_LIMIT)
def save_secret():
    print("\n22222222222222222222- In Save Secret API in save_secret() -22222222222222222222")

    tokenMissing = g.get('tokenHeaderMissing')
    if tokenMissing:
        print("token header is missing so need to check if formdata contains Okta User ID")
        form_data = admin_secret.parse_form_data_for_okta_userid(request)
        okta_user_id_in_form_data = form_data['oktaUserId']
        print("okta_user_id_in_form_data: " + okta_user_id_in_form_data)
        if form_data[SECRET] and form_data['oktaUserId']:
            if totp.is_secret_valid(form_data[SECRET]):
                if admin_secret.update_secret(form_data, okta_user_id_in_form_data):
                    print("22222222222222222222- Out of Save Secret API in save_secret() -22222222222222222222")
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
        print("logged_in_Okta_user_id: " + logged_in_Okta_user_id)
        # if AUTHORIZE_CLAIM_NAME in token_info and token_info[AUTHORIZE_CLAIM_NAME] and form_data[SECRET]:
        if form_data[SECRET]:
            if totp.is_secret_valid(form_data[SECRET]):
                if admin_secret.update_secret(form_data, logged_in_Okta_user_id):
                    print("22222222222222222222- Out of Save Secret API in save_secret() -22222222222222222222")
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
    print("\n22222222222222222222- In Generate Secret API in generate_random_secret() -22222222222222222222")
    token_info = g.get('user')
    # if AUTHORIZE_CLAIM_NAME in token_info and token_info[AUTHORIZE_CLAIM_NAME]:
    if True:
        admin_secret = pyotp.random_base32(32)
        print("22222222222222222222- Out of Generate Secret API in generate_random_secret() -22222222222222222222")
        return {"adminSecret": admin_secret}, 200
    else:
        return {'error': 'UnAuthorized !!!'}, 403


@app.route('/api/v1/secret/<secret_id>', methods=['DELETE'])
@limiter.limit(RATE_LIMIT)
def delete_secret(secret_id):
    print("\n22222222222222222222- In Delete Secret API in delete_secret(secret_id) -22222222222222222222")
    token_info = g.get('user')
    # if AUTHORIZE_CLAIM_NAME in token_info and token_info[AUTHORIZE_CLAIM_NAME]:
    if True:
        secrets_list = admin_secret.read()
        for secret in secrets_list:
            if secret_id in secret.values():
                secrets_list.remove(secret)
                admin_secret.write(secrets_list)
                print("22222222222222222222- Out of Delete Secret API in delete_secret(secret_id) -22222222222222222222")
                return {'Deleted': True}, 200
    else:
        return {'error': 'UnAuthorized !!!'}, 403


@app.route('/api/v1/totp', methods=['GET'])
@limiter.limit(RATE_LIMIT)
def get_totp():
    print("\n22222222222222222222- In TOTP API in get_totp() -22222222222222222222")
    token_info = g.get('user')
    # print("token_info: ")
    # print(token_info)
    logged_in_Okta_user_id = token_info['sub']
    print("logged_in_Okta_user_id: " + logged_in_Okta_user_id)
    # if AUTHORIZE_CLAIM_NAME in token_info:
    if True:
        secrets_list = admin_secret.read()
        totp_list = totp.generate_totp_for_all_secrets(secrets_list, logged_in_Okta_user_id)
        print("22222222222222222222- Out of TOTP API in get_totp() -22222222222222222222")
        return jsonify(totp_list), 200
    else:
        print("AUTHORIZE_CLAIM_NAME is not in token_info")
        print("So, I need to send accessToken to userinfo API call to get AUTHORIZE_CLAIM_NAME")
        print("22222222222222222222- Out of TOTP API in get_totp() -22222222222222222222")
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
