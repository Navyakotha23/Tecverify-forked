import abc

import uuid
from datetime import datetime

class Generic_DB(metaclass=abc.ABCMeta):

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
        This method reads Secrets list from database
        """

        pass


    @abc.abstractmethod
    def write(self, data) -> bool:
        """
        This method writes Secret into the database
        """

        pass
            

    def prepare_secret_dictionary_for_auto_save_secret(self, okta_shared_secret, okta_logged_in_user_id, okta_logged_in_username, okta_factor_id):
        """
        This method prepares Secret for auto saving
        """
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
        This method auto saves secret into the database
        """
        
        pass
            

    def prepare_secret_dictionary_for_update_secret(self, form_data, okta_logged_in_user_id):
        """
        This method prepares Secret from the form data received
        """
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
        This method manually saves secret into the database from the form data received.
        """
        
        pass


    @abc.abstractmethod
    def delete_secret(self, secret_id) -> bool:
        """
        This method deletes a secret record in the database based on the secret_id
        """

        pass            
        

    def parse_form_data(self, request, neededOktaUserIDinRequestForm):
        """
        If idToken is there in Headers then this method parses form-data and returns SecretName, SecretKey
        Else this method expects oktaUserId in form-data to parse it and return SecretName, SecretKey and OktaUserId
        """
        # print("request: ", request)
        # print("request.form:", request.form)
        secret_name_VALUE_in_request_form = request.form[self.secret_name_KEY_in_request_form] if self.secret_name_KEY_in_request_form in request.form else None
        secret_key_VALUE_in_request_form = request.form[self.secret_key_KEY_in_request_form] if self.secret_key_KEY_in_request_form in request.form else None
        if not neededOktaUserIDinRequestForm:
            return {self.secret_name: secret_name_VALUE_in_request_form, self.secret_key: secret_key_VALUE_in_request_form}
        else:
            okta_user_id_VALUE_in_request_form = request.form[self.okta_user_id_KEY_in_request_form] if self.okta_user_id_KEY_in_request_form in request.form else None
            return {self.secret_name: secret_name_VALUE_in_request_form, self.secret_key: secret_key_VALUE_in_request_form, self.okta_user_id: okta_user_id_VALUE_in_request_form}


    