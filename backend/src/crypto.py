import pyDes

class Crypto:
    def __init__(self, salt) -> None:
        self.key = pyDes.des(salt, pyDes.CBC, "\0\0\0\0\0\0\0\0", pad=None, padmode=pyDes.PAD_PKCS5)

    def encrypt(self, text) -> str:
        """
        This method encrypts text to ciphered text using Salt specified in config file
        """
        bytes = self.key.encrypt(text)
        return str(bytes)

    def decrypt(self, cipher) -> str:
        """
        This method decrypts cipher to text using Salt specified as environment variable
        """
        bytes = eval(cipher)
        return self.key.decrypt(bytes).decode()  

    ###################################################################
    def decryptAPIkey(self, EncryptedAPIkey, SaltOfAPIkey) -> str:
        # print("\nIn decryptAPIkey()")
        # print("EncryptedAPIkey: ", EncryptedAPIkey)
        # print("SaltOfAPIkey: ", SaltOfAPIkey)
        keyMadeWithSaltOfAPIkey = pyDes.des(SaltOfAPIkey, pyDes.CBC, "\0\0\0\0\0\0\0\0", pad=None, padmode=pyDes.PAD_PKCS5)
        bytes = eval(EncryptedAPIkey)
        decryptedAPIkey = keyMadeWithSaltOfAPIkey.decrypt(bytes).decode() 
        # print("decryptedAPIkey: ", decryptedAPIkey)
        # print("Out decryptAPIkey()\n")
        return decryptedAPIkey
    ###################################################################