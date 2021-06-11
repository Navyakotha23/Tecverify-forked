import json
import os.path
import os
import uuid
import base64
from random import randint
from datetime import datetime
from logging.config import dictConfig

import pyotp
import pyDes
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


# grab config values from file
ISSUER = app.config['ISSUER']
CLIENT_ID = app.config['CLIENT_ID']
SECRETS_FILE = app.config['SECRETS_FILE']
AUTHORIZING_TOKEN = app.config['AUTHORIZING_TOKEN']
AUTHORIZE_CLAIM_NAME = app.config['CLAIM_NAME']
ENABLE_API_RATE_LIMITS = app.config['ENABLE_API_RATE_LIMITS']
# API_RATE_LIMITS = app.config['API_RATE_LIMITS']
WHITELISTED_IPS = app.config['WHITELISTED_IPS']
SALT = app.config['SALT']

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
print(RATE_LIMIT)

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
log_folder = './logs'
if not os.path.exists(log_folder):
    os.makedirs(log_folder)

logging_config = dict(
    version=1,
    formatters={
        'f': {'format': '%(asctime)s %(name)-12s %(levelname)-8s %(message)s'}},
    handlers={'h': {'class': 'logging.handlers.RotatingFileHandler', 'formatter': 'f',
                    'level': level,
                    'filename': './logs/logs.log',
                    'mode': 'a',
                    'maxBytes': max_bytes,
                    'backupCount': backup_count},
              'file': {'class': 'logging.StreamHandler', 'formatter': 'f', 'level': level}},
    root={'handlers': ['h', 'file'], 'level': level, })
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
    if request.method == OPTIONS:
        return {}, 200
    if SWAGGER_URL not in request.url:
        if TOKEN not in request.headers:
            return {'error': 'Required Headers missing.'}, 400
        elif request.headers[TOKEN] == '':
            return {'error': "The 'token' parameter can't be empty"}, 400
        elif request.headers[TOKEN]:
            is_token_valid, token_info = introspect(request.headers[TOKEN])
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
    return response

# routes


@app.route('/api/v1/secret', methods=['POST'])
@limiter.limit(RATE_LIMIT)
def save_secret():
    form_data = validate_and_retrieve_formdata(request)
    token_info = g.get('user')
    if AUTHORIZE_CLAIM_NAME in token_info and token_info[AUTHORIZE_CLAIM_NAME] and form_data[SECRET]:
        if is_secret_valid(form_data[SECRET]):
            if update_secret(form_data):
                return {"updated": True}, 200
            else:
                return {"updated": False, "error": "Update Failed !!!"}, 500
        else:
            return {"updated": False, "error": ADMIN_SECRET + " is invalid. Try another one."}, 500
    elif form_data[SECRET] is None or not form_data[SECRET]:
        return {'error': "'adminSecret' is missing"}, 400
    else:
        return {'error': 'UnAuthorized !!!'}, 403


@app.route('/api/v1/secret', methods=['GET'])
@limiter.limit(RATE_LIMIT)
def generate_secret():
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
        secrets_list = fread()
        for secret in secrets_list:
            if secret_id in secret.values():
                secrets_list.remove(secret)
                fwrite(secrets_list)
                return {'Deleted': True}, 200
    else:
        return {'error': 'UnAuthorized !!!'}, 403


@app.route('/api/v1/totp', methods=['GET'])
@limiter.limit(RATE_LIMIT)
def get_totp():
    token_info = g.get('user')
    if AUTHORIZE_CLAIM_NAME in token_info:
        secrets_json = fread()
        if secrets_json is not None:
            totp = generate_totp_for_all_secrets(secrets_json)
            return jsonify(totp), 200
    else:
        return {'error': 'UnAuthorized !!!'}, 403

# helper functions


def introspect(token):
    response = get_token_info(token)
    token_info = response.json()
    if response.status_code == 200:
        return is_valid_token(token_info), token_info
    else:
        return False, token_info


