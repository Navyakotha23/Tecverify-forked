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
        print("-----In generate_totp_for_all_secrets(self, secrets_list, okta_logged_in_user_id) in totp.py-----")
        secrets_with_totp = []
        if self.show_logs: print("***okta_logged_in_user_id: " + okta_logged_in_user_id)
        for user in secrets_list:
            secret = self.crypt_obj.decrypt(user['secret'])
            saved_secret_okta_user_id = user['oktaUserId']
            if self.show_logs: print("saved_secret_okta_user_id: " + saved_secret_okta_user_id)
            if okta_logged_in_user_id == saved_secret_okta_user_id :
                if self.show_logs: print("okta_logged_in_user_id and saved_secret_okta_user_id are SAME. So, generating OTP for that secret key.")
                totp = self.generate_totp(secret)
                print("secret: ", secret)
                secrets_with_totp.append(
                {'id': user['id'], 'otp': totp, 'secretName': user['secretName'], 'secretUpdatedAt': user['updatedAt']})
            else:
                if self.show_logs: print("okta_logged_in_user_id and saved_secret_okta_user_id are NOT same")
        print("-----Out of generate_totp_for_all_secrets(self, secrets_list, okta_logged_in_user_id) in totp.py-----")
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
    