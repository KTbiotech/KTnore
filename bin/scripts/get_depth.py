#!/usr/bin/env python3

import argparse
import random
from jinja2 import Template
import glob

parser = argparse.ArgumentParser(description='get depth file and return html')
parser.add_argument('-i','--depth-files',dest="depth_files", nargs='+',default=None)
parser.add_argument('-s','--step_size',dest="step_size",default=500)
parser.add_argument('-t','--depth-html-template',dest="html_template",default=None)
parser.add_argument('-a','--synx_stats-file',dest="synx_stats_file",default="*.bamcovstast")
parser.add_argument('-b','--bed-regions-file',dest="bed_file",default="None")
parser.add_argument('-o','--depth-html-output',dest="html_output",default="render_out")
args = parser.parse_args()

####

def random_depth(max_n):
    '''
    only use for test functions
    '''
    with open ("raw_depth.tsv", "w") as f:
        pos, depth = [], []
        for i in range (max_n):
            pos_i = i
            depth_i = random.choice([i for i in range (0,10000)])
            pos.append(pos_i)
            depth.append(depth_i)
            print("{}\t{}".format(pos_i, depth_i), file=f)
                
        return {"pos": pos, "depth": depth}
#random_depth(4000)
# open template
with open(args.html_template, "r") as file_:
    template = Template(file_.read())

data_label = ["now", "last"]

"""
# render section
render = template.render(
    xdata = random_depth(100)["pos"],
    y1data = random_depth(100)["depth"],
    y2data = random_depth(100)["depth"],
    data_pool = data_label,
    y1label = "'{}'".format(data_label[0]),
    y2label = "'{}'".format(data_label[1])
    )
"""

def get_depth_onfile(file,stepsize):

    def mean(lst):
        sum = 0
        for i in lst:
            sum = sum + int(i)
        
        return round(sum/len(lst), 0)

    with open (file, "r") as f:
        i = 0 # line number
        pos_temp = []
        depth_temp = []
        pos_pool = []
        depth_pool = []
        step_count = 1
        for line in f:
            if line.startswith("#"):
                continue
            i+=1
            pos = int(line.split("\t")[0])
            depth = int(line.split("\t")[1])
            if i == 1:
                pos_pool.append(pos)
                depth_pool.append(depth)
            pos_temp.append(pos)
            depth_temp.append(depth)
            if i / stepsize >= step_count:
                pos_pool.append(mean(pos_temp))
                depth_pool.append(mean(depth_temp))
                pos_temp = []
                depth_temp = []
                step_count +=1

        pos_pool.append(pos)
        depth_pool.append(depth)

    return {"file": file,
            "pos": pos_pool,
            "depth": depth_pool}
## get stats_table
def get_stats_table(syntax_stats_files):

    timepoint = []
    rname = []
    numread = []
    startpos = []
    endpos = []
    covbase = []
    coverage = []
    meanbaseq = []
    meanmapq = []
   
    stats_files = glob.glob(syntax_stats_files)
    assert stats_files != []

    for file in stats_files:
        file_name=file.split("/")[-1]
        with open (file, "r") as f:
            for line in f:
                line = line.strip("\n")
                lineObj = line.split("\t")
                timepoint.append(file_name.split(".")[-1])
                rname.append(lineObj[0])
                numread.append(lineObj[1])
                startpos.append(lineObj[2])
                endpos.append(lineObj[3])
                covbase.append(lineObj[4])
                coverage.append(lineObj[5])
                meanbaseq.append(lineObj[6])
                meanmapq.append(lineObj[7])

    return {
        "timepoint": timepoint,
        "rname" : rname,
        "numread" : numread,
        "startpos" : startpos,
        "endpos" :endpos,
        "covbase" : covbase,
        "coverage" : coverage,
        "meanbaseq" :meanbaseq,
        "meanmapq" :meanmapq
        }
stats_table = get_stats_table(args.synx_stats_file) 
data_stats_html = ""
for i in range (len (stats_table["timepoint"])):
   
    col_data = \
    """id: "{}",timepoint: "{}",rname :"{}",numread: "{}",startpos: "{}",endpos: "{}", covbase: "{}", coverage : "{}", meanbaseq: "{}", meanmapq: "{}" """.format(
    i +1,
    stats_table["timepoint"][i],
    stats_table["rname"][i],
    stats_table["numread"][i],
    stats_table["startpos"][i],
    stats_table["endpos"][i],
    stats_table["covbase"][i],
    stats_table["coverage"][i],
    stats_table["meanbaseq"][i],
    stats_table["meanmapq"][i]
    )
    data_stats_html = data_stats_html + "{" + col_data + "},"

data_stats_html = data_stats_html.rstrip(",")


file1, file2 = args.depth_files
step_size = int(args.step_size)

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

