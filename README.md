# MeetingPlanner

Meeting Planner prototype consists of 3 modules:

1. Meeting Planner Virtual Assistant created in platform https://va.tilde.com - the source code in folder `Bot`

2. Meeting Planner Web Service - the source code in folder `MeetingPlannerWS`

3. Meeting Planner database - the source code in folder `SQLDatabase`

![Architecture of the Meeting Planner](architecture.jpg)

## MeetingPlanner Virtual Assistant

## MeetingPlanner Web Service

## MeetingPlanner database

Meeting Planner database has 5 tables.

![Meeting Planner database](SQLdatabase.jpg)

-	*Meeting* table has unique meeting identifier, organizer identifier, meeting subject and length, meeting creation time, and status of meeting. Possible values of the field *Status* are ‘active’, ‘approved’, ‘canceled’.

-	*Meeting times* table has potential meeting times for the meeting. The field *Approved* holds information which time is the final for the meeting: 1 – this time is the final, 0 – for other potential times.

-	*Persons* table has unique person identifier, the person’s e-mail and unique 10-symbol access code.

-	*Invitees* table has identifiers of persons invited for the particular meeting, and the last time when the invitation e-mail was sent (field *Last time reminded* is empty if the e-mail is not yet sent).

-	*Accept status* table has information how each invitee responded about each proposed time of the meeting in the field *Status*. Possible values: 1 – time accepted, 0 – time rejected. 


@Tilde, 2022
