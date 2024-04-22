# import dependencies
import pandas as pd
import plotly.express as px
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

df = pd.read_csv('clean_data.csv', dtype={'CountyFIPS': str, 'StateFIPS': str})

"""INITIALIZATION CODE ABOVE, DO NOT EDIT"""


def get_counts_by_county(dataframe):
    counts = dataframe['CountyFIPS'].value_counts().to_frame().reset_index()
    counts = counts.rename(columns={"count": "Number of Accidents"})
    return counts


def get_counts_by_state(dataframe):
    counts = dataframe['State'].value_counts().to_frame().reset_index()
    counts = counts.rename(columns={"count": "Number of Accidents"})
    return counts


def get_weather_counts(dataframe):
    counts = dataframe['Weather_Condition'].value_counts().to_frame().reset_index()
    counts = counts.rename(columns={"count": "Number of Accidents"})
    return counts


def get_daynight_counts(dataframe):
    counts = dataframe['Sunrise_Sunset'].value_counts().to_frame().reset_index()
    counts = counts.rename(columns={"count": "Number of Accidents"})
    return counts


# Load the county boundary coordinates
with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
    counties = json.load(response)

# create html div for the choropleth
graph_div = html.Div([
    dcc.Graph(
        id='graph',
        style={'height': '60vh'}
    ),
])

map_selector_div = html.Div([
    dcc.Dropdown(
        id='map-selector',
        options=['States', 'Counties'],
        value='Counties'
    )
])

# state filter dropdown
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

conditions_selector_div = html.Div([
    dcc.RadioItems(
        id='conditions-selector',
        options=['Any', 'Amenity', 'Bump', 'Crossing', 'Give_Way', 'Junction',
                 'No_Exit', 'Railway', 'Roundabout', 'Station', 'Stop', 'Traffic_Signal'],
        value='Any',
        inline=True,
    )
])

"""MAP ELEMENTS ABOVE"""

pie_chart_div = html.Div([
    dcc.Graph(
        id='pie-chart',
    )
])

pie_selector = html.Div([
    dcc.Dropdown(
        id='pie-selector',
        options=['Weather', 'DayNight'],
        multi=False,
        value='Weather'
    )
])

scatter_div = html.Div([
    dcc.Graph(
        id='scatter-plot',
    )
])

scatter_x_selector = html.Div([
    dcc.Dropdown(
        id='scatter-x-selector',
        options=['Temperature(F)', 'Visibility(mi)', 'Wind_Speed(mph)', 'Precipitation(in)'],
        value='Temperature(F)'
    )
])

scatter_y_selector = html.Div([
    dcc.Dropdown(
        id='scatter-y-selector',
        options=['Severity', 'Distance(mi)'],
        value='Severity'
    )
])

buff_height = 20
vert_buff = html.Div(style={'marginBottom': buff_height, 'marginTop': buff_height})

layout = html.Div([
    html.Div([
        html.Div([
            html.Div([
                html.Div([
                    state_dropdown_div,
                ], className='six columns'),
                html.Div([
                    conditions_selector_div,
                ], className='two columns'),
            ], className='row'),
            date_slider_div,
            html.Div([
                graph_div,
                map_selector_div,
            ], style={'border': '2px solid black', 'padding': '5px'}),
        ], className='eight columns'),
        html.Div([
            html.Div([
                pie_chart_div,
                pie_selector,
            ], style={'border': '2px solid black', 'padding': '5px'}),
            vert_buff,
            html.Div([
                scatter_div,
                scatter_x_selector,
                scatter_y_selector,
            ], style={'border': '2px solid black', 'padding': '5px'}),
        ], className='four columns'),
    ], className='row'),
], className='row')

"""
app.layout = html.Div([
    graph_div,
    state_dropdown_div,
    date_slider_div,
    conditions_selector_div,
    pie_chart_div,
    pie_selector,
    scatter_div,
    scatter_x_selector,
    scatter_y_selector
], className="row")
"""
app.layout = layout


@callback(Output(component_id='scatter-plot', component_property='figure'),
          Input(component_id='scatter-x-selector', component_property='value'),
          Input(component_id='scatter-y-selector', component_property='value'))
def update_scatter_plot(x_selection, y_selection):
    scatter_fig = px.scatter(df.sample(100000), x=x_selection, y=y_selection,
                             color='State', color_discrete_sequence=px.colors.sequential.Inferno_r)
    return scatter_fig


@callback(Output(component_id='pie-chart', component_property='figure'),
          Input(component_id='pie-selector', component_property='value'))
def update_pie_chart(selected_pie):
    if selected_pie == 'Weather':
        pie_counts = get_weather_counts(df)
        pie_fig = px.pie(pie_counts, values='Number of Accidents', names='Weather_Condition',
                         color_discrete_sequence=px.colors.sequential.Inferno_r)
        pie_fig.update_traces(textposition='inside')
        pie_fig.update_layout(uniformtext_minsize=12, uniformtext_mode='hide')
        return pie_fig

    elif selected_pie == 'DayNight':
        pie_counts = get_daynight_counts(df)
        pie_fig = px.pie(pie_counts, values='Number of Accidents', names='Sunrise_Sunset',
                         color_discrete_sequence=px.colors.sequential.Inferno_r)
        pie_fig.update_traces(textposition='inside')
        pie_fig.update_layout(uniformtext_minsize=12, uniformtext_mode='hide')
        return pie_fig


@callback(Output('graph', 'figure'),
          Input('state-dropdown', 'value'),
          Input('date-slider', 'value'),
          Input('conditions-selector', 'value'),
          Input('map-selector', 'value'))
def update_figure(states, date_range, condition, map_type):
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

    if not condition == 'Any':
        filtered_df = filtered_df[filtered_df[condition]]

    if map_type == 'Counties':
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

    else:
        filtered_df_counts = get_counts_by_state(filtered_df)
        filtered_fig = px.choropleth(filtered_df_counts,
                                     locationmode='USA-states',
                                     locations='State',
                                     color=np.log10(filtered_df_counts['Number of Accidents']),
                                     color_continuous_scale="inferno",
                                     scope="usa",
                                     hover_data={'Number of Accidents': True, 'State': False},
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
