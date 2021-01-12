# This script should generate a graph based on the .csv file recording when motion started/ended
# Since motion detection starts but doesn't stop, this script doesn't work :)

from motion_detector import df
from bokeh.plotting import figure, show, output_file
from bokeh.models import HoverTool, ColumnDataSource

df["Start_string"]=df["Start"].dt.strftime("%Y-%m-%d %H:%M:%S")
df["End_string"]=df["End"].dt.strftime("%Y-%m-%d %H:%M:%S")

cds=ColumnDataSource(df)

p=figure(x_axis_type='datetime', height=100, widht=500, sizing_mode="stretch_both", title="Motion Graph")
p.yaxis.minor_tick_line_color=None    # makes the scale subunits on the y axis disappear
p.ygrid[0].ticker.desire_num_ticks=1  # makes the horizontal gridlines disappear


hover=HoverTool(tooltips=[("Start","@Start_string"),("End","@End_string")])
p.add_tools(hover)

q=p.quad(left="Start",right="End",bottom=0,top=1,color="green",source=cds)

output_file("Graph.html")
show(p)
