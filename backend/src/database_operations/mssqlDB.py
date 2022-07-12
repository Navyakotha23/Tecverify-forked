import pymssql

from database_operations.genericDB import Generic_DB
from common.envVars import EnvVars

class MSSQL_DB(Generic_DB):

    def __init__(self, idGenerator_obj, crypt_obj, mssql_conn, app) -> None:
        self.idGenerator_obj = idGenerator_obj
        self.crypt_obj = crypt_obj
        self.mssql_conn = mssql_conn
        self.app = app
    
    
    def establish_db_connection():
        """
        This method establishes connection with the database server
        """
        # print("DB Connection Established")
        try:
            conn = pymssql.connect(EnvVars.MS_SQL_SERVER, EnvVars.MS_SQL_USERNAME, EnvVars.MS_SQL_PASSWORD)
            
            cursor = conn.cursor()
            conn.autocommit(True)

            create_db_query = '''
                        if not exists (select * from sys.databases where name = '''"'" + EnvVars.DATABASE_NAME + "'"''') 
                        begin 
                            create database ''' + EnvVars.DATABASE_NAME + ''' 
                        end
                      '''
            cursor.execute(create_db_query)

            use_db_query = "use " + EnvVars.DATABASE_NAME
            cursor.execute(use_db_query)

            create_table_query = '''
                                    if not exists (SELECT * FROM sys.tables where name = '''"'" + EnvVars.TABLE_NAME + "'"''') 
                                    begin 
                                        CREATE TABLE ''' + EnvVars.TABLE_NAME + '''
                                        (
                                            ''' + EnvVars.SECRET_NAME + '''    VARCHAR(50)     NOT NULL, 
                                            ''' + EnvVars.SECRET_KEY + '''    VARCHAR(300)    NOT NULL, 
                                            ''' + EnvVars.OKTA_USER_ID + '''    VARCHAR(30)     NOT NULL,
                                            ''' + EnvVars.SECRET_ID + '''    VARCHAR(50)     NOT NULL, 
                                            ''' + EnvVars.SECRET_UPDATED_AT + '''    VARCHAR(30)     NOT NULL,
                                            ''' + EnvVars.OKTA_FACTOR_ID + '''    VARCHAR(30)
                                        )
                                    end
                                '''
            cursor.execute(create_table_query)

            conn.autocommit(False)
            conn.commit()
            return conn
        except Exception as e:
            print("\nException in establish_db_connection(): ", e)


    def read(self):
        # conn = self.establish_db_connection()
        conn = self.mssql_conn
        try:
            cursor = conn.cursor()
            select_query = '''SELECT ''' + EnvVars.SECRET_NAME + ''', ''' + EnvVars.SECRET_KEY + ''', ''' + EnvVars.OKTA_USER_ID + ''', ''' + EnvVars.SECRET_ID + ''', ''' + EnvVars.SECRET_UPDATED_AT + ''', ''' + EnvVars.OKTA_FACTOR_ID + ''' from ''' + EnvVars.TABLE_NAME
            cursor.execute(select_query)
            secrets = []
            for row in cursor:
                secretInfo = {}
                secretInfo[EnvVars.SECRET_NAME] = row[0]
                secretInfo[EnvVars.SECRET_KEY] = row[1]
                secretInfo[EnvVars.OKTA_USER_ID] = row[2]
                secretInfo[EnvVars.SECRET_ID] = row[3]
                secretInfo[EnvVars.SECRET_UPDATED_AT] = row[4]
                secretInfo[EnvVars.OKTA_FACTOR_ID] = row[5]
                secrets.append(secretInfo)
            # conn.close()
            # print("DB Connection Closed in read()")
            return secrets
        except Exception as e:
            print("\nException in read(): ", e)
            self.app.logger.info("\n\nException in read(): {0}\n".format(e))
            return None


    def write(self, data) -> bool:
        # conn = self.establish_db_connection()
        conn = self.mssql_conn
        try:
            cursor = conn.cursor()
            insert_query = '''INSERT INTO '''+ EnvVars.TABLE_NAME + '''(''' + EnvVars.SECRET_NAME + ''', ''' + EnvVars.SECRET_KEY + ''', ''' + EnvVars.OKTA_USER_ID + ''', ''' + EnvVars.SECRET_ID + ''', ''' + EnvVars.SECRET_UPDATED_AT + ''', ''' + EnvVars.OKTA_FACTOR_ID + ''') VALUES(%s, %s, %s, %s, %s, %s)'''
            string1 = data[EnvVars.SECRET_NAME]
            string2 = data[EnvVars.SECRET_KEY]
            string3 = data[EnvVars.OKTA_USER_ID]
            string4 = data[EnvVars.SECRET_ID]
            string5 = data[EnvVars.SECRET_UPDATED_AT]
            string6 = data[EnvVars.OKTA_FACTOR_ID]
            cursor.execute(insert_query, (string1, string2, string3, string4, string5, string6))
            conn.commit()
            # conn.close()
            # print("DB Connection Closed in write()")
            return True
        except Exception as e:
            print("\nException in write(): ", e)
            self.app.logger.info("\n\nException in write(): {0}\n".format(e))
            return False

        
    def delete_secret(self, secret_id) -> bool:
        # conn = self.establish_db_connection()
        conn = self.mssql_conn
        try:
            cursor = conn.cursor()
            delete_query = '''DELETE from ''' + EnvVars.TABLE_NAME + ''' where ''' + EnvVars.SECRET_ID + ''' = %s'''
            cursor.execute(delete_query, secret_id)
            conn.commit()
            # conn.close()
            # print("DB Connection Closed in delete_secret()")
            return True
        except Exception as e:
            print("\nException in delete_secret(): ", e)
            self.app.logger.info("\n\nException in delete_secret(): {0}\n".format(e))
            return False

    
    def auto_save_secret(self, okta_shared_secret, okta_logged_in_user_id, okta_logged_in_username, okta_factor_id) -> bool:
        secretInfo = self.prepare_secret_dictionary_for_auto_save_secret(okta_shared_secret, okta_logged_in_user_id, okta_logged_in_username, okta_factor_id)
        self.write(secretInfo)


    def manual_save_secret(self, form_data, okta_logged_in_user_id) -> bool:
        secretInfo = self.prepare_secret_dictionary_for_manual_save_secret(form_data, okta_logged_in_user_id)
        return self.write(secretInfo)


    def destroy_db_connection(self, mssql_conn):
        """
        This method destroys connection with the database server
        """
        conn = mssql_conn
        try:
            conn.close()
            return True
        except Exception as e:
            print("\nException in destroy_db_connection(): ", e)
            return False