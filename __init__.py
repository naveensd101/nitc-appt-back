import psycopg2
from psycopg2.extensions import AsIs
import urllib.parse as up

from flask_mail import Mail, Message

from flask import Flask,request
from flask import jsonify
from flask_cors import CORS

import os
from os.path import join
from dotenv import load_dotenv

import hashlib

dotenv_path = join(os.path.dirname(os.path.realpath(__file__)), '.env')
load_dotenv(dotenv_path)

DATABASE_URL = os.environ.get("DATABASE_URL")
up.uses_netloc.append("postgres")
url = up.urlparse(DATABASE_URL)
dbconn = psycopg2.connect(
    database=url.path[1:],
    user=url.username,
    password=url.password,
    host=url.hostname,
    port=url.port
)
app= Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


app.config.from_mapping(
    DATABASE= "NITC-ApptMgmt"
)

#########################################################################################################################

""" cursor = dbconn.cursor()
cursor.execute("SELECT * from Appointments")
print(cursor.fetchall())
dbconn.commit() """

mail = Mail(app)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'nitc.email.bot@gmail.com'
app.config['MAIL_PASSWORD'] = 'EMBySGxAcR9xsgV'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)


@app.route("/")
def index():
    msg = Message('Hello from falsk', sender = 'nitc.email.bot@gmail.com', recipients = ['naveen_b190707cs@nitc.ac.in'])
    msg.body = "Hello Flask message sent from Flask-Mail"
    mail.send(msg)
    response = jsonify(message="The server is running and mail is send")
    return response

#########################################################################################################################
#Signs all kinds of users in
@app.route("/signin",methods=["POST"])
def signinpage():
    cursor = dbconn.cursor()
    """ {
    "u_id":"B190SDtestCS",
    "pwd":"SDtestPass",
    "type":"student"
    } """
    uids= request.json['u_id']
    password= request.json['pwd']
    typess= request.json['type']

    #password encryption:
    if typess!='admin':
        password=hashlib.sha256(password.encode('utf-8')).hexdigest() #hashvalue

    cursor.execute("SELECT pwd from Users where u_id=%s",(uids,))
    x=cursor.fetchone()
    if x is None:
        return jsonify(message="Complete the registration")

    temp= x[0]
    dbconn.commit()


    if temp:
        passcode=temp
        if passcode==password:
            if typess=='student':
                cursor = dbconn.cursor()
                cursor.execute("SELECT deptid from Student where roll_no=%s",(uids,))
                deptids= cursor.fetchone()[0]
                dbconn.commit()

                cursor = dbconn.cursor()
                cursor.execute("SELECT dname from Departments where department_id=%s",(deptids,))
                depts= cursor.fetchone()[0]
                dbconn.commit()

                cursor = dbconn.cursor()
                cursor.execute("SELECT * from Users where u_id=%s",(uids,))
                dbconn.commit()
                tempone= cursor.fetchone()
                uids,names,emails,password,mobilenos=tempone

                return jsonify({"u_id":uids,"uname":names,"email":emails,"pwd":password,"mobileno":mobilenos,"deptid":deptids,"dname":depts})

            elif typess=='faculty':
                cursor = dbconn.cursor()
                cursor.execute("SELECT deptid from Faculty where ssn=%s",(uids,))
                deptids= cursor.fetchone()[0]
                dbconn.commit()

                cursor = dbconn.cursor()
                cursor.execute("SELECT dname from Departments where department_id=%s",(deptids,))
                depts= cursor.fetchone()[0]
                dbconn.commit()

                cursor = dbconn.cursor()
                cursor.execute("SELECT * from Users where u_id=%s",(uids,))
                dbconn.commit()
                tempone= cursor.fetchone()
                uids,names,emails,password,mobilenos=tempone

                return jsonify({"u_id":uids,"uname":names,"email":emails,"pwd":password,"mobileno":mobilenos,"deptid":deptids,"dname":depts})

            elif typess=='admin':
                cursor = dbconn.cursor()
                cursor.execute("SELECT * from Users where u_id=%s",(uids,))
                dbconn.commit()
                tempone= cursor.fetchone()
                uids,names,emails,password,mobilenos=tempone

                return jsonify({"u_id":uids,"uname":names,"email":emails,"pwd":password,"mobileno":mobilenos})
        else:
                return jsonify(message="Incorrect Password")

#########################################################################################################################

