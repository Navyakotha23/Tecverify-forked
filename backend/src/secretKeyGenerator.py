import pyotp

class SecretKey_Generator:

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


    def generate_secret(self):
        """
        This method generates random secret.
        """
        admin_secret = pyotp.random_base32(32)
        return {"adminSecret": admin_secret}, 200