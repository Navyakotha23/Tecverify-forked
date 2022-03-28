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

ENCRYPTED_API_KEY = app.config['ENCRYPTED_API_KEY']
API_KEY_SALT = app.config['API_KEY_SALT']

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

# DECRYPTED_API_KEY = crypt_obj.decryptAPIkey(ENCRYPTED_API_KEY, API_KEY_SALT)
# # tecnics-demoTenant 
DECRYPTED_API_KEY = "00Bh5ACdw92LhpfdoOlyzCIVIW0tpzeB8ylbNOvdZN"
# # tecnics-dev Tenant 
# # DECRYPTED_API_KEY = "00ovAgZhFKU3QoiU4w_yqJo55qUBfNTiSdXK9HmxI_"
# print("\nDECRYPTED_API_KEY: ", DECRYPTED_API_KEY, "\n")

admin_secret = AdminSecret(SECRETS_FILE, crypt_obj, MS_SQL_SERVER, MS_SQL_USERNAME, MS_SQL_PASSWORD, DATABASE_NAME, TABLE_NAME, AUTOSAVED_SECRET_USERNAME_HEAD, DATABASE_TYPE, SHOW_LOGS)
totp = TOTP(crypt_obj, SHOW_LOGS)
okta = OktaOperations(CLIENT_ID, ISSUER, AUTHORIZING_TOKEN, AUTHORIZE_CLAIM_NAME, DECRYPTED_API_KEY, SHOW_LOGS)

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
SECRET = 'secretKey'
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
        if not secrets_list:
            print("No secret in secrets_list")
            return {"ERROR": "Secret List is Empty"}, 400
        else:     
            for secret in secrets_list:
                if secret_id in secret.values():
                    if DATABASE_TYPE == "json":
                        secrets_list.remove(secret)
                        admin_secret.write(secrets_list)
                    elif DATABASE_TYPE == "mssql":
                        # admin_secret.delete_secret(secret_id, CONNECTION_OBJECT)
                        admin_secret.delete_secret(secret_id)

                    if secret['oktaFactorId'] == "":
                            print("Manually Saved Secret Deleted")
                            return {'Deleted': True}, 200
                    else:
                        delete_factor_response = okta.call_delete_factor_API(secret['oktaUserId'], secret['oktaFactorId'])
                        if delete_factor_response.status_code == 204:
                            print("Auto Saved Secret Deleted and Okta TOTP Factor deleted")
                            return {'Deleted both Secret and Okta TOTP factor': True}, 200
            return {"ERROR": "Secret with given secretId is not found"}, 400
    else:
        return {'error': 'UnAuthorized !!!'}, 403


####################################################################################################################
# @app.route('/api/v1/totp', methods=['GET'])
# @limiter.limit(RATE_LIMIT)
# def get_totp():
#     print("TOTP API")
#     token_info = g.get('user')
#     logged_in_Okta_user_id = token_info['sub']
#     # if AUTHORIZE_CLAIM_NAME in token_info:
#     if True:
#         # secrets_list = admin_secret.read(CONNECTION_OBJECT)
#         secrets_list = admin_secret.read()
#         totp_list = totp.generate_totp_for_all_secrets(secrets_list, logged_in_Okta_user_id)
#         return jsonify(totp_list), 200
#     else:
#         if SHOW_LOGS: print("AUTHORIZE_CLAIM_NAME is not in token_info")
#         if SHOW_LOGS: print("So, I need to send accessToken to userinfo API call to get AUTHORIZE_CLAIM_NAME")
#         if SHOW_LOGS: print("22222222222222222222- Out of TOTP API in get_totp() -22222222222222222222")
#         return {'error': 'UnAuthorized !!!'}, 403

