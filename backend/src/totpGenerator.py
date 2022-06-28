import pyotp

from envVars import EnvVars

class TOTP_Generator:

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


    def generate_totp_for_login_user(self, secrets_list, okta_logged_in_user_id):
        """
        This method generates TOTPs for login user.
        """
        secrets_with_totp = []
        for secret in secrets_list:
            shared_secret = self.crypt_obj.decrypt(secret[EnvVars.SECRET_KEY])
            saved_secret_okta_user_id = secret[EnvVars.OKTA_USER_ID]
            if okta_logged_in_user_id == saved_secret_okta_user_id :
                # if self.show_logs: print("okta_logged_in_user_id and saved_secret_okta_user_id are same. So, generating OTPs")
                totp = self.generate_totp(shared_secret)
                secrets_with_totp.append(
                {'id': secret[EnvVars.SECRET_ID], 'otp': totp, 'secretName': secret[EnvVars.SECRET_NAME], 'secretUpdatedAt': secret[EnvVars.SECRET_UPDATED_AT]})
            # else:
            #     if self.show_logs: print("okta_logged_in_user_id and saved_secret_okta_user_id are NOT same")
        return secrets_with_totp


    
    