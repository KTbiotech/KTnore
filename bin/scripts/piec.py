#!/bin/env python3
import plotly.graph_objects as go
import plotly.io as pio
import sys
import ast



if len(sys.argv) < 3:
    print ("piec.py <file> <out>")
    exit()
f=sys.argv[1]
out=sys.argv[2]

with open (f, "r") as file:
    for line in file:
        overview=line.strip('var overview= ')[:-2]
        overview=ast.literal_eval(overview) ## to dict
        name=list(overview.keys())
        
        value=[i[2] for i in list(overview.values()) ]
        
        break
# Use `hole` to create a donut-like pie chart
fig = go.Figure(data=[go.Pie(labels=name, values=value, hole=.7)])
#fig.update_layout(legend=dict(x=0, y=0))

#
pio.write_html(fig, file=out, auto_open=True)
