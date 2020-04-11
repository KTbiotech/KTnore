#!/usr/bin/env python3

#Last update: 10/11/2019
#Author: H-Van-Phuc
#
#Chương trình này không tao ra thư mục mới, do đó sẽ có lỗi xảy ra khi không tìm thấy files

#import modules
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
from time import time
from datetime import datetime
import json
from termcolor import cprint
import random
import shutil


##################
global this
this=os.getcwd()


def compare (job,samplelist,ncontrol,timepoint):
    '''
    Sử dụng crf để so sánh kết quả từ centrifuge
    params
    ---------
    job: (str) job id ~folder name~ container
    samplelist: list, eg: ["S1", "S2", "S3","S5"]
    ncontrol: int, số  lượng các mẫu control từ trái sang phải của samplelist
    timepoint: thời điểm so sánh các mẫu # các params cần thiết đề tìm đến vị trí của files

    return
    --------
    No return
    Kết quả trả về
    '''
    files=['']
    for sample in samplelist:
        pathto="{}/{}/{}/{}/{}".format(this,job,sample, timepoint, "4.Taxonomy/4.1.Centrifuge/*.cf.detail.out")
        files.append(pathto)
    files=" -f ".join(files)
    taxdumpdir='/media/kt02/DATA/Phuc_folders/Dev/py/taxonomy/taxdump'
    rcf_cmd="rcf"+ " -n {} -y {} -o {} -e FULL -c {} {}".format(
            taxdumpdir, #-n 
            35, # minscore centrifuge
            "{}/{}/{}/{}/tp-{}-{}.html".format(this,job,"0.compare",timepoint,timepoint,"-".join(samplelist)), # -o output html
            ncontrol, # -c số lượng mẫu control từ trái sang phải,
            files
            )
    print (rcf_cmd)

    proc0=Popen(rcf_cmd, stdout=PIPE, stderr=PIPE, shell=True)
    proc0.wait()

#main()

def main():


    parser = argparse.ArgumentParser(
        prog='compare.py',
        description="something about compare.py"
    )
    parser.add_argument("-id", "--id-user", dest="job",default="123", 
        help="something about id jobs")
    parser.add_argument("-tp", "--time-point", dest="timepoint",default="t1", 
        help="something about timepoint")
    parser.add_argument("-spl", "--sample-list", dest="samplelist",default="S1", 
        help="something about samplelist eg: S1,S2,S3")
    parser.add_argument("-nctrl", "--ncontrol", dest="ncontrol",default="1", 
        help="something about ncontrol : eg: 1")

    args=parser.parse_args()

#check input argv

####################

    #compare mutiple sample
    compare(args.job, args.samplelist.split(","),ncontrol=args.ncontrol,timepoint='t1')

if __name__ == "__main__":
    main()