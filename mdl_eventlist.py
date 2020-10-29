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

class ModelEventslist:

# FileUpload insert operations -- Begin --
    def insertmedia(insertdata):
        print('inside insertfileupload')
        try:
            connection = psycopg2.connect(host=global_host, user=global_user, password=global_password,
                                          dbname=global_db, port=global_port)
            cursor = connection.cursor()
            insert_query = 'INSERT INTO tbl_media (eventlistid, mediafilename, mediapathid) VALUES %s'
            psycopg2.extras.execute_values(cursor, insert_query, insertdata, template=None, page_size=100)
            connection.commit()
            print('media insert success')
        except Exception as e:
            print(str(e))
            raise
        connection.close()
# FileUpload insert operations -- End --

# Events CRUD operations -- Begin --
    def bulktemplate_inserteventlist(assigndate, user_TimeZone, userid, weekdayid):
        print('inside bulktemplate_inserteventlist')
        try:
            connection = psycopg2.connect(host=global_host, user=global_user, password=global_password,
                                          dbname=global_db, port=global_port)
            cursor = connection.cursor()

            # Create Dictionary for holding update columns.
            paramlist = []

            # Add dictionary items based on update fields. -- BEGIN --
            if (assigndate and str(assigndate).strip() != ""):
                paramlist.insert(0, str(assigndate + " "))

            if (user_TimeZone and str(user_TimeZone).strip() != ""):
                paramlist.insert(1, str(" " + user_TimeZone))

            if (assigndate and str(assigndate).strip() != ""):
                paramlist.insert(2, str(assigndate + " "))

            if (user_TimeZone and str(user_TimeZone).strip() != ""):
                paramlist.insert(3, str(" " + user_TimeZone))

            if (userid and str(userid).strip() != ""):
                paramlist.insert(4, str(userid))

            if (weekdayid and str(weekdayid).strip() != ""):
                paramlist.insert(5, str(weekdayid))
            # Add dictionary items based on update fields. -- END --

            insert_query = "INSERT INTO tbl_eventlist ( event_description, starttime, expectfinishtime, objectiveid, categoryid, userid) (SELECT template_event_description, (%s || cast(template_starttime::timestamp as time) || %s)::timestamp with time zone as stime,  (%s || cast(template_expectfinishtime::timestamp as time)  || %s)::timestamp with time zone as etime, template_objectiveid, template_categoryid, userid from tbl_eventtemplate where template_removed=false and userid = %s and template_weekdayid = %s) "
            psycopg2.extras.execute_batch(cursor, insert_query,  (paramlist,))
            connection.commit()
            print('insert success')
        except Exception as e:
            print(str(e))
            raise
        connection.close()

    def insertevents(event_description, starttime, expectfinishtime, objectiveid, categoryid, userid):
        print('inside insertevents')
        engine = create_engine(db_string)
        connection = engine.connect()
        transaction = connection.begin()
        try:
            if(str(objectiveid).strip() != "undefined" and str(objectiveid).strip() != ""):
                connection.execute("INSERT INTO tbl_eventlist(event_description, starttime, expectfinishtime, objectiveid, userid) VALUES (%s, %s, %s, %s, %s);", event_description, starttime, expectfinishtime, objectiveid, userid)
            elif(str(categoryid).strip() != "undefined" and str(categoryid).strip() != ""):
                connection.execute("INSERT INTO tbl_eventlist(event_description, starttime, expectfinishtime, categoryid, userid) VALUES (%s, %s, %s, %s, %s);", event_description, starttime, expectfinishtime, categoryid, userid)
            transaction.commit()
            print('insert success')
        except Exception as e:
            transaction.rollback()
            print(str(e))
            raise
        connection.close()
        engine.dispose()

    def updateevents(eventlist_id, event_description, starttime, expectfinishtime, eventcompletedstatus, objectiveid, categoryid):
        print('inside updateevents')
        # Create Dictionary for holding update columns.
        Dictionary_Updatelist = {}

        # Add dictionary items based on update fields. -- BEGIN --
        if(event_description and str(event_description).strip() != ""):
            Dictionary_Updatelist['event_description'] = event_description

        if(starttime and str(starttime).strip() != ""):
            Dictionary_Updatelist['starttime'] = starttime

        if(expectfinishtime and str(expectfinishtime).strip() != ""):
            Dictionary_Updatelist['expectfinishtime'] = expectfinishtime

        if(str(eventcompletedstatus).strip() != "undefined"):
            Dictionary_Updatelist['eventcompletedstatus'] = eventcompletedstatus

        if(objectiveid and str(objectiveid).strip() != ""):
            Dictionary_Updatelist['objectiveid'] = objectiveid
            Dictionary_Updatelist['categoryid'] = None

        if (categoryid and str(categoryid).strip() != "" and str(objectiveid).strip() == ""):
            Dictionary_Updatelist['categoryid'] = categoryid
            Dictionary_Updatelist['objectiveid'] = None
        # -- END --

        # Create Update Query and Parameters for execution.
        Query_Update_String = "UPDATE tbl_eventlist SET %s WHERE eventlist_id = %s" % (', '.join("%s = %%s" % u for u in Dictionary_Updatelist.keys()), eventlist_id)
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

    def bulkeventcompletedstatus(eventlistid_collection):
        print('inside bulkeventcompletedstatus')
        engine = create_engine(db_string)
        connection = engine.connect()
        transaction = connection.begin()
        try:
            # Split string and convert the data into array format.
            eventlistid_collection_array = eventlistid_collection.strip().split(",")
            # Make as many "%s" based on the amount or count of values in the "eventlistid_collection_array" array.
            formated_eventlistid = ','.join(['%s'] * len(eventlistid_collection_array))
            # connection.execute("UPDATE tbl_eventlist SET eventcompletedstatus = TRUE WHERE eventlist_id IN (%s) " % formated_eventlistid, tuple(eventlistid_collection_array))
            connection.execute("UPDATE tbl_eventlist SET eventcompletedstatus = CASE  WHEN	COALESCE(eventcompletedstatus, FALSE) = FALSE  THEN	TRUE  ELSE	FALSE END WHERE eventlist_id IN (%s) " % formated_eventlistid, tuple(eventlistid_collection_array))
            transaction.commit()
            print('bulk marked completed success.')
        except Exception as e:
            transaction.rollback()
            print(str(e))
            raise
        connection.close()
        engine.dispose()

    def removeevent(eventlist_id):
        print('inside removeevent')
        engine = create_engine(db_string)
        connection = engine.connect()
        transaction = connection.begin()
        try:
            connection.execute("UPDATE tbl_eventlist SET eventlist_removed = TRUE WHERE eventlist_id = %s", eventlist_id)
            transaction.commit()
            print('removed success')
        except Exception as e:
            transaction.rollback()
            print(str(e))
            raise
        connection.close()
        engine.dispose()
