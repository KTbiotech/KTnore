
#!/usr/bin/env python3

#Last update: 10/11/2019
#Author: H-Van-Phuc
#
#

#import modules
import argparse
import os
from os import path
from subprocess import Popen, PIPE
from time import time
from datetime import datetime
from termcolor import cprint
import sys
import glob
from time import sleep

####
this=os.getcwd()
#Chon đường dẫn đến tất cả các foler, tên folder là tên sample
samplefolder=sys.argv[1]
samples=filter(os.path.isdir, os.listdir(samplefolder))
samples=list(samples)

#
for t in range(10):
    sampledict=dict()
    for sample in samples:
    # tìm kiems các tập tin fastq
        files=glob.glob("{}/{}/*".format(samplefolder,sample))
        sampledict[sample]=files
    timenow=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    f=open("supperlist.txt", "a")
    f.write("t{}|{}|{}\n".format(t,sampledict,timenow))
    f.close()
    sleep(2)





#####
