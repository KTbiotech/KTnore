#!/usr/bin/env python3

import sys

USAGE='my_script <CENTRIFUGEreport(.tsv)> <CENTRIFUGEdetail (.tsv)> <GUPPYsummary (.tsv)> <seqcount_cutoff (int)> <output(html)>'

if len(sys.argv)< 6:
	print ("USAGE:  " + USAGE)
	exit()
else:
	CENTRIFUGEreport=sys.argv[1]
	CENTRIFUGE=sys.argv[2]
	GUPPY=sys.argv[3]
	cutoff=sys.argv[4]
	html=sys.argv[5]
	sample=CENTRIFUGEreport.split("/")[-1].split(".")[0]




#

import pandas as pd
import plotly.graph_objects as go
import math
from plotly.tools import FigureFactory as FF

import numpy as np

import scipy

#

dfCENTRIFUGEreport=pd.read_csv(CENTRIFUGEreport,sep='\t')
dfCENTRIFUGE=pd.read_csv(CENTRIFUGE,sep='\t')
dfGUPPY=pd.read_csv(GUPPY,sep='\t')

#rename
dfGUPPY.rename(columns={'read_id': 'readID'},inplace=True)
# merge


df=dfCENTRIFUGE.merge(dfCENTRIFUGEreport, on='taxID', how='outer')


df=df.merge(dfGUPPY,on='readID',how='inner')
#sort by template_start

df=df.sort_values(by='template_start', ascending=True)

'''
df.columns
Index(['readID', 'seqID', 'taxID', 'score', '2ndBestScore', 'hitLength',
       'queryLength', 'numMatches', 'name', 'taxRank', 'genomeSize',
       'numReads', 'numUniqueReads', 'abundance', 'filename', 'run_id',
       'channel', 'start_time', 'duration', 'num_events', 'passes_filtering',
       'template_start', 'num_events_template', 'template_duration',
       'sequence_length_template', 'mean_qscore_template',
       'strand_score_template', 'median_template', 'mad_template'],
      dtype='object')

'''

#speice by time
df=df.query('taxID != 0 and taxRank == "species"')
df=df.sort_values(by='template_start', ascending=True)

df.reset_index(inplace=True)
#
taxidpools,taxidpoolsuniq=[],[]
countpools=dict()
i=0
count=1
for taxID in df['taxID']:
	taxidpools.append(taxID)
	if taxID not in taxidpoolsuniq and taxidpools.count(taxID) > int(cutoff) :
		taxidpoolsuniq.append(taxID)
		count=count+1
	time=round(df['template_start'][i]/60,0)
	countpools[time]=count
	i=i+1

#build chart

time=list(countpools.keys())
count=list(countpools.values())



def countBytime(df, taxID):
	i=0
	count=0
	countpools=dict()
	for tid in df['taxID']:
		if tid==taxID:
			count=count+1
			time=round(df['template_start'][i]/60,0)
			countpools[time]=count
			name=df['name'][i]
		i=i+1

	return [name,countpools]
#top 10 loai dau tien
df_top=dfCENTRIFUGEreport.query('taxRank == "species"').sort_values(by='numReads', ascending=False)
df_top.reset_index(inplace=True)

species_pools=list()
species_lens=list()
for i in df_top.loc[:12,'taxID']:
	if int(i) != 9606 and int(i) != 32630:
	
		species_pools.append(countBytime(df,i))

		name=df.query('taxID =='+str(i)).reset_index()['name'][0]
		
		
		len_lst=df.query('taxID =='+str(i)).reset_index()['sequence_length_template'].values.tolist()
		species_lens.append([name,len_lst])

#chart
fig=go.Figure()

fig.add_trace(go.Scatter(x=time, y=count, name='Species count',line=dict(color='royalblue', width=4)))

fig.update_layout(
	title='Rarefaction Curve: Sample ' + sample +", cutoff: " + cutoff, 
	xaxis_title = "Time(minutes)", 
	yaxis_title="Species count",
	font=dict(
        family="Courier New, monospace",
        size=18,
        color="#7f7f7f"
    ))


fig.write_html(html+'-1.html', auto_open=False)

#chart
fig2=go.Figure()
color_lst=[
    '#1f77b4',  # muted blue
    '#ff7f0e',  # safety orange
    '#2ca02c',  # cooked asparagus green
    '#d62728',  # brick red
    '#9467bd',  # muted purple
    '#8c564b',  # chestnut brown
    '#e377c2',  # raspberry yogurt pink
    '#7f7f7f',  # middle gray
    '#bcbd22',  # curry yellow-green
    '#17becf',   # blue-teal
    '#FF00FF',
    '#7FFFD4'
]
color=0
for i in species_pools:
	
	
	fig2.add_trace(go.Scatter(x=list(i[1].keys()),y=list(i[1].values()),name=i[0],line=dict(color=color_lst[color], width=4)))
	color=color+1

fig2.update_layout(
	title='Rarefaction Curve: Sample ' + sample,
	xaxis_title = "Time(minutes)", 
	yaxis_title="reads",
	font=dict(
        family="Courier New, monospace",
        size=18,
        color="#7f7f7f"
    ))


fig2.write_html(html+'-2.html', auto_open=False)

#blot length

fig3=go.Figure()
color_lst=[
    '#1f77b4',  # muted blue
    '#ff7f0e',  # safety orange
    '#2ca02c',  # cooked asparagus green
    '#d62728',  # brick red
    '#9467bd',  # muted purple
    '#8c564b',  # chestnut brown
    '#e377c2',  # raspberry yogurt pink
    '#7f7f7f',  # middle gray
    '#bcbd22',  # curry yellow-green
    '#17becf',   # blue-teal
    '#FF00FF',
    '#7FFFD4'
]
color=0
for i in species_lens:
	fig3.add_trace(go.Box(y=i[1],name = i[0],boxpoints='all',jitter=0.3,marker = dict(color = color_lst[color])))
	color=color+1
	
fig3.update_layout(yaxis=dict(title='Length',zeroline=False))
    



fig3.write_html(html+'-3.html', auto_open=False)



