def get_token_info(token):
    url = ISSUER + "/v1/introspect?client_id=" + CLIENT_ID
    body = {TOKEN: token, TOKEN_TYPE_HINT: AUTHORIZING_TOKEN}
    response = requests.post(url, data=body)
    app.logger.info("OKTA INTROSPECT URL: {0}".format(url))
    app.logger.info(
        "OKTA INTROSPECT STATUSCODE: {0}".format(response.status_code))
    app.logger.info("USER INFO: {0}".format(response.json()))
    return response


def is_valid_token(response):
    if ACTIVE in response:
        app.logger.info("TOKEN STATUS: {0}".format(response[ACTIVE]))
        return response[ACTIVE]
    else:
        app.logger.info("TOKEN STATUS: ACTIVE key Not Found.")
        app.logger.debug("INTROSPECT RESPONSE: {0}".format(response))
        return False


def is_secret_valid(secret):
    try:
        pyotp.TOTP(secret).now()
        return True
    except Exception as e:
        app.logger.error(e)
        return False


def generate_totp(secret):
    try:
        totp = pyotp.TOTP(secret).now()
        return totp
    except Exception as e:
        app.logger.error(e)
        return None


def generate_totp_for_all_secrets(secrets_json):
    secrets_with_totp = []
    for user in secrets_json:
        secret = decrypt_secret(user[SECRET])
        totp = generate_totp(secret)
        secrets_with_totp.append(
            {'id': user['id'], 'otp': totp, SECRETNAME: user[SECRETNAME], 'secretUpdatedAt': user['updatedAt']})
    return secrets_with_totp


def update_secret(form_data):
    secrets_list = fread()
    if secrets_list is not None:
        uid = generate_unique_uid(secrets_list)
        form_data['secret'] = encrypt_secret(form_data['secret'])
        form_data['id'] = uid
        form_data['updatedAt'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        secrets_list.append(form_data)
        return fwrite(secrets_list)
    else:
        return False


def generate_unique_uid(secrets_list):
    uid = generate_id()
    if is_uid_unique(uid, secrets_list):
        return uid
    else:
        return generate_unique_uid(secrets_list)


def generate_id():
    # range_start = 10**(ID_LENGTH-1)
    # range_end = (10**ID_LENGTH)-1
    # return str(randint(range_start, range_end))
    return str(uuid.uuid4())


def is_uid_unique(uid, secrets_list):
    uid_list = [secret['id'] for secret in secrets_list]
    if uid not in uid_list:
        return True
    else:
        return False


def validate_and_retrieve_formdata(req):
    admin_secret = req.form[ADMIN_SECRET] if ADMIN_SECRET in req.form else None
    username = req.form[SECRETNAME] if SECRETNAME in req.form else None
    return {SECRETNAME: username, SECRET: admin_secret}


def fwrite(data):
    try:
        with open(SECRETS_FILE, 'w') as fHandle:
            json.dump(data, fHandle, indent=4)
        return True
    except Exception as e:
        app.logger.error(e)
        return False


def fcreate():
    try:
        default_data = []
        fwrite(default_data)
        return True
    except Exception as e:
        app.logger.error(e)
        return False


def fread():
    try:
        if not os.path.isfile(SECRETS_FILE) or os.stat(SECRETS_FILE).st_size == 0:
            fcreate()
        with open(SECRETS_FILE, 'r') as fHandle:
            secrets = json.load(fHandle)
        return secrets
    except Exception as e:
        app.logger.error(e)
        return None

def encrypt_secret(secret):
    key = pyDes.des(SALT, pyDes.CBC, "\0\0\0\0\0\0\0\0", pad=None, padmode=pyDes.PAD_PKCS5)
    cipher_bytes = key.encrypt(secret)
    cipher_string = str(cipher_bytes)
    return cipher_string

def decrypt_secret(ciphered_secret):
    key = pyDes.des(SALT, pyDes.CBC, "\0\0\0\0\0\0\0\0", pad=None, padmode=pyDes.PAD_PKCS5)
    ciphered_bytes = eval(ciphered_secret)
    deciphered_secret = key.decrypt(ciphered_bytes).decode()
    return deciphered_secret


if __name__ == '__main__':
    app.run(host="0.0.0.0")