# Events CRUD operations -- End --

# Load "Event list Gallery" -- BEGIN --
    def loadeventlistgallery(filestorepath, eventlistid_collection):
        print('inside loadeventlistgallery')
        try:
            connection = psycopg2.connect(host=global_host, user=global_user, password=global_password,
                                          dbname=global_db, port=global_port)
            medialist_query = "SELECT CONCAT((select mediapath from tbl_op_mediapath where mediapath_id = %s)::TEXT, mediafilename::TEXT) AS src, CONCAT((select mediapath from tbl_op_mediapath where mediapath_id = 1)::TEXT, mediafilename::TEXT) as thumb FROM tbl_media WHERE eventlistid IN %s AND media_removed = false;"
            cursor = connection.cursor('cursor_unique_name', cursor_factory=psycopg2.extras.RealDictCursor)
            # Note: This is a variation of "getfeedbackgrid" method in mdl_feedback.py
            cursor.execute(medialist_query, (filestorepath, tuple(eventlistid_collection)))
            loadeventmedialist_data = list(cursor)
            # print(loadeventmedialist_data)
            print('loaddata success')
        except Exception as e:
            loadeventmedialist_data = "[{errormessage: 'error'}]"
            print(str(e))
            raise
        connection.close()
        return loadeventmedialist_data
# Load "Event list Gallery" -- END --

