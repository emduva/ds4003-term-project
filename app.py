# import dependencies
import pandas as pd
import plotly.express as px
#import matplotlib.pyplot as plt
from dash import Dash, dcc, html, Input, Output, callback
from urllib.request import urlopen
import json

# load the CSS stylesheet
stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
# initialize the app
app = Dash(__name__, external_stylesheets=stylesheets)
server = app.server

# Import the data from the web
# Temporary data
df_temp = pd.read_csv("https://raw.githubusercontent.com/plotly/datasets/master/fips-unemp-16.csv",
                   dtype={"fips": str})

# Load the county boundary coordinates
with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
    counties = json.load(response)

# Build the choropleth
fig = px.choropleth(df_temp, 
    geojson=counties, 
    locations='fips', 
    color='unemp',
    color_continuous_scale="Viridis",
    range_color=(0, 12),
    scope="usa",
    labels={'unemp':'unemployment rate'}
)
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

# Improve the legend
fig.update_layout(coloraxis_colorbar=dict(
    thicknessmode="pixels", thickness=10,
    lenmode="pixels", len=150,
    yanchor="top", y=0.8,
    ticks="outside", ticksuffix=" %",
    dtick=5
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

# run app
if __name__ == '__main__':
    app.run_server(debug=True)
