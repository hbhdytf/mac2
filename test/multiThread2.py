#!/usr/bin/env python
# -*- coding:utf-8 -*-
import os
import time
import threading
import datetime

content = os.popen("curl -D- -H 'X-Storage-User:1233' http://127.0.0.1:8080/auth/v1.0").readlines()
token = content[2].strip()
url = content[1].split(':',1)[-1].strip()
for i in range(100,105):
    temp=i
    content = os.popen("curl -X PUT  -H '%s' %s/ytf%s" %(token,url,temp))

