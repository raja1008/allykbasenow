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

class ModelGoallist:
    # Load "Goal on Data Grid" -- BEGIN --
    def loadgoal(userid):
        print('inside loadgoal')
        loadgoal_query = "select goal_id, goal_name, goal_description, categoryid, goalcompletedstatus from tbl_goal where COALESCE(goal_removed, FALSE) = FALSE and userid = %s ORDER BY goal_name; "
        try:
            connection = psycopg2.connect(host=global_host, user=global_user, password=global_password,
                                          dbname=global_db, port=global_port)
            cursor = connection.cursor('cursor_unique_name', cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute(loadgoal_query, userid)
            loadgoal_data = list(cursor)
            print('loaddata success')
        except Exception as e:
            loadgoal_data = "[{errormessage: 'error'}]"
            print(str(e))
            raise
        connection.close()
        return loadgoal_data

    # Load "goal list on Data Grid" -- END --
    # Category list -- BEGIN --
    def loadgoalcategory(userid):
        print('inside loadcategory')
        loadcategory_query = "select category_id, category_name from tbl_category where COALESCE(category_removed, FALSE) = FALSE and userid = %s ORDER BY category_name "
        try:
            connection = psycopg2.connect(host=global_host, user=global_user, password=global_password, dbname=global_db,
                                          port=global_port)
            cursor = connection.cursor('cursor_unique_name', cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute(loadcategory_query, userid)
            loadcategory_data = list(cursor)
            print('loaddata success')
        except Exception as e:
            loadgoal_data = "[{errormessage: 'error'}]"
            print(str(e))
            raise
        connection.close()
        return loadcategory_data
    # Category list -- END --
    # goal CRUD operations -- Begin --
    def insertgoal(goal_name, goal_description, categoryid, userid):
        print('inside insertgoal')
        engine = create_engine(db_string)
        connection = engine.connect()
        transaction = connection.begin()
        try:
            connection.execute(
                "INSERT INTO tbl_goal (goal_name, goal_description, categoryid, userid) VALUES (%s, %s, %s, %s);",
                goal_name, goal_description, categoryid, userid)
            transaction.commit()
            print('insert success')
        except Exception as e:
            transaction.rollback()
            print(str(e))
            raise
        connection.close()
        engine.dispose()

    def updategoal(goal_id, goal_name, goal_description, categoryid, goalcompletedstatus):
        print('inside updategoal')
        # Create Dictionary for holding update columns.
        Dictionary_Updatelist = {}

        # Add dictionary items based on update fields. -- BEGIN --
        if (goal_name and str(goal_name).strip() != ""):
            Dictionary_Updatelist['goal_name'] = goal_name

        if (goal_description and str(goal_description).strip() != ""):
            Dictionary_Updatelist['goal_description'] = goal_description

        if (categoryid and str(categoryid).strip() != ""):
            Dictionary_Updatelist['categoryid'] = categoryid

        if (str(goalcompletedstatus).strip() != "undefined"):
            Dictionary_Updatelist['goalcompletedstatus'] = goalcompletedstatus
        # -- END --

        # Create Update Query and Parameters for execution.
        Query_Update_String = "UPDATE tbl_goal SET %s WHERE goal_id = %s" % (
        ', '.join("%s = %%s" % u for u in Dictionary_Updatelist.keys()), goal_id)
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

    def bulkgoalcompletedstatus(goalid_collection):
        print('inside bulkgoalcompletedstatus')
        engine = create_engine(db_string)
        connection = engine.connect()
        transaction = connection.begin()
        try:
            # Split string and convert the data into array format.
            goalid_collection_array = goalid_collection.strip().split(",")
            # print(goalid_collection_array)
            # Make as many "%s" based on the amount or count of values in the "goalid_collection_array" array.
            formated_goalid = ','.join(['%s'] * len(goalid_collection_array))
            connection.execute(
                "UPDATE tbl_goal SET goalcompletedstatus = CASE  WHEN	COALESCE(goalcompletedstatus, FALSE) = FALSE  THEN	TRUE  ELSE	FALSE END WHERE goal_id IN (%s) " % formated_goalid,
                tuple(goalid_collection_array))
            transaction.commit()
            print('bulk marked completed success.')
        except Exception as e:
            transaction.rollback()
            print(str(e))
            raise
        connection.close()
        engine.dispose()

    def removegoal(goal_id):
        print('inside removegoal')
        engine = create_engine(db_string)
        connection = engine.connect()
        transaction = connection.begin()
        try:
            connection.execute("UPDATE tbl_goal SET goal_removed = TRUE WHERE goal_id = %s", goal_id)
            transaction.commit()
            print('removed success')
        except Exception as e:
            transaction.rollback()
            print(str(e))
            raise
        connection.close()
        engine.dispose()
# goal CRUD operations -- End --