import json
import os.path
import os
import base64
from random import randint
from datetime import datetime
from logging.config import dictConfig

import pyotp
import requests
from flask_swagger_ui import get_swaggerui_blueprint
from flask import Flask, request, g, jsonify
from flask_cors import CORS

# app specific
app = Flask(__name__)
# config_file = app.config.from_envvar('TEC_CONFIG')
app.config.from_pyfile('config.py')
CORS(app)

#grab config values from file
ISSUER = app.config['ISSUER']
CLIENT_ID = app.config['CLIENT_ID']
SECRETS_FILE = app.config['SECRETS_FILE']
BE_AUTHORIZING_TOKEN = app.config['AUTHORIZING_TOKEN']
AUTHORIZE_CLAIM_NAME = app.config['CLAIM_NAME']
print(app.config)

# logger specific #
level = app.config['LOGGING_LEVEL'] if 'LOGGING_LEVEL' in app.config else 'DEBUG'
max_bytes = int(app.config['LOGGING_MAX_BYTES'] if 'LOGGING_MAX_BYTES' in app.config else 1048576)
backup_count = int(app.config['LOGGING_BACKUP_COUNT'] if 'LOGGING_BACKUP_COUNT' in app.config else 10)

logging_config = dict(
    version = 1,
    formatters = { 'f': {'format': '%(asctime)s %(name)-12s %(levelname)-8s %(message)s'}},
    handlers = {'h': {'class': 'logging.handlers.RotatingFileHandler', 'formatter': 'f',
            'level': level,
            'filename': './logs/logs.log',
            'mode': 'a',
            'maxBytes': max_bytes,
            'backupCount': backup_count}},
    root = {'handlers': ['h'], 'level': level,})
dictConfig(logging_config)
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
ADMIN_SECRET = "admin_secret"
SECRETNAME = "secretname"
ACTIVE = 'active'
ISS = 'iss'
UID = 'uid'
AUD = 'aud'
OPTIONS = 'OPTIONS'
SECRET = 'secret'
ID_LENGTH = 7

# Middlewares
@app.before_request
def check_token_header():
    if request.method == OPTIONS:
        return {}, 200
    if SWAGGER_URL not in request.url:
        if TOKEN not in request.headers:
            return {'error': 'Required Headers missing.'}, 400
        elif request.headers[TOKEN] == '':
            return {'error': 'The \'token\' parameter cant be empty'}, 400
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
    return response

# routes
@app.route('/api/v1/secret', methods=['POST'])
def save_secret():
    form_data = validate_and_retrieve_formdata(request)
    token_info = g.get('user')
    if token_info[AUTHORIZE_CLAIM_NAME] and form_data[SECRET]:
        if is_secret_valid(form_data[SECRET]):
            if update_secret(form_data):
                return {"updated": True}, 200
            else:
                return {"updated": False, "error": "Update Failed. Contact Administrator."}, 500
        else:
            return {"updated": False, "error": ADMIN_SECRET + " is invalid. Try another one."}, 500
    elif form_data[SECRET] is None or not form_data[SECRET]:
        return {'error': '\'admin_secret\' is missing'}, 400
    else:
        return {'error': 'Access Denied.'}, 403


@app.route('/api/v1/secret', methods=['GET'])
def generate_secret():
    token_info = g.get('user')
    if token_info[AUTHORIZE_CLAIM_NAME]:
        admin_secret = pyotp.random_base32(32)
        return {"adminSecret": admin_secret}, 200
    else:
        return {'error': 'Access Denied.'}, 403


@app.route('/api/v1/secret/<secret_id>', methods=['DELETE'])
def delete_secret(secret_id):
    token_info = g.get('user')
    if token_info[AUTHORIZE_CLAIM_NAME]:
        secrets_list = fread()
        for secret in secrets_list:
            if secret_id in secret.values():
                secrets_list.remove(secret)
                fwrite(secrets_list)
                return {'Deleted': True}, 200
    else:
        return {'error': 'Access Denied.'}, 403


@app.route('/api/v1/totp', methods=['GET'])
def get_totp():
    secrets_json = fread()
    if secrets_json is not None:
        totp = generate_totp_for_all_users(secrets_json)
        return jsonify(totp), 200

# helper functions
def introspect(token):
    response = get_token_info(token)
    token_info = response.json()
    if response.status_code == 200:
        return is_valid_token(token_info), token_info
    else:
        return False, token_info


def get_token_info(access_token):
    url = app.config['ISSUER'] + "/v1/introspect?client_id=" + app.config['CLIENT_ID']
    body = {TOKEN: access_token, TOKEN_TYPE_HINT: BE_AUTHORIZING_TOKEN}
    response = requests.post(url, data=body)
    app.logger.info("OKTA INTROSPECT URL: {0}".format(url))
    app.logger.info("OKTA INTROSPECT STATUSCODE: {0}".format(response.status_code))
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


def generate_totp_for_all_users(secrets_json):
    users_list_with_totp = []
    for user in secrets_json:
        totp = generate_totp(user[SECRET])
        users_list_with_totp.append({SECRETNAME: user[SECRETNAME], 'code': totp, 'id': user['id'], 'secretUpdatedAt': user['updatedAt']})
    return users_list_with_totp


def update_secret(form_data):
    secrets_list = fread()
    if secrets_list is not None:
        uid = generate_unique_uid(secrets_list)
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
    range_start = 10**(ID_LENGTH-1)
    range_end = (10**ID_LENGTH)-1
    return str(randint(range_start, range_end))

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
        if not os.path.isfile(SECRETS_FILE):
            fcreate()
        with open(SECRETS_FILE, 'r') as fHandle:
            secrets = json.load(fHandle)
        return secrets
    except Exception as e:
        app.logger.error(e)
        return None


if __name__ == '__main__':
    app.run(host="0.0.0.0")
