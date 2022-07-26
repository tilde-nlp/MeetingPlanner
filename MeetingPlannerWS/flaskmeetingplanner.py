#!/usr/bin/python
##############################################################################
# Meeting Planner Web Service                                                #
# Created by D.Deksne, @Tilde, 2022                                          #
##############################################################################

import os.path, sys, re, inspect
from flask import Flask, request, Response, jsonify
import argparse
import json
import pyodbc
import smtplib, ssl
from email.message import EmailMessage
from email.policy import SMTP
import configparser
import sendgrid
from sendgrid.helpers.mail import *
import uuid

app = Flask(__name__)


sql_meeting = 'DECLARE @PY_OUT int \
EXEC AddNewMeeting @subject=?, @length=?, @organizerid=?, @meetingid=@PY_OUT OUTPUT \
SELECT @PY_OUT'
sql_person = 'DECLARE @PY_OUT int \
EXEC AddNewPerson @email=?, @code=?, @personid=@PY_OUT OUTPUT \
SELECT @PY_OUT'

sql_invitees = 'INSERT INTO [Invitees] ([Invitees].[Meeting ID], [Invitees].[Person ID]) VALUES(?, ?)'
sql_updateinvitees = 'UPDATE [Invitees] SET [Last time reminded]=GETDATE() WHERE [Meeting ID]=? AND [Person ID]=?'

sql_times = 'INSERT INTO [Meeting times] ([Meeting ID], [Time]) VALUES(?, ?)'
sql_updatetimes = 'UPDATE [Meeting times] SET [Approved]=1 WHERE [Meeting ID]=? AND [Time]=?'
sql_updatemeeting = 'UPDATE [Meeting] SET [Status]=? WHERE [Meeting ID]=?'
sql_gettimes = 'SELECT [MeetingTime ID], [Time], [Approved] FROM [Meeting times] WHERE [Meeting ID]=?'
sql_getapprovedtime = 'SELECT [Time] FROM [Meeting times] WHERE [Meeting ID]=? AND [Approved]=1'
sql_deletestatus = 'DELETE FROM [Accept status] WHERE [Meeting ID]=? AND [Person ID]=?'
sql_updatestatus = 'INSERT INTO [Accept status] ([Meeting ID], [Person ID], [MeetingTime ID],Status) VALUES(?, ?, ?, ?)'
sql_selectstatus = 'SELECT currtime, status, email FROM [AcceptStatusView] WHERE meeting=? ORDER BY currtime ASC, status DESC'
sql_selectstatusbyorganizer = 'SELECT meeting, currtime, status, email  FROM [AcceptStatusView] WHERE organizer=? ORDER BY meeting, currtime ASC, status DESC'

sql_selectcodefromemail = "SELECT Persons.[Code] FROM Persons WHERE Persons.[E-mail]=?"
sql_selectcodefromid = "SELECT Persons.[Code] FROM Persons WHERE Persons.[Person ID]=?"

sql_selectnotresponded = 'SELECT invitee, email, code from [NotResponded] WHERE meetingid=?'
sql_selectinvitees = "SELECT Persons.[E-mail] FROM Invitees INNER JOIN Persons ON Invitees.[Person ID] = Persons.[Person ID] WHERE [Invitees].[Meeting ID]=?"
sql_meetingdetails = "SELECT Persons.[E-mail], Meeting.Subject, str(Meeting.Length), Meeting.Status as status \
FROM Meeting INNER JOIN Persons ON Meeting.[Organizer ID] = Persons.[Person ID] WHERE [Meeting].[Meeting ID]=?"

sql_meetings_invitees = "select distinct meetingid, org_email, subject from MeetingList where pers_code=?"
sql_meetings_organizer = "select distinct meetingid, org_email, subject from MeetingList where org_code=?"

def my_random_string(string_length=10):
    """Returns a random string of length string_length."""
    random = str(uuid.uuid4()) # Convert UUID format to a Python string.
    random = random.upper() # Make all characters uppercase.
    random = random.replace("-","") # Remove the UUID '-'.
    return random[0:string_length] # Return the random string.

