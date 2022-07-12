import abc
from datetime import datetime

from common.envVars import EnvVars


class Generic_DB(metaclass=abc.ABCMeta):
    
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
        id = self.idGenerator_obj.generate_unique_id(secrets_list)
        secretInfo = {}
        secretInfo[EnvVars.SECRET_NAME] = EnvVars.AUTOSAVED_SECRET_USERNAME_HEAD + '.' + okta_logged_in_username
        secretInfo[EnvVars.SECRET_KEY] = self.crypt_obj.encrypt(okta_shared_secret)
        secretInfo[EnvVars.OKTA_USER_ID] = okta_logged_in_user_id
        secretInfo[EnvVars.SECRET_ID] = id
        secretInfo[EnvVars.SECRET_UPDATED_AT] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        secretInfo[EnvVars.OKTA_FACTOR_ID] = okta_factor_id
        return secretInfo


    @abc.abstractmethod
    def auto_save_secret(self, okta_shared_secret, okta_logged_in_user_id, okta_logged_in_username, okta_factor_id) -> bool:
        """
        This method auto saves secret into the database
        """
        
        pass
            

    def prepare_secret_dictionary_for_manual_save_secret(self, form_data, okta_logged_in_user_id):
        """
        This method prepares Secret from the form data received
        """
        secrets_list = self.read()
        id = self.idGenerator_obj.generate_unique_id(secrets_list)
        # Making changes to received form_data to make it as a secretInfo.
        form_data[EnvVars.SECRET_KEY] = self.crypt_obj.encrypt(form_data[EnvVars.SECRET_KEY])
        form_data[EnvVars.OKTA_USER_ID] = okta_logged_in_user_id
        form_data[EnvVars.SECRET_ID] = id
        form_data[EnvVars.SECRET_UPDATED_AT] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        form_data[EnvVars.OKTA_FACTOR_ID] = ""
        # Assigning changed form_data to a secretInfo
        secretInfo = form_data
        return secretInfo


    @abc.abstractmethod
    def manual_save_secret(self, form_data, okta_logged_in_user_id) -> bool:
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
        

    