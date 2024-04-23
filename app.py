# import dependencies
import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc
from urllib.request import urlopen
import json
import numpy as np
import datetime
import time

# load the CSS stylesheet
stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css', dbc.themes.MINTY]
# initialize the app
app = Dash(__name__, external_stylesheets=stylesheets)
server = app.server

df = pd.read_csv('data/clean_data.csv', dtype={'CountyFIPS': str, 'StateFIPS': str})

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


def get_state_counts(dataframe):
    counts = dataframe['State'].value_counts().to_frame().reset_index()
    counts = counts.rename(columns={"count": "Number of Accidents"})
    return counts


def get_severity_counts(dataframe):
    counts = dataframe['Severity'].value_counts().to_frame().reset_index()
    counts = counts.rename(columns={"count": "Number of Accidents"})
    return counts


# Load the county boundary coordinates
with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
    counties = json.load(response)

# create html div for the choropleth
map_div = html.Div([
    dcc.Graph(
        id='graph',
        style={'height': '60vh'}
    ),
])

map_selector_div = html.Div([
    dcc.Dropdown(
        id='map-selector',
        options=['States', 'Counties'],
        value='Counties',
        clearable=False,
    )
], style={'font-size': '16px'})

# state filter dropdown
state_dropdown_div = html.Div([
    dcc.Dropdown(
        id='state-dropdown',
        options=df['State'].unique(),
        multi=True,
        value=df['State'].unique(),
    )
], style={'font-size': '18px', 'margin-left': '10px'})

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
], style={'font-size': '18px'})

"""MAP ELEMENTS ABOVE"""

pie_chart_div = html.Div([
    dcc.Graph(
        id='pie-chart',
    )
])

pie_selector = html.Div([
    dcc.Dropdown(
        id='pie-selector',
        options=['Weather', 'DayNight', 'State', 'Severity'],
        multi=False,
        value='Weather',
        clearable=False,
    )
], style={'font-size': '16px'})

scatter_div = html.Div([
    dcc.Graph(
        id='scatter-plot',
    )
])

scatter_x_selector = html.Div([
    dcc.Dropdown(
        id='scatter-x-selector',
        options=['Temperature(F)', 'Visibility(mi)', 'Wind_Speed(mph)', 'Precipitation(in)'],
        value='Temperature(F)',
        clearable=False,
    )
], style={'font-size': '16px'})

scatter_y_selector = html.Div([
    dcc.Dropdown(
        id='scatter-y-selector',
        options=['Severity', 'Distance(mi)'],
        value='Severity',
        clearable=False,
    )
], style={'font-size': '16px'})

buff_height = 20
vert_buff = html.Div(style={'marginBottom': buff_height, 'marginTop': buff_height})

"""APP LAYOUT BELOW"""

info_text = 'Global Options: The following options apply to all three visualizations.'
description_text = '''This dashboard visualizes traffic accidents occurring in the United States from 2016-2023.
    The intended use for this dashboard is to explore how factors like location, time of day, weather,
    and road features can affect the frequency and severity of accidents.'''

app.layout = html.Div([
    html.Div([
        html.Nav(html.Span('US Traffic Accident Data, 2016-2023', style={'margin-left': '10px'}),
                 style={'color': 'white', 'font-size': '45px'},
                 className='navbar-nav-style bg-dark')
    ]),
    html.Div(style={'marginBottom': 10, 'marginTop': 10}),
    html.Div([
        html.Div([
            html.H2(description_text, style={'margin-left': '10px'}),
            html.Div(style={'marginBottom': 10, 'marginTop': 10}),
            html.H3(info_text, style={'margin-left': '10px'}),

            html.Div([
                html.Div([
                    state_dropdown_div,
                ], className='six columns'),
                html.Div([
                    conditions_selector_div,
                ], className='two columns'),
            ], className='row'),
            html.Div(style={'marginBottom': 10, 'marginTop': 10}),
            date_slider_div,
            html.Div([
                html.H3('Number of Accidents by Locality'),
                map_div,
                html.H4('Select Map Division Level:'),
                map_selector_div,
            ], style={'border': '2px solid black', 'padding': '5px', 'margin': '10px'}),
        ], className='eight columns'),
        html.Div([
            html.Div([
                html.H3('Accident Breakdown'),
                pie_chart_div,
                html.H4('Select Breakdown Type:'),
                pie_selector,
            ], style={'border': '2px solid black', 'padding': '5px'}),
            vert_buff,
            html.Div([
                html.H3('Accident Severity Based on Weather Conditions'),
                scatter_div,
                html.H4('Select Axes:'),
                scatter_x_selector,
                scatter_y_selector,
            ], style={'border': '2px solid black', 'padding': '5px'}),
        ], className='four columns'),
    ], className='row'),
], className='row')


