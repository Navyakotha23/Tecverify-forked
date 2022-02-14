import json
import os
import uuid
from datetime import datetime

import pymssql

class AdminSecret:

    def __init__(self, file: str, crypt_obj, MS_SQL_SERVER, MS_SQL_USERNAME, MS_SQL_PASSWORD, DATABASE_NAME, TABLE_NAME, SHOW_LOGS) -> None:
        self.file = file
        self.crypt_obj = crypt_obj
        self.ms_sql_server = MS_SQL_SERVER
        self.ms_sql_username = MS_SQL_USERNAME
        self.ms_sql_password = MS_SQL_PASSWORD
        self.database_name = DATABASE_NAME
        self.table_name = TABLE_NAME
        self.show_logs = SHOW_LOGS

    
    def establish_db_connection(self):
        print("\nIn establish_db_connection()\n")
        try:
            conn = pymssql.connect(self.ms_sql_server, self.ms_sql_username, self.ms_sql_password)
            if self.show_logs: print("self.ms_sql_server: ", self.ms_sql_server)
            if self.show_logs: print("self.ms_sql_username: ", self.ms_sql_username)
            if self.show_logs: print("self.ms_sql_password: ", self.ms_sql_password)
            if self.show_logs: print("Successfully Connected to MS-SQL server")

            cursor = conn.cursor()
            conn.autocommit(True)

            #
            if self.show_logs: print("self.database_name: ", self.database_name)
            # dbName_WithQuotes = "'" + self.database_name + "'"
            # print("dbName_WithQuotes: ", dbName_WithQuotes)
            create_db_query = '''
                        if not exists (select * from sys.databases where name = '''"'" + self.database_name + "'"''') 
                        begin 
                            create database ''' + self.database_name + ''' 
                        end
                      '''
            if self.show_logs: print("create_db_query: ", create_db_query)
            cursor.execute(create_db_query)
            if self.show_logs: print("Created the Database")
            #

            ##
            use_db_query = "use " + self.database_name
            if self.show_logs: print("use_db_query: ", use_db_query)
            cursor.execute(use_db_query)
            if self.show_logs: print("Used the Database")
            ##

            ###
            if self.show_logs: print("self.table_name: ", self.table_name)
            # tableName_WithQuotes = "'" + self.table_name + "'"
            # print("tableName_WithQuotes: ", tableName_WithQuotes)
            create_table_query = '''
                                    if not exists (SELECT * FROM sys.tables where name = '''"'" + self.table_name + "'"''') 
                                    begin 
                                        CREATE TABLE ''' + self.table_name + '''
                                        (
                                            secretName    VARCHAR(50)     NOT NULL, 
                                            secret     VARCHAR(300)    NOT NULL, 
                                            oktaUserId     VARCHAR(30)    NOT NULL,
                                            id     VARCHAR(50)     NOT NULL, 
                                            updatedAt      VARCHAR(30)    NOT NULL
                                        )
                                    end
                                '''
            if self.show_logs: print("create_table_query: ", create_table_query)
            cursor.execute(create_table_query)
            if self.show_logs: print("Created the Table")
            ###

            conn.autocommit(False)
            conn.commit()
            if self.show_logs: print("Successfully executed the queries")
            print("Out establish_db_connection()\n")
            return conn
        except Exception as e:
            print("\nERROR in establish_db_connection(): ", e)

    
    # def destroy_db_connection(self, connObj):
    #     print("In destroy_db_connection() in adminSecret.py")
    #     try:
    #         connObj.close()
    #         return True
    #     except Exception as e:
    #         print("\nERROR in destroy_db_connection(): ", e)
    #         return False

        
    ###################################################################
    # def auto_save_secret(self, okta_shared_secret, okta_logged_in_user_id, connObj) -> bool:
    def auto_save_secret(self, okta_shared_secret, okta_logged_in_user_id) -> bool:
        """
        This method updates file with form data received.
        """
        print("-----In auto_save_secret() in adminSecret.py-----")
        # secrets_list = self.read(connObj)
        secrets_list = self.read()
        id = self.generate_unique_id(secrets_list)
        secretInfo = {}
        secretInfo['secretName'] = 'AutoSavedSecret'
        secretInfo['secret'] = self.crypt_obj.encrypt(okta_shared_secret)
        secretInfo['oktaUserId'] = okta_logged_in_user_id
        secretInfo['id'] = id
        secretInfo['updatedAt'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print("secretInfo: ", secretInfo)
        print("-----Out of auto_save_secret() in adminSecret.py-----")
        # return self.write(secretInfo, connObj)
        return self.write(secretInfo)
    ###################################################################


    # def update_secret(self, form_data, okta_logged_in_user_id, connObj) -> bool:
    def update_secret(self, form_data, okta_logged_in_user_id) -> bool:
        """
        This method updates file with form data received.
        """
        if self.show_logs: print("-----In update_secret(self, form_data, okta_logged_in_user_id) in adminSecret.py-----")
        # secrets_list = self.read(connObj)
        secrets_list = self.read()
        id = self.generate_unique_id(secrets_list)
        form_data['secret'] = self.crypt_obj.encrypt(form_data['secret'])
        if self.show_logs: print("okta_logged_in_user_id: " + okta_logged_in_user_id)
        form_data['oktaUserId'] = okta_logged_in_user_id
        if self.show_logs: print("form_data['oktaUserId']: " + form_data['oktaUserId'])
        form_data['id'] = id
        form_data['updatedAt'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if self.show_logs: print("form_data: ", form_data)
        if self.show_logs: print("-----Out of update_secret(self, form_data, okta_logged_in_user_id) in adminSecret.py-----")
        # return self.write(form_data, connObj)
        return self.write(form_data)

    # def delete_secret(self, secretId, connObj) -> bool:
    def delete_secret(self, secretId) -> bool:
        """
        This method deletes a record based on the secretId
        """
        conn = self.establish_db_connection()
        try:
            # cursor = connObj.cursor()
            cursor = conn.cursor()
            delete_query = '''DELETE from ''' + self.table_name + ''' where id = %s'''
            if self.show_logs: print("delete_query: ", delete_query)
            cursor.execute(delete_query, secretId)
            # connObj.commit()
            conn.commit()
            if self.show_logs: print("Deleted successfully")
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
        conn = self.establish_db_connection()
        try:
            # cursor = connObj.cursor()
            cursor = conn.cursor()
            insert_query = '''INSERT INTO '''+ self.table_name + '''(secretName, secret, oktaUserId, id, updatedAt) VALUES(%s, %s, %s, %s, %s)'''
            if self.show_logs: print("insert_query: ", insert_query)
            string1 = data['secretName']
            string2 = data['secret']
            string3 = data['oktaUserId']
            string4 = data['id']
            string5 = data['updatedAt']
            cursor.execute(insert_query, (string1, string2, string3, string4, string5))
            if self.show_logs: print("form_data inserted as a record in Secrets table")
            # connObj.commit()
            conn.commit()
            # connObj.close()
            conn.close()
            return True
        except Exception as e:
            print("\nERROR in write(): ", e)
            return False

        # try:
        #     with open(self.file, 'w') as fHandle:
        #         json.dump(data, fHandle, indent=4)
        #     return True
        # except Exception as e:
        #     return False

    # def read(self, connObj):
    def read(self):
        """
        This method reads from file which stores Admin Secrets
        """
        conn = self.establish_db_connection()
        try:
            # cursor = connObj.cursor()
            cursor = conn.cursor()
            select_query = '''SELECT secretName, secret, oktaUserId, id, updatedAt from ''' + self.table_name
            if self.show_logs: print("select_query: ", select_query)
            cursor.execute(select_query)
            secrets = []
            for row in cursor:
                secretInfo = {}
                secretInfo["secretName"] = row[0]
                secretInfo["secret"] = row[1]
                secretInfo["oktaUserId"] = row[2]
                secretInfo["id"] = row[3]
                secretInfo["updatedAt"] = row[4]
                if self.show_logs: print("\nsecretInfo: ", secretInfo)
                secrets.append(secretInfo)
            if self.show_logs: print("\nsecrets_list: ", secrets)    
            if self.show_logs: print("Successfully retrieved records from Secrets Table")
            # connObj.close()
            conn.close()
            return secrets
        except Exception as e:
            print("\nERROR in read(): ", e)
            return None

        # try:
        #     if not os.path.isfile(self.file) or os.stat(self.file).st_size == 0:
        #         self.create_empty_json_file()
        #     with open(self.file, 'r') as fHandle:
        #         secrets = json.load(fHandle)
        #     return secrets
        # except Exception as e:
        #     return None

    # def create_empty_json_file(self) -> bool:
    #     """
    #     This method creates empty JSON file 
    #     """
    #     try:
    #         default_data = []
    #         self.write(default_data)
    #         return True
    #     except Exception as e:
    #         print("\nERROR in create_empty_json_file(): ", e)
    #         return False

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
        secret_name = request.form['secretName'] if 'secretName' in request.form else None
        admin_secret = request.form['adminSecret'] if 'adminSecret' in request.form else None
        return {'secretName': secret_name, 'secret': admin_secret}

    def parse_form_data_for_okta_userid(self, request):
        """
        This method parse form data and returns SecretName, Secret and OktaUserId
        """
        secret_name = request.form['secretName'] if 'secretName' in request.form else None
        admin_secret = request.form['adminSecret'] if 'adminSecret' in request.form else None
        okta_userid = request.form['oktaUserId'] if 'oktaUserId' in request.form else None
        return {'secretName': secret_name, 'secret': admin_secret, 'oktaUserId': okta_userid}

