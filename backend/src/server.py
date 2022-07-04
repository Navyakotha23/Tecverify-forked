import requests
from flask import Flask, request, g, jsonify
from flask_cors import CORS


from constants import Constants
from envVars import EnvVars
from be_swagger import BE_SWAGGER
from be_logger import BE_LOGGER
from rateLimits import RATE_LIMITS
from crypto import Crypto
from totpGenerator import TOTP_Generator
from secretKeyGenerator import SecretKey_Generator
from oktaAPIs import OktaAPIs
from uniqueIdGenerator import UniqueId_Generator
from requestForm import RequestForm
from jsonDB import JSON_DB
from mssqlDB import MSSQL_DB


# app specific #
app = Flask(__name__)
app.config.from_pyfile('config.py')
CORS(app)
# end app specific #


# swagger specific #
swagger_obj = BE_SWAGGER(app)
swagger_obj.prepare_swagger_UI_for_BE()
# end swagger specific #


# logger specific #
logger_obj = BE_LOGGER(app)
logger_obj.implement_logging_for_BE()
# end logger specifc #


# Begin Rate Limiter
rateLimits_obj = RATE_LIMITS(app)
limiter =  rateLimits_obj.prepare_limiter_obj()
RATE_LIMIT = rateLimits_obj.construct_rate_limit() if EnvVars.ENABLE_API_RATE_LIMITS else None
# print("RATE_LIMIT: ", RATE_LIMIT)
# End Rate Limiter


# Objects Creation #
crypt_obj = Crypto(EnvVars.SALT)
idGenerator_obj = UniqueId_Generator()

if(EnvVars.DATABASE_TYPE == "json"):
    db_obj = JSON_DB(idGenerator_obj, crypt_obj, EnvVars.SECRETS_FILE)
elif(EnvVars.DATABASE_TYPE == "mssql"):
    mssql_conn = MSSQL_DB.establish_db_connection()
    db_obj = MSSQL_DB(idGenerator_obj, crypt_obj, mssql_conn, app)

DECRYPTED_API_KEY = crypt_obj.decryptAPIkey(EnvVars.ENCRYPTED_API_KEY, EnvVars.API_KEY_SALT)
okta_obj = OktaAPIs(DECRYPTED_API_KEY)

totpGenerator_obj = TOTP_Generator(crypt_obj, EnvVars.SHOW_LOGS)
requestForm_obj = RequestForm()
secretGenerator_obj = SecretKey_Generator()
# end Objects Creation #


@limiter.request_filter
def ip_whitelist():
    # print("request.remote_addr : ", request.remote_addr)
    # print("eval(EnvVars.WHITELISTED_IPS) : ", eval(EnvVars.WHITELISTED_IPS))
    # print(request.remote_addr in eval(EnvVars.WHITELISTED_IPS), "\n")
    return request.remote_addr in eval(EnvVars.WHITELISTED_IPS)


