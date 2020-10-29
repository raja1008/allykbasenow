from sqlalchemy import create_engine
import datetime as DateTime, time as Time
import psycopg2
import json
from psycopg2.extras import RealDictCursor

### Postgresql Connection ###
global_host = "localhost"
global_user = "allykadmin"
global_password = "systems"
global_db = "live"
global_port = 5432
db_string = "postgresql+psycopg2://" + global_user + ":" + global_password + "@" + global_host + "/" + global_db + ""
#############################

class ModelEventTemplate:

    # Load "Template Eventlist on Data Grid" -- BEGIN --
    def loadeventtemplate(weekday, userid):
        print('inside loadeventtemplate')

        # With daybegin and dayend for "starttime".
        loadeventtemplate_query = "select templatelist_id, template_event_description, template_starttime, template_expectfinishtime, template_objectiveid, template_categoryid from tbl_eventtemplate where COALESCE(template_removed, FALSE) = FALSE  and template_weekdayid = %s and userid = %s order by template_starttime, template_expectfinishtime, template_event_description; "

        try:
            connection = psycopg2.connect(host=global_host, user=global_user, password=global_password,
                                          dbname=global_db, port=global_port)
            cursor = connection.cursor('cursor_unique_name', cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute(loadeventtemplate_query, [weekday, userid])
            loadeventtemplate_data = list(cursor)
            print('loaddata success')
        except Exception as e:
            loadeventtemplate_data = "[{errormessage: 'error'}]"
            print(str(e))
            raise
        connection.close()
        return loadeventtemplate_data
# Load "Template Eventlist on Data Grid" -- END -


# Events CRUD operations -- Begin --
    def inserteventtemplate(event_description, starttime, expectfinishtime, objectiveid, categoryid, weekdayid, userid):
        print('inside inserteventtemplate')
        engine = create_engine(db_string)
        connection = engine.connect()
        transaction = connection.begin()
        try:
            if(str(objectiveid).strip() != "undefined" and str(objectiveid).strip() != ""):
                connection.execute("INSERT INTO tbl_eventtemplate(template_event_description, template_starttime, template_expectfinishtime, template_objectiveid, template_weekdayid, userid) VALUES (%s, %s, %s, %s, %s, %s);", event_description, starttime, expectfinishtime, objectiveid, weekdayid, userid)
            elif(str(categoryid).strip() != "undefined" and str(categoryid).strip() != ""):
                connection.execute("INSERT INTO tbl_eventtemplate(template_event_description, template_starttime, template_expectfinishtime, template_categoryid, template_weekdayid, userid) VALUES (%s, %s, %s, %s, %s, %s);", event_description, starttime, expectfinishtime, categoryid, weekdayid, userid)
            transaction.commit()
            print('insert success')
        except Exception as e:
            transaction.rollback()
            print(str(e))
            raise
        connection.close()
        engine.dispose()

    def updateeventtemplate(templatelist_id, event_description, starttime, expectfinishtime, objectiveid, categoryid):
        print('inside updateeventtemplate')
        # Create Dictionary for holding update columns.
        Dictionary_Updatelist = {}

        # Add dictionary items based on update fields. -- BEGIN --
        if(event_description and str(event_description).strip() != ""):
            Dictionary_Updatelist['template_event_description'] = event_description

        if(starttime and str(starttime).strip() != ""):
            Dictionary_Updatelist['template_starttime'] = starttime

        if(expectfinishtime and str(expectfinishtime).strip() != ""):
            Dictionary_Updatelist['template_expectfinishtime'] = expectfinishtime

        if(objectiveid and str(objectiveid).strip() != ""):
            Dictionary_Updatelist['template_objectiveid'] = objectiveid
            Dictionary_Updatelist['template_categoryid'] = None

        if (categoryid and str(categoryid).strip() != "" and str(objectiveid).strip() == ""):
            Dictionary_Updatelist['template_categoryid'] = categoryid
            Dictionary_Updatelist['template_objectiveid'] = None
        # -- END --

        # Create Update Query and Parameters for execution.
        Query_Update_String = "UPDATE tbl_eventtemplate SET %s WHERE templatelist_id = %s" % (', '.join("%s = %%s" % u for u in Dictionary_Updatelist.keys()), templatelist_id)
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

    def updatetemplateweekdayid(templatelistid_collection, weekdayid):
        print('inside updatetemplateweekdayid')
        engine = create_engine(db_string)
        connection = engine.connect()
        transaction = connection.begin()
        try:
            # Split string and convert the data into array format.
            templatelistid_collection_array = templatelistid_collection.strip().split(",")
            # Make as many "%s" based on the amount or count of values in the "eventlistid_collection_array" array.
            formated_templatelistid = ','.join(['%s'] * len(templatelistid_collection_array))
            # Build query for appending "weekdayid" then, concat "templatelist_id" and then appending %s for templatelist_id.
            buildQuery = "UPDATE tbl_eventtemplate SET template_weekdayid = (%s) " % weekdayid + " WHERE templatelist_id IN (%s) " % formated_templatelistid
            connection.execute(buildQuery, tuple(templatelistid_collection_array))
            transaction.commit()
            print('bulk weekdayid update success.')
        except Exception as e:
            transaction.rollback()
            print(str(e))
            raise
        connection.close()
        engine.dispose()

    def removeeventtemplate(templatelist_id):
        print('inside removeeventtemplate')
        engine = create_engine(db_string)
        connection = engine.connect()
        transaction = connection.begin()
        try:
            connection.execute("UPDATE tbl_eventtemplate SET template_removed = TRUE WHERE templatelist_id = %s", templatelist_id)
            transaction.commit()
            print('removed success')
        except Exception as e:
            transaction.rollback()
            print(str(e))
            raise
        connection.close()
        engine.dispose()
# Events CRUD operations -- End --