def SendEmail(email, msgsubject, plainmsgstr, htmlmsgstr):

    try:
        sg = sendgrid.SendGridAPIClient(api_key = os.environ.get('APIKey'))
        message = Mail(Email(os.environ.get('SMTPSender')),
                       To(email),
                       msgsubject,
                       Content("text/plain", plainmsgstr),
                       HtmlContent(htmlmsgstr))

        response = sg.client.mail.send.post(request_body=message.get())

    except SendGridException as e:
        print( json.dumps({'output': str(e)}))
    except:
        print( json.dumps({'output': 'Error'}))

@app.route('/', methods=['GET', 'POST'])
def getparameters():
    str = my_random_string()
    return jsonify("This is the Meeting Planner Web Service")

@app.route('/getmeetinglist', methods=['GET', 'POST'])
def getmeetinglist():
    if request.method=='GET':
        code = request.args.get("code", "-")
        meetingtype = request.args.get("meetingtype", "1")
    elif request.method=='POST':
        code = int(request.form['code'])
        meetingtype = str(request.form['meetingtype'])

    if(code == '-'):
        return json.dumps({'output': 'Missing essential parameter - code!'})

    try:
        cnxn = pyodbc.connect(os.environ.get('Sql_connect'), autocommit=True)
        cursor = cnxn.cursor()
        print("Connected to SQL Server")

        if meetingtype == '1': #meetings for invitees
            cursor.execute(sql_meetings_invitees,code)
        else: #meetings for organizer
            cursor.execute(sql_meetings_organizer,code)
        idx = 0
        subjectlist = []
        organizerlist = []
        idlist = []
        for row in cursor.fetchall():
            idx = idx + 1
            idlist.append(str(row[0]))
            organizerlist.append(row[1])
            subjectlist.append(row[2])

        cursor.close()
        del cursor
        cnxn.close()
        del cnxn
        return json.dumps({'output': 'Success', 'total': str(idx), 'mid': ';'.join(idlist), 'organizer': ';'.join(organizerlist), 'subject': ';'.join(subjectlist)})
    except pyodbc.Error as e:
        return json.dumps({'output': str(e), 'total': '', 'mid': '', 'organizer': '', 'subject': ''})
    except:
        return json.dumps({'output': 'Error', 'total': '', 'mid': '', 'organizer': '', 'subject': ''})

@app.route('/newmeeting', methods=['GET', 'POST'])
def newmeeting():
    if request.method=='GET':
        emails = request.args.get("emails", "")
        length = int(request.args.get("length", "60"))
        subject = request.args.get("subject", "-")
        times = request.args.get("times", "")
    elif request.method=='POST':
        emails = str(request.form['emails'])
        length = int(request.form['length'])
        subject = str(request.form['subject'])
        times = str(request.form['times'])

    if(len(emails)*len(times) == 0):
        return json.dumps({'output': 'Missing essential parameters - emails or times!'})
    meetingid = 0
    emaillist = emails.split(';')
    timeslist = times.split(';')

    try:
        cnxn = pyodbc.connect(os.environ.get('Sql_connect'), autocommit=True)
        cursor = cnxn.cursor()
        print("Connected to SQL Server")
        for idx, curremail in enumerate(emaillist):
            curremail = curremail.strip()
            if len(curremail)>0:
                cursor.execute(sql_person,curremail,my_random_string())
                personid = cursor.fetchval()
                if idx == 0: #for meeting organizer
                    cursor.execute(sql_meeting,subject, length, personid) #add new meeting
                    meetingid = cursor.fetchval()
                    for currtime in timeslist:
                        currtime = currtime.strip()
                        if len(currtime)>0:
                            #currtime = re.sub("^(\d\d)\.(\d\d)\.", "\\2.\\1.", currtime) #SQL Server expects first month, then date
                            cursor.execute(sql_times,meetingid, currtime)
                else: #for invitees
                        cursor.execute(sql_invitees,meetingid, personid)

        cursor.close()
        del cursor
        cnxn.close()
        del cnxn
        return json.dumps({'output': 'Success', 'meeting': meetingid})
    except pyodbc.Error as e:
        return json.dumps({'output': str(e), 'meeting': '-'})
    except:
        return json.dumps({'output': 'Error', 'meeting': '-'})

