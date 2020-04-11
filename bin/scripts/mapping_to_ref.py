#!/usr/bin/env python3

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


parser = argparse.ArgumentParser(description='mapping and produce depth file')
parser.add_argument('-i','--fastq-input', dest='fastq_input')
parser.add_argument('-r','--references-file', dest='ref_input')
parser.add_argument('-x','--prefix-file', dest='prefix', default="sample")
parser.add_argument('-o','--output-path', dest='output_path', default=os.getcwd())
parser.add_argument('--bamcov-exe', dest='bamcov', default="./bamcov/bamcov")
parser.add_argument('--bed-file', dest='bed_file', default=None)
parser.add_argument('--minlen-feature', dest='min_len_feature', default=500)
parser.add_argument('--filter-feature', dest='filter_feature', default="CDS")


args = parser.parse_args()


def RUNCMD (run=True, cmd=None, verbose=True, wait=True, log=None, description=None, id=None,print_cmd=True):
    cmd = " ".join([str(i) for i in cmd])
    if verbose and print_cmd :
        print ("----------------------")
        print ('{0:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now()))
        print (colored('IDSTEP :', 'blue','on_white'), id)
        print (colored('INFOR :', 'blue','on_white'), description)
        print (colored('RUN :', 'blue','on_white'), cmd)
        print (">>>")
        

    if not run:
        return False

    start = time.time()
    procc = Popen(cmd, shell=True,stdout=PIPE)
    print (colored('OUTPUTZONE:', 'blue','on_white'))
    while True:
        output = procc.stdout.readline()
        if procc.poll() is not None:

            if verbose:
                elapsed = (time.time() - start)
                print (colored('Exit Code:', 'blue','on_white'),procc.returncode)
                print (colored('ELAPSED: ', 'blue','on_white'), elapsed)
                print ("----------------------")
                if procc.returncode > 0:
                    exit()
            break
        if output:
            print (colored(output.strip(), 'green'))
    return procc.poll()


#mapping to ref using minimap2
ref_name = args.ref_input. split("/")[-1].replace(".fasta", "")
cmd =["minimap2 -ax map-ont",
        args.ref_input,
        args.fastq_input,
        "|samtools view -bS -q 5 >",
        "{}/{}_map_{}.bam".format(args.output_path, ref_name,args.prefix)
]

RUNCMD(cmd=cmd, description="mapping to ref using minimap2", id="minimap2", run=False)
# get depth file
cmd = ["bedtools genomecov -d",
         "-ibam", "{}/{}_map_{}.bam".format(args.output_path, ref_name,args.prefix) ,
         """| awk -F"\\t" '{print $2"\\t"$3}' >""",
         "{}/{}_map_{}.depthstast".format(args.output_path, ref_name,args.prefix)
]

RUNCMD(cmd=cmd, description="get genome coverage", id="genomecov", run=False)

# run bamcov statics
cmd = [args.bamcov,
        "-H", "{}/{}_map_{}.bam".format(args.output_path, ref_name,args.prefix),
        ">", "{}/{}_map_{}.bamcovstast".format(args.output_path, ref_name,args.prefix)
]

RUNCMD(cmd=cmd, description="get genome coverage stats", id="bamcov", run=False)

if args.bed_file is not None:
    ouput_region = "{}/{}_map_{}.regionstats".format(args.output_path, ref_name,args.prefix)
    os.remove(ouput_region)
    with open (args.bed_file, "r") as f:
        for line in f:
            if line.startswith("#"):
                continue
            lineObj  = line.strip("\n").split("\t")
            chrom = lineObj[0]
            start = lineObj[1]
            stop  = lineObj[2]
            if int(start) > int(stop):
                stop,start = [start, stop]

            len  = abs(int(lineObj[3]))
            feature = lineObj[4]
            product = lineObj[5]

            if len < args.min_len_feature or  feature not in args.filter_feature.split(","):
                continue
            bed = "{}:{}-{}".format(chrom, start,stop)
            
            cmd = ["bamcov=$(",args.bamcov,
                        "-H", "{}/{}_map_{}.bam".format(args.output_path, ref_name,args.prefix),
                        "-r", bed,
                        ");printf $bamcov\\t{}\\t{}\\t{}\n >> {}".format(len,feature,product,ouput_region)
                ]

            RUNCMD(cmd=cmd, verbose=False)

