# -*- coding: utf-8 -*-
"""
Created on Mon Nov 14 16:47:29 2022

@author: Elliot
"""

import numpy as np
import pandas as pd
#import matplotlib.pyplot as plt
#import seaborn as sns
import dash
import dash_core_components as dcc
import dash_html_components as html
import os
from dash.dependencies import Output, Input
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go

#%run ./src/build_dataset.py

# Find most recent Generated dataset in the folder `./datasets/Generated`
most_recent_date = 0
most_recent_fp = ''

with os.scandir(os.path.join('.','datasets','Generated')) as directory:
    for f in directory:
        if (f.stat().st_ctime > most_recent_date) and ('US_' in f.name):
            most_recent_fp = f.path
            most_recent_date = f.stat().st_ctime
            print(f, f.stat().st_ctime, f.path)


covid_df = pd.read_csv(most_recent_fp)

# Clean covid_df
#covid_df['submit_date'] = pd.to_datetime(covid_df['submit_date'], format='%Y-%m-%d')

covid_df = covid_df.rename(
    columns= {
        'new_cases':'new_cases (1d)',
        'sum_cases_last_14_days':'new_cases (14d)',
        'new_cases_percent':'new_cases % pop (1d)',
        'cases_last_14_pop_percent':'new_cases % pop (14d)',
    }
)

covid_df = covid_df[covid_df['new_cases (1d)']>=0]

covid_df['new_cases % pop (1d)'] = covid_df['new_cases % pop (1d)']*100
covid_df['new_cases % pop (14d)'] = covid_df['new_cases % pop (14d)']*100


# Build Dash dashboard
external_stylesheets = [
    {
        "href": "https://fonts.googleapis.com/css2?"
                "family=Lato:wght@400;700&display=swap",
        "rel": "stylesheet",
     },
]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app.title = "DataViz COVID Infection Rates"  # Appears in web browser bar and in goodle search results

app.layout = html.Div(
    children=[
        html.Div(
            children=[
                html.H1(
                    children='US CDC Reported COVID-19 Data Normalized by State Populations 🔬📊',
                    className='header-title',
                ),
                html.P(
                    children='''A dashboard that presents daily new cases of COVID-19 reported by the US CDC, transformed into a percentage of each state population.
                        The left side of this dashboard shows new cases in each state on a selected date.
                        The right side of this dashboard shows new cases in a selected state over a selected date range.
                        The top visuals show data for each 1-day period and the bottom visuals show data over 14-day periods.
                    ''',
         
#                      The daily new case data is transformed to new cases summed over 14-days
#                      The new case data are further transformed to represent the percentage of a state population
#                      that are new cases during the past 1-day and past 14-days
                    className='header-description'
                ),
            ],
            className='header',
        ),
        # Create Div for left and right charts
        html.Div(
            children=[
                # Create Div for left side
                html.Div(
                    children=[
                        # Create Dropdown then Map Bubble charts on left side
                        html.Div(
                            children=[
                                    html.Div('Date', className='menu-title'),
                                    dcc.DatePickerSingle(
                                        id='date-filter',
                                        min_date_allowed=covid_df['submit_date'].min(),
                                        max_date_allowed=covid_df['submit_date'].max(),
#                                        display_format='MMM D YYYY',
#                                        date=covid_df['submit_date'].max(),
                                        clearable=False,
                                        date='2022-01-18',
                                    ),
                            ],
                            className='menu',
                        ),
                        # Create Map Bubble charts
                        html.Div(
                            children=[
                                html.Div(
                                    children=dcc.Graph(
                                        id='daily-cases-map',
                                        config={'displayModeBar':True},
                                    ),
                                    className='card'
                                ),
                                html.Div(
                                    children=dcc.Graph(
                                        id='d14-cases-map',
                                        config={'displayModeBar':True},
                                    ),
                                    className='card'
                                ),    
                            ],
                            className='wrapper'
                        ),
                    ],
                ),      
                
                # Create Individual state line chart on right side
                html.Div(
                    children=[
                        # Create Dropdowns
                        html.Div(
                            children=[
                                html.Div(
                                    children=[
                                        html.Div(children='State', className='menu-title'),
                                        dcc.Dropdown(
                                            id="state-filter",
                                            options=[
                                                {"label":state, "value":state}
                                                for state in np.sort(covid_df['state'].unique())
                                            ],
                                            value="NY",
                                            clearable=False,
                                            searchable=True,
#                                       multi=True,
                                            className='dropdown',
                                        ),
                                    ],  
                                ),
                                html.Div(
                                    children=[
                                        html.Div(children='Date Range', className='menu-title'),
                                        dcc.DatePickerRange(
                                            id='date-range',
#                                            min_date_allowed=covid_df['submit_date'].min().date(),
#                                            max_date_allowed=covid_df['submit_date'].max().date(),
                                            min_date_allowed=covid_df['submit_date'].min(),
                                            max_date_allowed=covid_df['submit_date'].max(),
#                                            start_date=covid_df['submit_date'].min(),
                                            start_date = '2021-10-01',
                                            end_date=covid_df['submit_date'].max(),
                                        ),
                                    ]
                                ),
                            ],
                            className='menu', 
                        ),
                        html.Div(
                            children=[
                                html.Div(
                                    children=dcc.Graph(
                                        id='daily-cases-chart', 
                                        config={
                                            'displayModeBar':True,
#                                            'responsive':True,
#                                            'fillFrame':True,
                                        },
                                    ),
                                    className='card',
                                ),
                                html.Div(
                                    children=dcc.Graph(
                                        id='d14-cases-chart', 
                                        config={
                                            'displayModeBar':True,
#                                            'responsive':True,
#                                            'fillFrame':True,
                                        },
                                    ),
                                    className='card',
                                ),
                            ],
                            className='wrapper',
                        ),
                    ]
                )
            ],
            className='left-right',
        )
    ]
)
                        
