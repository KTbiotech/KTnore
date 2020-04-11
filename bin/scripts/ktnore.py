#!/usr/bin/env python3


import argparse
import os
from os import path
import re
import operator
import shutil
import plotly
import plotly.graph_objects as go
from subprocess import Popen, PIPE
from Bio import SeqIO
from time import time, sleep
from datetime import datetime
import json
from termcolor import cprint
import random
import shutil
import plotly.graph_objects as go
import plotly.io as pio
from Bio import SeqIO
import pandas as pd
import ast
from termcolor import colored
import psutil # kiểm tra pid
from shutil import copyfile



def main():
   

    parser = argparse.ArgumentParser(
        prog='KTnore.py',
        description="something about Ktnore.py"
    )
    parser.add_argument("-id", "--job-id", dest="jobid", required=True,
        help="Some thing about jobid")
    parser.add_argument("-f5", "--path-fast5", dest="path5", required=True,
        help="Some thing about path fast5")
    parser.add_argument("-sig", "--sig-barcode", dest="sigBC", required=True,
        help="Some thing about path sigBC")
    
    args=parser.parse_args()

    if not os.path.exists("{}/CALL".format(args.jobid)):
        os.makedirs("{}/CALL".format(args.jobid)) 

    
    ## some
    ##chạy ẩn chương trình fast5.py
    fast5_cmd="python3 fast5py.py -f5 {} -fq {} -bc {}".format(
        args.path5,
        "{}/CALL".format(args.jobid),
        "{}/Barcode".format(args.jobid)
    )
    print (fast5_cmd)
    proc1=Popen(fast5_cmd, shell=True,close_fds=True)
    
    sleep(10)

    Total_cmd="python3 Total.py -id {} -sig {} -mon {} -gpy {}".format(
        args.jobid,
        "{}/Barcode/{}".format(args.jobid,args.sigBC),
        "{}/Barcode".format(args.jobid),
        "{}/Barcode/summary.txt".format(args.jobid)

    )
    flag=False
    while not flag:
        if  os.path.exists("{}/Barcode/{}".format(args.jobid,args.sigBC)):
            flag=True
            print (Total_cmd)
            proc2=Popen(Total_cmd,shell=True)
            
if __name__ == "__main__":
    main()