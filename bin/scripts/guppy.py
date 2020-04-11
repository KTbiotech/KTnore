#!/usr/bin/env python3
import sys
import argparse
import os
from os import path
import operator
from subprocess import Popen, PIPE
from Bio import SeqIO
from time import time
from datetime import datetime
import json
from termcolor import cprint
import shutil
import glob






def guppy_caller(newfast5,output,outBC):
    guppy_basecaller="ls {} |guppy_basecaller \
                -s {} -c {} dna_r9.4.1_450bps_fast.cfg \
                            --cpu_threads_per_caller {} --num_callers {}".format(
                            newfast5,
                            output,
                            "dna_r9.4.1_450bps_fast.cfg",
                            6,
                            4
                            )
    proc=Popen(guppy_basecaller,shell=True, close_fds=True )
    proc.wait()

    ###prefix=newfast5.split("/")[-1].split(".")[0] ## something like that

   

    '''
    prefix="_".join(newfast5.split("/")[-1].split(".")[0].split("_")[1:])
    guppy_basecaller:
    /media/kt02/DATA/Phuc_folders/Dev/Modules/fast5caller/relpy/FAK56848_ddaeeab4f0fc8428b7ae0a84e7e8d3498465e49d_0.fast5
    /media/kt02/DATA/Phuc_folders/Dev/Modules/fast5caller/demo/fastq_runid_ddaeeab4f0fc8428b7ae0a84e7e8d3498465e49d_0_0.fastq

    gyppy_barcoder:

    '''
    guppy_barcoder="guppy_barcoder -i {} -s {} --barcode_kits {} -t 16".format(
                        output,
                        output +"/BC",
                        "SQK-RPB004"
        )
    print (guppy_barcoder)
    
    proc2=Popen(guppy_barcoder,shell=True, close_fds=True )
    proc2.wait()


    file="basecalling.txt"
    with open (file, "a") as f:
        f.write("{}\t{}\t{}\n".format(
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                path,
                "finish"
        ))
    #mỗi tập fast5 đi vào 1 folder riêng và có có 1 barcoder riêng cho nó
    # cần gộp lại các file summary tồn tại
    container=outBC
    if not os.path.exists(container):
            os.makedirs(container) # 

    filesummary=open(container+"/summary.txt", "w")
    sumpath="/".join(output.split("/")[:-1])
    proc3=Popen("cat {}/{}/sequencing_summary.txt|sort -r -k 7|uniq".format(sumpath,"*"),
                shell=True,
                stdout=filesummary)
    filesummary.close()
    
    # cần gộp các file barcode tồn tại
    filesummary=open(container+"/barcode.txt", "w")
    proc3=Popen("cat {}/{}/{}/barcoding_summary.txt|sort -r -k 11|uniq".format(sumpath,"*","BC"),
                shell=True,
                stdout=filesummary)
    filesummary.close()
    # gộp file fastq theo sample
    ###Thưc mục chứa sample
    
    
    for file in glob.glob("{}/{}/{}/*.fastq".format(output,"BC","*")):
        #folder contain sample name
        barcode=file.split("/")[-2]
        filename=file.split("/")[-1]
        time=datetime.now().strftime("%H-%M-%S")
        # kiểm tra folder barcode đã tồn tại chưa ở thư mục container
        barcodefolder="{}/{}".format(container,barcode)
        if not os.path.exists(barcodefolder):
            os.makedirs(barcodefolder) # tạo thư mục barcode
        # di chuyển file đến và đổi tên
        filedest="{}/{}_{}.fastq".format(barcodefolder,filename.strip(".fastq"),time)
        shutil.copy(file,filedest)

def main():
    newfast5= sys.argv[1] 
    
    output=sys.argv[2]
    outBC=sys.argv[3]
    guppy_caller(newfast5,output,outBC)



if __name__ == "__main__":
    main()