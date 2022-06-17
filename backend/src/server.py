import os.path
import os
from logging.config import dictConfig

from crypto import Crypto
from totpGenerator import TOTP_Generator
from secretKeyGenerator import SecretKey_Generator
from oktaAPIs import OktaAPIs
from jsonDB import JSON_DB
from mssqlDB import MSSQL_DB

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
CLIENT_ID = app.config['CLIENT_ID']
ISSUER = app.config['ISSUER']
AUTHORIZE_CLAIM_NAME = app.config['CLAIM_NAME']
AUTHORIZING_TOKEN = app.config['AUTHORIZING_TOKEN']
ENCRYPTED_API_KEY = app.config['ENCRYPTED_API_KEY']
API_KEY_SALT = app.config['API_KEY_SALT']


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

crypt_obj = Crypto(SALT)
DECRYPTED_API_KEY = crypt_obj.decryptAPIkey(ENCRYPTED_API_KEY, API_KEY_SALT)

SECRET_NAME_KEY_IN_REQUEST_FORM = "adminScrtName" # In home.jsx(FE) and in docs.json(BE Swagger) also this should be same
SECRET_KEY_KEY_IN_REQUEST_FORM = "adminScrtKey" # In home.jsx(FE) and in docs.json(BE Swagger) also this should be same
OKTA_USER_ID_KEY_IN_REQUEST_FORM = "adminOktaUserId"

if(DATABASE_TYPE == "json"):
    db_obj = JSON_DB(SECRETS_FILE, crypt_obj, AUTOSAVED_SECRET_USERNAME_HEAD, SECRET_NAME, SECRET_KEY, OKTA_USER_ID, SECRET_ID, SECRET_UPDATED_AT, OKTA_FACTOR_ID, SECRET_NAME_KEY_IN_REQUEST_FORM, SECRET_KEY_KEY_IN_REQUEST_FORM, OKTA_USER_ID_KEY_IN_REQUEST_FORM, SHOW_LOGS)
elif(DATABASE_TYPE == "mssql"):
    db_obj = MSSQL_DB(crypt_obj, MS_SQL_SERVER, MS_SQL_USERNAME, MS_SQL_PASSWORD, DATABASE_NAME, TABLE_NAME, AUTOSAVED_SECRET_USERNAME_HEAD, SECRET_NAME, SECRET_KEY, OKTA_USER_ID, SECRET_ID, SECRET_UPDATED_AT, OKTA_FACTOR_ID, SECRET_NAME_KEY_IN_REQUEST_FORM, SECRET_KEY_KEY_IN_REQUEST_FORM, OKTA_USER_ID_KEY_IN_REQUEST_FORM, SHOW_LOGS)

totp_obj = TOTP_Generator(crypt_obj, SECRET_NAME, SECRET_KEY, OKTA_USER_ID, SECRET_ID, SECRET_UPDATED_AT, SHOW_LOGS)
secret_obj = SecretKey_Generator()
okta_obj = OktaAPIs(CLIENT_ID, ISSUER, AUTHORIZING_TOKEN, AUTHORIZE_CLAIM_NAME, DECRYPTED_API_KEY, SHOW_LOGS)

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
ACTIVE = 'active'
ISS = 'iss'
UID = 'uid'
AUD = 'aud'
OPTIONS = 'OPTIONS'
ID_LENGTH = 12
# CONNECTION_OBJECT = db_obj.establish_db_connection()


# Middlewares

@app.before_request
def check_token_header():
    print("\n\n\n----------Start request----------")
    if request.method == OPTIONS:
        return {}, 200
    if SWAGGER_URL not in request.url:
        if TOKEN not in request.headers:
            if 'secret' in request.url and request.method == 'POST':
                # print("request.url: ", request.url)
                # print("request.method: ", request.method)
                g.tokenHeaderMissing = True
            else:
                return {'error': 'Required Headers missing.'}, 400
        elif request.headers[TOKEN] == '':
            return {'error': "The 'token' parameter can't be empty"}, 400
        elif request.headers[TOKEN]:
            is_token_valid, token_info = okta_obj.introspect_token(request.headers[TOKEN])
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

