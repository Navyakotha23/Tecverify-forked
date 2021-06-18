import pyotp

class TOTP:

    def __init__(self, crypt_obj) -> None:
        self.crypt_obj = crypt_obj

    def generate_totp(self, secret):
        """
        This method generates TOTP for the received admin secret.
        """
        try:
            totp = pyotp.TOTP(secret).now()
            return totp
        except Exception as e:
            return None

    def generate_totp_for_all_secrets(self, secrets_list):
        """
        This method generates TOTPs for all admin secrets.
        """
        secrets_with_totp = []
        for user in secrets_list:
            secret = self.crypt_obj.decrypt(user['secret'])
            totp = self.generate_totp(secret)
            secrets_with_totp.append(
                {'id': user['id'], 'otp': totp, 'secretName': user['secretName'], 'secretUpdatedAt': user['updatedAt']})
        return secrets_with_totp

    def is_secret_valid(self, secret):
        """
        This method checks whether the secret is compatible to generate a totp or not.
        """
        try:
            pyotp.TOTP(secret).now()
            return True
        except Exception as e:
            return False
    