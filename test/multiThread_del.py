#!/usr/bin/env python
# -*- coding:utf-8 -*-
import os
import time


'''name = raw_input("Please input the name(for token):")
while not name:
    name = raw_input("Please input the name(for token):")
if name == "Admin" or name == "sandy":
    content = os.popen("curl -D- -H 'X-Storage-User:%s' -H 'X-Storage-Pass:admin' http://127.0.0.1:8080/auth/v1.0" %name).readlines()
else:
    content = os.popen("curl -D- -H 'X-Storage-User:%s' http://127.0.0.1:8080/auth/v1.0" %name).readlines()'''
content = os.popen("curl -D- -H 'X-Storage-User:tn5' http://127.0.0.1:8080/auth/v1.0").readlines()
token = content[2].strip()
url = content[1].split(':',1)[-1].strip()
geturl = '/'.join([url,'ytf'])
#print time.strftime('%Y-%m-%d %H:%M:%S')
#f = file('./temp.log','w+')
#t = time.strftime('%Y-%m-%d %H:%M:%S')
#f.write(t)
#f.write('\n')
for i in range(20000,25000):
    temp=i
    content = os.popen("curl -X DELETE -H '%s' http://127.0.0.1:8080/v1/AUTH_mac/ytf/%s.txt" %(token,temp))
#t2=time.strftime('%Y-%m-%d %H:%M:%S')
#f.write(t2)
#f.write('\n')
#f.close()