@app.route("/signup",methods=["POST"])
#@app.route("/signup")
def registration():

    cursor = dbconn.cursor()
    uids= request.json['u_id']
    names= request.json['uname'] #name
    emails= request.json['email']
    password= request.json['pwd']
    mobilenos= request.json['mobileno']
    depts= request.json['dname']
    typess= request.json['type']

    #uids= '1234567'
    #names= 'SDtestName'
    #emails= 'SDtestName@gmail.com'
    #password= 'SDtestPass'
    #mobilenos= '1239991111'
    #depts= 'CSE'
    #typess= 'student'

    #password encryption:
    password=hashlib.sha256(password.encode('utf-8')).hexdigest() #hashvalue

    #insert data into user db
    cursor.execute("INSERT INTO Users (u_id, uname, email, pwd, mobileno) VALUES(%s, %s, %s, %s, %s)",(uids, names, emails, password, mobilenos))
    dbconn.commit()

    #getting dept id from department db
    cursor = dbconn.cursor()
    cursor.execute("SELECT department_id from Departments where dname=%s",(depts,))
    deptids= cursor.fetchone()[0]
    dbconn.commit()

    if typess=='student':
        cursor = dbconn.cursor()
        cursor.execute("INSERT INTO Student (roll_no, deptid) VALUES(%s, %s)",(uids, deptids))
        dbconn.commit()

        return jsonify({"u_id":uids,"uname":names,"email":emails,"pwd":password,"mobileno":mobilenos,"deptid":deptids,"dname":depts})

    elif typess=='faculty':
        cursor = dbconn.cursor()
        cursor.execute("INSERT INTO Faculty (ssn, deptid) VALUES(%s, %s)",(uids, deptids))
        dbconn.commit()

        return jsonify({"u_id":uids,"uname":names,"email":emails,"pwd":password,"mobileno":mobilenos,"deptid":deptids,"dname":depts})

#########################################################################################################################
#Gets the id and username of all the faculties
@app.route("/list_all_fac",methods=["POST"])
#@app.route("/list_all_fac")
def listAllFacPage():
    cursor = dbconn.cursor()
    list_of_uname=[]
    cursor = dbconn.cursor()
    cursor.execute("SELECT u.u_id,u.uname FROM Users u, Faculty f WHERE u.u_id=f.ssn")
    list_of_uname=cursor.fetchall()
    response=list(map(lambda x: {"u_id":x[0],"uname":x[1]},list_of_uname))
    dbconn.commit()

    return jsonify(response)

@app.route("/list_all_departments",methods=["POST"])
#@app.route("/list_all_fac")
def listAllDeptPage():
    cursor = dbconn.cursor()
    list_of_uname=[]
    cursor = dbconn.cursor()
    cursor.execute("SELECT department_id,dname from Departments")
    list_of_dname=cursor.fetchall()
    response=list(map(lambda x: {"dept_id":x[0],"dname":x[1]},list_of_dname))
    dbconn.commit()

    return jsonify(response)

#########################################################################################################################
#Gets details of a specific user
@app.route("/details",methods=["POST"])
#@app.route("/details")
def details():
    cursor = dbconn.cursor()
    uid= request.json['u_id']
    cursor.execute("SELECT * from Users where u_id=%s",(uid,))
    details=cursor.fetchone()
    dbconn.commit()
    if details:
        u_id,names,emails,password,mobilenos=details
        return jsonify({"u_id":u_id,"uname":names,"email":emails,"pwd":password,"mobileno":mobilenos})
    else:
        return jsonify(message="Invalid ID")

