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

class ModelObjectivelist:

    # Events CRUD operations -- Begin --
    # Load "Event list on Data Grid" -- BEGIN --
    def loadobjective(goalid):
        print('inside loadobjective')
        loadeobjective_query = "select objective_id, objective_name, objective_description, goalid, categoryid, objectivecompletedstatus from tbl_objective where COALESCE(objective_removed, FALSE) = FALSE and goalid = %s ORDER BY objective_name "
        try:
            connection = psycopg2.connect(host=global_host, user=global_user, password=global_password,
                                          dbname=global_db, port=global_port)
            cursor = connection.cursor('cursor_unique_name', cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute(loadeobjective_query, [goalid])
            loadeobjective_data = list(cursor)
            print('loaddata success')
        except Exception as e:
            loadeventlist_data = "[{errormessage: 'error'}]"
            print(str(e))
            raise
        connection.close()
        return loadeobjective_data
    # Load "Event list on Data Grid" -- END --
    def insertobjective(objective_name, objective_description, goalid, categoryid):
        print('inside insertobjective')
        engine = create_engine(db_string)
        connection = engine.connect()
        transaction = connection.begin()
        try:
            connection.execute(
                "INSERT INTO tbl_objective(objective_name, objective_description, goalid, categoryid) VALUES (%s, %s, %s, %s);",
                objective_name, objective_description, goalid, categoryid)
            transaction.commit()
            print('insert success')
        except Exception as e:
            transaction.rollback()
            print(str(e))
            raise
        connection.close()
        engine.dispose()

    def updateobjective(objective_id, objective_name, objective_description, objectivecompletedstatus):
        print('inside updateobjective')
        # Create Dictionary for holding update columns.
        Dictionary_Updatelist = {}

        # Add dictionary items based on update fields. -- BEGIN --
        if (objective_id and str(objective_id).strip() != ""):
            Dictionary_Updatelist['objective_id'] = objective_id

        if (objective_name and str(objective_name).strip() != ""):
            Dictionary_Updatelist['objective_name'] = objective_name

        if (objective_description and str(objective_description).strip() != ""):
            Dictionary_Updatelist['objective_description'] = objective_description

        if (str(objectivecompletedstatus).strip() != "undefined"):
            Dictionary_Updatelist['objectivecompletedstatus'] = objectivecompletedstatus
        # -- END --

        # Create Update Query and Parameters for execution.
        Query_Update_String = "UPDATE tbl_objective SET %s WHERE objective_id = %s" % (
        ', '.join("%s = %%s" % u for u in Dictionary_Updatelist.keys()), objective_id)
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

    def removeobjective(objective_id):
        print('inside removeobjective')
        engine = create_engine(db_string)
        connection = engine.connect()
        transaction = connection.begin()
        try:
            connection.execute("UPDATE tbl_objective SET objective_removed = TRUE WHERE objective_id = %s", objective_id)
            transaction.commit()
            print('removed success')
        except Exception as e:
            transaction.rollback()
            print(str(e))
            raise
        connection.close()
        engine.dispose()
# Events CRUD operations -- End --