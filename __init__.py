import psycopg2
import urllib.parse as up

from flask import Flask,request
from flask import jsonify
from flask_cors import CORS,cross_origin
from datetime import date
from datetime import datetime

import os
from os.path import join, dirname
from dotenv import load_dotenv


import math
import requests
import random
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



def create_app():
#create_app is a keyword.
    app= Flask(__name__)
    #CORS(app)
    app.config.from_mapping(
        DATABASE= "NITC-ApptMgmt"
    )

#########################################################################################################################

    @app.route("/")
    def index():
        response = jsonify(message="The server is running")
        return response

#########################################################################################################################
    
    #@app.route("/signin",methods=["POST"])
    @app.route("/signin")
    def signinpage():
        cursor = dbconn.cursor()
        #uids= request.json['u_id']
        #password= request.json['pwd']
        #typess= request.json['type']
        
        uids= 'B190SDtestCS'
        password= 'SDtestPass'
        typess= 'student'

        #password encryption:
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


            else:
                    return jsonify(message="Incorrect Password")
                    
#########################################################################################################################

    #@app.route("/signup",methods=["POST"])
    @app.route("/signup")
    def registration():
    
        cursor = dbconn.cursor()
        #uids= request.json['u_id']
        #names= request.json['uname'] #name 
        #emails= request.json['email']
        #password= request.json['pwd']
        #mobilenos= request.json['mobileno']
        #depts= request.json['dname']
        #typess= request.json['type']
        
        uids= 'B190SDtestCS'
        names= 'SDtestName'
        emails= 'SDtestName@gmail.com'
        password= 'SDtestPass'
        mobilenos= '1239991111'
        depts= 'CSE'
        typess= 'student'
        
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

    #@app.route("/list_all_fac",methods=["POST"])
    @app.route("/list_all_fac")
    def listAllFacPage():
        cursor = dbconn.cursor()
        cursor.execute("SELECT ssn from Faculty")
        list_of_ssn=cursor.fetchall()
        dbconn.commit()

        list_of_uname=[]
        for i in list_of_ssn:
            cursor = dbconn.cursor()
            cursor.execute("SELECT uname FROM Users WHERE u_id=%s",(i[0],))
            uname=cursor.fetchone()[0]
            list_of_uname.append({i[0]: uname})
            dbconn.commit()

        return jsonify(list_of_uname)

#########################################################################################################################

    #@app.route("/details",methods=["POST"])
    @app.route("/details")
    def details():
        cursor = dbconn.cursor()
        u_id = "B190SDtestCS"
        #u_id= request.json['u_id']
        cursor.execute("SELECT * from Users where u_id=%s",(u_id,))
        details=cursor.fetchone()
        dbconn.commit()
        u_id,names,emails,password,mobilenos=details
        return jsonify({"u_id":u_id,"uname":names,"email":emails,"pwd":password,"mobileno":mobilenos})

########################################  STUDENT  ###############################################

    #insert into the appointment table
    #@app.route("/request_stud",methods=["POST"])
    @app.route("/request_stud")
    def request_stud():
        #Details that we take in: date_created, date_appointment, time_appointment, title, description, stud_id, fac_id
        cursor = dbconn.cursor()
        date_created = "2020-12-30"
        date_appointment = "2020-12-31"
        time_appointment = "10:00:00"
        title = "test3"
        description = "3rd test description"
        stud_id = "B190SDtestCS"
        fac_id = "123"
        #date_created= request.json['date_created']
        #date_appointment= request.json['date_appointment']
        #time_appointment= request.json['time_appointment']
        #title= request.json['title']
        #description= request.json['description']
        #stud_id= request.json['stud_id']
        #fac_id= request.json['fac_id']
        dateTime = date_appointment + "#" + time_appointment
        # we are concatinating the date and time to get the datetime
        # because our database only has one column for datetime

        #status will be 1 for pending
        try:
            cursor.execute("INSERT INTO Appointments (status, date_created, date_scheduled, title, decription, stu_id, fac_id) VALUES(%s, %s, %s, %s, %s, %s, %s)",("1", date_created, dateTime, title, description, stud_id, fac_id))
        except:
            return jsonify(message="Give correct values muthe")
        dbconn.commit()

        return jsonify(message="Appointment Requested")

    #view all appointments requested by that perticular student
    #@app.route("/view_appointments_stud",methods=["POST"])
    @app.route("/view_all_apt_stud")
    def view_all_apt_stud():
        stud_id = "B190SDtestCS"
        #stud_id= request.json['stud_id']
        cursor = dbconn.cursor()
        cursor.execute("SELECT * from Appointments where stu_id=%s",(stud_id,))
        details=cursor.fetchall()
        dbconn.commit()
        if not details:
            return jsonify(message="No appointments found")
        list_of_appointments=[]
        for apt in details:
            appointment_id, status, date_created, dateTime, title, decription, stu_id, fac_id, suggested_date, faculty_message = apt
            date_appointment, time_appointment = dateTime.split("#")
            list_of_appointments.append(
                    {
                        'appointment_id': appointment_id,
                        'status': status,
                        'date_created': date_created,
                        'date_appointment': date_appointment,
                        'time_appointment': time_appointment,
                        'title': title,
                        'description': decription,
                        'stu_id': stu_id,
                        'fac_id': fac_id,
                        'suggested_date': suggested_date,
                        'faculty_message': faculty_message
                    }
                )
        return jsonify(list_of_appointments)


