import requests
import json

class OktaAPIs:

    def __init__(self, CLIENT_ID, ISSUER, AUTHORIZING_TOKEN, AUTHORIZE_CLAIM_NAME, TECVERIFY_API_KEY, SHOW_LOGS) -> None:
        self.client_id = CLIENT_ID
        self.issuer = ISSUER
        self.authorizing_token = AUTHORIZING_TOKEN
        self.authorizing_claim = AUTHORIZE_CLAIM_NAME
        self.tecverify_api_key = TECVERIFY_API_KEY
        self.show_logs = SHOW_LOGS


    def is_token_active(self, response) -> bool:
        """
        This method checks whether token is still Active or not.
        """
        if 'active' in response:
            return response['active']
        else:
            return False


    def call_introspect_api(self, token):
        """
        This method makes an introspect api call to Okta with token and returns Okta API response.
        """
        url = self.issuer + "/oauth2/v1/introspect?client_id=" + self.client_id
        body = {'token': token, 'token_type_hint': self.authorizing_token}
        response = requests.post(url, data=body)   
        return response
    
    def introspect_token(self, token):
        """
        This method introspects idToken or accessToken with Okta.
        If Active, returns True and TokenInfo; else, returns False and TokenInfo.
        """
        response = self.call_introspect_api(token)
        token_info = response.json()
        if response.status_code == 200:
            return self.is_token_active(token_info), token_info
        else:
            return False, token_info


    def call_list_factors_API(self, oktaUid):
        """
        This method makes List Factors API call to Okta with OktaUserID, APIkey and returns Okta API response.
        """
        url = self.issuer + "/api/v1/users/" + oktaUid + "/factors"
        headers={'Content-Type':'application/json', 'Authorization': 'SSWS {}'.format(self.tecverify_api_key)}
        response = requests.get(url, headers=headers)  
        return response

    def list_factors(self, oktaUid):
        """
        This method makes List Factors API call to Okta and returns custom response.
        """
        list_factors_response = self.call_list_factors_API(oktaUid)
        if list_factors_response.status_code == 200:
            return {'Got the List of factors for that user': True}, 200
        elif list_factors_response.status_code == 401:
            if list_factors_response.json()['errorCode'] == "E0000011":
                print("API token provided is invalid. So, cannot get factors list.")
            return {"errorSummary": "Invalid API token provided. So, cannot get factors list."}, 400
        elif list_factors_response.status_code == 403:
            if list_factors_response.json()['errorCode'] == "E0000006":
                print("This user is not in the group for which API token is generated. So, cannot get factors list.")
            return {"errorSummary": "Current user is not in the group for which API token is generated. So, cannot get factors list."},400


    def call_delete_factor_API(self, oktaUid, oktaFactorID):
        """
        This method makes Delete Factor API call to Okta with OktaUserID, OktaTOTPfactorId, APIkey and returns Okta API response.
        """
        url = self.issuer + "/api/v1/users/" + oktaUid + "/factors/" + oktaFactorID
        headers={'Content-Type':'application/json', 'Authorization': 'SSWS{}'.format(self.tecverify_api_key)}
        response = requests.delete(url, headers=headers)
        return response
    
    def delete_factor(self, oktaUid, oktaFactorID):
        """
        This method makes Delete Factor API call to Okta and returns custom response.
        """
        delete_factor_response = self.call_delete_factor_API(oktaUid, oktaFactorID)
        if delete_factor_response.status_code == 204:
            print("Okta TOTP Factor enrolled from OktaVerify is deleted")
            return {'Deleted Okta TOTP Factor enrolled from OktaVerify': True}, 200
        elif delete_factor_response.status_code == 401:
            if delete_factor_response.json()['errorCode'] == "E0000011":
                print("API token provided is invalid. So, cannot delete the factor.")
            return {"errorSummary": "Invalid API token provided. So, cannot delete the factor."}, 400
        elif delete_factor_response.status_code == 403:
            if delete_factor_response.json()['errorCode'] == "E0000006":
                print("Current user is the Super admin. Group admin API token cannot delete the factor of Super admin user.")
            return {"errorSummary": "Current user is the Super admin user. He has to delete the TOTP factor in Okta to get enrolled in TecVerify."},400

    
    def call_enroll_okta_verify_TOTP_factor_API(self, oktaUid):
        """
        This method makes an Enroll Okta Verify TOTP factor API call to Okta with OktaUserID, APIkey and returns Okta API response.
        """
        url = self.issuer + "/api/v1/users/" + oktaUid + "/factors"
        headers={'Content-Type':'application/json', 'Authorization': 'SSWS {}'.format(self.tecverify_api_key)}
        body = {'factorType': 'token:software:totp', 'provider': 'OKTA'}
        response = requests.post(url, data=json.dumps(body), headers=headers)   
        return response
    
    def enroll_okta_verify_TOTP_factor(self, oktaUid):
        """
        This method makes an Enroll Okta Verify TOTP factor API call to Okta and returns custom response.
        """
        enroll_response = self.call_enroll_okta_verify_TOTP_factor_API(oktaUid)
        if enroll_response.status_code == 200:
            return {"SUCCESS": "Enrolled TOTP factor Successfully. Need to Activate that."}
        elif enroll_response.status_code == 400:
            if enroll_response.json()['errorCode'] == "E0000001":
                print("A factor of this type is already set up.")
            return {"WARNING": "A factor of this type is already set up."}
        elif enroll_response.status_code == 401:
            if enroll_response.json()['errorCode'] == "E0000011":
                print("API token provided is invalid. So, cannot enroll the user.")
            return {"errorSummary": "Invalid API token provided. So, cannot enroll the user."}, 400
        elif enroll_response.status_code == 403:
            if enroll_response.json()['errorCode'] == "E0000006":
                print("This user is not in the group for which API token is generated. So, cannot enroll the user.")
            return {"errorSummary": "Current user is not in the group for which API token is generated. So, cannot enroll the user."},400
    

    def call_activate_TOTP_factor_API(self, oktaUid, oktaFactorID, generatedOTP):
        """
        This method makes an Activate TOTP Factor API call to Okta with OktaUserID, OktaTOTPfactorId, OTP generated with OktaSharedSecret, APIkey and returns Okta API response.
        """
        url = self.issuer + "/api/v1/users/" + oktaUid + "/factors/" + oktaFactorID + "/lifecycle/activate"
        headers={'Content-Type':'application/json', 'Authorization': 'SSWS {}'.format(self.tecverify_api_key)}
        body = {'passCode': generatedOTP}
        response = requests.post(url, data=json.dumps(body), headers=headers)   
        return response

    def activate_TOTP_factor(self, oktaUid, oktaFactorID, generatedOTP):
        """
        This method makes an Activate TOTP Factor API call to Okta and returns custom response.
        """
        activation_response = self.call_activate_TOTP_factor_API(oktaUid, oktaFactorID, generatedOTP)
        if activation_response.status_code == 200:
            return {"SUCCESS": "Auto-enrolled Successfully"}
        return {"ERROR": "Auto-enrollment Failed"}
    

    def call_get_factor_API(self, oktaUid, oktaFactorID):
        """
        This method makes Get Factor API call to Okta with OktaUserID, OktaTOTPfactorId, APIkey and returns Okta API response.
        """
        url = self.issuer + "/api/v1/users/" + oktaUid + "/factors/" + oktaFactorID
        headers={'Content-Type':'application/json', 'Authorization': 'SSWS {}'.format(self.tecverify_api_key)}
        response = requests.get(url, headers=headers)
        return response

    def get_factor(self, oktaUid, oktaFactorID):
        """
        This method makes Get Factor API call to Okta and returns custom response.
        """
        get_factor_response = self.call_get_factor_API(oktaUid, oktaFactorID)
        if get_factor_response.status_code == 200:
            print("TOTP factor is Active. No need to delete the secret.")
            return {"SUCCESS": "TOTP factor is Active. No need to delete the secret."}, 200
        elif get_factor_response.status_code == 404:
            print("TOTP factor is Inactive. So, deleting the secret.")
            return {"errorSummary": "TOTP factor is Inactive. So, deleting the secret."}, 200
        elif get_factor_response.status_code == 401:
            if get_factor_response.json()['errorCode'] == "E0000011":
                print("API token provided is invalid. So, cannot get the Factor.")
            return {"errorSummary": "Invalid API token provided. So, cannot get the Factor."}, 400
        elif get_factor_response.status_code == 403:
            if get_factor_response.json()['errorCode'] == "E0000006":
                print("This user is not in the group for which API token is generated. So, cannot get the Factor.")
            return {"errorSummary": "Current user is not in the group for which API token is generated. So, cannot get the Factor."},400
    
    