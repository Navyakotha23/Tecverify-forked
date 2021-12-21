import requests

class OktaOperations:

    def __init__(self, CLIENT_ID, ISSUER, AUTHORIZING_TOKEN, AUTHORIZE_CLAIM_NAME) -> None:
        self.client_id = CLIENT_ID
        self.issuer = ISSUER
        self.authorizing_token = AUTHORIZING_TOKEN
        self.authorizing_claim = AUTHORIZE_CLAIM_NAME

    def introspect_token(self, token):
        """
        This method introspects idToken or accessToken with Okta.
        If Active, returns True and TokenInfo; else, returns False and TokenInfo.
        """
        print("-----In introspect_token(self, token)-----")
        response = self.call_introspect_api(token)
        print("Token response: ")
        print(response)
        token_info = response.json()
        print("token_info: ")
        print(token_info)
        if response.status_code == 200:
            print("Token status: ")
            print(self.is_token_active(token_info))
            print("-----Out of introspect_token(self, token)-----")
            return self.is_token_active(token_info), token_info
        else:
            print("Token status: ")
            print(self.is_token_active(token_info))
            print("-----Out of introspect_token(self, token)-----")
            return False, token_info

    def call_introspect_api(self, token):
        """
        This method makes an introspect api call to Okta with token and returns Okta API response.
        """
        print("----------In call_introspect_api(self, token)----------")
        url = self.issuer + "/oauth2/v1/introspect?client_id=" + self.client_id
        print("url: ")
        print(url)
        body = {'token': token, 'token_type_hint': self.authorizing_token}
        print("body: ")
        print(body)
        response = requests.post(url, data=body)   
        print("response: ")
        print(response)  
        print("----------Out of call_introspect_api(self, token)----------")
        return response

    def is_token_active(self, response) -> bool:
        """
        This method checks whether token is still Active or not.
        """
        if 'active' in response:
            return response['active']
        else:
            return False