# Objective >> Goal >> Category list -- BEGIN --
    def loadOGC(userid):
        print('inside Objective >> Goal >> Category list')
        loadcategory_query = "select o.objective_id as objectiveid, CONCAT (' >>O: ' , o.objective_name , ' >>G: ' , g.goal_name , ' >>C: ' , c.category_name) as event_objectivename from tbl_objective as o left join tbl_goal as g on	g.goal_id = o.goalid left join	tbl_category as c on c.category_id = o.categoryid where	COALESCE(objective_removed, FALSE) = FALSE and COALESCE(objectivecompletedstatus, FALSE) = FALSE and COALESCE(goal_removed, FALSE) = FALSE and COALESCE(goalcompletedstatus, FALSE) = FALSE  and g.userid = %s; "
        try:
            connection = psycopg2.connect(host=global_host, user=global_user, password=global_password, dbname=global_db,
                                          port=global_port)
            cursor = connection.cursor('cursor_unique_name', cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute(loadcategory_query, userid)
            loadogc_data = list(cursor)
            print('loaddata success')
        except Exception as e:
            loadgoal_data = "[{errormessage: 'error'}]"
            print(str(e))
            raise
        connection.close()
        return loadogc_data
# Objective >> Goal >> Category list -- END --

# Category list -- BEGIN --
    def loadCategory(userid):
        print('inside Events-Category list')
        loadcategory_query = "select category_id  as categoryid, category_name as event_categoryname from tbl_category where COALESCE(category_removed, FALSE) = FALSE  and userid = %s order by category_name; "
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

# Load "Event list on Data Grid" -- BEGIN --
    def loadeventlist(daybegin, dayend, userid):
        print('inside loadeventlist')
        if not daybegin or not dayend:
            utc_offset_sec = Time.altzone if Time.localtime().tm_isdst else Time.timezone
            utc_offset = DateTime.timedelta(seconds=-utc_offset_sec)
            #Datetime with timezone --Begin--
            daybegin_nowdt_replace = DateTime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0,
                                                                     tzinfo=DateTime.timezone(
                                                                         offset=utc_offset)).isoformat()
            daybegin = daybegin_nowdt_replace
            dayend_nowdt_replace = DateTime.datetime.now().replace(hour=23, minute=59, second=59, microsecond=999999,
                                                                   tzinfo=DateTime.timezone(offset=utc_offset)).isoformat()
            dayend = dayend_nowdt_replace
            # Datetime with timezone --End--


            # # Datetime without timezone --Begin--
            # daybegin_nowdt_replace = DateTime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
            # daybegin = daybegin_nowdt_replace
            # dayend_nowdt_replace = DateTime.datetime.now().replace(hour=23, minute=59, second=59, microsecond=999999).isoformat()
            # dayend = dayend_nowdt_replace
            # # Datetime without timezone --End--

            # if not daybegin:
            #     daybegin = daybegin_nowdt_replace
            # if not dayend:
            #     dayend = dayend_nowdt_replace

    # With daybegin and dayend for "starttime".
        loadeventlist_query = "select eventlist_id, event_description, starttime, expectfinishtime, objectiveid, categoryid, eventcompletedstatus from tbl_eventlist where COALESCE(eventlist_removed, FALSE) = FALSE  and starttime >= %s and starttime <= %s and userid = %s order by starttime, expectfinishtime, event_description;"

    # WITHOUT daybegin and dayend for "starttime". + WITHOUT table "tbl_feedbacknote" and table "tbl_media"
    #         loadeventlist_query = "select eventlist_id, event_description, starttime, expectfinishtime, objectiveid, eventcompletedstatus from tbl_eventlist where COALESCE(eventlist_removed, FALSE) = FALSE ORDER BY starttime, expectfinishtime; "

    # WITHOUT daybegin and dayend for "starttime". + WITH table "tbl_feedbacknote" "
    #         loadeventlist_query = "select el.eventlist_id, el.event_description, el.starttime, el.expectfinishtime, el.objectiveid, el.eventcompletedstatus, fn.feedback_id, fn.feedbacknote from tbl_eventlist el left join	tbl_feedback fn on	el.eventlist_id = fn.eventlistid where COALESCE(el.eventlist_removed, FALSE) = FALSE order by el.starttime,	el.expectfinishtime ;"

        try:
            connection = psycopg2.connect(host= global_host, user= global_user, password= global_password, dbname= global_db, port = global_port)
            cursor = connection.cursor('cursor_unique_name', cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute(loadeventlist_query, [daybegin, dayend, userid])
            loadeventlist_data = list(cursor)
            # print(loadeventlist_data)
            # loadeventlist_data = json.dumps(cursor.fetchall(), cls=DateTimeEncoder)
            # loadeventlist_data = json.dumps(cursor.fetchall(), cls=JSONEncoder)
            print('loaddata success')
        except Exception as e:
            loadeventlist_data = "[{errormessage: 'error'}]"
            print(str(e))
            raise
        connection.close()
        return loadeventlist_data
# Load "Event list on Data Grid" -- END --



# Unused code --Begin--
# class DateTimeEncoder(json.JSONEncoder):
#     def default(self, o):
#         if isinstance(o, DateTime.datetime):
#             return o.isoformat()
#
#         return json.JSONEncoder.default(self, o)
#
# class JSONEncoder(json.JSONEncoder):
#     """JSONEncoder subclass that knows how to encode date/time, decimal types, and UUIDs."""
#
#     def default(self, o):
#         # See "Date Time String Format" in the ECMA-262 specification.
#         if isinstance(o, DateTime.datetime):
#             r = o.isoformat()
#             if o.microsecond:
#                 r = r[:23] + r[26:]
#             if r.endswith('+00:00'):
#                 r = r[:-6] + 'Z'
#             return r
#         elif isinstance(o, DateTime.date):
#             return o.isoformat()
#         elif isinstance(o, DateTime.time):
#             if o.utcoffset() is not None:
#                 raise ValueError("JSON can't represent timezone-aware times.")
#             r = o.isoformat()
#             if o.microsecond:
#                 r = r[:12]
#             return r
#         elif isinstance(o, (DateTime.Decimal, uuid.UUID)):
#             return str(o)
#         else:
#             return super(JSONEncoder, self).default(o)
# Unused code --End--