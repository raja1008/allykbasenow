from sqlalchemy import create_engine
import datetime as DateTime, time as Time
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

class ModelCategorylist:
# Load "Category on Data Grid" -- BEGIN --
    def loadcategory(userid):
        print('inside loadcategory')
        loadcategory_query = "select category_id, category_name from tbl_category where COALESCE(category_removed, FALSE) = FALSE and userid = %s ORDER BY category_name; "
        try:
            connection = psycopg2.connect(host=global_host, user=global_user, password=global_password,
                                          dbname=global_db, port=global_port)
            cursor = connection.cursor('cursor_unique_name', cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute(loadcategory_query, userid)
            loadcategory_data = list(cursor)
            print('loaddata success')
        except Exception as e:
            loadcategory_data = "[{errormessage: 'error'}]"
            print(str(e))
            raise
        connection.close()
        return loadcategory_data
# Load "Category list on Data Grid" -- END --

# Category CRUD operations -- Begin --
    def insertcategory(category_name, userid):
        print('inside insertcategory')
        engine = create_engine(db_string)
        connection = engine.connect()
        transaction = connection.begin()
        try:
            connection.execute(
                "INSERT INTO tbl_category (category_name, userid) VALUES (%s, %s);",
                category_name, userid)
            transaction.commit()
            print('insert success')
        except Exception as e:
            transaction.rollback()
            print(str(e))
            raise
        connection.close()
        engine.dispose()

    def updatecategory(category_id, category_name):
        print('inside updatecategory')
        # Create Dictionary for holding update columns.
        Dictionary_Updatelist = {}
        # Add dictionary items based on update fields. -- BEGIN --
        if (category_id and str(category_id).strip() != ""):
            Dictionary_Updatelist['category_id'] = category_id
        if (category_name and str(category_name).strip() != ""):
            Dictionary_Updatelist['category_name'] = category_name
        # -- END --
        # Create Update Query and Parameters for execution.
        Query_Update_String = "UPDATE tbl_category SET %s WHERE category_id = %s" % (
        ', '.join("%s = %%s" % u for u in Dictionary_Updatelist.keys()), category_id)
        Parameters = (tuple(Dictionary_Updatelist.values()),)
        # print (Query_Update_String, Parameters)
        # Create engine, connection, begin transaction and after execution dispose.
        engine = create_engine(db_string)
        connection = engine.connect()
        transaction = connection.begin()
        try:
            connection.execute(Query_Update_String, Parameters)
            transaction.commit()
            print('update success')
        except Exception as e:
            transaction.rollback()
            print(str(e))
            raise
        connection.close()
        engine.dispose()

    def removecategory(category_id):
        print('inside removecategory')
        engine = create_engine(db_string)
        connection = engine.connect()
        transaction = connection.begin()
        try:
            connection.execute("UPDATE tbl_category SET category_removed = TRUE WHERE category_id = %s", category_id)
            transaction.commit()
            print('removed success')
        except Exception as e:
            transaction.rollback()
            print(str(e))
            raise
        connection.close()
        engine.dispose()
# Category CRUD operations -- End --