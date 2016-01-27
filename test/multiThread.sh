#!/bin/bash
#for j in {1..90}
#do
#    for i in {1..1000}
#        do
#            curl -X PUT -T ./1.txt -D- -H 'object_name:小酒窝' -H 'parent_secl_id:7' -H 'obj_seclevel:4' -H 'Content-Type:audio/mp3' -H 'X-Auth-Token: AUTH_tk3a23360c7b2f4f17b49b46718a2eb25d' http://127.0.0.1:8080/v1/AUTH_mac/ytf$j/$jytf$i.txt &> /dev/null
#    done
#done
#user:1233
for j in {100..104}
do
    for i in {1..10000}
    do
        curl -X PUT -T ./1.txt -D- -H 'object_name:小酒窝' -H 'parent_secl_id:7' -H 'obj_seclevel:4' -H 'Content-Type:audio/mp3' -H 'X-Auth-Token: AUTH_tk8dee884d4fa448f7b51bb887d5f0b823' http://127.0.0.1:8080/v1/AUTH_mac/ytf$j/{$j}ytf{$i}.txt &> /dev/null
    done
done
