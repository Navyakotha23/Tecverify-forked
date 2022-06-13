import abc

import uuid
from datetime import datetime

class AdminSecret(metaclass=abc.ABCMeta):

    def __init__(self, file: str, crypt_obj, MS_SQL_SERVER, MS_SQL_USERNAME, MS_SQL_PASSWORD, DATABASE_NAME, TABLE_NAME, AUTOSAVED_SECRET_USERNAME_HEAD, DATABASE_TYPE, SECRET_NAME, SECRET_KEY, OKTA_USER_ID, SECRET_ID, SECRET_UPDATED_AT, OKTA_FACTOR_ID, SECRET_NAME_KEY_IN_REQUEST_FORM, SECRET_KEY_KEY_IN_REQUEST_FORM, SHOW_LOGS) -> None:
        self.file = file
        self.crypt_obj = crypt_obj
        self.ms_sql_server = MS_SQL_SERVER
        self.ms_sql_username = MS_SQL_USERNAME
        self.ms_sql_password = MS_SQL_PASSWORD
        self.database_name = DATABASE_NAME
        self.table_name = TABLE_NAME
        self.auto_saved_secret_username_head = AUTOSAVED_SECRET_USERNAME_HEAD
        self.database_type = DATABASE_TYPE
        self.secret_name = SECRET_NAME
        self.secret_key = SECRET_KEY
        self.okta_user_id = OKTA_USER_ID
        self.secret_id = SECRET_ID
        self.secret_updated_at = SECRET_UPDATED_AT
        self.okta_factor_id = OKTA_FACTOR_ID
        self.secret_name_KEY_in_request_form = SECRET_NAME_KEY_IN_REQUEST_FORM
        self.secret_key_KEY_in_request_form = SECRET_KEY_KEY_IN_REQUEST_FORM
        self.show_logs = SHOW_LOGS


    def generate_random_id(self) -> str:
        """
        This method returns a random id
        """
        return str(uuid.uuid4())


    def is_id_unique(self, id: str, secrets_list) -> bool:
        """
        This method returns boolean by checking whether Id is unique or not
        """
        id_list = [secret[self.secret_id] for secret in secrets_list]
        if id not in id_list:
            return True
        else:
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

    
    @abc.abstractmethod
    def read(self):
        """
        This method reads from file which stores Admin Secrets
        """

        pass


    @abc.abstractmethod
    def write(self, data) -> bool:
        """
        This method writes in to file which stores Admin Secrets
        """

        pass
            

    def prepare_secret_dictionary_for_auto_save_secret(self, okta_shared_secret, okta_logged_in_user_id, okta_logged_in_username, okta_factor_id):
        secrets_list = self.read()
        id = self.generate_unique_id(secrets_list)
        secretInfo = {}
        secretInfo[self.secret_name] = self.auto_saved_secret_username_head + '.' + okta_logged_in_username
        secretInfo[self.secret_key] = self.crypt_obj.encrypt(okta_shared_secret)
        secretInfo[self.okta_user_id] = okta_logged_in_user_id
        secretInfo[self.secret_id] = id
        secretInfo[self.secret_updated_at] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        secretInfo[self.okta_factor_id] = okta_factor_id
        return secretInfo


    @abc.abstractmethod
    def auto_save_secret(self, okta_shared_secret, okta_logged_in_user_id, okta_logged_in_username, okta_factor_id) -> bool:
        """
        This method updates file with form data received.
        """
        
        pass
            

    def prepare_secret_dictionary_for_update_secret(self, form_data, okta_logged_in_user_id):
        secrets_list = self.read()
        id = self.generate_unique_id(secrets_list)
        form_data[self.secret_key] = self.crypt_obj.encrypt(form_data[self.secret_key])
        form_data[self.okta_user_id] = okta_logged_in_user_id
        form_data[self.secret_id] = id
        form_data[self.secret_updated_at] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        form_data[self.okta_factor_id] = ""
        return form_data


    @abc.abstractmethod
    def update_secret(self, form_data, okta_logged_in_user_id) -> bool:
        """
        This method updates file with form data received.
        """
        
        pass


    @abc.abstractmethod
    def delete_secret(self, secret_id) -> bool:
        """
        This method deletes a record based on the secret_id
        """

        pass            
        

    def parse_form_data(self, request):
        """
        This method parse form data and returns SecretName and Secret
        """
        secret_name_VALUE_in_request_form = request.form[self.secret_name_KEY_in_request_form] if self.secret_name_KEY_in_request_form in request.form else None
        secret_key_VALUE_in_request_form = request.form[self.secret_key_KEY_in_request_form] if self.secret_key_KEY_in_request_form in request.form else None
        return {self.secret_name: secret_name_VALUE_in_request_form, self.secret_key: secret_key_VALUE_in_request_form}


    def parse_form_data_for_okta_userid(self, request):
        """
        This method parse form data and returns SecretName, Secret and OktaUserId
        """
        secret_name_VALUE_in_request_form = request.form[self.secret_name_KEY_in_request_form] if self.secret_name_KEY_in_request_form in request.form else None
        secret_key_VALUE_in_request_form = request.form[self.secret_key_KEY_in_request_form] if self.secret_key_KEY_in_request_form in request.form else None
        okta_user_id_in_request_form = request.form[self.okta_user_id] if self.okta_user_id in request.form else None
        return {self.secret_name: secret_name_VALUE_in_request_form, self.secret_key: secret_key_VALUE_in_request_form, self.okta_user_id: okta_user_id_in_request_form}


    