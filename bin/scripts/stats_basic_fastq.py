import sys, os
from  subprocess import Popen, PIPE
import random
import time
import datetime
import argparse
import glob
from shutil import copyfile,rmtree
from termcolor import colored
import pandas as pd
from jinja2 import Template


parser = argparse.ArgumentParser(description='count read, len histogram')
parser.add_argument('-i','--fastq-input', dest='fastq_input')
parser.add_argument('-b','--bin-len', dest='bin_len', default="500,1000,5000,10000,20000,40000")
parser.add_argument('-o','--out-path', dest='output_path', default=os.getcwd())
parser.add_argument('-x','--prefix', dest='prefix', default="sample")

args = parser.parse_args()

bin_len = [int(i) for i in args.bin_len.split(",")]
bin_his = {}
for i in bin_len:
    bin_his[i] = 0
output_file = "{}/{}.basisstats".format(args.output_path,args.prefix)
with open (args.fastq_input, "r") as f:
    read_count = 0
    sum_len = 0
    next_lineis_seq = False
    for line in f:
        line = line.strip()
        if line.startswith("@"):
            next_lineis_seq = True
            read_count +=1
            continue
        if next_lineis_seq == True:
            len_seq= len(line)
            sum_len = sum_len + len_seq
            next_lineis_seq = False
            
            for i in bin_len:
                if len_seq > i:
                    seq_is_his = i
            bin_his[seq_is_his] =  bin_his[seq_is_his] +1
out=open (output_file, "w")
print ("Totalread\t{}".format(read_count), file=out)
print ("Totalbases\t{}".format(sum_len), file=out)
print ("MeanLength\t{}".format(round(sum_len/read_count),0), file=out)
for key, value in bin_his.items():
    print ("Hist\t{}\t{}".format(key,value), file=out)

out.close()
