from sqlalchemy import create_engine
import psycopg2
from psycopg2.extras import RealDictCursor

### Postgresql Connection ###
global_host = "localhost"
global_user = "allykadmin"
global_password = "systems"
global_db = "live"
global_port = 5432
db_string = "postgresql+psycopg2://" + global_user + ":" + global_password + "@" + global_host + "/" + global_db + ""
#############################

class ModelAuthentication:

    # Authentication systems -- Begin --
    # Signup authentication check -- BEGIN --
    def signupauthentication(mobilenumber, email):
        print('inside signupauthentication')
        signupauthentication_query = "select count(user_id) from tbl_user where user_mobilenumber = %s or user_email = %s "
        try:
            connection = psycopg2.connect(host=global_host, user=global_user, password=global_password,
                                          dbname=global_db, port=global_port)
            cursor = connection.cursor('cursor_unique_name', cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute(signupauthentication_query, [mobilenumber, email])
            signupauthentication_data = list(cursor)
            print('signup authdata success')
        except Exception as e:
            signupauthentication_data = "[{errormessage: 'error'}]"
            print(str(e))
            raise
        connection.close()
        return signupauthentication_data

    def insertauthentication(mobilenumber, email, hashedpassword):
         print('inside insertauthentication')
         engine = create_engine(db_string)
         connection = engine.connect()
         transaction = connection.begin()
         try:
             connection.execute("INSERT INTO tbl_user(user_mobilenumber, user_email, user_password) VALUES (%s, %s, %s);", mobilenumber, email, hashedpassword)
             transaction.commit()
             print('insert success')
         except Exception as e:
             transaction.rollback()
             print(str(e))
             raise
         connection.close()
         engine.dispose()
    # Signup authentication check -- END --

    # Signin authentication check -- BEGIN --
    def getsignindetail(mobilenumber, email):
        print('inside signupauthentication')
        getsignindetail_query = "select * from tbl_user where user_mobilenumber = %s and user_email = %s "
        try:
            connection = psycopg2.connect(host=global_host, user=global_user, password=global_password,
                                          dbname=global_db, port=global_port)
            cursor = connection.cursor('cursor_unique_name', cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute(getsignindetail_query, [mobilenumber, email])
            getsignindetail_data = list(cursor)
            print('getsignindetail success')
        except Exception as e:
            signupauthentication_data = "[{errormessage: 'error'}]"
            print(str(e))
            raise
        connection.close()
        return getsignindetail_data
    # Signin authentication check -- END --
    # Authentication systems -- END --