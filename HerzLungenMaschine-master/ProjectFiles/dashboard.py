from cmath import nan
from tempfile import SpooledTemporaryFile
from turtle import color
import dash
from dash import Dash, html, dcc, Output, Input, dash_table
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import utilities as ut
import numpy as np
import os
import re

app = Dash(__name__)


list_of_subjects = []
subj_numbers = []
number_of_subjects = 0

folder_current = os.path.dirname(__file__) 
print(folder_current)
folder_input_data = os.path.join(folder_current, "input_data")
for file in os.listdir(folder_input_data):
    
    if file.endswith(".csv"):
        number_of_subjects += 1
        file_name = os.path.join(folder_input_data, file)
        print(file_name)
        list_of_subjects.append(ut.Subject(file_name))


df = list_of_subjects[0].subject_data


for i in range(number_of_subjects):
    subj_numbers.append(list_of_subjects[i].subject_id)

data_names = ["SpO2 (%)", "Blood Flow (ml/s)","Temp (C)"]
algorithm_names = ['min','max']
blood_flow_functions = ['CMA','SMA','Show Limits']


fig0= go.Figure()
fig1= go.Figure()
fig2= go.Figure()
fig3= go.Figure()

fig0 = px.line(df, x="Time (s)", y = "SpO2 (%)")
fig1 = px.line(df, x="Time (s)", y = "Blood Flow (ml/s)")
fig2 = px.line(df, x="Time (s)", y = "Temp (C)")
fig3 = px.line(df, x="Time (s)", y = "Blood Flow (ml/s)")

app.layout = html.Div(children=[
    html.H1(children='Cardiopulmonary Bypass Dashboard', 
        style={'color': 'dimgrey', 'font-family': 'verdana', 'fontSize': 46, 'text-align': 'center'}),

    html.Div(children='Auswahl zum anzeigen von Minimum und Maximum bei SpO2, Blood FLow und Temp',
        style={'font-family': 'arial', 'fontSize': 17}),

    dcc.Checklist(
        id= 'checklist-algo',
        options=algorithm_names,
        inline=False,
        style={'font-family': 'arial'},
        ),

    html.Div(children='Auswahl des Patienten',
        style={'font-family': 'arial', 'fontSize': 17, 'margin-top': 25}),

    html.Div([
        dcc.Dropdown(options = subj_numbers, placeholder='Select a subject', value='1', id='subject-dropdown'),
    html.Div(id='dd-output-container')
    ],
        style={"width": "15%", 'font-family': 'arial'}
    ),

    dcc.Graph(
        id='dash-graph0',
        figure=fig0
    ),

    dcc.Graph(
        id='dash-graph1',
        figure=fig1
    ),
    dcc.Graph(
        id='dash-graph2',
        figure=fig2
    ),

    html.Div(children='Auswahl zum anzeigen von SMA und CMA im Blood Flow',
        style={'font-family': 'arial', 'fontSize': 17}),
    
    dcc.Checklist(
        id= 'checklist-bloodflow',
        options=blood_flow_functions,
        inline=False,
        style={'font-family': 'arial'},
    ),
    dcc.Graph(
        id='dash-graph3',
        figure=fig3
    )
])
### Callback Functions ###
## Graph Update Callback
@app.callback(
    # In- or Output('which html element','which element property')
    Output('dash-graph0', 'figure'),
    Output('dash-graph1', 'figure'),
    Output('dash-graph2', 'figure'),
    Input('subject-dropdown', 'value'),
    Input('checklist-algo','value')
)
def update_figure(value, algorithm_checkmarks):
    print("Current Subject: ",value)
    print("current checked checkmarks are: ", algorithm_checkmarks)
    ts = list_of_subjects[int(value)-1].subject_data
    #SpO2
    fig0 = px.line(ts, x="Time (s)", y = data_names[0])
    # Blood Flow
    fig1 = px.line(ts, x="Time (s)", y = data_names[1])
    # Blood Temperature
    fig2 = px.line(ts, x="Time (s)", y = data_names[2])
    
    ### Aufgabe 2: Min / Max ###
    # erstellen einer group
    grp = ts.agg(['max','min','idxmax','idxmin'])
    # 'agg' holt sich die benötigten Daten aus 'list_of_subjects'
    print(grp)

    # wenn nichts angecklickt wird, wird nichts gemacht
    if algorithm_checkmarks is not None:

        # wenn 'max' angeklickt wird, werden für die drei Graphen das jeweilige Maximum angezeigt
        if 'max' in algorithm_checkmarks:
            # 'add_trace' setzt für 'fig0' bis 'fig3' am Maximum eine Makierung
            fig0.add_trace(go.Scatter(x=[grp.loc['idxmax',data_names[0]]],y=[grp.loc['max',data_names[0]]],
                mode='markers',marker_symbol='triangle-down',marker_size=13,name='max',marker_color='black'))
            fig1.add_trace(go.Scatter(x=[grp.loc['idxmax',data_names[1]]],y=[grp.loc['max',data_names[1]]],
                mode='markers',marker_symbol='triangle-down',marker_size=13,name='max',marker_color='black'))
            fig2.add_trace(go.Scatter(x=[grp.loc['idxmax',data_names[2]]],y=[grp.loc['max',data_names[2]]],
                mode='markers',marker_symbol='triangle-down',marker_size=13,name='max',marker_color='black'))
        
        # wenn ein min angeklickt wir, werden für die drei Graphen das Minima angezeigt
        if 'min' in algorithm_checkmarks:
            # 'add_trace' setzt für 'fig0' bis 'fig3' am Minimum eine Makierung
            # 'loc' lokalisiert die gesuchten Daten in 'grp'
            fig0.add_trace(go.Scatter(x=[grp.loc['idxmin',data_names[0]]],y=[grp.loc['min',data_names[0]]],
                mode='markers',marker_symbol='triangle-up',marker_size=13,name='min',marker_color='black'))
            fig1.add_trace(go.Scatter(x=[grp.loc['idxmin',data_names[1]]],y=[grp.loc['min',data_names[1]]],
                mode='markers',marker_symbol='triangle-up',marker_size=13,name='min',marker_color='black'))
            fig2.add_trace(go.Scatter(x=[grp.loc['idxmin',data_names[2]]],y=[grp.loc['min',data_names[2]]],
                mode='markers',marker_symbol='triangle-up',marker_size=13,name='min',marker_color='black'))



    fig0.update_traces(line_color='steelblue') # ändern der Farbe vom Plot 0
    fig1.update_traces(line_color='firebrick') # ändern der Farbe vom Plot 1
    fig2.update_traces(line_color='dimgrey') # ändern der Farbe vom Plot 2
    return fig0, fig1, fig2  