@app.route('/api/v1/totp', methods=['GET'])
@limiter.limit(RATE_LIMIT)
def get_totp():
    print("TOTP API")
    token_info = g.get('user')
    logged_in_Okta_user_id = token_info['sub']

    secrets_list = admin_secret.read()

    if not secrets_list:
            print("No secret in secrets_list")
    else:     
        for secret in secrets_list:
            # print("secret['oktaFactorId']: ", secret['oktaFactorId'])
            if secret['oktaUserId'] == logged_in_Okta_user_id and secret['oktaFactorId'] != "":
                get_factor_response = okta.call_get_factor_API(logged_in_Okta_user_id, secret['oktaFactorId'])
                # print("get_factor_response.json(): ", get_factor_response.json())

                if get_factor_response.status_code == 200:
                    print("TOTP factor is Active. No need to delete the secret.")
                elif get_factor_response.status_code == 404:
                    print("TOTP factor is Inactive. So, deleting the secret.")
                    if DATABASE_TYPE == "json":
                        secrets_list.remove(secret)
                        admin_secret.write(secrets_list)
                    elif DATABASE_TYPE == "mssql":
                        # admin_secret.delete_secret(secret_id, CONNECTION_OBJECT)
                        admin_secret.delete_secret(secret['secretId'])
    
    secrets_list1 = admin_secret.read()             
    totp_list = totp.generate_totp_for_all_secrets(secrets_list1, logged_in_Okta_user_id)
    return jsonify(totp_list), 200
####################################################################################################################


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
        # admin_secret.auto_save_secret(oktaSharedSecret, logged_in_Okta_user_id, logged_in_username) # For saving secret in TecVerify with logged in username
        admin_secret.auto_save_secret(oktaSharedSecret, logged_in_Okta_user_id, logged_in_username, oktaFactorID) # For saving secret in TecVerify with logged in username and oktaFactorID
        is_enroll = okta.activate_TOTP_factor(logged_in_Okta_user_id, oktaFactorID, generatedOTP)
        if is_enroll: 
            print("Auto enrolling the user to TOTP factor from TecVerify")
            return {"enrolled": True}, 200
        else:
            return {"enrolled": False}, 400
    elif enroll_response.status_code == 400:
        if enroll_info['errorCode'] == "E0000001":
            print("A factor of this type is already set up.")
        return {"errorSummary": "A factor of this type is already set up."}


@app.route('/api/v1/deleteTOTPfactorIfEnrolledFromOktaVerify', methods=['GET'])
@limiter.limit(RATE_LIMIT)
def checkIfAlreadyEnrolledToOktaVerify():
    print("deleteTOTPfactorIfEnrolledFromOktaVerify API")
    token_info = g.get('user')
    logged_in_Okta_user_id = token_info['sub']

    secrets_list = admin_secret.read()
    usersAutoEnrolledFromTecVerify = 0
    usersAutoEnrolledFromTecVerify_excludingLoginUser = 0
    for secret in secrets_list:
        if secret['oktaFactorId'] != "":
            usersAutoEnrolledFromTecVerify += 1
            # print("Counting usersAutoEnrolledFromTecVerify: ", usersAutoEnrolledFromTecVerify)
        if secret['oktaFactorId'] != "" and secret['oktaUserId'] != logged_in_Okta_user_id:
            usersAutoEnrolledFromTecVerify_excludingLoginUser += 1
            # print("Counting usersAutoEnrolledFromTecVerify_excludingLoginUser: ", usersAutoEnrolledFromTecVerify_excludingLoginUser)
    print("usersAutoEnrolledFromTecVerify: ", usersAutoEnrolledFromTecVerify)
    print("usersAutoEnrolledFromTecVerify_excludingLoginUser: ", usersAutoEnrolledFromTecVerify_excludingLoginUser)

    list_factors_response = okta.call_list_factors_API(logged_in_Okta_user_id)
    factors_list = list_factors_response.json()
    # print("\nfactors_list: ", factors_list, "\n")
    for factor in factors_list:
        # print("factor['id']: ", factor['id'])
        # print("factor['factorType']: ", factor['factorType'])
        if factor['factorType'] == "token:software:totp":
            if not secrets_list:
                    print("No secret in secrets_list")
                    delete_factor_response = okta.call_delete_factor_API(logged_in_Okta_user_id, factor['id'])
                    if delete_factor_response.status_code == 204:
                        print("Okta TOTP Factor enrolled from OktaVerify is deleted")
                        return {'Deleted Okta TOTP Factor enrolled from OktaVerify': True}, 200
            else:     
                for secret in secrets_list:
                    # print("factor['id']: ", factor['id'])
                    # print("secret['oktaFactorId']: ", secret['oktaFactorId'])
                    if secret['oktaFactorId'] != "" and secret['oktaUserId'] == logged_in_Okta_user_id:
                        if factor['id'] == secret['oktaFactorId']:
                            print("factor IDs matched. So, user is enrolled to TOTP factor from TecVerify.")
                            # print("factor['id']: ", factor['id'])
                            # print("secret['oktaFactorId']: ", secret['oktaFactorId'])
                            return {'User is already Auto Enrolled to Okta from TecVerify': True}, 200
                        else: 
                            print("factor IDs didn't match. So, user is enrolled to TOTP factor from other TecVerify Build or OktaVerify.")
                            delete_factor_response = okta.call_delete_factor_API(logged_in_Okta_user_id, factor['id'])
                            if delete_factor_response.status_code == 204:
                                print("Okta TOTP Factor enrolled from other TecVerify Build or OktaVerify is deleted")
                                return {'Deleted Okta TOTP Factor enrolled from other TecVerify Build or OktaVerify': True}, 200
                        #     print("Offline scenario. User is logged out of TecVerify.")
                        #     print("This issue occurs when we do Development and Production in the same tenant.")
                        #     print("Because for Development and Production, secrets.json file is different.")
                        #     print("factor IDs didn't match. So, user is enrolled to TOTP factor from other Build.")
                        #     print("i.e. After Auto enrolling here, user logged out here and login to TecVerify from other build.")
                        #     print("So, he is auto enrolled to TOTP factor from other TecVerify build.")
                        #     print("When no auto enrollment is done in that build for that logged in user.")
                        #     print("So, deleting TOTP factor auto enrolled from other TecVerify Build.")
                        #     or
                        #     print("factor IDs didn't match. So, user is enrolled to TOTP factor from other Build.")
                        #     print("i.e. After auto enrolling here, user logged out from here and deleted TOTP factor in Okta and enrolled it from OktaVerify.")
                        #     print("As the user is in offline, changes didn't reflect in json file.")
                        #     print("So, while logging in again, TecVerify considers the user as an auto-enrolled user")
                        #     print("So, deleting TOTP factor enrolled from OktaVerify.")
                        # 
                        #     Need to delete the previous auto-enrolled secret here itself. Instead of deleting inactive factor's secret in TOTP API.
                
                if usersAutoEnrolledFromTecVerify == usersAutoEnrolledFromTecVerify_excludingLoginUser:
                    print("No auto enrollment is done in TecVerify for this logged in user.")
                    delete_factor_response = okta.call_delete_factor_API(logged_in_Okta_user_id, factor['id'])
                    if delete_factor_response.status_code == 204:
                        print("Okta TOTP Factor enrolled from OktaVerify is deleted")
                        return {'Deleted Okta TOTP Factor enrolled from OktaVerify': True}, 200

    print("This user is not enrolled to Okta TOTP factor")
    return {'Okta TOTP Factor is not enrolled for this user': True}, 200


