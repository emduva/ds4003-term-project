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


def get_counts_by_county(dataframe):
    counts = dataframe['CountyFIPS'].value_counts().to_frame().reset_index()
    counts = counts.rename(columns={"count":"Number of Accidents"})
    return counts


# Load the county boundary coordinates
with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
    counties = json.load(response)

# create html div for the graph
graph_div = html.Div([
    dcc.Graph(
        id='graph'
    ),
])

state_dropdown_div = html.Div([
    dcc.Dropdown(
        id='state-dropdown',
        options = df['State'].unique(),
        multi=True,
        value=["VA", "NY", "TX", "CA"],
    )
])

app.layout = html.Div([
    graph_div,
    state_dropdown_div
], className="row")


@callback(Output('graph', 'figure'),
          Input('state-dropdown', 'value'))
def update_figure(states):
    print("Callback activated")
    print(type(states))
    print(states)
    filtered_df = df[df['State'].isin(states)]

    filtered_df_counts = get_counts_by_county(filtered_df)
    filtered_fig = px.choropleth(filtered_df_counts,
                                 geojson=counties,
                                 locations='CountyFIPS',
                                 color=np.log10(filtered_df_counts['Number of Accidents']),
                                 color_continuous_scale="inferno",
                                 scope="usa",
                                 hover_data={'Number of Accidents': True, 'CountyFIPS': False},
                                 )
    filtered_fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

    # Improve the legend
    filtered_fig.update_layout(coloraxis_colorbar=dict(
        thicknessmode="pixels", thickness=20,
        lenmode="pixels", len=300,
        yanchor="top", y=0.8,
        ticks="outside",
        dtick=5,
        title="Number of Accidents",
        tickvals=[1, 2, 3, 4, 5],
        ticktext=["10", "100", "1000", "10k", "100k"],
    ))
    print("Got to end of callback")
    return filtered_fig


"""SERVER SPECIFIC CODE BELOW, DO NOT EDIT"""


# run app
if __name__ == '__main__':
    app.run_server(debug=True)