# Middlewares #
@app.before_request
def check_token_header():
    print("\n\n\n----------Start request----------")
    if request.method == Constants.OPTIONS:
        return {}, 200
    if Constants.SWAGGER_URL not in request.url:
        if Constants.TOKEN not in request.headers:
            if 'notProtectedByIdToken_saveSecret' in request.url and request.method == Constants.POST:
                # print("request.url: ", request.url)
                # print("request.method: ", request.method)
                g.tokenHeaderMissing = True
            else:
                # return {'error': 'Required Headers missing.'}, 400
                return {'error': 'Token is missing in headers.'}, 400
        elif request.headers[Constants.TOKEN] == '':
            return {'error': "The 'token' parameter can't be empty"}, 400
        elif request.headers[Constants.TOKEN]:
            is_token_valid, token_info = okta_obj.introspect_token(request.headers[Constants.TOKEN])
            if not is_token_valid:
                return {'error': 'Invalid Token', 'info': token_info}, 403
            g.user = token_info   
            g.loggedInUserName = token_info[Constants.USERNAME].split('@', 1)[0] 
            # print("token_info.keys(): ", token_info.keys())
            if EnvVars.AUTHORIZE_TOKEN_TYPE.lower() == Constants.ID_TOKEN:
                if token_info[Constants.AUD] == EnvVars.CLIENT_ID:
                    g.loggedInOktaUserId = token_info[Constants.SUB]
                else:
                    if 'deleteTOTPfactorIfEnrolledFromOktaVerify' in request.url and request.method == Constants.DELETE:
                        g.errorOccured = "AUTHORIZE_TOKEN_TYPE is idToken in BE but accessToken is passed from FE. AUTHORIZE_TOKEN_TYPE should be same in both FE and BE."
                    else:
                        return {'error': 'AUTHORIZE_TOKEN_TYPE is idToken in BE but accessToken is passed from FE. AUTHORIZE_TOKEN_TYPE should be same in both FE and BE.'}, 400
            elif EnvVars.AUTHORIZE_TOKEN_TYPE.lower() == Constants.ACCESS_TOKEN:
                if Constants.CLIENT_ID in token_info.keys():
                    g.loggedInOktaUserId = token_info[Constants.UID]
                else:
                    if 'deleteTOTPfactorIfEnrolledFromOktaVerify' in request.url and request.method == Constants.DELETE:
                        g.errorOccured = "AUTHORIZE_TOKEN_TYPE is accessToken in BE but idToken is passed from FE. AUTHORIZE_TOKEN_TYPE should be same in both FE and BE."
                    else:
                        return {'error': 'AUTHORIZE_TOKEN_TYPE is accessToken in BE but idToken is passed from FE. AUTHORIZE_TOKEN_TYPE should be same in both FE and BE.'}, 400


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
# end Middlewares #


# TecVerify EndPoints #
@app.route('/api/v1/deleteTOTPfactorIfEnrolledFromOktaVerify', methods=['DELETE'])
@limiter.limit(RATE_LIMIT)
def checkIfAlreadyEnrolledToOktaVerify():
    print("deleteTOTPfactorIfEnrolledFromOktaVerify API")
    # token_info = g.get('user')
    logged_in_Okta_user_id = g.get('loggedInOktaUserId')

    # This is for showing alert in FE.
    if g.get('errorOccured'):
        return {"errorSummary": g.get('errorOccured')}, 400
    
    secrets_list = db_obj.read()
    usersAutoEnrolledFromTecVerify = 0
    usersAutoEnrolledFromTecVerify_excludingLoginUser = 0
    for secret in secrets_list:
        if secret[EnvVars.OKTA_FACTOR_ID] != "":
            usersAutoEnrolledFromTecVerify += 1
        if secret[EnvVars.OKTA_FACTOR_ID] != "" and secret[EnvVars.OKTA_USER_ID] != logged_in_Okta_user_id:
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
        if factor[Constants.FACTOR_TYPE] == Constants.TOTP_FACTOR:
            if not secrets_list:
                    print("No secret in secrets_list")
                    return okta_obj.delete_factor(logged_in_Okta_user_id, factor[Constants.ID])
            else:     
                for secret in secrets_list:
                    if secret[EnvVars.OKTA_FACTOR_ID] != "" and secret[EnvVars.OKTA_USER_ID] == logged_in_Okta_user_id:
                        if factor[Constants.ID] == secret[EnvVars.OKTA_FACTOR_ID]:
                            print("factor IDs matched. So, user is enrolled to TOTP factor from TecVerify.")
                            return {'User is already Auto Enrolled to Okta from TecVerify': True}, 200
                        else:
                            # factor IDs didn't match. Previouly TecVerify enrolled TOTP factor got deleted and new factor got enrolled.
                            print("factor IDs didn't match. So, user is enrolled to TOTP factor from other TecVerify Build or OktaVerify.")
                            return okta_obj.delete_factor(logged_in_Okta_user_id, factor[Constants.ID])
                            
                if usersAutoEnrolledFromTecVerify == usersAutoEnrolledFromTecVerify_excludingLoginUser:
                    print("No auto enrollment is done in TecVerify for this logged in user.")
                    return okta_obj.delete_factor(logged_in_Okta_user_id, factor[Constants.ID])

    print("This user is not enrolled to Okta TOTP factor")
    return {'Okta TOTP Factor is not enrolled for this user': True}, 200


