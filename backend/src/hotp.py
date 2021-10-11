import pyotp

class HOTP:

    def __init__(self, crypt_obj) -> None:
        self.crypt_obj = crypt_obj

    def generate_hotp(self, secret, counterParam):
        """
        This method generates HOTP for the received admin secret.
        """
        try:
            hotp = pyotp.HOTP(secret).at(counterParam)
            return hotp
        except Exception as e:
            return None

    def generate_hotp_for_all_secrets(self, secrets_list, counterParam):
        """
        This method generates HOTPs for all admin secrets.
        """
        secrets_with_hotp = []
        for user in secrets_list:
            secret = self.crypt_obj.decrypt(user['secret'])
            hotp = self.generate_hotp(secret, counterParam)
            secrets_with_hotp.append(
                {'id': user['id'], 'otp': hotp, 'secretName': user['secretName'], 'secretUpdatedAt': user['updatedAt']})
        return secrets_with_hotp

    def is_secret_valid(self, secret):
        """
        This method checks whether the secret is compatible to generate a hotp or not.
        """
        try:
            pyotp.HOTP(secret).at(0)
            return True
        except Exception as e:
            return False
    