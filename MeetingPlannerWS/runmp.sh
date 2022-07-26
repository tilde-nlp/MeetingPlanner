#!/bin/bash

gunicorn flaskmeetingplanner:app -w 2 --threads 2 -b 0.0.0.0:5000 --env Sql_connect="${Sql_connect}" --env SMTPSender="${SMTPSender}" --env APIKey="${APIKey}"
 