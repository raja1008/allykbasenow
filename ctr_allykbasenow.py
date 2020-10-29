from flask import Flask, jsonify, request, render_template, make_response, Blueprint, redirect, flash
from flask_cors import CORS, cross_origin
from mdl_eventtemplate import ModelEventTemplate
from mdl_eventlist import ModelEventslist
from mdl_feedback import ModelFeedback
from mdl_category import ModelCategorylist
from mdl_goal import ModelGoallist
from mdl_objective import ModelObjectivelist
from mdl_authentication import ModelAuthentication
import json
# File upload modules -- BEGIN --
from urllib.parse import urlparse
from werkzeug.utils import secure_filename
import os
import shutil
from datetime import datetime, date, time
# File upload modules -- END --
# Login -- BEGIN --
# pip install flask flask-login flask-wtf flask-sqlalchemy Flask-Bootstrap
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, ValidationError, TextField, IntegerField
from wtforms.validators import InputRequired, Email, Length
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import phonenumbers #pip install phonenumbers
import jwt #pip install pyjwt
# Login -- END --


app = Flask(__name__)
app.config['SECRET_KEY'] = 'Thisissupposedtobesecret!'
JSONWebToken_SecretKey = 'Reciprok3780.002@Ttl1331mf6561$'
CORS(app, resources=r'/api/*')
events_restapi = Blueprint('events_restapi', __name__)


bootstrap = Bootstrap(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Fileupload  Configuration -- BEGIN --
# APP_ROOT = os.path.dirname(os.path.abspath(__file__))
# UPLOAD_FOLDER = "/home/ubuntu160403/AnacondaProjects/allykbasenow/static/uploads/"
UPLOAD_FOLDER = "static/uploads/"
PATH_ID = 1
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'mp4'])
max_file_size = 700 * 1024
# Fileupload  Configuration -- END --