@callback(Output(component_id='scatter-plot', component_property='figure'),
          Input(component_id='scatter-x-selector', component_property='value'),
          Input(component_id='scatter-y-selector', component_property='value'),
          Input('state-dropdown', 'value'),
          Input('date-slider', 'value'),
          Input('conditions-selector', 'value'))
def update_scatter_plot(x_selection, y_selection, states, date_range, condition):
    filtered_df = filter_dataframe(condition, date_range, states)
    scatter_fig = px.scatter(filtered_df, x=x_selection, y=y_selection,
                             color='State', color_discrete_sequence=px.colors.sequential.Inferno_r)
    return scatter_fig


@callback(Output(component_id='pie-chart', component_property='figure'),
          Input(component_id='pie-selector', component_property='value'),
          Input('state-dropdown', 'value'),
          Input('date-slider', 'value'),
          Input('conditions-selector', 'value'))
def update_pie_chart(selected_pie, states, date_range, condition):
    filtered_df = filter_dataframe(condition, date_range, states)

    if selected_pie == 'Weather':
        pie_counts = get_weather_counts(filtered_df)
        pie_fig = px.pie(pie_counts, values='Number of Accidents', names='Weather_Condition',
                         color_discrete_sequence=px.colors.sequential.Inferno_r)
        pie_fig.update_traces(textposition='inside')
        pie_fig.update_layout(uniformtext_minsize=12, uniformtext_mode='hide')
        return pie_fig

    elif selected_pie == 'DayNight':
        pie_counts = get_daynight_counts(filtered_df)
        pie_fig = px.pie(pie_counts, values='Number of Accidents', names='Sunrise_Sunset',
                         color_discrete_sequence=px.colors.sequential.Inferno_r)
        pie_fig.update_traces(textposition='inside')
        pie_fig.update_layout(uniformtext_minsize=12, uniformtext_mode='hide')
        return pie_fig

    elif selected_pie == 'State':
        pie_counts = get_state_counts(filtered_df)
        pie_fig = px.pie(pie_counts, values='Number of Accidents', names='State',
                         color_discrete_sequence=px.colors.sequential.Inferno_r)
        pie_fig.update_traces(textposition='inside')
        pie_fig.update_layout(uniformtext_minsize=12, uniformtext_mode='hide')
        return pie_fig

    elif selected_pie == 'Severity':
        pie_counts = get_severity_counts(filtered_df)
        pie_fig = px.pie(pie_counts, values='Number of Accidents', names='Severity',
                         color_discrete_sequence=px.colors.sequential.Inferno_r)
        pie_fig.update_traces(textposition='inside')
        pie_fig.update_layout(uniformtext_minsize=12, uniformtext_mode='hide')
        return pie_fig


@callback(Output('graph', 'figure'),
          Input('state-dropdown', 'value'),
          Input('date-slider', 'value'),
          Input('conditions-selector', 'value'),
          Input('map-selector', 'value'))
def update_map(states, date_range, condition, map_type):
    filtered_df = filter_dataframe(condition, date_range, states)

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

    return filtered_fig


def filter_dataframe(condition, date_range, states):
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
    return filtered_df


"""SERVER SPECIFIC CODE BELOW, DO NOT EDIT"""

# run app
if __name__ == '__main__':
    app.run_server(debug=True)