## Blodflow Simple Moving Average Update
@app.callback(
    # In- or Output('which html element','which element property')
    Output('dash-graph3', 'figure'),
    Input('subject-dropdown', 'value'),
    Input('checklist-bloodflow','value')
)
def bloodflow_figure(value, bloodflow_checkmarks):
    
    ## Calculate Moving Average: Aufgabe 2
    print(bloodflow_checkmarks)
    bf = list_of_subjects[int(value)-1].subject_data # bf deklaration
    fig3 = px.line(bf, x="Time (s)", y="Blood Flow (ml/s)")

    if bloodflow_checkmarks is not None:

        if 'SMA' in bloodflow_checkmarks: 
            bf['Simple Moving Average']=ut.calculate_SMA(bf['Blood Flow (ml/s)'],5)
            fig3 = px.line(bf, x="Time (s)", y="Simple Moving Average")

        if 'CMA' in bloodflow_checkmarks:
            bf['Cumulative Moving Average']=ut.calculate_CMA(bf['Blood Flow (ml/s)'],2)
            fig3 = px.line(bf, x="Time (s)", y="Cumulative Moving Average")

        ## Aufgabe 3
        if 'Show Limits' in bloodflow_checkmarks:
            # Durchschnitt
            # 'loc' lokalisiert die gesuchten Daten
            avg=bf.mean()
            x=[0,480]
            y=avg.loc['Blood Flow (ml/s)']
            # 'add_trace' erstellt eine Linie für den Durchschnitt
            fig3.add_trace(go.Scatter(x=x,y=[y,y],mode='lines',name='Durchschnitt',marker_color='lime'))

            # +/- 15%
            y_up=avg.loc['Blood Flow (ml/s)']*1.15
            y_down=avg.loc['Blood Flow (ml/s)']*0.85

            fig3.add_trace(go.Scatter(x=x,y=[y_up,y_up],mode='lines',name='+15%',marker_color='orangered'))
            fig3.add_trace(go.Scatter(x=x,y=[y_down,y_down],mode='lines',name='-15%',marker_color='orangered'))

    fig3.update_traces(line_color='firebrick') # ändern der Farbe vom Plot 3
    return fig3

if __name__ == '__main__':
    app.run_server(debug=True)