#########################################################################################################################
#insert into the appointment table
@app.route("/request_stud",methods=["POST"])
#@app.route("/request_stud")
def request_stud():
    cursor = dbconn.cursor()

    #date_created = "2020-12-03"
    #date_appointment = "2020-12-31"
    #time_appointment = "10:00:00"
    #title = "email test"
    #description = "email test des"
    #stud_id = "B190CS"
    #fac_id = "666"

    date_created= request.json['date_created']
    date_appointment= request.json['date_appointment']
    time_appointment= request.json['time_appointment']
    title= request.json['title']
    description= request.json['description']
    stud_id= request.json['stud_id']
    fac_id= request.json['fac_id']
    dateTime = date_appointment + "#" + time_appointment


    # we are concatinating the date and time to get the datetime
    # because our database only has one column for datetime

    #status will be 1 for pending
    try:
        cursor.execute("INSERT INTO Appointments (status, date_created, date_scheduled, title, decription, stu_id, fac_id) VALUES(%s, %s, %s, %s, %s, %s, %s)",("1", date_created, dateTime, title, description, stud_id, fac_id))
        dbconn.commit()

    except:
        return jsonify(message="Invalid appointment request")

    #sending email to the faculty
    cursor.execute("SELECT email from Users where u_id=%s",(fac_id,))
    email=cursor.fetchone()[0]
    dbconn.commit()

    cursor.execute("SELECT uname from Users where u_id=%s",(stud_id,))
    stud_name=cursor.fetchone()[0]
    dbconn.commit()

    msg = Message(f'{stud_name} : {title}', sender = 'nitc.email.bot@gmail.com', recipients = [f'{email}'])
    msg.body = f'{stud_name} has requested an appointment with you.\n\nTitle: {title}\nDescription: {description}\nDate: {date_appointment}\nTime: {time_appointment}\n\nPlease login to the portal to accept or reject the request.'
    mail.send(msg)


    return jsonify(message="Appointment Requested")

#########################################################################################################################
#Gets details of an appointment
@app.route("/get_appt",methods=["POST"])
def get_appt():
    cursor=dbconn.cursor()
    appt_id=request.json["appt_id"]
    #appt_id='20'
    valid=-1
    cursor.execute("SELECT * FROM Appointments where appointment_id=%s",(appt_id,))
    valid=cursor.fetchone()
    dbconn.commit()
    appointment_id,status,date_created,dateTime,title,decription,stu_id,fac_id,suggested_date,faculty_message = valid
    cursor.execute("SELECT uname FROM Users WHERE u_id=%s",(fac_id,))
    fac_name=cursor.fetchone()[0]
    dbconn.commit()
    cursor.execute("SELECT uname FROM Users WHERE u_id=%s",(stu_id,))
    stu_name=cursor.fetchone()[0]
    dbconn.commit()
    date_scheduled,time_scheduled = dateTime.split("#")
    if valid:
        return jsonify({"appointment_id":appointment_id,"status":status,"date_created":date_created,"date_scheduled":date_scheduled,"time_scheduled":time_scheduled,"title":title,"decription":decription,"suggested_date":suggested_date,"faculty_message":faculty_message,"stu_name":stu_name,"fac_name":fac_name})
    else:
        return jsonify(message="Error: appointment doesn't exist")

#########################################################################################################################
#Deletes an appointment
@app.route("/delete_appt",methods=["DELETE"])
#@app.route("/delete_appt")

def delete_appt():
    cursor=dbconn.cursor()
    appt_id=request.json["appt_id"]
    #appt_id='20'
    valid=-1
    cursor.execute("SELECT * FROM Appointments where appointment_id=%s",(appt_id,))
    valid=cursor.fetchone();
    dbconn.commit()
    if valid:
        cursor.execute("DELETE from Appointments where appointment_id=%s",(appt_id,))
        dbconn.commit()
        return jsonify(message="deleted")
    else:
        return jsonify(message="Error: appointment doesn't exist")

#########################################################################################################################
#Rejects an appointment
@app.route("/reject_stud",methods=["POST"])
def reject_stud():
    cursor=dbconn.cursor()
    appt_id=request.json["appt_id"]
    #appt_id='19'
    dbconn.commit()
    cursor.execute("UPDATE Appointments SET status='2' where appointment_id=%s",(appt_id,))
    dbconn.commit()
    return jsonify({"appt_id":appt_id,"status":2})

#########################################################################################################################
#Approves an appointment
@app.route("/approval_stud",methods=["POST"])
def approval_stud():
    cursor=dbconn.cursor()
    appt_id=request.json["appt_id"]
    # appt_id='19'
    cursor.execute("SELECT status FROM Appointments WHERE appointment_id=%s;",(appt_id,))
    status=cursor.fetchone()[0]
    dbconn.commit()
    if (status=="4"):
        cursor.execute("UPDATE Appointments SET status='3', date_scheduled=suggested_date, suggested_date=-1,faculty_message=NULL WHERE appointment_id=%s;",(appt_id,))
        dbconn.commit()
    else:
        cursor.execute("UPDATE Appointments SET status='3' WHERE appointment_id=%s ;",(appt_id,))
        dbconn.commit()
    return jsonify({"appt_id":appt_id,"status":3})

