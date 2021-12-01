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
            list_of_uname.append(uname)
            dbconn.commit()

        return jsonify(list_of_uname)

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
        print(details)
        return jsonify({"u_id":u_id,"uname":names,"email":emails,"pwd":password,"mobileno":mobilenos})

########################################  STUDENT  ###############################################




    return app
