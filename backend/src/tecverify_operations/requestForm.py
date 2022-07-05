from common.constants import Constants
from common.envVars import EnvVars


class RequestForm:

    def parse_form_data(self, request, neededOktaUserIDinRequestForm):
        """
        If idToken/accessToken is there in Headers then this method parses form-data and returns SecretName, SecretKey
        Else this method expects oktaUserId in form-data to parse it and return SecretName, SecretKey and OktaUserId
        """
        # print("request: ", request)
        # print("request.form:", request.form)
        secret_name_VALUE_in_request_form = request.form[Constants.SECRET_NAME_KEY_IN_REQUEST_FORM] if Constants.SECRET_NAME_KEY_IN_REQUEST_FORM in request.form else None
        secret_key_VALUE_in_request_form = request.form[Constants.SECRET_KEY_KEY_IN_REQUEST_FORM] if Constants.SECRET_KEY_KEY_IN_REQUEST_FORM in request.form else None
        if not neededOktaUserIDinRequestForm:
            return {EnvVars.SECRET_NAME: secret_name_VALUE_in_request_form, EnvVars.SECRET_KEY: secret_key_VALUE_in_request_form}
        else:
            okta_user_id_VALUE_in_request_form = request.form[Constants.OKTA_USER_ID_KEY_IN_REQUEST_FORM] if Constants.OKTA_USER_ID_KEY_IN_REQUEST_FORM in request.form else None
            return {EnvVars.SECRET_NAME: secret_name_VALUE_in_request_form, EnvVars.SECRET_KEY: secret_key_VALUE_in_request_form, EnvVars.OKTA_USER_ID: okta_user_id_VALUE_in_request_form}


    def test_function(self):
        print("called From secretKeyGenerator.py")