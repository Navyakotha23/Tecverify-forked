import requests
import json

class OktaOperations:

    def __init__(self, CLIENT_ID, ISSUER, AUTHORIZING_TOKEN, AUTHORIZE_CLAIM_NAME, TECVERIFY_API_KEY, SHOW_LOGS) -> None:
        self.client_id = CLIENT_ID
        self.issuer = ISSUER
        self.authorizing_token = AUTHORIZING_TOKEN
        self.authorizing_claim = AUTHORIZE_CLAIM_NAME
        self.tecverify_api_key = TECVERIFY_API_KEY
        self.show_logs = SHOW_LOGS

    ###################################################################
    def enroll_okta_verify_TOTP_factor(self, oktaUid):
        # if self.show_logs: print("In enroll_okta_verify_TOTP_factor()")
        url = self.issuer + "/api/v1/users/" + oktaUid + "/factors"
        # if self.show_logs: print("url: ", url)
        headers={'Content-Type':'application/json', 'Authorization': 'SSWS {}'.format(self.tecverify_api_key)}
        # if self.show_logs: print("headers: ", headers)
        body = {'factorType': 'token:software:totp', 'provider': 'OKTA'}
        # if self.show_logs: print("body: ", body)
        response = requests.post(url, data=json.dumps(body), headers=headers)   
        # if self.show_logs: print("Out enroll_okta_verify_TOTP_factor()")
        return response

    def activate_TOTP_factor(self, oktaUid, oktaFactorID, generatedOTP):
        # if self.show_logs: print("In activate_TOTP_factor()")
        url = self.issuer + "/api/v1/users/" + oktaUid + "/factors/" + oktaFactorID + "/lifecycle/activate"
        # if self.show_logs: print("url: ", url)
        headers={'Content-Type':'application/json', 'Authorization': 'SSWS {}'.format(self.tecverify_api_key)}
        # if self.show_logs: print("headers: ", headers)
        body = {'passCode': generatedOTP}
        # if self.show_logs: print("body: ", body)
        response = requests.post(url, data=json.dumps(body), headers=headers)   
        # if self.show_logs: print("response: ", response)
        # if self.show_logs: print("response.json(): ", response.json())
        activation_info = response.json()
        # if self.show_logs: print("activation_info['status']: ", activation_info['status'])
        # if self.show_logs: print("Out activate_TOTP_factor()")
        if activation_info['status'] == "ACTIVE":
            return True
        else:
            return False

    def call_delete_factor_API(self, oktaUid, oktaFactorID):
        # print("In call_delete_factor_API()")
        url = self.issuer + "/api/v1/users/" + oktaUid + "/factors/" + oktaFactorID
        # print("url: ", url)
        headers={'Content-Type':'application/json', 'Authorization': 'SSWS{}'.format(self.tecverify_api_key)}
        # print("headers: ", headers)
        response = requests.delete(url, headers=headers)
        # print("response: ", response)
        # print("Out call_delete_factor_API()")
        return response

    def call_list_factors_API(self, oktaUid):
        # print("In call_list_factors_API()")
        url = self.issuer + "/api/v1/users/" + oktaUid + "/factors"
        # print("url: ", url)
        headers={'Content-Type':'application/json', 'Authorization': 'SSWS {}'.format(self.tecverify_api_key)}
        # print("headers: ", headers)
        response = requests.get(url, headers=headers)  
        # print("Out call_list_factors_API()")
        return response

    def call_get_factor_API(self, oktaUid, oktaFactorID):
        # print("In call_get_factor_API()")
        url = self.issuer + "/api/v1/users/" + oktaUid + "/factors/" + oktaFactorID
        # print("url: ", url)
        headers={'Content-Type':'application/json', 'Authorization': 'SSWS {}'.format(self.tecverify_api_key)}
        # print("headers: ", headers)
        response = requests.get(url, headers=headers)
        # print("response: ", response)
        # print("Out call_get_factor_API()")
        return response
    ###################################################################

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

    def call_introspect_api(self, token):
        """
        This method makes an introspect api call to Okta with token and returns Okta API response.
        """
        url = self.issuer + "/oauth2/v1/introspect?client_id=" + self.client_id
        # if self.show_logs: print("url: ", url)
        body = {'token': token, 'token_type_hint': self.authorizing_token}
        # if self.show_logs: print("body: ", body)
        response = requests.post(url, data=body)   
        # if self.show_logs: print("response: ", response)
        return response

    def is_token_active(self, response) -> bool:
        """
        This method checks whether token is still Active or not.
        """
        if 'active' in response:
            return response['active']
        else:
            return False