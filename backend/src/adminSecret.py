import json
import os
import uuid
from datetime import datetime

class AdminSecret:

    def __init__(self, file: str, crypt_obj) -> None:
        self.file = file
        self.crypt_obj = crypt_obj

    def update_secret(self, form_data, okta_logged_in_user_id) -> bool:
        """
        This method updates file with form data received.
        """
        print("-----In update_secret(self, form_data, okta_logged_in_user_id) in adminSecret.py-----")
        secrets_list = self.read()
        id = self.generate_unique_id(secrets_list)
        form_data['secret'] = self.crypt_obj.encrypt(form_data['secret'])
        form_data['id'] = id
        form_data['updatedAt'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print("okta_logged_in_user_id: " + okta_logged_in_user_id)
        form_data['oktaUserId'] = okta_logged_in_user_id
        print("form_data['oktaUserId']: " + form_data['oktaUserId'])
        secrets_list.append(form_data)
        print("-----Out of update_secret(self, form_data, okta_logged_in_user_id) in adminSecret.py-----")
        return self.write(secrets_list)

    def write(self, data) -> bool:
        """
        This method writes in to file which stores Admin Secrets
        """
        try:
            with open(self.file, 'w') as fHandle:
                json.dump(data, fHandle, indent=4)
            return True
        except Exception as e:
            return False

    def read(self):
        """
        This method reads from file which stores Admin Secrets
        """
        try:
            if not os.path.isfile(self.file) or os.stat(self.file).st_size == 0:
                self.create_empty_json_file()
            with open(self.file, 'r') as fHandle:
                secrets = json.load(fHandle)
            return secrets
        except Exception as e:
            return None

    def create_empty_json_file(self) -> bool:
        """
        This method creates empty JSON file 
        """
        try:
            default_data = []
            self.write(default_data)
            return True
        except Exception as e:
            return False

    def generate_unique_id(self, secrets_list) -> str:
        """
        This method returns a unique id by checking against all secret id's
        """
        uid = self.generate_random_id()
        if self.is_id_unique(uid, secrets_list):
            return uid
        else:
            return self.generate_unique_id(secrets_list)

    def generate_random_id(self) -> str:
        """
        This method returns a random id
        """
        return str(uuid.uuid4())

    def is_id_unique(self, id: str, secrets_list) -> bool:
        """
        This method returns boolean by checking whether Id is unique or not
        """
        id_list = [secret['id'] for secret in secrets_list]
        if id not in id_list:
            return True
        else:
            return False
        
    def parse_form_data(self, request):
        """
        This method parse form data and returns SecretName and Secret
        """
        admin_secret = request.form['adminSecret'] if 'adminSecret' in request.form else None
        secret_name = request.form['secretName'] if 'secretName' in request.form else None
        return {'secretName': secret_name, 'secret': admin_secret}