@app.callback(
    [
         Output('daily-cases-map', 'figure'), 
         Output('d14-cases-map','figure'),
         Output('daily-cases-chart','figure'), 
         Output('d14-cases-chart','figure')
    ],
    [
         Input('date-filter','date'),
         Input('state-filter','value'),
         Input('date-range','start_date'),
         Input('date-range','end_date'),
    ],
)

def update_charts(date, state, start_date, end_date):
    
    # Build Maps for left-side of Dashboard
    map_mask = (covid_df['submit_date']==date)
    map_df = covid_df[map_mask]
    
    daily_cases_map_figure = px.scatter_geo(
            map_df, 
            locations='state', 
            locationmode='USA-states',
            size='new_cases % pop (1d)',
            color='new_cases % pop (1d)',
            scope='usa',
            #text='state',
            animation_group='submit_date',
            color_continuous_scale=px.colors.sequential.Hot[1:][::-1],
            range_color=[0,0.6],
            basemap_visible=True,
            hover_data={'new_cases (1d)':True,'new_cases % pop (1d)':':.2f','state':True,}
        )
    
    daily_cases_map_figure.update_layout(
            title_text='<b>Daily New Cases of Covid in US on %s</b>'% date,
            width=800,
    )
    

    d14_cases_map_figure =  px.scatter_geo(
            map_df, 
            locations='state', 
            locationmode='USA-states',
            size='new_cases % pop (14d)',
            color='new_cases % pop (14d)',
            scope='usa',
            #text='state',
            animation_group='submit_date',
            color_continuous_scale=px.colors.sequential.Hot[1:][::-1],
            range_color=[0,6],
            basemap_visible=True,
            hover_data={'new_cases (14d)':True,'new_cases % pop (14d)':':.2f','state':True, 'state_pop':True},
#            hovertemplate='State: %s<br>NewCases Percent (1d): %%{y:.2f}<br>NewCases Count(1d):%s'% (state, map_df['new_cases % pop (14d)']),
    )
    
    d14_cases_map_figure.update_layout(
            title_text='<b>14-day New Cases of Covid in US on %s</b>'% date,
            width=800,
    )
    
    
    # Build charts for right-side of Dashboard
    
    mask = (
         (covid_df['state'] == state)
         & (covid_df['submit_date'] >= start_date)
         & (covid_df['submit_date'] <= end_date)
    )
    
    filtered_data = covid_df[mask]
    
    # Daily Cases Chart
    daily_cases_chart_figure = make_subplots(specs=[[{"secondary_y":True}]])
    daily_cases_chart_figure.update_layout(
            title_text='<b>Daily New Cases of COVID in %s</b>'%state,
            width=800,
    )
    daily_cases_chart_figure.update_xaxes(title_text='Date')
    daily_cases_chart_figure.update_yaxes(title_text='New Cases <b>(Count)</b>', secondary_y=False, color=" #079A82")
    daily_cases_chart_figure.update_yaxes(title_text='New Cases <b>(%Population)</b>', secondary_y=True, color="#F39C12", ticksuffix='%')
    
    daily_cases_chart_figure.add_trace(
        go.Scatter(
            x=filtered_data['submit_date'],
            y=filtered_data['new_cases % pop (1d)'],                    
#            hovertemplate= "%{y:.3f}%<extra></extra>",
            name ='New Cases %',
            hovertemplate='State: %s<br>NewCases Percent (1d): %%{y:.2f}'% state,
#            legend_width='10px',
            legendgrouptitle={"text":"Legend"},
            showlegend=False,
            marker={'color':"#F39C12", "opacity":1},

        ),
        secondary_y=True
    )
        
    daily_cases_chart_figure.add_trace(
        go.Bar(
            x=filtered_data['submit_date'],
            y=filtered_data['new_cases (1d)'],
            name='New Cases Count',
            hovertemplate='State :%s<br>NewCases (1d): %%{y}'% state,
            legendgrouptitle={"text":"Legend"},
            showlegend=False,
            marker={'opacity':1, 'color':"#079A82"}
        ),
        secondary_y=False
    )
                                        
    # 14-Day Cases Chart
    d14_cases_chart_figure = make_subplots(specs=[[{"secondary_y":True}]])
    d14_cases_chart_figure.update_layout(
            title_text='<b>14-day New Cases of COVID in %s</b>'%state,
            width=800,
    )
    d14_cases_chart_figure.update_xaxes(title_text='Date')
    d14_cases_chart_figure.update_yaxes(title_text='New Cases (14d) <b>(Count)</b>', secondary_y=False, color=" #079A82")
    d14_cases_chart_figure.update_yaxes(title_text='New Cases (14d) <b>(%Population)</b>', secondary_y=True, color="#F39C12", ticksuffix='%')
    
    d14_cases_chart_figure.add_trace(
        go.Scatter(
            x=filtered_data['submit_date'],
            y=filtered_data['new_cases % pop (14d)'],                    
#            hovertemplate= "%{y:.3f}%<extra></extra>",
            name ='New Cases %',
            hovertemplate='State: %s<br>NewCases Percent (14d): %%{y:.2f}'% state,
#            legend_width='10px',
            legendgrouptitle={"text":"Legend"},
            showlegend=False,
            marker={'color':"#F39C12", "opacity":1},

        ),
        secondary_y=True
    )
        
    d14_cases_chart_figure.add_trace(
        go.Bar(
            x=filtered_data['submit_date'],
            y=filtered_data['new_cases (14d)'],
            name='New Cases Count',
            hovertemplate='State :%s<br>NewCases (14d): %%{y}'% state,
            legendgrouptitle={"text":"Legend"},
            showlegend=False,
            marker={'opacity':1, 'color':"#079A82"}
        ),
        secondary_y=False
    )