@app.route('/api/v1/deleteTOTPfactorIfEnrolledFromOktaVerify', methods=['DELETE'])
@limiter.limit(RATE_LIMIT)
def checkIfAlreadyEnrolledToOktaVerify():
    print("deleteTOTPfactorIfEnrolledFromOktaVerify API")
    token_info = g.get('user')
    logged_in_Okta_user_id = token_info['sub']

    secrets_list = db_obj.read()
    usersAutoEnrolledFromTecVerify = 0
    usersAutoEnrolledFromTecVerify_excludingLoginUser = 0
    for secret in secrets_list:
        if secret[OKTA_FACTOR_ID] != "":
            usersAutoEnrolledFromTecVerify += 1
        if secret[OKTA_FACTOR_ID] != "" and secret[OKTA_USER_ID] != logged_in_Okta_user_id:
            usersAutoEnrolledFromTecVerify_excludingLoginUser += 1
    print("usersAutoEnrolledFromTecVerify: ", usersAutoEnrolledFromTecVerify)
    print("usersAutoEnrolledFromTecVerify_excludingLoginUser: ", usersAutoEnrolledFromTecVerify_excludingLoginUser)

    list_factors_response = okta_obj.call_list_factors_API(logged_in_Okta_user_id)
    if list_factors_response.status_code == 401:
        if list_factors_response.json()['errorCode'] == "E0000011":
            print("API token provided is invalid. So, cannot get factors list.")
        return {"errorSummary": "Invalid API token provided. So, cannot get factors list."}, 400
    elif list_factors_response.status_code == 403:
        if list_factors_response.json()['errorCode'] == "E0000006":
            print("This user is not in the group for which API token is generated. So, cannot get factors list.")
        return {"errorSummary": "Current user is not in the group for which API token is generated. So, cannot get factors list."}, 400
    
    # list_factors_response = okta_obj.call_list_factors_API(logged_in_Okta_user_id)
    # print("list_factors_response.status_code: ", list_factors_response.status_code)
    # if(list_factors_response.status_code == 401 or 403):
    #     return okta_obj.list_factors(logged_in_Okta_user_id)

    factors_list = list_factors_response.json()
    for factor in factors_list:
        if factor['factorType'] == "token:software:totp":
            if not secrets_list:
                    print("No secret in secrets_list")
                    return okta_obj.delete_factor(logged_in_Okta_user_id, factor['id'])
            else:     
                for secret in secrets_list:
                    if secret[OKTA_FACTOR_ID] != "" and secret[OKTA_USER_ID] == logged_in_Okta_user_id:
                        if factor['id'] == secret[OKTA_FACTOR_ID]:
                            print("factor IDs matched. So, user is enrolled to TOTP factor from TecVerify.")
                            return {'User is already Auto Enrolled to Okta from TecVerify': True}, 200
                        else:
                            # factor IDs didn't match. Previouly TecVerify enrolled TOTP factor got deleted and new factor got enrolled.
                            print("factor IDs didn't match. So, user is enrolled to TOTP factor from other TecVerify Build or OktaVerify.")
                            return okta_obj.delete_factor(logged_in_Okta_user_id, factor['id'])
                            
                if usersAutoEnrolledFromTecVerify == usersAutoEnrolledFromTecVerify_excludingLoginUser:
                    print("No auto enrollment is done in TecVerify for this logged in user.")
                    return okta_obj.delete_factor(logged_in_Okta_user_id, factor['id'])

    print("This user is not enrolled to Okta TOTP factor")
    return {'Okta TOTP Factor is not enrolled for this user': True}, 200


@app.route('/api/v1/deleteSecretIfTOTPfactorIsDeletedInOkta', methods=['DELETE'])
@limiter.limit(RATE_LIMIT)
def deleteSecretIfTOTPfactorIsInactive():
    print("deleteSecretIfTOTPfactorIsDeletedInOkta API")
    token_info = g.get('user')
    logged_in_Okta_user_id = token_info['sub']

    secrets_list = db_obj.read()

    if not secrets_list:
        print("No secret in secrets_list")
        return {"Exception": "Secret List is Empty"}, 200
    else:     
        for secret in secrets_list:
            if secret[OKTA_USER_ID] == logged_in_Okta_user_id and secret[OKTA_FACTOR_ID] != "":
                get_factor_response = okta_obj.call_get_factor_API(logged_in_Okta_user_id, secret[OKTA_FACTOR_ID])
                if get_factor_response.status_code == 404:
                    db_obj.delete_secret(secret[SECRET_ID])
                
                return okta_obj.get_factor(logged_in_Okta_user_id, secret[OKTA_FACTOR_ID])
                
        return {"SUCCESS": "Secret List is not Empty"}, 200