########################################  STUDENT OVER  ##########################################

########################################  FACULTY STUFF  #########################################
    #api to view all appointment that the faculty has
    #@app.route("/view_all_apt",methods=["POST"])
    @app.route("/view_all_apt")
    def view_all_apt():
        # takes in the faculty id
        #fac_id= request.json['fac_id']
        fac_id="123asfa"
        cursor = dbconn.cursor()
        cursor.execute("SELECT * from Appointments where fac_id=%s",(fac_id,))
        list_of_apt=cursor.fetchall()
        dbconn.commit()
        if not list_of_apt:
            return jsonify(message="Lonely angel")

        list_of_apt_details=[]
        for i in list_of_apt:
            aptId, status, date_created, dateTime, title, description, stu_id, fac_id, suggested_date, faculty_message = i
            date_scheduled = dateTime.split("#")[0]
            time_scheduled = dateTime.split("#")[1]
            list_of_apt_details.append({aptId: {"status": status, "date_created": date_created, "date_scheduled": date_scheduled, "time_scheduled": time_scheduled, "title": title, "description": description, "stu_id": stu_id, "fac_id": fac_id, "suggested_date": suggested_date, "faculty_message": faculty_message}})
        return jsonify(list_of_apt_details)

##################################################################################################

    #api to accept the appointment
    #@app.route("/accept",methods=["POST"])
    @app.route("/accept")
    def accept():
        # takes in the appointment id
        #apt_id= request.json['apt_id']
        apt_id="2233asdfasd3"
        try:
            cursor = dbconn.cursor()
            cursor.execute("SELECT * from Appointments where appointment_id=%s",(apt_id,))
            apt_details=cursor.fetchone()
        except:
            return jsonify(message="Give correct apt_id muthe")
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

    #api to reject a request by faculty
    #@app.route("/cancel",methods=["POST"])
    @app.route("/cancel")
    def cancel():
        # takes in the appointment id
        #apt_id= request.json['appointment_id']
        apt_id="10"
        try:
            cursor = dbconn.cursor()
            cursor.execute("SELECT * from Appointments where appointment_id=%s",(apt_id,))
            apt_details=cursor.fetchone()
        except:
            return jsonify(message="Give correct apt_id muthe")
        if apt_details is None:
            return jsonify(message="No appointment with this id")
        appointment_id, status, date_created, dateTime, title, description, stu_id, fac_id, suggested_date, faculty_message = apt_details
        date_scheduled, time_scheduled = dateTime.split("#")
        #UPdate the status to 2 for rejected if the current status is 1
        if status == "1":
            cursor = dbconn.cursor()
            cursor.execute("UPDATE Appointments SET status=%s WHERE appointment_id=%s",("2",apt_id))
            dbconn.commit()
            return jsonify(
                    {
                        "message":"Appointment Rejected", 
                    },
                    {
                        appointment_id: {
                        "status": "2",
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
        elif status == "2":
            return jsonify(message="Appointment already rejected")
        elif status == "3":
            return jsonify(message="Appointment already accepted")
        else:
            return jsonify(message="Appointment waiting for student aproval")

########################################  FACULTY STUFF OVER  ####################################



    return app
