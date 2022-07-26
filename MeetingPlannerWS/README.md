# Meeting Planner service
## Introduction
Web Service for communication with Meeting Planner VA and SQL database.

## Getting Started
To set up the Docker container perform the following steps:

1. Get the code of the container from the source controle.

2. Change the directory to the one containing the source.

3. Build the container with the following command:

`docker build -t meetingplanner_app .`


## Functionality
 
To start the Meeting Planner Web Service start the container with the following command:

`docker run -it -p 22222:8888 --name meetingplanner --rm meetingplanner_app`

Meeting Planner Web Service uses 3 variables that must be added to the environment variables (or to Application settings of the App service if the container is deployed to the MS Azure portal):

1) Sql_connect - ODBC connection string to SQL Server

2) SMTPSender - e-mail address from which e-mails are sent

3) APIKey - API key for the SendGrid mail server


## Web Service API

1.	Method NewMeeting – info about a new meeting is stored in the database

o	Parameter emails – meeting organizer e-mail (as the first) and e-mails of invitees, e-mails separated by semicolon

o	Parameter subject – subject of the meeting

o	Parameter length – length of the meeting

o	Parameter times – potential times of the meeting in form dd.mm.yyyy hh:mm separated by semicolon

2.	Method SaveInviteeChoice – info about the invitee’s preferred time is stored in the database

o	Parameter invitee – ID of the invitee

o	Parameter meeting – ID of the meeting

o	Parameter times – preferred time/s of the meeting in form dd.mm.yyyy hh:mm separated by semicolon

3.	Method GetMeetingInfo – returns general information about meeting and info about times that invitees prefer

o	Parameter meeting – ID of the meeting to check

4.	Method SendReminders - sends reminders to invitees

o	Parameter meeting – ID of the meeting

o	Parameter time:

•	‘-’ - sends reminders to invitees that have not responded

•	‘0’ - sends e-mails telling that meeting has been canceled

•	other value - sends emails about the final accepted time for the meeting

5.	Method ScheduleMeeting – the final meeting time is stored in database

o	Parameter meeting – ID of the meeting

o	Parameter time – preferred time for the meeting in form dd.mm.yyyy hh:mm or ‘0’ if the meeting should be canceled

6.	Method GetMeetingList – gets the list of meetings filtered by access code

o	Parameter code – access code of the person

o	Parameter meetingtype:

•	‘1’ – meetings the person is invited to

•	‘0’ – meetings the person has organized

7.	Method Trigger – checks status of all meetings, e-mails links to the bot Web chat window to the invitees asking to vote for the preferred time (links contain invitee ID, invitee access code, and  meeting ID), or sends reminders to invitees that have not responded, informs organizer/s, sends information about final time of the meeting.

8.	Method SendCode – sends 10-symbol Meeting Planner access code to the e-mail address

o	Parameter email  – e-mail address

@Tilde, 2022
