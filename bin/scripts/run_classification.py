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
import pandas as pd


parser = argparse.ArgumentParser(description='taxonomic classifications')
parser.add_argument('-i','--input-fastq',dest="input_fastq")
parser.add_argument('-m','--summary-file',dest="summary_file")
parser.add_argument('-idx','--index-cen',dest="index_cen")
parser.add_argument('-t','-threads',dest="threads", default=2)
parser.add_argument('-x','--prefix',dest="prefix", default="sample")
parser.add_argument('-o','--output-path',dest="output_path", default=os.getcwd())


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

# run centrifuge
cmd = ["centrifuge", 
"-x", args.index_cen,
"--threads",args.threads,
"-S", "{}/{}.cenout".format(args.output_path,args.prefix),
"--report-file", "{}/{}.censummary".format(args.output_path,args.prefix),
"-q",args.input_fastq
]

RUNCMD(cmd=cmd, description="run centrifuge", id="centriguge", run=False)

process_meta = True
if process_meta:
    print ("processing metatadata")
    # filter *cenout by mutiple conditions
    #header : readID	seqID	taxID	score	2ndBestScore	hitLength	queryLength	numMatches
    cutoff_score = 0
    cutoff_hitLength = 0
    meta_read_infor = {} ## dict contain metada from summary.txt and taxonomy

    cenout = "{}/{}.cenout".format(args.output_path,args.prefix)
    cenfilter = "{}/{}.cenfilter".format(args.output_path,args.prefix)

    with open (cenout, "r") as out, open (cenfilter, "w") as outfilter:
        for line in out:
            line = line.strip("\n")
            if line.startswith("readID"):   
                filer_line = line
                print (filer_line, file =outfilter)
                continue
            lineObj =  line.split("\t")
            readID, seqID, taxID,score, BestScore2nd,hitLength,queryLength,numMatches = lineObj
            if int(score) < cutoff_score or int(hitLength) < cutoff_hitLength:
                seqID = "unclassified"
                score, taxID, BestScore2nd,hitLength = 0,0,0,0 ### reset value

            meta_read_infor [readID] = {
                "readID": readID,
                "seqID": seqID,
                "taxID" : taxID,
                "score" : score,
                "BestScore2nd" : BestScore2nd,
                "hitLength" : hitLength,
                "queryLength" : queryLength,
                "numMatches" : numMatches

            }

            filer_line = "\t".join(str(i) for i in [readID, seqID, taxID,score, BestScore2nd,hitLength,queryLength,numMatches])
            print (filer_line, file=outfilter)

    with open (args.summary_file, "r") as meta:
        for line in meta:
            line = line.strip("\n")
            if line.startswith("filename"):
                continue
            lineObj = line.split("\t")
            read_id = lineObj [1]
            
            if read_id in meta_read_infor:
                #print (read_id)
                # filename	read_id	run_id	channel	start_time	duration	num_events	passes_filtering	template_start	num_events_template	template_duration	sequence_length_template	mean_qscore_template	strand_score_template	median_template	mad_template
                filename,read_id,run_id,channel,start_time,duration,num_events,passes_filtering,template_start,num_events_template,template_duration,sequence_length_template,mean_qscore_template,strand_score_template,median_template,mad_template = lineObj
                meta_read_infor [read_id]["batch"] = filename.split("_")[-1].replace(".fast5","")
                meta_read_infor [read_id]["start_time"] = start_time
                meta_read_infor [read_id]["duration"] = duration
                meta_read_infor [read_id]["mean_qscore_template"] = mean_qscore_template
    print ("Ending process metatadata")  
#print (meta_read_infor)
## covert cenfilter to kreport
cmd = ["centrifuge-kreport", 
"-x", args.index_cen,
"{}/{}.cenfilter".format(args.output_path,args.prefix),
">", "{}/{}.kreport".format(args.output_path,args.prefix)
]
RUNCMD(cmd=cmd, description="centrifuge-kreport", id="centrifuge-kreport", run=False)


## add taxonomy to meta_read_infor dict

with open ("{}/{}.kreport".format(args.output_path,args.prefix),"r") as kreport:
        taxid_dict = {}
        for line in kreport:
            line = line.strip("\n")
            if line.startswith("#"):
                continue
            lineObj = line.split("\t")
            percent, readcount, child_read, rank, taxID, nameTaxonomy = lineObj
            # add taxonomy name
            taxid_dict[taxID] = {
                "percent":percent,
                "readcount": readcount,
                "child_read": child_read,
                "rank":rank,
                "nameTaxonomy": nameTaxonomy.strip()}


for read_id in list(meta_read_infor.keys()):
    taxID = meta_read_infor[read_id]["taxID"]
    if taxID not in taxid_dict:
        meta_read_infor[read_id]["taxID"] = 0 ## covert to 0
        meta_read_infor[read_id]["rank"] = "-"
        meta_read_infor[read_id]["nameTaxonomy"] = "unclassified"
        continue
    meta_read_infor[read_id]["rank"] = taxid_dict[taxID]["rank"]
    meta_read_infor[read_id]["nameTaxonomy"] = taxid_dict[taxID]["nameTaxonomy"]

print ("Ending process metatadata with taxonomy")
print (meta_read_infor)


def render_plot1_html(meta_read_infor,taxid_dict,html_template ):
    """ render html taxonomy """
    print ("render html")

    unclassifed_read = taxid_dict["0"]["readcount"]
    classifed_read = taxid_dict["1"]["readcount"]


    with open(html_template, "r") as file_:
        template = Template(file_.read())
    # render section plot
    render = template.render(
        xdata = get_depth_onfile(file1, step_size)["pos"],
        y1data =  get_depth_onfile(file1,step_size)["depth"],
        y2data =  get_depth_onfile(file2,step_size)["depth"],
        data_pool = data_label,
        y1label = "'{}'".format(data_label[0]),
        y2label = "'{}'".format(data_label[1]),
        stats_data = data_stats_html
        )





    # write render to new files
    output = open (args.html_output.replace(".html", "") + ".html", "w")
    print (render, file = output )
    print (" Render completed ")

        