if __name__ == '__main__':
    # app.run(host="0.0.0.0")
    app.run(host="0.0.0.0", ssl_context='adhoc') # feb3: This is for running backend devlpmnt server in secure context(HTTPS)


################## This is included in TOTP API ###############################################################
@app.route('/api/v1/deleteSecretIfTOTPfactorIsDeletedInOkta', methods=['GET'])
@limiter.limit(RATE_LIMIT)
def deleteSecretIfTOTPfactorIsInactive():
    print("deleteSecretIfTOTPfactorIsDeletedInOkta API")
    token_info = g.get('user')
    logged_in_Okta_user_id = token_info['sub']

    secrets_list = admin_secret.read()

    if not secrets_list:
            print("No secret in secrets_list")
            return {"ERROR": "Secret List is Empty"}, 400
    else:     
        for secret in secrets_list:
            # print("secret['oktaFactorId']: ", secret['oktaFactorId'])
            if secret['oktaUserId'] == logged_in_Okta_user_id and secret['oktaFactorId'] != "":
                get_factor_response = okta.call_get_factor_API(logged_in_Okta_user_id, secret['oktaFactorId'])
                # print("get_factor_response.json(): ", get_factor_response.json())

                if get_factor_response.status_code == 200:
                    print("TOTP factor is Active. No need to delete the secret.")
                elif get_factor_response.status_code == 404:
                    print("TOTP factor is Inactive. So, deleting the secret.")
                    if DATABASE_TYPE == "json":
                        secrets_list.remove(secret)
                        admin_secret.write(secrets_list)
                    elif DATABASE_TYPE == "mssql":
                        # admin_secret.delete_secret(secret_id, CONNECTION_OBJECT)
                        admin_secret.delete_secret(secret['secretId'])

        return {"SUCCESS": "Secret List is not Empty"}, 200
###############################################################################################################

