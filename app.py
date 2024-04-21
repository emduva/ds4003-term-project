# import dependencies
import pandas as pd
import plotly.express as px
#import matplotlib.pyplot as plt
from dash import Dash, dcc, html, Input, Output, callback
from urllib.request import urlopen
import json
import numpy as np
import datetime
import time

# load the CSS stylesheet
stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
# initialize the app
app = Dash(__name__, external_stylesheets=stylesheets)
server = app.server


"""INITIALIZATION CODE ABOVE, DO NOT EDIT"""

df = pd.read_csv('data_final_2.csv', dtype={'CountyFIPS':str, 'StateFIPS':str})


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
        options=df['State'].unique(),
        multi=True,
        value=df['State'].unique(),
    )
])

date_labels_dict = dict()
for i in range(24):
    num = i * 4
    month = str((num % 12) + 1)
    year_index = num // 12
    year = str(2016 + year_index)
    label = f'{year}-{month}'
    date_labels_dict.update({num: label})


date_slider_div = html.Div([
    dcc.RangeSlider(
        id='date-slider',
        min=0,
        max=95,
        step=2,
        value=[0, 95],
        allowCross=False,
        marks=date_labels_dict,

    )
])

app.layout = html.Div([
    graph_div,
    state_dropdown_div,
    date_slider_div,
], className="row")


@callback(Output('graph', 'figure'),
          Input('state-dropdown', 'value'),
          Input('date-slider', 'value'))
def update_figure(states, date_range):
    filtered_df = df[df['State'].isin(states)]

    min_date_index = date_range[0]
    max_date_index = date_range[1]

    min_month = (min_date_index % 12) + 1
    min_year_index = min_date_index // 12
    min_year = 2016 + min_year_index

    max_month = (max_date_index % 12) + 1
    max_year_index = max_date_index // 12
    max_year = 2016 + max_year_index

    min_timestamp = int(time.mktime(datetime.datetime(min_year, min_month, 1).timetuple()))
    max_timestamp = int(time.mktime(datetime.datetime(max_year, max_month, 1).timetuple()))

    filtered_df = filtered_df[filtered_df['timestamp'] >= min_timestamp]
    filtered_df = filtered_df[filtered_df['timestamp'] <= max_timestamp]

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
    print("end of callback")
    return filtered_fig


"""SERVER SPECIFIC CODE BELOW, DO NOT EDIT"""


# run app
if __name__ == '__main__':
    app.run_server(debug=True)