#    daily_cases_chart_figure = {
#            "data":[
#                {
#                    "x": filtered_data['submit_date'],
#                    "y": filtered_data['new_cases % pop (1d)'],
#                    "type":"scatter",
#                    "hovertemplate": "%{y:.3f}%<extra></extra>",
#                    "name":'New Cases %',
#                },
#                {
#                    "x": filtered_data['submit_date'],
#                    "y": filtered_data['new_cases (1d)'],
#                    "type":"bar",
#                    "name":'New Cases Count',
#                },
#            ], #layout
#            "layout":{
#                "autosize":True
#            }
#    }

#    d14_cases_chart_figure = {
#            "data":[
#                {
#                    "x":filtered_data['submit_date'],
#                    "y":filtered_data['new_cases % pop (14d)']*100,
#                    "type":"scatter",
#                    "name":"New Cases %",
#                },
#                {
#                    "x":filtered_data['submit_date'],
#                    "y":filtered_data['new_cases (14d)'],
#                    "type":"bar",
#                    "name":"New Cases Count",
#                },
#            ], #layout
#            "layout":{
#                "autosize":True
#            },
#    }
    
    return daily_cases_map_figure, d14_cases_map_figure, daily_cases_chart_figure, d14_cases_chart_figure

#data=covid_df.query("state == 'NY'")
#data.sort_values('submit_date', inplace=True, ascending=False)
#
#app.layout = html.Div(
#    children=[
#        html.H1(
#            children='🤒 Daily US Covid Cases By Percent Population',
#            className='header-title',
##            style={"fontSize":"60px", "color":"green"},
#        ),
#        html.P(
#            children='Daily Cases in NY State'
#        ),
#        dcc.Graph(
#            figure={
#                "data": [
#                    {
#                        "x": covid_df['submit_date'],
#                        "y": covid_df['new_cases_percent']*100,
#                        "type": "lines",
#                        "hovertemplate":"%{y:.3f}%"
#                                            "<extra></extra>",
#                    },
#                ],
#                "layout": {
#                    "title": "State Percentage",
#                    "yaxis": {
#                        "ticksuffix":"%"        
#                    },
#                },
#            },
#        ),
#        dcc.Graph(
#            figure={
#                "data":[
#                    {
#                        "x": covid_df['submit_date'],
#                        "y": covid_df['cases_last_14_pop_percent'],
#                        "type": "lines"
#                    },
#                ],
#                "layout":{"title":"Total Percentage Last 14 days"}
#                },
#            ),
#    ]
#)

    
if __name__ == "__main__":
    app.run_server(debug=True)