@app.route('/api/v1/deleteSecretIfTOTPfactorIsDeletedInOkta', methods=['DELETE'])
@limiter.limit(RATE_LIMIT)
def deleteSecretIfTOTPfactorIsInactive():
    print("deleteSecretIfTOTPfactorIsDeletedInOkta API")
    # token_info = g.get('user')
    logged_in_Okta_user_id = g.get('loggedInOktaUserId')

    secrets_list = db_obj.read()

    if not secrets_list:
        print("No secret in secrets_list")
        return {"Exception": "Secret List is Empty"}, 200
    else:     
        for secret in secrets_list:
            if secret[EnvVars.OKTA_USER_ID] == logged_in_Okta_user_id and secret[EnvVars.OKTA_FACTOR_ID] != "":
                get_factor_response = okta_obj.call_get_factor_API(logged_in_Okta_user_id, secret[EnvVars.OKTA_FACTOR_ID])
                if get_factor_response.status_code == 404:
                    db_obj.delete_secret(secret[EnvVars.SECRET_ID])
                
                return okta_obj.get_factor(logged_in_Okta_user_id, secret[EnvVars.OKTA_FACTOR_ID])
                
        return {"SUCCESS": "Secret List is not Empty"}, 200


@app.route('/api/v1/autoEnroll', methods=['POST'])
@limiter.limit(RATE_LIMIT)
def enrollToTecVerify():
    print("autoEnroll API")
    # token_info = g.get('user')
    logged_in_Okta_user_id = g.get('loggedInOktaUserId')
    logged_in_username = g.get('loggedInUserName')
    enroll_response = okta_obj.call_enroll_okta_verify_TOTP_factor_API(logged_in_Okta_user_id)
    enroll_info = enroll_response.json()

    if enroll_response.status_code == 200:
        oktaFactorID = enroll_info[Constants.ID]
        oktaSharedSecret = enroll_info[Constants.EMBEDDED][Constants.ACTIVATION][Constants.SHARED_SECRET]
        generatedOTP = totpGenerator_obj.generate_totp(oktaSharedSecret)
        # db_obj.auto_save_secret(oktaSharedSecret, logged_in_Okta_user_id, CONNECTION_OBJECT) # For saving secret in TecVerify
        db_obj.auto_save_secret(oktaSharedSecret, logged_in_Okta_user_id, logged_in_username, oktaFactorID) # For saving secret in TecVerify with logged in username and oktaFactorID
        return okta_obj.activate_TOTP_factor(logged_in_Okta_user_id, oktaFactorID, generatedOTP)
        
    return okta_obj.enroll_okta_verify_TOTP_factor(logged_in_Okta_user_id)


@app.route('/api/v1/totp', methods=['GET'])
@limiter.limit(RATE_LIMIT)
def get_totp():
    print("TOTP API")
    # token_info = g.get('user')
    logged_in_Okta_user_id = g.get('loggedInOktaUserId')
    # if AUTHORIZE_CLAIM_NAME in token_info:
    secrets_list = db_obj.read()             
    totp_list = totpGenerator_obj.generate_totp_for_login_user(secrets_list, logged_in_Okta_user_id)
    return jsonify(totp_list), 200
    # else:
    #     return {'error': 'UnAuthorized !!!'}, 403


@app.route('/api/v1/secret/<secret_id>', methods=['DELETE'])
@limiter.limit(RATE_LIMIT)
def delete_secret(secret_id):
    print("Delete Secret API")
    # token_info = g.get('user')
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
                if secret[EnvVars.OKTA_FACTOR_ID] == "":
                    deleteManuallySavedSecret = True
                else:
                    delete_factor_response = okta_obj.call_delete_factor_API(secret[EnvVars.OKTA_USER_ID], secret[EnvVars.OKTA_FACTOR_ID])
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
    # token_info = g.get('user')
    # if AUTHORIZE_CLAIM_NAME in token_info and token_info[AUTHORIZE_CLAIM_NAME]:
    return secretGenerator_obj.generate_secret()
    # else:
    #     return {'error': 'UnAuthorized !!!'}, 403


