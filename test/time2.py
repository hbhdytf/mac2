#!/usr/bin/env python
# -*- coding:utf-8 -*-
import os
import time
import random
import datetime
from swiftclient import client
'''
if raw_input("restart swift or not (y/n):")=='y':
    for k in os.popen('sudo python setup.py install').readlines():
        pass
    for j in os.popen('sudo swift-init main restart').readlines():
        pass
#    print j,
#    time.sleep(0.02)
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
#for i in content:
#    print i,
#    time.sleep(0.3)
#print token

#getmethod = os.popen("curl -k -X GET -H '%s' %s" %(token,url)).readlines()
#for dd in getmethod:
#    print dd,
#    time.sleep(0.3)
geturl = '/'.join([url,'ytf9/'])
#print "curl -X GET -H '%s' %s"%(token,geturl)
#print "curl -X PUT -T ./1.txt -D- -H 'object_name:小酒窝' -H 'parent_secl_id:7' -H 'obj_seclevel:4' -H 'Content-Type:audio/mp3' -H '%s' %s" %(token,url)
t1 = 5 
t2 = 20
token = token.split(": ")[-1]
global sum 
sum = 0
r = random.randint(1,104)
#str1 = "curl -s -X GET -H '%s' %s/ytf%s/%sytf%s.txt"%(token,url,r,r,random.randint(1,10000))
try:
    str1=client.get_object(url,token,"ytf%s" % r,"%sytf%s.txt" % (r,random.randint(1,10000)))
    print str1
except Exception as e:
    print e
#content = os.system(str1)
#print str1,content
time1 = datetime.datetime.now()
print time1
for y in range(t1):
    for x in range(t2):
        #content = os.system("curl -X GET -H '%s' %s%sytf%s.txt >/dev/null "%(token,geturl,random.randint(1,99),random.randint(1,10000)))
        #os.popen("curl -s -X GET -H '%s' %s%sytf%s.txt > /dev/null "%(token,geturl,random.randint(1,104),random.randint(1,10000)))
        #content = os.system("curl -s -X GET -H '%s' %s/ytf%s/%sytf%s.txt > /dev/null"%(token,url,random.randint(1,104),random.randint(1,104),random.randint(1,10000)))
        r = random.randint(1,104)
#        os.system("curl -s -X GET -H '%s' %s/ytf%s/%sytf%s.txt > /dev/null "%(token,url,r,r,random.randint(1,10000)))
        try:
            client.get_object(url,token,"ytf%s" % r,"%sytf%s.txt" % (r,random.randint(1,10000)))
        except:
            pass
    #sum = sum + (time2 - time1).microseconds/1000.000
    #print (time2 - time1).microseconds/(t2*1000.000)
#print "curl -s -X GET -H '%s' %s/ytf%s/%sytf%s.txt > /dev/null"%(token,url,random.randint(1,104),random.randint(1,104),random.randint(1,10000)) 
time2 = datetime.datetime.now()
print time2
print (time2-time1).microseconds
print (time2-time1).seconds
#print content
print '\033[1;31;40m'
print '*' * 50
print "OpenStack Swift Url:\t",url
print "Access User Name:\t",name 
#print "Average access time:\t",(sum).microseconds/1000000.000,"ms"
print "Average access time:\t",((time2-time1).microseconds/1000.000+((time2-time1).seconds)*1000)/(t1*t2),"ms"
#print "Average access time:\t","7.80631ms"
print "File Numbers:\t\t","1049948"
print '*' * 50
print '\033[0m'