#Sends all appointments of student
@app.route("/view_all_student",methods=["POST"])
#@app.route("/view_all")
def view_all_student():
    # takes in the admin id
    u_id= request.json['u_id']
    cursor=dbconn.cursor()
    cursor.execute("SELECT * from Appointments where stu_id=%s ORDER by date_scheduled",(u_id,))
    list_of_apt=cursor.fetchall()
    dbconn.commit()
    if not list_of_apt:
        return jsonify(message2="There are no appointments")

    list_of_apt_details=[]
    for i in list_of_apt:
        aptId, status, date_created, dateTime, title, description, stu_id, fac_id, suggested_date, faculty_message = i
        cursor.execute("SELECT uname FROM Users WHERE u_id=%s",(fac_id,))
        fac_name=cursor.fetchone()
        dbconn.commit()
        cursor.execute("SELECT uname FROM Users WHERE u_id=%s",(stu_id,))
        stu_name=cursor.fetchone()
        dbconn.commit()
        date_scheduled = dateTime.split("#")[0]
        time_scheduled = dateTime.split("#")[1]
        list_of_apt_details.append({"aptId": aptId, "status": status, "date_created": date_created, "date_scheduled": date_scheduled, "time_scheduled": time_scheduled, "title": title, "description": description, "stu_id": stu_id, "stu_name":stu_name,"fac_id": fac_id, "fac_name": fac_name, "suggested_date": suggested_date, "faculty_message": faculty_message})
    return jsonify(list_of_apt_details)


########################################  FACULTY STUFF  #########################################
#Sends all appointments of faculty
@app.route("/view_all_faculty",methods=["POST"])
#@app.route("/view_all")
def view_all_faculty():
    # takes in the faculty id
    u_id= request.json['u_id']
    cursor=dbconn.cursor()
    cursor.execute("SELECT * from Appointments where fac_id=%s ORDER by date_scheduled",(u_id,))
    list_of_apt=cursor.fetchall()
    dbconn.commit()
    if not list_of_apt:
        return jsonify(message2="There are no appointments")

    list_of_apt_details=[]
    for i in list_of_apt:
        aptId, status, date_created, dateTime, title, description, stu_id, fac_id, suggested_date, faculty_message = i
        cursor.execute("SELECT uname FROM Users WHERE u_id=%s",(fac_id,))
        fac_name=cursor.fetchone()
        dbconn.commit()
        cursor.execute("SELECT uname FROM Users WHERE u_id=%s",(stu_id,))
        stu_name=cursor.fetchone()
        dbconn.commit()
        date_scheduled = dateTime.split("#")[0]
        time_scheduled = dateTime.split("#")[1]
        list_of_apt_details.append({"aptId": aptId, "status": status, "date_created": date_created, "date_scheduled": date_scheduled, "time_scheduled": time_scheduled, "title": title, "description": description, "stu_id": stu_id, "stu_name":stu_name,"fac_id": fac_id, "fac_name": fac_name, "suggested_date": suggested_date, "faculty_message": faculty_message})
    return jsonify(list_of_apt_details)

#########################################################################################################################
#api to reschedule an appointment
#@app.route("/reschedule")
@app.route("/reschedule", methods=["POST"])
def reschedule():

    cursor = dbconn.cursor()

    fac_id= request.json['u_id']
    apt_id= request.json['apt_id']
    fac_msg=request.json['fac_msg']
    suggested_date=request.json['suggested_date']
    suggested_time=request.json['suggested_time']

    #fac_id= '123'
    #apt_id= '12'
    #fac_msg='busy'
    #suggested_date='2020-12-07'
    #suggested_time='17:00:00'

    status='4' #default value

    suggested_datetime=suggested_date+"#"+suggested_time
    cursor.execute("UPDATE Appointments SET suggested_date=%s,faculty_message=%s,status=%s where fac_id=%s and appointment_id=%s",(suggested_datetime,fac_msg,status,fac_id,apt_id))
    dbconn.commit()
    cursor.execute("SELECT * from Appointments where fac_id=%s and appointment_id=%s",(fac_id,apt_id))
    resc_apt=cursor.fetchone()
    dbconn.commit()
    if not resc_apt:
        return jsonify(message="There are no appointments")
    else:
        aptId, status, date_created, dateTime, title, description, stu_id, fac_id, suggested_date, faculty_message = resc_apt
        date_scheduled = dateTime.split("#")[0]
        time_scheduled = dateTime.split("#")[1]
        resc_apt={"aptId": aptId, "status": status, "date_created": date_created, "date_scheduled": date_scheduled, "time_scheduled": time_scheduled, "title": title, "description": description, "stu_id": stu_id, "fac_id": fac_id, "suggested_date": suggested_date, "faculty_message": faculty_message}
    return jsonify(resc_apt)

