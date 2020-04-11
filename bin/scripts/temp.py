#!/usr/bin/env python3

#Last update: 10/11/2019
#Author: H-Van-Phuc
#
#

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
import plotly.graph_objects as go
import plotly.io as pio
from Bio import SeqIO
import pandas as pd

dfkreport=pd.read_csv('/media/kt02/DATA/Phuc_folders/Dev/py/j1/S1/t1/4.Taxonomy/4.1.Centrifuge/BC08.cf.kraken.tsv', sep="\t", header=None)
dfkreport.columns=['Percentage','taxonRead', 'cladeRead','Rank','taxID','Name']
overview, summary=dict(), dict()
def taxonRead(df, taxID):
    '''
    '''
    taxID=int(taxID)
    query=df[df['taxID']== taxID]
    taxonRead=0 if len(query)==0 else query.iloc[0]['taxonRead']
    taxonName='N/A' if len(query)==0 else query.iloc[0]['Name']
    return [taxID,taxonName,taxonRead]



overview['BACTERIA']=taxonRead(dfkreport,"2")
overview['EUKARYOTA']=taxonRead(dfkreport,"2759")
overview['VIRUSES']=taxonRead(dfkreport,"10239")
overview['ARCHAEA']=taxonRead(dfkreport,"2157")
summary["read-analysed"]=taxonRead(dfkreport,"1")
summary["read-unclassified"]=taxonRead(dfkreport,"0")
summary["read-classified"]=summary["read-analysed"][-1] -  summary["read-unclassified"][-1]



f='temp_sum.txt'
with open(f,"w") as f:
    f.write("var overview = {} ;\n".format(overview))
    f.write("var summary = {} ;\n".format(summary))