class LoginSignupForm(FlaskForm):
    mobilenumber = IntegerField('Mobile', validators=[InputRequired()])
    email = StringField('Email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=80)])

# App load render login system. ---
@app.route('/')
@cross_origin()
def index():
    loginsignupform = LoginSignupForm()
    return render_template('login-index.html', LoginSignupForm=loginsignupform)

@app.route('/loginsignup', methods=['GET', 'POST'])
@cross_origin()
def loginsignup():
    loginsignupform = LoginSignupForm()
    #Validate Email and Password
    if not loginsignupform.validate_on_submit():
        flash('Invalid credentials')
        return render_template('login-index.html', LoginSignupForm=loginsignupform)
    withplus_mobilenumber = "+" + str(loginsignupform.mobilenumber.data)
    parsed_mobilenumber = phonenumbers.parse(withplus_mobilenumber, None)
    # Validate Mobilenumber
    if not phonenumbers.is_valid_number(parsed_mobilenumber):
        flash('Invalid phone number credentials')
        return render_template('login-index.html', LoginSignupForm=loginsignupform)
    email = loginsignupform.email.data
    password = loginsignupform.password.data
    hashed_password = generate_password_hash(loginsignupform.password.data, method='sha256')
    # print(email)
    # print(password)
    # print(hashed_password)
    # print(withplus_mobilenumber)
    if (request.form['action'] == "btn_login"):
        print("inside login")
        getsignindetail_result = ModelAuthentication.getsignindetail(withplus_mobilenumber, email)
        if (getsignindetail_result):
            saved_user_password = getsignindetail_result[0]['user_password']
            if check_password_hash(saved_user_password, password):
                # print(JSONWebToken_SecretKey)
                access_encoded = jwt.encode({'user_id': ''+ str(getsignindetail_result[0]['user_id']) + ''}, JSONWebToken_SecretKey, algorithm='HS256')
                response = make_response(render_template('index.html'))
                response.set_cookie('access_cookie', access_encoded)
                return response
            else:
                flash('Signin credintials are invalid. Please sign in with correct details.')
                return render_template('login-index.html', LoginSignupForm=loginsignupform)
        else:
            flash('Signin credintials are invalid. Please sign in with correct details.')
            return render_template('login-index.html', LoginSignupForm=loginsignupform)
    elif (request.form['action'] == "btn_signup"):
        print("inside signup")
        signupauthentication_result = ModelAuthentication.signupauthentication(withplus_mobilenumber, email)
        # print(signupauthentication_result[0]['count'])
        if (signupauthentication_result[0]['count'] == 0):
            ModelAuthentication.insertauthentication(withplus_mobilenumber, email, hashed_password)
            flash('Signup successful. Now, please sign in.')
        else:
            flash('Already existing details. Please sign in.')
        # print(email)
        # print(password)
        # print(hashed_password)
        # print(withplus_mobilenumber)
        return render_template('login-index.html', LoginSignupForm=loginsignupform)

@app.route('/logout')
@cross_origin()
def logout():
    # --- Deauthenticate --- BEGIN ---
    loginsignupform = LoginSignupForm()
    response = make_response(render_template('login-index.html', LoginSignupForm=loginsignupform))
    access_encoded = jwt.encode({'user_id': '' + str(0) + ''}, JSONWebToken_SecretKey, algorithm='HS256')
    response.set_cookie('access_cookie', access_encoded)
    return response
    # --- Deauthenticate --- END ---
# Login System --- END ---

# Decode cookie --- START ---
def decodecookie_authenticate(encodedjwtaccess):
    print('inside decodecookie_authenticate')
    decodedjwt_access_cookie = jwt.decode(encodedjwtaccess, JSONWebToken_SecretKey, algorithms=['HS256'])
    userid = decodedjwt_access_cookie['user_id']
    if type(int(userid)) == int and int(userid) > 0:
        return userid
    else:
        return 0
# Decode cookie --- END ---


# EventTemplate Get, Create, Update Delete --Start--
@app.route('/loadeventtemplate', methods=['POST'])
@cross_origin()
def loadeventtemplate():
    try:
        # --- Authenticate --- BEGIN ---
        if(request.cookies.get('access_cookie')):
            encodedjwt_access_cookie = request.cookies.get('access_cookie')
            decoded_userid = decodecookie_authenticate(encodedjwt_access_cookie)
            if(decoded_userid == 0):
                return jsonify(loginstatus=0)
        else:
            return jsonify(loginstatus=0)
        # --- Authenticate --- END ---
        content = request.json
        weekdayid = content["weekdayid"]
        templateevent = ModelEventTemplate.loadeventtemplate(weekdayid, decoded_userid)
        event_objectiveslist = ModelEventslist.loadOGC(decoded_userid)
        event_categorylist = ModelEventslist.loadCategory(decoded_userid)
        print('success getting eventlist and event_objectiveslist')
    except Exception as e:
        print('error = ' + str(e))
    return  jsonify(templateeventlist=templateevent, event_objectiveslist=event_objectiveslist, event_categorylist=event_categorylist)

@app.route('/inserttemplateevent', methods=['POST'])
@cross_origin()
def inserttemplateevent():
    try:
        # --- Authenticate --- BEGIN ---
        if(request.cookies.get('access_cookie')):
            encodedjwt_access_cookie = request.cookies.get('access_cookie')
            decoded_userid = decodecookie_authenticate(encodedjwt_access_cookie)
            if(decoded_userid == 0):
                return jsonify(loginstatus=0)
        else:
            return jsonify(loginstatus=0)
        # --- Authenticate --- END ---
        content = request.json
        event_description = content["template_event_description"]
        starttime = content["template_starttime"]
        expectfinishtime = content["template_expectfinishtime"]
        objectiveid = content["template_objectiveid"]
        categoryid = content["template_categoryid"]
        weekdayid = content["template_weekdayid"]
        ModelEventTemplate.inserteventtemplate(event_description, starttime, expectfinishtime, objectiveid, categoryid, weekdayid, decoded_userid)
        templateevent = ModelEventTemplate.loadeventtemplate(weekdayid, decoded_userid)
        print('success')
    except Exception as e:
        print('error = ' + str(e))
    return jsonify(templateeventlist=templateevent)

@app.route('/updatetemplateevent', methods=['PUT'])
@cross_origin()
def updatetemplateevent():
    try:
        # --- Authenticate --- BEGIN ---
        if(request.cookies.get('access_cookie')):
            encodedjwt_access_cookie = request.cookies.get('access_cookie')
            decoded_userid = decodecookie_authenticate(encodedjwt_access_cookie)
            if(decoded_userid == 0):
                return jsonify(loginstatus=0)
        else:
            return jsonify(loginstatus=0)
        # --- Authenticate --- END ---
        content = request.json
        templatelistid = content["templatelist_id"]
        event_description = content["template_event_description"]
        starttime = content["template_starttime"]
        expectfinishtime = content["template_expectfinishtime"]
        objectiveid = content["template_objectiveid"]
        categoryid = content["template_categoryid"]
        weekdayid = content["template_weekdayid"]
        ModelEventTemplate.updateeventtemplate(templatelistid, event_description, starttime, expectfinishtime, objectiveid, categoryid)
        templateevent = ModelEventTemplate.loadeventtemplate(weekdayid, decoded_userid)
        print('success')
    except Exception as e:
        print('error = ' + str(e))
    return jsonify(templateeventlist=templateevent)

@app.route('/bulkeventtemplateweekdayid', methods=['PUT'])
@cross_origin()
def bulkeventtemplateweekdayid():
    try:
        # --- Authenticate --- BEGIN ---
        if(request.cookies.get('access_cookie')):
            encodedjwt_access_cookie = request.cookies.get('access_cookie')
            decoded_userid = decodecookie_authenticate(encodedjwt_access_cookie)
            if(decoded_userid == 0):
                return jsonify(loginstatus=0)
        else:
            return jsonify(loginstatus=0)
        # --- Authenticate --- END ---
        content = request.json
        templatelistid_collection = content["templatelistid_collection"]
        weekdayid = content["weekdayid"]
        ModelEventTemplate.updatetemplateweekdayid(templatelistid_collection, weekdayid)
        templateevent = ModelEventTemplate.loadeventtemplate(weekdayid, decoded_userid)
        print('success')
    except Exception as e:
        print('error = ' + str(e))
    return jsonify(templateeventlist=templateevent)

@app.route('/removetemplateevent', methods=['PUT'])
@cross_origin()
def removetemplateevent():
    try:
        # --- Authenticate --- BEGIN ---
        if(request.cookies.get('access_cookie')):
            encodedjwt_access_cookie = request.cookies.get('access_cookie')
            decoded_userid = decodecookie_authenticate(encodedjwt_access_cookie)
            if(decoded_userid == 0):
                return jsonify(loginstatus=0)
        else:
            return jsonify(loginstatus=0)
        # --- Authenticate --- END ---
        content = request.json
        templatelistid = content["templatelist_id"]
        weekdayid = content["template_weekdayid"]
        ModelEventTemplate.removeeventtemplate(templatelistid)
        templateevent = ModelEventTemplate.loadeventtemplate(weekdayid, decoded_userid)
        print('success')
    except Exception as e:
        print('error = ' + str(e))
    return jsonify(templateeventlist=templateevent)
# EventTemplate Get, Create, Update Delete --End--


# BulkInsert - EventTemplate to Events Grid --Start--
@app.route('/bulkinserteventtemplate', methods=['POST'])
@cross_origin()
def bulkinserteventtemplate():
    try:
        # --- Authenticate --- BEGIN ---
        if(request.cookies.get('access_cookie')):
            encodedjwt_access_cookie = request.cookies.get('access_cookie')
            decoded_userid = decodecookie_authenticate(encodedjwt_access_cookie)
            if(decoded_userid == 0):
                return jsonify(loginstatus=0)
        else:
            return jsonify(loginstatus=0)
        # --- Authenticate --- END ---
        content = request.json
        weekdayid = content["weekdayid"]
        assigndate = content["assigndate"]
        user_TimeZone = content["user_TimeZone"]
        fetchdate = date(*map(int, assigndate.split('-')))
        daybegin = datetime.combine(fetchdate, time(00, 00))
        dayend = datetime.combine(fetchdate, time(23, 59))
        ModelEventslist.bulktemplate_inserteventlist(assigndate, user_TimeZone, decoded_userid, weekdayid)
        eventlist = ModelEventslist.loadeventlist(daybegin, dayend, decoded_userid)
        print('success')
    except Exception as e:
        print('error = ' + str(e))
    # return jsonify(success=True)
    return jsonify(eventlist=eventlist)
# BulkInsert - EventTemplate to Events Grid --End--

# Events Get, Create, Update Delete --Start--
@app.route('/geteventlist', methods=['POST'])
@cross_origin()
def geteventlist():
    try:
        # --- Authenticate --- BEGIN ---
        if(request.cookies.get('access_cookie')):
            encodedjwt_access_cookie = request.cookies.get('access_cookie')
            decoded_userid = decodecookie_authenticate(encodedjwt_access_cookie)
            if(decoded_userid == 0):
                return jsonify(loginstatus=0)
        else:
            return jsonify(loginstatus=0)
        # --- Authenticate --- END ---
        content = request.json
        daybegin = content["daybegin"]
        dayend = content["dayend"]
        eventlist = ModelEventslist.loadeventlist(daybegin, dayend, decoded_userid)
        event_objectiveslist = ModelEventslist.loadOGC(decoded_userid)
        event_categorylist = ModelEventslist.loadCategory(decoded_userid)
        print('success getting eventlist and event_objectiveslist')
    except Exception as e:
        print('error = ' + str(e))
    return  jsonify(eventlist=eventlist, event_objectiveslist=event_objectiveslist, event_categorylist=event_categorylist)

@app.route('/inserteventslist', methods=['POST'])
@cross_origin()
def inserteventslist():
    try:
        # --- Authenticate --- BEGIN ---
        if(request.cookies.get('access_cookie')):
            encodedjwt_access_cookie = request.cookies.get('access_cookie')
            decoded_userid = decodecookie_authenticate(encodedjwt_access_cookie)
            if(decoded_userid == 0):
                return jsonify(loginstatus=0)
        else:
            return jsonify(loginstatus=0)
        # --- Authenticate --- END ---
        content = request.json
        event_description = content["event_description"]
        starttime = content["starttime"]
        expectfinishtime = content["expectfinishtime"]
        objectiveid = content["objectiveid"]
        categoryid = content["categoryid"]
        daybegin = content["daybegin"]
        dayend = content["dayend"]
        ModelEventslist.insertevents(event_description, starttime, expectfinishtime, objectiveid, categoryid, decoded_userid)
        eventlist = ModelEventslist.loadeventlist(daybegin, dayend, decoded_userid)
        print('success')
    except:
        print ('error')
    # return jsonify(success=True)
    return jsonify(eventlist)

@app.route('/updateeventslist', methods=['PUT'])
@cross_origin()
def updateeventslist():
    try:
        # --- Authenticate --- BEGIN ---
        if(request.cookies.get('access_cookie')):
            encodedjwt_access_cookie = request.cookies.get('access_cookie')
            decoded_userid = decodecookie_authenticate(encodedjwt_access_cookie)
            if(decoded_userid == 0):
                return jsonify(loginstatus=0)
        else:
            return jsonify(loginstatus=0)
        # --- Authenticate --- END ---
        content = request.json
        eventlist_id = content["eventlist_id"]
        event_description = content["event_description"]
        starttime = content["starttime"]
        expectfinishtime = content["expectfinishtime"]
        eventcompletedstatus = content["eventcompletedstatus"]
        objectiveid = content["objectiveid"]
        categoryid = content["categoryid"]
        daybegin = content["daybegin"]
        dayend = content["dayend"]
        ModelEventslist.updateevents(eventlist_id, event_description, starttime, expectfinishtime, eventcompletedstatus, objectiveid, categoryid)
        eventlist = ModelEventslist.loadeventlist(daybegin, dayend, decoded_userid)
        print('success')
    except:
        print ('error')
    return jsonify(eventlist)

@app.route('/bulkeventcompletedstatus', methods=['PUT'])
@cross_origin()
def bulkeventcompletedstatus():
    try:
        # --- Authenticate --- BEGIN ---
        if(request.cookies.get('access_cookie')):
            encodedjwt_access_cookie = request.cookies.get('access_cookie')
            decoded_userid = decodecookie_authenticate(encodedjwt_access_cookie)
            if(decoded_userid == 0):
                return jsonify(loginstatus=0)
        else:
            return jsonify(loginstatus=0)
        # --- Authenticate --- END ---
        content = request.json
        eventlistid_collection = content["eventlistid_collection"]
        daybegin = content["daybegin"]
        dayend = content["dayend"]
        ModelEventslist.bulkeventcompletedstatus(eventlistid_collection)
        eventlist = ModelEventslist.loadeventlist(daybegin, dayend, decoded_userid)
        print('success')
    except:
        print ('error')
    return jsonify(eventlist)

@app.route('/removeeventslist', methods=['PUT'])
@cross_origin()
def removeeventslist():
    try:
        # --- Authenticate --- BEGIN ---
        if(request.cookies.get('access_cookie')):
            encodedjwt_access_cookie = request.cookies.get('access_cookie')
            decoded_userid = decodecookie_authenticate(encodedjwt_access_cookie)
            if(decoded_userid == 0):
                return jsonify(loginstatus=0)
        else:
            return jsonify(loginstatus=0)
        # --- Authenticate --- END ---
        content = request.json
        eventlist_id = content["eventlist_id"]
        daybegin = content["daybegin"]
        dayend = content["dayend"]
        ModelEventslist.removeevent(eventlist_id)
        eventlist = ModelEventslist.loadeventlist(daybegin, dayend, decoded_userid)
        print('success')
    except:
        print ('error')
    return jsonify(eventlist)
# Events Create, Update Delete --End--


# Feedback Notes CRUD --Start--
@app.route('/getfeedbacknote', methods=['POST'])
@cross_origin()
def getfeedbacknote():
    try:
        # --- Authenticate --- BEGIN ---
        if(request.cookies.get('access_cookie')):
            encodedjwt_access_cookie = request.cookies.get('access_cookie')
            decoded_userid = decodecookie_authenticate(encodedjwt_access_cookie)
            if(decoded_userid == 0):
                return jsonify(loginstatus=0)
        else:
            return jsonify(loginstatus=0)
        # --- Authenticate --- END ---
        content = request.json
        eventlist_id = content["eventlist_id"]
        getfeedbacknote = "success=False"
        getfeedbacknote = ModelFeedback.getfeedbacknote(eventlist_id)
        print('success getting feedbacknote')
    except Exception as e:
        print('error = ' + str(e))
    return jsonify(getfeedbacknote)

@app.route('/loadfeedbackgrid', methods=['POST'])
@cross_origin()
def loadfeedbackgrid():
    try:
        # --- Authenticate --- BEGIN ---
        if(request.cookies.get('access_cookie')):
            encodedjwt_access_cookie = request.cookies.get('access_cookie')
            decoded_userid = decodecookie_authenticate(encodedjwt_access_cookie)
            if(decoded_userid == 0):
                return jsonify(loginstatus=0)
        else:
            return jsonify(loginstatus=0)
        # --- Authenticate --- END ---
        content = request.json
        eventlistid_collection = content["eventlistid_collection"]
        list_eventlistid = eventlistid_collection.strip().split(",")
        feedbackgrid = ModelFeedback.getfeedbackgrid(list_eventlistid)
        print('success getting feedbackgrid')
    except Exception as e:
        print('error = ' + str(e))
    return jsonify(feedbackgrid = feedbackgrid)

@app.route('/insertfeedbacknote', methods=['POST'])
@cross_origin()
def insertfeedbacknote():
    try:
        # --- Authenticate --- BEGIN ---
        if(request.cookies.get('access_cookie')):
            encodedjwt_access_cookie = request.cookies.get('access_cookie')
            decoded_userid = decodecookie_authenticate(encodedjwt_access_cookie)
            if(decoded_userid == 0):
                return jsonify(loginstatus=0)
        else:
            return jsonify(loginstatus=0)
        # --- Authenticate --- END ---
        content = request.json
        eventlistid = content["eventlistid"]
        feedbacknote = content["feedbacknote"]
        ModelFeedback.insertfeedbacknote(eventlistid, feedbacknote)
        print('success')
    except:
        print ('error')
    return jsonify(success=True)

@app.route('/updatefeedbacknote', methods=['POST'])
@cross_origin()
def updatefeedbacknote():
    try:
        # --- Authenticate --- BEGIN ---
        if(request.cookies.get('access_cookie')):
            encodedjwt_access_cookie = request.cookies.get('access_cookie')
            decoded_userid = decodecookie_authenticate(encodedjwt_access_cookie)
            if(decoded_userid == 0):
                return jsonify(loginstatus=0)
        else:
            return jsonify(loginstatus=0)
        # --- Authenticate --- END ---
        content = request.json
        eventlistid = content["eventlistid"]
        feedbacknote = content["feedbacknote"]
        ModelFeedback.updatefeedbacknote(eventlistid, feedbacknote)
        print('success')
    except:
        print ('error')
    return jsonify(success=True)

@app.route('/removefeedbacknote', methods=['POST'])
@cross_origin()
def removefeedbacknote():
    try:
        # --- Authenticate --- BEGIN ---
        if(request.cookies.get('access_cookie')):
            encodedjwt_access_cookie = request.cookies.get('access_cookie')
            decoded_userid = decodecookie_authenticate(encodedjwt_access_cookie)
            if(decoded_userid == 0):
                return jsonify(loginstatus=0)
        else:
            return jsonify(loginstatus=0)
        # --- Authenticate --- END ---
        content = request.json
        eventlistid = content["eventlistid"]
        ModelFeedback.removefeedbacknote(eventlistid)
        print('success')
    except:
        print ('error')
    return jsonify(success=True)
# Feedback Notes CRUD --End--


# Fileupload -- BEGIN --
@app.route('/eventsfileupload', methods=['GET', 'POST'])
@cross_origin()
def eventsfileupload():
    try:
        # --- Authenticate --- BEGIN ---
        if(request.cookies.get('access_cookie')):
            encodedjwt_access_cookie = request.cookies.get('access_cookie')
            decoded_userid = decodecookie_authenticate(encodedjwt_access_cookie)
            if(decoded_userid == 0):
                return jsonify(loginstatus=0)
        else:
            return jsonify(loginstatus=0)
        # --- Authenticate --- END ---
        if request.method == 'POST':
            print('fileupload begin')
            if 'file' not in request.files:
                print('No file part')
                return redirect(request.url)
            file = request.files['file']
            # if user does not select file, browser also
            # submit an empty part without filename
            if file.filename == '' or not allowed_file(file.filename):
                print('No selected file or selected file is not allowed')
                return redirect(request.url)
            if file and allowed_file(file.filename):
                urlparsed = urlparse(request.url)
                urlquery = urlparsed.query
                urlquery_partition = urlquery.rpartition('=')[2]
                if "eventlistid_collection" not in urlquery:
                    print('No eventlistid collection present')
                    return redirect(request.url)

                # Saving in the folder -- BEGIN --
                file_name = secure_filename(file.filename)
                file.save(os.path.join(UPLOAD_FOLDER, file_name))
                # Saving in the folder -- END--

                # Rename the saved file -- BEGIN --
                new_filename = datetime.utcnow().strftime('%Y-%m-%d_hh%H_mm%M_ss%S_ms%f')[:-3]
                shutil.move(os.path.join(UPLOAD_FOLDER, file_name), os.path.join(UPLOAD_FOLDER, new_filename), copy_function=shutil.copy2)
                # Rename the savedfile -- END --


                # creating list of tuples (sequence of sequences). -- BEGIN --
                list_urlquery = urlquery_partition.strip().split(",") # list for "eventlistid"
                lst_filename = [] # list for "filename"
                lst_pathid = [] #list for "pathid"
                lst_tpl_insertdata = [] #combine all list using "zip()" for creating "List of Tuples == Sequence of sequences".

                for i in range(len(list_urlquery)):
                    lst_filename.append(str(new_filename).strip())
                    lst_pathid.append(PATH_ID)

                lst_tpl_insertdata = list(zip(list_urlquery,lst_filename,lst_pathid)) #combine all list using "zip()" for creating "List of Tuples == Sequence of sequences".
                # creating list of tuples (sequence of sequences). -- END --
                ModelEventslist.insertmedia(lst_tpl_insertdata)
                print('success')
    except Exception as e:
        print('error = ' + str(e))
    return json.dumps({'filename':file.filename})

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
# Fileupload -- END --


# Load Eventlist Gallery -- BEGIN --
@app.route('/eventlistgallery', methods=['GET', 'POST'])
@cross_origin()
def eventlistgallery():
    try:
        # --- Authenticate --- BEGIN ---
        if(request.cookies.get('access_cookie')):
            encodedjwt_access_cookie = request.cookies.get('access_cookie')
            decoded_userid = decodecookie_authenticate(encodedjwt_access_cookie)
            if(decoded_userid == 0):
                return jsonify(loginstatus=0)
        else:
            return jsonify(loginstatus=0)
        # --- Authenticate --- END ---
        content = request.json
        eventlistid_collection = content["eventlistid_collection"]
        list_eventlistid = eventlistid_collection.strip().split(",")  # list for "eventlistid"
        geteventlistgallery = ModelEventslist.loadeventlistgallery(PATH_ID, list_eventlistid)
        print('success getting gallery data')
    except Exception as e:
        print('error = ' + str(e))
    return jsonify(geteventlistgallery)
# Load Eventlist Gallery -- END --


#Category CRUD -- BEGIN --
@app.route('/get_grid_categorylist', methods=['GET'])
@cross_origin()
def getgridcategorylist():
    try:
        # --- Authenticate --- BEGIN ---
        if(request.cookies.get('access_cookie')):
            encodedjwt_access_cookie = request.cookies.get('access_cookie')
            decoded_userid = decodecookie_authenticate(encodedjwt_access_cookie)
            if(decoded_userid == 0):
                return jsonify(loginstatus=0)
        else:
            return jsonify(loginstatus=0)
        # --- Authenticate --- END ---
        categorylist = ModelCategorylist.loadcategory(decoded_userid)
        print('success getting category list')
    except Exception as e:
        print('error = ' + str(e))
    return  jsonify(categorylist=categorylist)

@app.route('/insert_grid_category', methods=['POST'])
@cross_origin()
def insertgridcategory():
    try:
        # --- Authenticate --- BEGIN ---
        if(request.cookies.get('access_cookie')):
            encodedjwt_access_cookie = request.cookies.get('access_cookie')
            decoded_userid = decodecookie_authenticate(encodedjwt_access_cookie)
            if(decoded_userid == 0):
                return jsonify(loginstatus=0)
        else:
            return jsonify(loginstatus=0)
        # --- Authenticate --- END ---
        content = request.json
        category_name = content["category_name"]
        ModelCategorylist.insertcategory(category_name, decoded_userid)
        categorylist = ModelCategorylist.loadcategory(decoded_userid)
        print('success')
    except:
        print ('error')
    return jsonify(categorylist)

@app.route('/update_grid_category', methods=['PUT'])
@cross_origin()
def updategridcategory():
    try:
        # --- Authenticate --- BEGIN ---
        if(request.cookies.get('access_cookie')):
            encodedjwt_access_cookie = request.cookies.get('access_cookie')
            decoded_userid = decodecookie_authenticate(encodedjwt_access_cookie)
            if(decoded_userid == 0):
                return jsonify(loginstatus=0)
        else:
            return jsonify(loginstatus=0)
        # --- Authenticate --- END ---
        content = request.json
        category_id = content["category_id"]
        category_name = content["category_name"]
        ModelCategorylist.updatecategory(category_id, category_name)
        categorylist = ModelCategorylist.loadcategory(decoded_userid)
        print('success')
    except:
        print ('error')
    return jsonify(categorylist)

@app.route('/remove_grid_category', methods=['PUT'])
@cross_origin()
def removegridcategory():
    try:
        # --- Authenticate --- BEGIN ---
        if(request.cookies.get('access_cookie')):
            encodedjwt_access_cookie = request.cookies.get('access_cookie')
            decoded_userid = decodecookie_authenticate(encodedjwt_access_cookie)
            if(decoded_userid == 0):
                return jsonify(loginstatus=0)
        else:
            return jsonify(loginstatus=0)
        # --- Authenticate --- END ---
        content = request.json
        category_id = content["category_id"]
        ModelCategorylist.removecategory(category_id)
        categorylist = ModelCategorylist.loadcategory(decoded_userid)
        print('success')
    except:
        print ('error')
    return jsonify(categorylist)
#Category CRUD --End--

# Goals CRUD -- BEGIN --
@app.route('/getgoalcategorylist', methods=['GET'])
@cross_origin()
def getgoalcategorylist():
    try:
        # --- Authenticate --- BEGIN ---
        if(request.cookies.get('access_cookie')):
            encodedjwt_access_cookie = request.cookies.get('access_cookie')
            decoded_userid = decodecookie_authenticate(encodedjwt_access_cookie)
            if(decoded_userid == 0):
                return jsonify(loginstatus=0)
        else:
            return jsonify(loginstatus=0)
        # --- Authenticate --- END ---
        goallist = ModelGoallist.loadgoal(decoded_userid)
        categorylist = ModelGoallist.loadgoalcategory(decoded_userid)
        print('success getting goal and category list')
    except Exception as e:
        print('error = ' + str(e))
    return  jsonify(goallist=goallist, categorylist=categorylist)
@app.route('/insertgoal', methods=['POST'])
@cross_origin()
def insertgoal():
    try:
        # --- Authenticate --- BEGIN ---
        if(request.cookies.get('access_cookie')):
            encodedjwt_access_cookie = request.cookies.get('access_cookie')
            decoded_userid = decodecookie_authenticate(encodedjwt_access_cookie)
            if(decoded_userid == 0):
                return jsonify(loginstatus=0)
        else:
            return jsonify(loginstatus=0)
        # --- Authenticate --- END ---
        content = request.json
        goal_name = content["goal_name"]
        goal_description = content["goal_description"]
        categoryid = content["categoryid"]
        ModelGoallist.insertgoal(goal_name, goal_description, categoryid, decoded_userid)
        goallist = ModelGoallist.loadgoal(decoded_userid)
        print('success')
    except:
        print ('error')
    return jsonify(goallist)

@app.route('/updategoal', methods=['PUT'])
@cross_origin()
def updategoal():
    try:
        # --- Authenticate --- BEGIN ---
        if(request.cookies.get('access_cookie')):
            encodedjwt_access_cookie = request.cookies.get('access_cookie')
            decoded_userid = decodecookie_authenticate(encodedjwt_access_cookie)
            if(decoded_userid == 0):
                return jsonify(loginstatus=0)
        else:
            return jsonify(loginstatus=0)
        # --- Authenticate --- END ---
        content = request.json
        goal_id = content["goal_id"]
        goal_name = content["goal_name"]
        goal_description = content["goal_description"]
        categoryid = content["categoryid"]
        goalcompletedstatus = content["goalcompletedstatus"]
        ModelGoallist.updategoal(goal_id, goal_name, goal_description, categoryid, goalcompletedstatus)
        goallist = ModelGoallist.loadgoal(decoded_userid)
        print('success')
    except:
        print ('error')
    return jsonify(goallist)

@app.route('/bulkgoalcompletedstatus', methods=['POST'])
@cross_origin()
def bulkgoalcompletedstatus():
    try:
        # --- Authenticate --- BEGIN ---
        if(request.cookies.get('access_cookie')):
            encodedjwt_access_cookie = request.cookies.get('access_cookie')
            decoded_userid = decodecookie_authenticate(encodedjwt_access_cookie)
            if(decoded_userid == 0):
                return jsonify(loginstatus=0)
        else:
            return jsonify(loginstatus=0)
        # --- Authenticate --- END ---
        content = request.json
        goalid_collection = content["goalid_collection"]
        ModelGoallist.bulkgoalcompletedstatus(goalid_collection)
        goallist = ModelGoallist.loadgoal(decoded_userid)
        print('success')
    except:
        print ('error')
    return jsonify(goallist)

@app.route('/removegoal', methods=['PUT'])
@cross_origin()
def removegoal():
    try:
        # --- Authenticate --- BEGIN ---
        if(request.cookies.get('access_cookie')):
            encodedjwt_access_cookie = request.cookies.get('access_cookie')
            decoded_userid = decodecookie_authenticate(encodedjwt_access_cookie)
            if(decoded_userid == 0):
                return jsonify(loginstatus=0)
        else:
            return jsonify(loginstatus=0)
        # --- Authenticate --- END ---
        content = request.json
        goal_id = content["goal_id"]
        ModelGoallist.removegoal(goal_id)
        goallist = ModelGoallist.loadgoal(decoded_userid)
        print('success')
    except:
        print ('error')
    return jsonify(goallist)
# Goals CRUD --End--


# Load Objective -- BEGIN --
@app.route('/getobjectiveslist', methods=['POST'])
@cross_origin()
def getobjectiveslist():
    try:
        # --- Authenticate --- BEGIN ---
        if(request.cookies.get('access_cookie')):
            encodedjwt_access_cookie = request.cookies.get('access_cookie')
            decoded_userid = decodecookie_authenticate(encodedjwt_access_cookie)
            if(decoded_userid == 0):
                return jsonify(loginstatus=0)
        else:
            return jsonify(loginstatus=0)
        # --- Authenticate --- END ---
        content = request.json
        goal_id = content["goal_id"]
        getobjectiveslist = "success=False"
        getobjectiveslist = ModelObjectivelist.loadobjective(goal_id)
        print('success getting objectiveslist')
    except Exception as e:
        print('error = ' + str(e))
    return jsonify(getobjectiveslist)
# Load Objective -- END --
# Objective CRUD -- BEGIN --
@app.route('/insertobjective', methods=['POST'])
@cross_origin()
def insertobjective():
    try:
        # --- Authenticate --- BEGIN ---
        if(request.cookies.get('access_cookie')):
            encodedjwt_access_cookie = request.cookies.get('access_cookie')
            decoded_userid = decodecookie_authenticate(encodedjwt_access_cookie)
            if(decoded_userid == 0):
                return jsonify(loginstatus=0)
        else:
            return jsonify(loginstatus=0)
        # --- Authenticate --- END ---
        content = request.json
        objective_name = content["objective_name"]
        objective_description = content["objective_description"]
        goalid = content["goalid"]
        categoryid = content["categoryid"]
        ModelObjectivelist.insertobjective(objective_name, objective_description, goalid, categoryid)
        getobjectiveslist = ModelObjectivelist.loadobjective(goalid)
        print('success')
    except:
        print ('error')
    return jsonify(getobjectiveslist)

@app.route('/updateobjective', methods=['PUT'])
@cross_origin()
def updateobjective():
    try:
        # --- Authenticate --- BEGIN ---
        if(request.cookies.get('access_cookie')):
            encodedjwt_access_cookie = request.cookies.get('access_cookie')
            decoded_userid = decodecookie_authenticate(encodedjwt_access_cookie)
            if(decoded_userid == 0):
                return jsonify(loginstatus=0)
        else:
            return jsonify(loginstatus=0)
        # --- Authenticate --- END ---
        content = request.json
        objective_id = content["objective_id"]
        objective_name = content["objective_name"]
        objective_description = content["objective_description"]
        objectivecompletedstatus = content["objectivecompletedstatus"]
        goalid = content["goalid"]
        ModelObjectivelist.updateobjective(objective_id, objective_name, objective_description, objectivecompletedstatus)
        getobjectiveslist = ModelObjectivelist.loadobjective(goalid)
        print('success')
    except:
        print ('error')
    return jsonify(getobjectiveslist)

@app.route('/removeobjective', methods=['PUT'])
@cross_origin()
def removeobjective():
    try:
        # --- Authenticate --- BEGIN ---
        if(request.cookies.get('access_cookie')):
            encodedjwt_access_cookie = request.cookies.get('access_cookie')
            decoded_userid = decodecookie_authenticate(encodedjwt_access_cookie)
            if(decoded_userid == 0):
                return jsonify(loginstatus=0)
        else:
            return jsonify(loginstatus=0)
        # --- Authenticate --- END ---
        content = request.json
        objective_id = content["objective_id"]
        goalid = content["goalid"]
        ModelObjectivelist.removeobjective(objective_id)
        getobjectiveslist = ModelObjectivelist.loadobjective(goalid)
        print('success')
    except:
        print ('error')
    return jsonify(getobjectiveslist)
# Objective CRUD --End--

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8001, debug=True)