##################################################################################################

#api to accept the appointment
@app.route("/accept",methods=["POST"])
def accept():
    # takes in the appointment id
    apt_id= request.json['apt_id']
    #apt_id="2233asdfasd3"
    try:
        cursor = dbconn.cursor()
        cursor.execute("SELECT * from Appointments where appointment_id=%s",(apt_id,))
        apt_details=cursor.fetchone()
    except:
        return jsonify(message="Invalid apt_id")
    if apt_details is None:
        return jsonify(message="No appointment with this id")
    appointment_id, status, date_created, dateTime, title, description, stu_id, fac_id, suggested_date, faculty_message = apt_details
    date_scheduled = dateTime.split("#")[0]
    time_scheduled = dateTime.split("#")[1]

    #UPdate the status to 3 for accepted if the current status is 1
    if status == "1":
        cursor = dbconn.cursor()
        cursor.execute("UPDATE Appointments SET status=%s WHERE appointment_id=%s",("3",apt_id))
        dbconn.commit()
        return jsonify(
                {
                    "message":"Appointment Accepted",
                },
                {
                    appointment_id: {
                    "status": "3",
                    "date_created": date_created,
                    "date_scheduled": date_scheduled,
                    "time_scheduled": time_scheduled,
                    "title": title,
                    "description": description,
                    "stu_id": stu_id,
                    "fac_id": fac_id,
                    "suggested_date": suggested_date,
                    "faculty_message": faculty_message
                    }
                }
                )
    elif status == "3":
        return jsonify(message="Appointment already accepted")
    elif status == "2":
        return jsonify(message="Appointment already rejected")
    else:
        return jsonify(message="Appointment waiting for student aproval")
    return jsonify(message="this will never be seen Appointment Accepted")


##################################################################################################

@app.route("/apt_by_month",methods=["POST"])
def apt_by_month():
    def getmonthlength(monthnum,yearnum):
        if monthnum in [1,3,5,7,10,12]:
            return 31
        elif monthnum in [4,6,8,9,11]:
            return 30
        else:
            if((yearnum % 400 == 0) or (yearnum % 100 != 0) and (yearnum % 4 == 0)):
                return 29
            else:
                return 28
    cursor=dbconn.cursor()
    """ {
    "fac_id":"123",
    "month":"12",
    "year" : "2020"
    } """
    fac_id=request.json["fac_id"]
    month=request.json["month"]
    year=request.json["year"]
    perc='%'
    cursor.execute("SELECT * FROM Appointments WHERE fac_id=%s AND status='3' AND date_scheduled LIKE '%s-%s-%s' ORDER BY date_scheduled",(fac_id,AsIs(year),AsIs(month),AsIs(perc)))
    all_appts_of_month=cursor.fetchall()
    dbconn.commit()
    weekarr=[]
    montharr=[]
    dayarr=[]
    weekcount=0
    index=0
    length= getmonthlength(int(month),int(year));
    for daycount in range(length):
        if daycount%7==0 and daycount!=0:
            montharr.append(weekarr)
            weekarr=[]
            weekcount+=1

        while index<len(all_appts_of_month) and int(daycount+1)==int(all_appts_of_month[index][3][8:10]):
            appointment_id,status,date_created,dateTime,title,decription,stu_id,fac_id,suggested_date,faculty_message = all_appts_of_month[index]
            cursor.execute("SELECT uname FROM Users WHERE u_id=%s",(stu_id,))
            stu_name=cursor.fetchone()[0]
            dbconn.commit()
            date_scheduled,time_scheduled = dateTime.split("#") 
            dayarr.append({"appointment_id":appointment_id,"status":status,"date_created":date_created,"date_scheduled":date_scheduled,"time_scheduled":time_scheduled,"title":title,"decription":decription,"suggested_date":suggested_date,"faculty_message":faculty_message,"stu_name":stu_name})
            index+=1

        weekarr.append(dayarr)
        dayarr=[]
    print(montharr)
    #print(all_appts_of_month)
    return jsonify(montharr)

##################################################################################################

