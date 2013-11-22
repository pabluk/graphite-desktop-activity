#!/bin/bash

python report.py activity.log
scp web/index.html web/data.json pabluk@ssh.alwaysdata.com:~/www/activity.seminar.io/
#scp web/data.json pabluk@ssh.alwaysdata.com:~/www/activity.seminar.io/