@app.route('/saveinviteechoice', methods=['GET', 'POST'])
def saveinviteechoice():
    if request.method=='GET':
        personid = int(request.args.get("invitee", "0"))
        meetingid = int(request.args.get("meeting", "0"))
        times = request.args.get("times", "")
    elif request.method=='POST':
        personid = int(request.form['invitee'])
        meetingid = int(request.form['meeting'])
        times = str(request.form['times'])

    if(len(times) == 0):
        return json.dumps({'output': 'Missing essential parameter - times!'})

    try:
        cnxn = pyodbc.connect(os.environ.get('Sql_connect'), autocommit=True)
        cursor = cnxn.cursor()
        print("Connected to SQL Server")

        cursor.execute(sql_deletestatus,meetingid,personid)
        cursor.execute(sql_gettimes,meetingid)
        for row in cursor.fetchall():
            if row[1] in times:
                cursor.execute(sql_updatestatus,meetingid, personid, row[0], 1)
            else:
                cursor.execute(sql_updatestatus,meetingid, personid, row[0], 0)

        cursor.close()
        del cursor
        cnxn.close()
        del cnxn
        return json.dumps({'output': 'Success'})
    except pyodbc.Error as e:
        return json.dumps({'output': str(e)})
    except:
        return json.dumps({'output': 'Error'})

@app.route('/getmeetinginfo', methods=['GET', 'POST'])
def getmeetinginfo():
    if request.method=='GET':
        meetingid = int(request.args.get("meeting", "0"))
    elif request.method=='POST':
        meetingid = int(request.form['meeting'])

    try:
        cnxn = pyodbc.connect(os.environ.get('Sql_connect'), autocommit=True)
        cursor = cnxn.cursor()

        print("Connected to SQL Server")
        if meetingid > 0: #info about single meeting
            cursor.execute(sql_meetingdetails,meetingid)
            row = cursor.fetchone()
            if row == None:
                return json.dumps({'output': '-', 'invitees': '-', 'organizer': '-', 'subject': '-', 'length': '-', 'status': '-'})

            organizer = row[0].strip()
            subject = row[1].strip()
            length = row[2].strip()
            status = row[3].strip()
            cursor.execute(sql_selectinvitees,meetingid) #invitees
            invitees = ''
            for row in cursor.fetchall():
                invitees = invitees + '\n' + row[0]

        else:
            return json.dumps({'output': 'Error - meeting is not specified!', 'invitees': '-', 'organizer': '-', 'subject': '-', 'length': '-', 'status': '-'})

        results = ""

        if status == 'approved':
            cursor.execute(sql_getapprovedtime,meetingid)
            approvedtime = cursor.fetchone()[0]
            results = '\n***\n**' + approvedtime + '**'
        else:
            meetingtimes = {}
            cursor.execute(sql_gettimes,meetingid)
            for row in cursor.fetchall():
                meetingtimes[row[1]] = row[2]

            cursor.execute(sql_selectstatus,meetingid)
            currenttimeslot = ''

            idx = 0
            for row in cursor.fetchall():
                if currenttimeslot != row[0]:
                    currenttimeslot = row[0]
                    idx = idx + 1
                    results = results + '\n***\n'+ str(idx) + ' - **' + currenttimeslot + '**'
                    meetingtimes.pop(row[0], None)
                results = results + '\n* ' + row[2] + ' '
                if row[1] == 1:
                    results = results + '✔' 
                else:
                    results = results + '❌'
            for item in meetingtimes:
                idx = idx + 1
                results = results + '\n***\n'+ str(idx) + ' - **' + item + '**'

        print(results)
        cursor.close()
        del cursor
        cnxn.close()
        del cnxn
        return json.dumps({'output': results, 'invitees': invitees, 'organizer': organizer, 'subject': subject, 'length': length, 'status': status})
    except pyodbc.Error as e:
        return json.dumps({'output': str(e), 'invitees': '-', 'organizer': '-', 'subject': '-', 'length': '-', 'status': '-'})
    except:
        return json.dumps({'output': 'Error', 'invitees': '-', 'organizer': '-', 'subject': '-', 'length': '-', 'status': '-'})