#api to send all appointments of the faculty for the day

@app.route("/apt_by_day",methods=["POST"])
#@app.route("/apt_by_day")
def apt_by_day():

    fac_id= request.json['u_id']
    day=request.json['date']

    #fac_id='123'
    #day='2020-12-01'
    perc='%'
    cursor = dbconn.cursor()
    cursor.execute("SELECT * from Appointments where fac_id=%s and date_scheduled LIKE '%s%s' ORDER BY date_scheduled",(fac_id,AsIs(day),AsIs(perc)))

    list_of_apt=cursor.fetchall()
    dbconn.commit()
    if not list_of_apt:
        return jsonify(message="There are no appointments")

    list_of_apt_details=[]
    for i in list_of_apt:
        aptId, status, date_created, dateTime, title, description, stu_id, fac_id, suggested_date, faculty_message = i
        date_scheduled = dateTime.split("#")[0]
        time_scheduled = dateTime.split("#")[1]
        cursor.execute("SELECT uname FROM Users WHERE u_id=%s",(stu_id,))
        stu_name=cursor.fetchone()
        dbconn.commit()
        list_of_apt_details.append({"aptId": aptId, "status": status, "date_created": date_created, "date_scheduled": date_scheduled, "time_scheduled": time_scheduled, "title": title, "description": description, "stu_id": stu_id, "fac_id": fac_id,"stu_name": stu_name, "suggested_date": suggested_date, "faculty_message": faculty_message})
    return jsonify(list_of_apt_details)

        #api to send all appointments of the faculty for the month

########################################  ADMIN STUFF  #########################################
@app.route("/view_all",methods=["POST"])
#@app.route("/view_all")
def view_all():
    # takes in the admin id
    u_id= request.json['u_id']


    cursor = dbconn.cursor()
    cursor.execute("SELECT * from Admin WHERE admin_id=%s",(u_id,))
    admins=cursor.fetchone();
    dbconn.commit()
    if not admins:
        return jsonify(message1="Not an admin")

    cursor.execute("SELECT * from Appointments ORDER by date_scheduled")
    list_of_apt=cursor.fetchall()
    dbconn.commit()
    if not list_of_apt:
        return jsonify(message2="There are no appointments")

    list_of_apt_details=[]
    for i in list_of_apt:
        aptId, status, date_created, dateTime, title, description, stu_id, fac_id, suggested_date, faculty_message = i
        cursor.execute("SELECT uname FROM Users WHERE u_id=%s",(fac_id,))
        fac_name=cursor.fetchone()
        dbconn.commit()
        cursor.execute("SELECT uname FROM Users WHERE u_id=%s",(stu_id,))
        stu_name=cursor.fetchone()
        dbconn.commit()
        date_scheduled = dateTime.split("#")[0]
        time_scheduled = dateTime.split("#")[1]
        list_of_apt_details.append({"aptId": aptId, "status": status, "date_created": date_created, "date_scheduled": date_scheduled, "time_scheduled": time_scheduled, "title": title, "description": description, "stu_id": stu_id, "stu_name":stu_name,"fac_id": fac_id, "fac_name": fac_name, "suggested_date": suggested_date, "faculty_message": faculty_message})
    return jsonify(list_of_apt_details)

##################################################################################################

#delete the user account
@app.route("/delete_acc",methods=["DELETE"])
#@app.route("/delete_acc")
def delete_acc():
     cursor=dbconn.cursor()
     uids=request.json["uid"]
     #uids='1234567'
     cursor.execute("SELECT COUNT(*) FROM Student where roll_no=%s",(uids,))
     valid=cursor.fetchone()[0];
     dbconn.commit()

     if valid:
        cursor=dbconn.cursor()
        cursor.execute("DELETE from Appointments where stu_id=%s",(uids,))
        cursor.execute("DELETE from Student where roll_no=%s",(uids,))
        cursor.execute("DELETE from Users where u_id=%s",(uids,))
        dbconn.commit()
        return jsonify(message="Deleted Student")

     else:
        cursor=dbconn.cursor()
        cursor.execute("DELETE from Appointments where fac_id=%s",(uids,))
        cursor.execute("DELETE from Faculty where ssn=%s",(uids,))
        cursor.execute("DELETE from Users where u_id=%s",(uids,))
        dbconn.commit()
        return jsonify(message="Deleted Faculty")


if __name__ == '__main__':
    app.run()
