import pymssql

from genericDB import Generic_DB

class MSSQL_DB(Generic_DB):

    def __init__(self, crypt_obj, MS_SQL_SERVER, MS_SQL_USERNAME, MS_SQL_PASSWORD, DATABASE_NAME, TABLE_NAME, AUTOSAVED_SECRET_USERNAME_HEAD, SECRET_NAME, SECRET_KEY, OKTA_USER_ID, SECRET_ID, SECRET_UPDATED_AT, OKTA_FACTOR_ID, SECRET_NAME_KEY_IN_REQUEST_FORM, SECRET_KEY_KEY_IN_REQUEST_FORM, OKTA_USER_ID_KEY_IN_REQUEST_FORM, SHOW_LOGS) -> None:
        self.crypt_obj = crypt_obj
        self.ms_sql_server = MS_SQL_SERVER
        self.ms_sql_username = MS_SQL_USERNAME
        self.ms_sql_password = MS_SQL_PASSWORD
        self.database_name = DATABASE_NAME
        self.table_name = TABLE_NAME
        self.auto_saved_secret_username_head = AUTOSAVED_SECRET_USERNAME_HEAD
        self.secret_name = SECRET_NAME
        self.secret_key = SECRET_KEY
        self.okta_user_id = OKTA_USER_ID
        self.secret_id = SECRET_ID
        self.secret_updated_at = SECRET_UPDATED_AT
        self.okta_factor_id = OKTA_FACTOR_ID
        self.secret_name_KEY_in_request_form = SECRET_NAME_KEY_IN_REQUEST_FORM
        self.secret_key_KEY_in_request_form = SECRET_KEY_KEY_IN_REQUEST_FORM
        self.okta_user_id_KEY_in_request_form = OKTA_USER_ID_KEY_IN_REQUEST_FORM
        self.show_logs = SHOW_LOGS
    
    def establish_db_connection(self):
        """
        This method establishes connection with the database server
        """
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


    # def read(self, connObj):
    def read(self):
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


    # def write(self, data, connObj) -> bool:
    def write(self, data) -> bool:
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

        
    # def delete_secret(self, secret_id, connObj) -> bool:
    def delete_secret(self, secret_id) -> bool:
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

    
    # def auto_save_secret(self, okta_shared_secret, okta_logged_in_user_id, connObj) -> bool:
    # def auto_save_secret(self, okta_shared_secret, okta_logged_in_user_id, okta_logged_in_username) -> bool:
    def auto_save_secret(self, okta_shared_secret, okta_logged_in_user_id, okta_logged_in_username, okta_factor_id) -> bool:
        secretInfo = self.prepare_secret_dictionary_for_auto_save_secret(okta_shared_secret, okta_logged_in_user_id, okta_logged_in_username, okta_factor_id)
        self.write(secretInfo)


    # def update_secret(self, form_data, okta_logged_in_user_id, connObj) -> bool:
    def update_secret(self, form_data, okta_logged_in_user_id) -> bool:
        # secrets_list = self.read(connObj)
        form_data = self.prepare_secret_dictionary_for_update_secret(form_data, okta_logged_in_user_id)
        return self.write(form_data)


    def destroy_db_connection(self, connObj):
        """
        This method destroys connection with the database server
        """
        try:
            connObj.close()
            return True
        except Exception as e:
            print("\nERROR in destroy_db_connection(): ", e)
            return False