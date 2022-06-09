import json
import os
import uuid
from datetime import datetime

import pymssql

class AdminSecret:

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

    
    def establish_db_connection(self):
        try:
            conn = pymssql.connect(self.ms_sql_server, self.ms_sql_username, self.ms_sql_password)
            
            cursor = conn.cursor()
            conn.autocommit(True)

            create_db_query = '''
                        if not exists (select * from sys.databases where name = '''"'" + self.database_name + "'"''') 
                        begin 
                            create database ''' + self.database_name + ''' 
                        end
                      '''
            cursor.execute(create_db_query)

            use_db_query = "use " + self.database_name
            cursor.execute(use_db_query)

            create_table_query = '''
                                    if not exists (SELECT * FROM sys.tables where name = '''"'" + self.table_name + "'"''') 
                                    begin 
                                        CREATE TABLE ''' + self.table_name + '''
                                        (
                                            ''' + self.secret_name + '''    VARCHAR(50)     NOT NULL, 
                                            ''' + self.secret_key + '''    VARCHAR(300)    NOT NULL, 
                                            ''' + self.okta_user_id + '''    VARCHAR(30)     NOT NULL,
                                            ''' + self.secret_id + '''    VARCHAR(50)     NOT NULL, 
                                            ''' + self.secret_updated_at + '''    VARCHAR(30)     NOT NULL,
                                            ''' + self.okta_factor_id + '''    VARCHAR(30)
                                        )
                                    end
                                '''
            cursor.execute(create_table_query)

            conn.autocommit(False)
            conn.commit()
            return conn
        except Exception as e:
            print("\nERROR in establish_db_connection(): ", e)

    
    # def destroy_db_connection(self, connObj):
    #     try:
    #         connObj.close()
    #         return True
    #     except Exception as e:
    #         print("\nERROR in destroy_db_connection(): ", e)
    #         return False

        
    # def auto_save_secret(self, okta_shared_secret, okta_logged_in_user_id, connObj) -> bool:
    # def auto_save_secret(self, okta_shared_secret, okta_logged_in_user_id, okta_logged_in_username) -> bool:
    def auto_save_secret(self, okta_shared_secret, okta_logged_in_user_id, okta_logged_in_username, okta_factor_id) -> bool:
        """
        This method updates file with form data received.
        """
        # secrets_list = self.read(connObj)
        secrets_list = self.read()
        id = self.generate_unique_id(secrets_list)
        secretInfo = {}
        secretInfo[self.secret_name] = self.auto_saved_secret_username_head + '.' + okta_logged_in_username
        secretInfo[self.secret_key] = self.crypt_obj.encrypt(okta_shared_secret)
        secretInfo[self.okta_user_id] = okta_logged_in_user_id
        secretInfo[self.secret_id] = id
        secretInfo[self.secret_updated_at] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        secretInfo[self.okta_factor_id] = okta_factor_id
        # return self.write(secretInfo, connObj)
        if self.database_type == "mssql":
            return self.write(secretInfo)
        elif self.database_type == "json":
            secrets_list.append(secretInfo)
            return self.write(secrets_list)


    # def update_secret(self, form_data, okta_logged_in_user_id, connObj) -> bool:
    def update_secret(self, form_data, okta_logged_in_user_id) -> bool:
        """
        This method updates file with form data received.
        """
        # secrets_list = self.read(connObj)
        secrets_list = self.read()
        id = self.generate_unique_id(secrets_list)
        form_data[self.secret_key] = self.crypt_obj.encrypt(form_data[self.secret_key])
        form_data[self.okta_user_id] = okta_logged_in_user_id
        form_data[self.secret_id] = id
        form_data[self.secret_updated_at] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        form_data[self.okta_factor_id] = ""
        # return self.write(form_data, connObj)
        if self.database_type == "mssql":
            return self.write(form_data)
        elif self.database_type == "json":
            secrets_list.append(form_data)
            return self.write(secrets_list)


    # def delete_secret(self, secret_id, connObj) -> bool:
    def delete_secret(self, secret_id) -> bool:
        """
        This method deletes a record based on the secret_id
        """
        if self.database_type == "mssql":
            conn = self.establish_db_connection()
            try:
                # cursor = connObj.cursor()
                cursor = conn.cursor()
                delete_query = '''DELETE from ''' + self.table_name + ''' where ''' + self.secret_id + ''' = %s'''
                cursor.execute(delete_query, secret_id)
                # connObj.commit()
                conn.commit()
                # connObj.close()
                conn.close()
                return True
            except Exception as e:
                print("\nERROR in delete_secret(): ", e)
                return False


    # def write(self, data, connObj) -> bool:
    def write(self, data) -> bool:
        """
        This method writes in to file which stores Admin Secrets
        """

        if self.database_type == "mssql":
            conn = self.establish_db_connection()
            try:
                # cursor = connObj.cursor()
                cursor = conn.cursor()
                insert_query = '''INSERT INTO '''+ self.table_name + '''(''' + self.secret_name + ''', ''' + self.secret_key + ''', ''' + self.okta_user_id + ''', ''' + self.secret_id + ''', ''' + self.secret_updated_at + ''', ''' + self.okta_factor_id + ''') VALUES(%s, %s, %s, %s, %s, %s)'''
                string1 = data[self.secret_name]
                string2 = data[self.secret_key]
                string3 = data[self.okta_user_id]
                string4 = data[self.secret_id]
                string5 = data[self.secret_updated_at]
                string6 = data[self.okta_factor_id]
                cursor.execute(insert_query, (string1, string2, string3, string4, string5, string6))
                # connObj.commit()
                conn.commit()
                # connObj.close()
                conn.close()
                return True
            except Exception as e:
                print("\nERROR in write(): ", e)
                return False
        elif self.database_type == "json":
            try:
                with open(self.file, 'w') as fHandle:
                    json.dump(data, fHandle, indent=4)
                return True
            except Exception as e:
                print("\nERROR in write(): ", e)
                return False


    # def read(self, connObj):
    def read(self):
        """
        This method reads from file which stores Admin Secrets
        """

        if self.database_type == "mssql":
            conn = self.establish_db_connection()
            try:
                # cursor = connObj.cursor()
                cursor = conn.cursor()
                select_query = '''SELECT ''' + self.secret_name + ''', ''' + self.secret_key + ''', ''' + self.okta_user_id + ''', ''' + self.secret_id + ''', ''' + self.secret_updated_at + ''', ''' + self.okta_factor_id + ''' from ''' + self.table_name
                cursor.execute(select_query)
                secrets = []
                for row in cursor:
                    secretInfo = {}
                    secretInfo[self.secret_name] = row[0]
                    secretInfo[self.secret_key] = row[1]
                    secretInfo[self.okta_user_id] = row[2]
                    secretInfo[self.secret_id] = row[3]
                    secretInfo[self.secret_updated_at] = row[4]
                    secretInfo[self.okta_factor_id] = row[5]
                    secrets.append(secretInfo)
                # connObj.close()
                conn.close()
                return secrets
            except Exception as e:
                print("\nERROR in read(): ", e)
                return None
        elif self.database_type == "json":
            try:
                if not os.path.isfile(self.file) or os.stat(self.file).st_size == 0:
                    self.create_empty_json_file()
                with open(self.file, 'r') as fHandle:
                    secrets = json.load(fHandle)
                return secrets
            except Exception as e:
                print("\nERROR in read(): ", e)
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
            print("\nERROR in create_empty_json_file(): ", e)
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
        id_list = [secret[self.secret_id] for secret in secrets_list]
        if id not in id_list:
            return True
        else:
            return False
        

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

