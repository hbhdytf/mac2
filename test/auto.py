#!/usr/bin/env python
# -*- coding:utf-8 -*-
import os
import time

if raw_input("restart swift or not (y/n):")=='y':
    for k in os.popen('sudo python setup.py install').readlines():
        pass
    for j in os.popen('sudo swift-init main restart').readlines():
        pass
#    print j,
#    time.sleep(0.02)

name = raw_input("Please input the name(for token):")
while not name:
    name = raw_input("Please input the name(for token):")
if name == "Admin" or name == "sandy":
    content = os.popen("curl -D- -H 'X-Storage-User:%s' -H 'X-Storage-Pass:admin' http://127.0.0.1:8080/auth/v1.0" %name).readlines()
else:
    content = os.popen("curl -D- -H 'X-Storage-User:%s' http://127.0.0.1:8080/auth/v1.0" %name).readlines()
token = content[2].strip()
url = content[1].split(':',1)[-1].strip()
#for i in content:
#    print i,
#    time.sleep(0.3)
#print token

#getmethod = os.popen("curl -k -X GET -H '%s' %s" %(token,url)).readlines()
#for dd in getmethod:
#    print dd,
#    time.sleep(0.3)
geturl = '/'.join([url,'ytf'])
print "curl -X GET -H '%s' %s"%(token,geturl)

print "curl -X PUT -T ./1.txt -D- -H 'object_name:小酒窝' -H 'parent_secl_id:7' -H 'obj_seclevel:4' -H 'Content-Type:audio/mp3' -H '%s' %s" %(token,url)
