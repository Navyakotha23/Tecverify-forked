import pyotp

class TOTP:

    def __init__(self, crypt_obj, SHOW_LOGS) -> None:
        self.crypt_obj = crypt_obj
        self.show_logs = SHOW_LOGS

    def generate_totp(self, secret):
        """
        This method generates TOTP for the received admin secret.
        """
        try:
            totp = pyotp.TOTP(secret).now()
            return totp
        except Exception as e:
            print("Error in generate_totp(): ", e)
            return None

    def generate_totp_for_all_secrets(self, secrets_list, okta_logged_in_user_id):
        """
        This method generates TOTPs for all admin secrets.
        """
        secrets_with_totp = []
        for user in secrets_list:
            secret = self.crypt_obj.decrypt(user['secretKey'])
            saved_secret_okta_user_id = user['oktaUserId']
            if okta_logged_in_user_id == saved_secret_okta_user_id :
                # if self.show_logs: print("okta_logged_in_user_id and saved_secret_okta_user_id are same. So, generating OTPs")
                totp = self.generate_totp(secret)
                secrets_with_totp.append(
                {'id': user['secretId'], 'otp': totp, 'secretName': user['secretName'], 'secretUpdatedAt': user['updatedAt']})
            # else:
            #     if self.show_logs: print("okta_logged_in_user_id and saved_secret_okta_user_id are NOT same")
        return secrets_with_totp

    def is_secret_valid(self, secret):
        """
        This method checks whether the secret is compatible to generate a totp or not.
        """
        try:
            pyotp.TOTP(secret).now()
            return True
        except Exception as e:
            print("Error in is_secret_valid(): ", e)
            return False
    