@app.route('/api/v1/secret', methods=['POST'])
@limiter.limit(RATE_LIMIT)
def save_secret():
    print("Save Secret API")
    neededOktaUserIDinRequestForm = False
    form_data = requestForm_obj.parse_form_data(request, neededOktaUserIDinRequestForm)
    # token_info = g.get('user')
    logged_in_Okta_user_id = g.get('loggedInOktaUserId')
    # if AUTHORIZE_CLAIM_NAME in token_info and token_info[AUTHORIZE_CLAIM_NAME] and form_data[SECRET_KEY]:
    if form_data[EnvVars.SECRET_NAME] and form_data[EnvVars.SECRET_KEY]:
        if secretGenerator_obj.is_secret_valid(form_data[EnvVars.SECRET_KEY]):
            # if db_obj.manual_save_secret(form_data, logged_in_Okta_user_id, CONNECTION_OBJECT):
            if db_obj.manual_save_secret(form_data, logged_in_Okta_user_id):
                return {"updated": True}, 200
            else:
                return {"updated": False, "error": "Update Failed !!!"}, 500
        else:
            return {"updated": False, "error": Constants.SECRET_KEY_KEY_IN_REQUEST_FORM + " is in invalid format. Try another one."}, 500
    elif form_data[EnvVars.SECRET_NAME] is None or not form_data[EnvVars.SECRET_NAME]:
        return {'error': "Secret Name is missing"}, 400
    elif form_data[EnvVars.SECRET_KEY] is None or not form_data[EnvVars.SECRET_KEY]:
        return {'error': "Admin Secret is missing"}, 400
    # else:
    #     return {'error': 'UnAuthorized !!!'}, 403


@app.route('/api/v1/notProtectedByIdToken_saveSecret', methods=['POST'])
@limiter.limit(RATE_LIMIT)
def save_secret_byTakingOktaUserIDfromRequestForm():
    print("notProtectedByIdToken_saveSecret API")
    neededOktaUserIDinRequestForm = True
    form_data = requestForm_obj.parse_form_data(request, neededOktaUserIDinRequestForm)
    if form_data[EnvVars.SECRET_NAME] and form_data[EnvVars.SECRET_KEY] and form_data[EnvVars.OKTA_USER_ID]:
        if secretGenerator_obj.is_secret_valid(form_data[EnvVars.SECRET_KEY]):
            okta_user_id_in_form_data = form_data[EnvVars.OKTA_USER_ID]
            get_user_response = okta_obj.call_get_user_API(okta_user_id_in_form_data)
            if get_user_response.status_code == 200:
                # if db_obj.manual_save_secret(form_data, okta_user_id_in_form_data, CONNECTION_OBJECT):
                if db_obj.manual_save_secret(form_data, okta_user_id_in_form_data):
                    return {"updated": True}, 200
                else:
                    return {"updated": False, "error": "Update Failed !!!"}, 500
            else:
                return okta_obj.get_user(okta_user_id_in_form_data)
        else:
            return {"updated": False, "error": Constants.SECRET_KEY_KEY_IN_REQUEST_FORM + " is in invalid format. Try another one."}, 500
    elif form_data[EnvVars.SECRET_NAME] is None or not form_data[EnvVars.SECRET_NAME]:
        return {'error': "Secret Name is missing"}, 400
    elif form_data[EnvVars.SECRET_KEY] is None or not form_data[EnvVars.SECRET_KEY]: # if secret key is empty or key itself is not there
        return {'error': "Admin Secret is missing"}, 400
    elif form_data[EnvVars.OKTA_USER_ID] is None or not form_data[EnvVars.OKTA_USER_ID]:
        return {'error': "Okta User ID is missing"}, 400


@app.route('/api/v1/destroyConnection', methods=['GET'])
@limiter.limit(RATE_LIMIT)
def closeConnection():
    print("destroyConnection API")
    if(EnvVars.DATABASE_TYPE == "json"):
        return {"ERROR": "No need to close DB connection for JSON object"}, 400
    elif(EnvVars.DATABASE_TYPE == "mssql"):
        is_closed = db_obj.destroy_db_connection(mssql_conn)
        if is_closed:
            return {"SUCCESS": "DB connection closed successfully"}, 200
        else:
            return {"ERROR": "Failed in closing the DB connection"}, 400
# end TecVerify EndPoints #


if __name__ == '__main__':
    # app.run(host="0.0.0.0")
    app.run(host="0.0.0.0", ssl_context='adhoc') # This is for running backend devlpmnt server in secure context(HTTPS)

