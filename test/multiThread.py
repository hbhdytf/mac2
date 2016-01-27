#!/usr/bin/env python
# -*- coding:utf-8 -*-
import os
import time
import threading
import datetime

'''class mythread(threading.Thread):
    def __init__(self,threadname):
        threading.Thread.__init__(self,name=threadname)
        #self.threadname=threadname
    def run(self): 
	global x
        lock.acquire()	
        for i in range(0,100000):
    	    content = os.popen("curl -X PUT -T ./1.txt -D- -H 'object_name:小酒窝2' -H 'parent_secl_id:7' -H 'obj_seclevel:4' -H 'Content-Type:audio/mp3' -H 'X-Storage-Token: AUTH_tk0178febed9e94596bdcec6826b8b330a' http://127.0.0.1:8080/v1/AUTH_mac/ytf/c%s.txt" %(x))
	lock.release()
lock=threading.RLock()
t1=[]
for i in range(10):
    t=mythread(str(i))
    t1.append(t)
x=200000
for i in t1:
    i.start()'''
'''
name = raw_input("Please input the name(for token):")
while not name:
    name = raw_input("Please input the name(for token):")
if name == "Admin" or name == "sandy":
    content = os.popen("curl -D- -H 'X-Storage-User:%s' -H 'X-Storage-Pass:admin' http://127.0.0.1:8080/auth/v1.0" %name).readlines()
else:
    content = os.popen("curl -D- -H 'X-Storage-User:%s' http://127.0.0.1:8080/auth/v1.0" %name).readlines()
token = content[2].strip()
url = content[1].split(':',1)[-1].strip()
geturl = '/'.join([url,'ytf'])'''
#####################
content = os.popen("curl -D- -H 'X-Storage-User:1233' http://127.0.0.1:8080/auth/v1.0").readlines()
token = content[2].strip()
url = content[1].split(':',1)[-1].strip()
#f = file('./temp.log','w+')
#t = time.strftime('%Y-%m-%d %H:%M:%S')
#f.write(t)
#f.write('\n')
'''for j in range(10,50):
    temp=j
    content = os.popen("curl -X PUT  -H '%s' %s/ytf%s" %(token,url,temp))
'''
for j in range(1,10):
    temp1=j
    for i in range(1,2000):
        temp=i
        content = os.popen("curl -X PUT -T ./1.txt -D- -H 'object_name:小酒窝' -H 'parent_secl_id:7' -H 'obj_seclevel:4' -H 'Content-Type:audio/mp3' -H '%s' %s/ytf%s/%sytf%s.mp3" %(token,url,temp1,temp1,temp))

#t2 = time.strftime('%Y-%m-%d %H:%M:%S')
#f.write(t2)
#f.write('\n')
#f.close()