@app.route('/sendreminders', methods=['GET', 'POST'])
def sendreminders():
    if request.method=='GET':
        meetingid = int(request.args.get("meeting", "0"))
        prefferedtime = request.args.get("time", "-")
    elif request.method=='POST':
        meetingid = int(request.form['meeting'])
        prefferedtime = str(request.form['time'])

    if(meetingid == 0):
        return json.dumps({'output': 'Missing essential parameter - meeting!'})
    if (prefferedtime == '-'):
        return sendremindersformeeting(meetingid)
    else:
        return sendapprovedtimeformeeting(meetingid, '', prefferedtime)

def sendremindersformeeting(meetingid):
    try:
        cnxn = pyodbc.connect(os.environ.get('Sql_connect'), autocommit=True)
        cursor = cnxn.cursor()
        cursor.execute(sql_meetingdetails,meetingid)
        minfo = cursor.fetchone()
        cursor.execute(sql_selectnotresponded,meetingid)

        for row in cursor.fetchall():
            plainmsgstr = "Hello!\n\nYou have a new meeting request.\nOrganizer: {}\nSubject: {}\nChoose the most appropriate meeting time in the Meeting Planner chat window https://va.tilde.com/api/prodk8sbotmeeti0/chat/default.htm?meeting={}&amp;invitee={}&amp;code={}\n\nYour Meeting Planner".format(minfo[0], minfo[1], meetingid, row[0], row[2])
            htmlmsgstr = "Hello!<br><br>You have a new meeting request.<br>Organizer: {}<br>Subject: {}<br>Choose the most appropriate meeting time in the Meeting Planner chat window https://va.tilde.com/api/prodk8sbotmeeti0/chat/default.htm?meeting={}&amp;invitee={}&amp;code={} <br><br>Your Meeting Planner".format(minfo[0], minfo[1], meetingid, row[0],row[2])
            SendEmail(row[1], f'Meeting Planner - new meeting request {meetingid}',plainmsgstr,htmlmsgstr)

        cursor.close()
        del cursor
        cnxn.close()
        del cnxn
        return json.dumps({'output': 'Success'})
    except pyodbc.Error as e:
        return json.dumps({'output': str(e)})
    except:
        return json.dumps({'output': 'Error'})

@app.route('/sendcode', methods=['GET', 'POST'])
def sendcode():
    if request.method=='GET':
        email = request.args.get("email", "-")
    elif request.method=='POST':
        email = request.form['email']

    try:
        if(email == '-'):
            return json.dumps({'output': 'Missing essential parameter - email!'})
        else:
            cnxn = pyodbc.connect(os.environ.get('Sql_connect'), autocommit=True)
            cursor = cnxn.cursor()
            cursor.execute(sql_selectcodefromemail,email)
            if cursor.rowcount == 0:
                cursor.execute(sql_person,email,my_random_string())
                personid = cursor.fetchval()
                cursor.execute(sql_selectcodefromid,personid)
            
            code=cursor.fetchone()

            plainmsgstr = "Hello!\n\nHere is your 10-symbol access code\n{}\nTo avoid asking for the code every time use this link to open Meeting Planner chat window https://va.tilde.com/api/prodk8sbotmeeti0/chat/default.htm?code={}\n\nYour Meeting Planner".format(code[0], code[0])
            htmlmsgstr = "Hello!<br><br>Here is your 10-symbol access code<br>{}<br>To avoid asking for the code every time use this link to open Meeting Planner chat window https://va.tilde.com/api/prodk8sbotmeeti0/chat/default.htm?code={}<br><br>Your Meeting Planner".format(code[0], code[0])
            SendEmail(email, f'Meeting Planner - your code',plainmsgstr,htmlmsgstr)

        cursor.close()
        del cursor
        cnxn.close()
        del cnxn
        return json.dumps({'output': 'Success'})
    except pyodbc.Error as e:
        return json.dumps({'output': str(e)})
    except:
        return json.dumps({'output': 'Error'})