@app.route('/api/v1/autoEnroll', methods=['POST'])
@limiter.limit(RATE_LIMIT)
def enrollToTecVerify():
    print("autoEnroll API")
    token_info = g.get('user')
    logged_in_Okta_user_id = token_info['sub']
    logged_in_username = token_info['username'].split('@', 1)[0]
    enroll_response = okta_obj.call_enroll_okta_verify_TOTP_factor_API(logged_in_Okta_user_id)
    enroll_info = enroll_response.json()

    if enroll_response.status_code == 200:
        oktaFactorID = enroll_info['id']
        oktaSharedSecret = enroll_info['_embedded']['activation']['sharedSecret']
        generatedOTP = totp_obj.generate_totp(oktaSharedSecret)
        # db_obj.auto_save_secret(oktaSharedSecret, logged_in_Okta_user_id, CONNECTION_OBJECT) # For saving secret in TecVerify
        db_obj.auto_save_secret(oktaSharedSecret, logged_in_Okta_user_id, logged_in_username, oktaFactorID) # For saving secret in TecVerify with logged in username and oktaFactorID
        return okta_obj.activate_TOTP_factor(logged_in_Okta_user_id, oktaFactorID, generatedOTP)
        
    return okta_obj.enroll_okta_verify_TOTP_factor(logged_in_Okta_user_id)


@app.route('/api/v1/totp', methods=['GET'])
@limiter.limit(RATE_LIMIT)
def get_totp():
    print("TOTP API")
    token_info = g.get('user')
    logged_in_Okta_user_id = token_info['sub']
    # if AUTHORIZE_CLAIM_NAME in token_info:
    secrets_list = db_obj.read()             
    totp_list = totp_obj.generate_totp_for_login_user(secrets_list, logged_in_Okta_user_id)
    return jsonify(totp_list), 200
    # else:
    #     return {'error': 'UnAuthorized !!!'}, 403


@app.route('/api/v1/secret/<secret_id>', methods=['DELETE'])
@limiter.limit(RATE_LIMIT)
def delete_secret(secret_id):
    print("Delete Secret API")
    token_info = g.get('user')
    # if AUTHORIZE_CLAIM_NAME in token_info and token_info[AUTHORIZE_CLAIM_NAME]:
    deleteManuallySavedSecret = False
    deleteAutoSavedSecret = False
    # secrets_list = db_obj.read(CONNECTION_OBJECT)
    secrets_list = db_obj.read()
    if not secrets_list:
        print("No secret in secrets_list")
        return {"ERROR": "Secret List is Empty"}, 400
    else:     
        for secret in secrets_list:
            if secret_id in secret.values():
                if secret[OKTA_FACTOR_ID] == "":
                    deleteManuallySavedSecret = True
                else:
                    delete_factor_response = okta_obj.call_delete_factor_API(secret[OKTA_USER_ID], secret[OKTA_FACTOR_ID])
                    if delete_factor_response.status_code == 204:
                        print("Auto Enrolled Okta TOTP Factor deleted")
                        deleteAutoSavedSecret = True
                    elif delete_factor_response.status_code == 401:
                        if delete_factor_response.json()['errorCode'] == "E0000011":
                            print("API token provided is invalid. So, cannot delete the Factor in Okta. So, not deleting the secret.")
                        return {"errorSummary": "Invalid API token provided. So, cannot delete the Factor in Okta. So, not deleting the secret."},400
                    elif delete_factor_response.status_code == 403:
                        if delete_factor_response.json()['errorCode'] == "E0000006":
                            print("Current user is the Super admin. Group admin API token cannot delete the factor of Super admin user. So, not deleting the secret.")
                        return {"errorSummary": "Current user is the Super admin user. He has to delete the TOTP factor in Okta to delete secret in TecVerify."},400
                    # else:
                    #     return okta_obj.delete_factor(secret[OKTA_USER_ID], secret[OKTA_FACTOR_ID])

                if deleteManuallySavedSecret or deleteAutoSavedSecret:
                    db_obj.delete_secret(secret_id)

                if deleteManuallySavedSecret:
                    print("Manually Saved Secret Deleted")
                    return {'Deleted Manually Saved Secret': True}, 200
                elif deleteAutoSavedSecret:
                    print("Auto Saved Secret Deleted")
                    return {'Deleted both Auto Saved Secret and Auto Enrolled Okta TOTP factor': True}, 200

        return {"ERROR": "Secret with given " + secret_id + " is not found"}, 400
    # else:
    #     return {'error': 'UnAuthorized !!!'}, 403


