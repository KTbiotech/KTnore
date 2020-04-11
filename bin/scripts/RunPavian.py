#!/usr/bin/env python3

import sys
from subprocess import Popen, PIPE

if len(sys.argv) < 3:
    print ("RunPavian.py <preset-folder> <off/null ( tắt pavain đã chạy)>")
    exit()


#3 kiểm tra pavian đã hoạt động trên port 5000 chưa

pavian=Popen('./checkPavianOn.sh', stdout=PIPE)
isPavian = str(pavian.stdout.readline())[2] # Pavian is on b'1\n' , url http://127.0.0.1:5000/
onPavian=str(1)
if isPavian != onPavian:
    print("Pavian not running>> start now")
    ##Run pavian
    Pavian_cmd='Rscript --vanilla RunPavian.R ' + sys.argv[1] + ' &'
    pavian=Popen(Pavian_cmd,stdout=PIPE, stderr=PIPE, shell=True)
    pavian.wait()
    print (Pavian_cmd)

else:
    print("OK pavian")
print("OK. continues")