@app.route('/schedulemeeting', methods=['GET', 'POST'])
def schedulemeeting():
    if request.method=='GET':
        meetingid = int(request.args.get("meeting", "0"))
        prefferedtime = request.args.get("time", "0")
    elif request.method=='POST':
        meetingid = int(request.form['meeting'])
        prefferedtime = str(request.form['time'])

    try:
        cnxn = pyodbc.connect(os.environ.get('Sql_connect'), autocommit=True)
        cursor = cnxn.cursor()
        print("Connected to SQL Server")
        if(prefferedtime == '0'):
            cursor.execute(sql_updatemeeting,'canceled',meetingid)
        else:
            cursor.execute(sql_updatetimes,meetingid,prefferedtime)
            if cursor.rowcount > 0:
                cursor.execute(sql_updatemeeting,'approved',meetingid)
            else:
                prefferedtime='Invalid'
        cursor.close()
        del cursor
        cnxn.close()
        del cnxn

        if(prefferedtime == 'Invalid'):
            return json.dumps({'output': f'Invalid preffered time!'})
        else:
            return json.dumps({'output': f'Success'})
    except pyodbc.Error as e:
        return json.dumps({'output': str(e)})
    except:
        return json.dumps({'output': 'Error'})

@app.route('/trigger', methods=['GET', 'POST'])
def trigger():
    try:
        cnxn = pyodbc.connect(os.environ.get('Sql_connect'), autocommit=True)
        cursor = cnxn.cursor()
        cursor.execute("SELECT [Meeting ID], [Status], [Subject] from [Meeting]")
        for row in cursor.fetchall():
            if row[1] == 'active':
                sendremindersformeeting(row[0])
            elif row[1] == 'approved':
                sendapprovedtimeformeeting(row[0], row[2], '')
            elif row[1] == 'canceled':
                sendapprovedtimeformeeting(row[0], row[2], '-')
        cursor.close()
        del cursor
        cnxn.close()
        del cnxn
        return json.dumps({'output': 'Success'})
    except pyodbc.Error as e:
        return json.dumps({'output': str(e)})
    except:
        return json.dumps({'output': 'Error'})

def sendapprovedtimeformeeting(meetingid, subject='', approvedtime=''):
    try:
        cnxn = pyodbc.connect(os.environ.get('Sql_connect'), autocommit=True)
        cursor = cnxn.cursor()
        if not approvedtime:
            cursor.execute(sql_getapprovedtime,meetingid)
            approvedtime = cursor.fetchone()[0]
        if not subject:
            cursor.execute(sql_meetingdetails,meetingid)
            subject = cursor.fetchone()[1]
        cursor.execute(sql_selectinvitees,meetingid)

        if (approvedtime=='0'):
            for row in cursor.fetchall():
                plainmsgstr = "Hello!\n\nThe meeting {} with the subject '{}' has been canceled.\n\nYour Meeting Planner".format(meetingid, subject)
                htmlmsgstr = "Hello!<br><br>The meeting {} with the subject '{}' has been canceled.<br><br>Your Meeting Planner".format(meetingid,subject)
                SendEmail(row[0], f'Meeting Planner - the meeting {meetingid} canceled',plainmsgstr,htmlmsgstr)
        else:
            for row in cursor.fetchall():
                plainmsgstr = "Hello!\n\nYou are invited to join the meeting with the subject {}.\nThe time of the meeting is {}\n\nYour Meeting Planner".format(subject, approvedtime)
                htmlmsgstr = "Hello!<br><br>You are invited to join the meeting with the subject {}.<br>The time of the meeting is {}<br><br>Your Meeting Planner".format(subject, approvedtime)
                SendEmail(row[0], f'Meeting Planner - the final meeting time {meetingid}',plainmsgstr,htmlmsgstr)
        cursor.close()
        del cursor
        cnxn.close()
        del cnxn
        return json.dumps({'output': 'Success'})
    except pyodbc.Error as e:
        return json.dumps({'output': str(e)})
    except:
        return json.dumps({'output': 'Error'})



if __name__ == '__main__':

    app.run(debug=True, host='0.0.0.0',use_reloader=False)