@app.route('/api/v1/secret', methods=['GET'])
@limiter.limit(RATE_LIMIT)
def generate_random_secret():
    print("Generate Secret API")
    token_info = g.get('user')
    # if AUTHORIZE_CLAIM_NAME in token_info and token_info[AUTHORIZE_CLAIM_NAME]:
    return secret_obj.generate_secret()
    # else:
    #     return {'error': 'UnAuthorized !!!'}, 403


@app.route('/api/v1/secret', methods=['POST'])
@limiter.limit(RATE_LIMIT)
def save_secret():
    print("Save Secret API")
    tokenMissing = g.get('tokenHeaderMissing')
    if tokenMissing:
        neededOktaUserIDinRequestForm = True
        form_data = db_obj.parse_form_data(request, neededOktaUserIDinRequestForm)
        okta_user_id_in_form_data = form_data[OKTA_USER_ID]
        if form_data[SECRET_NAME] and form_data[SECRET_KEY] and form_data[OKTA_USER_ID]:
            if secret_obj.is_secret_valid(form_data[SECRET_KEY]):
                # if db_obj.update_secret(form_data, okta_user_id_in_form_data, CONNECTION_OBJECT):
                if db_obj.update_secret(form_data, okta_user_id_in_form_data):
                    return {"updated": True}, 200
                else:
                    return {"updated": False, "error": "Update Failed !!!"}, 500
            else:
                return {"updated": False, "error": SECRET_KEY_KEY_IN_REQUEST_FORM + " is in invalid format. Try another one."}, 500
        elif form_data[SECRET_NAME] is None or not form_data[SECRET_NAME]:
            return {'error': "Secret Name is missing"}, 400
        elif form_data[SECRET_KEY] is None or not form_data[SECRET_KEY]: # if secret key is empty or key itself is not there
            return {'error': "Admin Secret is missing"}, 400
        elif form_data[OKTA_USER_ID] is None or not form_data[OKTA_USER_ID]:
            return {'error': "Okta User ID is missing"}, 400
    else:
        neededOktaUserIDinRequestForm = False
        form_data = db_obj.parse_form_data(request, neededOktaUserIDinRequestForm)
        token_info = g.get('user')
        logged_in_Okta_user_id = token_info['sub']
        # if AUTHORIZE_CLAIM_NAME in token_info and token_info[AUTHORIZE_CLAIM_NAME] and form_data[SECRET_KEY]:
        if form_data[SECRET_NAME] and form_data[SECRET_KEY]:
            if secret_obj.is_secret_valid(form_data[SECRET_KEY]):
                # if db_obj.update_secret(form_data, logged_in_Okta_user_id, CONNECTION_OBJECT):
                if db_obj.update_secret(form_data, logged_in_Okta_user_id):
                    return {"updated": True}, 200
                else:
                    return {"updated": False, "error": "Update Failed !!!"}, 500
            else:
                return {"updated": False, "error": SECRET_KEY_KEY_IN_REQUEST_FORM + " is in invalid format. Try another one."}, 500
        elif form_data[SECRET_NAME] is None or not form_data[SECRET_NAME]:
            return {'error': "Secret Name is missing"}, 400
        elif form_data[SECRET_KEY] is None or not form_data[SECRET_KEY]:
            return {'error': "Admin Secret is missing"}, 400
        # else:
        #     return {'error': 'UnAuthorized !!!'}, 403


if __name__ == '__main__':
    # app.run(host="0.0.0.0")
    app.run(host="0.0.0.0", ssl_context='adhoc') # This is for running backend devlpmnt server in secure context(HTTPS)

