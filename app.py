# import dependencies
import pandas as pd
import plotly.express as px
#import matplotlib.pyplot as plt
from dash import Dash, dcc, html, Input, Output, callback
from urllib.request import urlopen
import json
import numpy as np

# load the CSS stylesheet
stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
# initialize the app
app = Dash(__name__, external_stylesheets=stylesheets)
server = app.server


"""INITIALIZATION CODE ABOVE, DO NOT EDIT"""


df = pd.read_csv('data_final.csv', dtype={'CountyFIPS':str, 'StateFIPS':str})

df_counts = df['CountyFIPS'].value_counts().to_frame().reset_index()
df_counts = df_counts.rename(columns={"count":"Number of Accidents"})


# Load the county boundary coordinates
with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
    counties = json.load(response)

# Build the choropleth
fig = px.choropleth(df_counts,
    geojson=counties,
    locations='CountyFIPS',
    color=np.log10(df_counts['Number of Accidents']),
    color_continuous_scale="inferno",
    scope="usa",
    hover_data={'Number of Accidents':True, 'CountyFIPS':False},
)
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

# Improve the legend
fig.update_layout(coloraxis_colorbar=dict(
    thicknessmode="pixels", thickness=20,
    lenmode="pixels", len=300,
    yanchor="top", y=0.8,
    ticks="outside",
    dtick=5,
    title="Number of Accidents",
    tickvals=[1,2,3,4,5],
    ticktext=["10","100","1000","10k","100k"],
))

# create html div for the graph
graph_div = html.Div([
    dcc.Graph(
        figure=fig,
        id='graph'
    ),
])

app.layout = html.Div([
    graph_div
], className="row")

"""SERVER SPECIFIC CODE BELOW, DO NOT EDIT"""


# run app
if __name__ == '__main__':
    app.run_server(debug=True)
