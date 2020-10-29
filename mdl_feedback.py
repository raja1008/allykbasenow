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

class ModelFeedback:
    # Feedback Note GET && CRUD operations -- Begin --
    def getfeedbacknote(eventlist_id):
        print('inside getfeedbacknote')
        getfeedbacknote_query = "select * from tbl_feedback where COALESCE(feedback_removed, FALSE) = FALSE and eventlistid = %s"
        try:
            connection = psycopg2.connect(host=global_host, user=global_user, password=global_password,
                                          dbname=global_db, port=global_port)
            cursor = connection.cursor('cursor_unique_name', cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute(getfeedbacknote_query, [eventlist_id])
            getfeedbacknote_data = list(cursor)
            print('getfeedbacknote success')
        except Exception as e:
            getfeedbacknote_data = "[{errormessage: 'error'}]"
            print(str(e))
            raise
        connection.close()
        return getfeedbacknote_data

    def getfeedbackgrid(eventlistid_collection):
        print('inside getfeedbackgrid')
        getfeedbackgrid_query = "select eventlistid, '' as eventdescription, feedbacknote from tbl_feedback where eventlistid IN %(eventlistid)s AND COALESCE(feedback_removed, FALSE) = FALSE;"
        try:
            connection = psycopg2.connect(host=global_host, user=global_user, password=global_password,
                                          dbname=global_db, port=global_port)
            cursor = connection.cursor('cursor_unique_name', cursor_factory=psycopg2.extras.RealDictCursor)
            # Note: This is a variation of "loadeventlistgallery" method in mdl_eventlist.py
            cursor.execute(getfeedbackgrid_query,
                           {
                               'eventlistid': tuple(eventlistid_collection),  # Converts the list to a tuple.
                           })
            getfeedbacknote_data = list(cursor)
            print('getfeedbackgrid success')
        except Exception as e:
            getfeedbacknote_data = "[{errormessage: 'error'}]"
            print(str(e))
            raise
        connection.close()
        return getfeedbacknote_data

    def insertfeedbacknote(eventlistid, feedbacknote):
        print('inside insertfeedbacknote')
        engine = create_engine(db_string)
        connection = engine.connect()
        transaction = connection.begin()
        try:
            connection.execute("INSERT INTO tbl_feedback(eventlistid, feedbacknote) VALUES (%s, %s);", eventlistid,
                               feedbacknote)
            transaction.commit()
            print('insert success')
        except Exception as e:
            transaction.rollback()
            print(str(e))
            raise
        connection.close()
        engine.dispose()

    def updatefeedbacknote(eventlistid, feedbacknote):
        print('inside updatefeedbacknote')
        # Create Dictionary for holding update columns.
        Dictionary_Updatelist = {}

        # Add dictionary items based on update fields. -- BEGIN --
        if (feedbacknote and str(feedbacknote).strip() != ""):
            Dictionary_Updatelist['feedbacknote'] = feedbacknote
        # Add dictionary items based on update fields. -- END --

        # Create Update Query and Parameters for execution.
        Query_Update_String = "UPDATE tbl_feedback SET %s WHERE eventlistid = %s" % (
        ', '.join("%s = %%s" % u for u in Dictionary_Updatelist.keys()), eventlistid)
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

    def removefeedbacknote(eventlistid):
        print('inside removefeedbacknote')
        engine = create_engine(db_string)
        connection = engine.connect()
        transaction = connection.begin()
        try:
            connection.execute("UPDATE tbl_feedback SET feedback_removed = TRUE WHERE eventlistid = %s", eventlistid)
            transaction.commit()
            print('removed success')
        except Exception as e:
            transaction.rollback()
            print(str(e))
            raise
        connection.close()
        engine.dispose()
# Feedback Note CRUD operations -- End --