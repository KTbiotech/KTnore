#!/bin/env python3
import plotly.graph_objects as go
import plotly.io as pio


overview={ 'BACTERIA':189523, 'EUKARYOTA': 52369, 'VIRUSES': 526, 'ARCHAEA': 253}

# Use `hole` to create a donut-like pie chart
fig = go.Figure(data=[go.Pie(labels=list(overview.keys()), values=list(overview.values()), hole=.7)])
#fig.update_layout(legend=dict(x=0, y=0))


#
pio.write_html(fig, file='demo.html', auto_open=True)
