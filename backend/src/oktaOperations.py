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
        print("In enroll_okta_verify_TOTP_factor()")
        url = self.issuer + "/api/v1/users/" + oktaUid + "/factors"
        print("url: ", url)
        headers={'Content-Type':'application/json', 'Authorization': 'SSWS {}'.format(self.tecverify_api_key)}
        print("headers: ", headers)
        body = {'factorType': 'token:software:totp', 'provider': 'OKTA'}
        print("body: ", body)
        response = requests.post(url, data=json.dumps(body), headers=headers)   
        # print("response: ", response)
        # print("response.json(): ", response.json())
        # enroll_info = response.json()
        # if response.status_code == 200:
        #     factor_id = enroll_info['id']
        #     print("factor_id: ", factor_id)
        #     shared_secret = enroll_info['_embedded']['activation']['sharedSecret']
        #     print("shared_secret: ", shared_secret)
        #     print("Out enroll_okta_verify_TOTP_factor()")
        #     return factor_id, shared_secret
        return response

    def activate_TOTP_factor(self, oktaUid, oktaFactorID, generatedOTP):
        print("In activate_TOTP_factor()")
        url = self.issuer + "/api/v1/users/" + oktaUid + "/factors/" + oktaFactorID + "/lifecycle/activate"
        print("url: ", url)
        headers={'Content-Type':'application/json', 'Authorization': 'SSWS {}'.format(self.tecverify_api_key)}
        print("headers: ", headers)
        body = {'passCode': generatedOTP}
        print("body: ", body)
        response = requests.post(url, data=json.dumps(body), headers=headers)   
        print("response: ", response)
        print("response.json(): ", response.json())
        activation_info = response.json()
        print("activation_info['status']: ", activation_info['status'])
        print("Out activate_TOTP_factor()")
        if activation_info['status'] == "ACTIVE":
            return True
        else:
            return False
    ###################################################################

    def introspect_token(self, token):
        """
        This method introspects idToken or accessToken with Okta.
        If Active, returns True and TokenInfo; else, returns False and TokenInfo.
        """
        if self.show_logs: print("-----In introspect_token(self, token)-----")
        response = self.call_introspect_api(token)
        if self.show_logs: print("Token response: ", response)
        token_info = response.json()
        if self.show_logs: print("token_info: ", token_info)
        if response.status_code == 200:
            if self.show_logs: print("Token status: ", self.is_token_active(token_info))
            if self.show_logs: print("-----Out of introspect_token(self, token)-----")
            return self.is_token_active(token_info), token_info
        else:
            if self.show_logs: print("Token status: ", self.is_token_active(token_info))
            if self.show_logs: print("-----Out of introspect_token(self, token)-----")
            return False, token_info

    def call_introspect_api(self, token):
        """
        This method makes an introspect api call to Okta with token and returns Okta API response.
        """
        if self.show_logs: print("----------In call_introspect_api(self, token)----------")
        url = self.issuer + "/oauth2/v1/introspect?client_id=" + self.client_id
        if self.show_logs: print("url: ", url)
        body = {'token': token, 'token_type_hint': self.authorizing_token}
        if self.show_logs: print("body: ", body)
        response = requests.post(url, data=body)   
        if self.show_logs: print("response: ", response)
        if self.show_logs: print("----------Out of call_introspect_api(self, token)----------")
        return response

    def is_token_active(self, response) -> bool:
        """
        This method checks whether token is still Active or not.
        """
        if 'active' in response:
            return response['active']
        else:
            return False