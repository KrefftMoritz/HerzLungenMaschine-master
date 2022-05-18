from cmath import nan
from tempfile import SpooledTemporaryFile
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
    html.H1(children='Cardiopulmonary Bypass Dashboard'),

    html.Div(children='''
        Hier könnten Informationen zum Patienten stehen....
    '''),

    dcc.Checklist(
    id= 'checklist-algo',
    options=algorithm_names,
    inline=False
    ),

    html.Div([
        dcc.Dropdown(options = subj_numbers, placeholder='Select a subject', value='1', id='subject-dropdown'),
    html.Div(id='dd-output-container')
    ],
        style={"width": "15%"}
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

    dcc.Checklist(
        id= 'checklist-bloodflow',
        options=blood_flow_functions,
        inline=False
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
    ## erstellen einer group
    grp = ts.agg(['max','min','idxmax','idxmin'])
    print(grp)

    ## wenn ein max angeklickt wir, werden für die drei Graphen das Maximum angezeigt
    if 'max' in algorithm_checkmarks:
        fig0.add_trace(go.Scatter(x=[grp.loc['idxmax',data_names[0]]],y=[grp.loc['max',data_names[0]]],
            mode='markers',name='max',marker_color='turquoise'))
        fig1.add_trace(go.Scatter(x=[grp.loc['idxmax',data_names[1]]],y=[grp.loc['max',data_names[1]]],
            mode='markers',name='max',marker_color='turquoise'))
        fig2.add_trace(go.Scatter(x=[grp.loc['idxmax',data_names[2]]],y=[grp.loc['max',data_names[2]]],
            mode='markers',name='max',marker_color='turquoise'))

    ## wenn ein min angeklickt wir, werden für die drei Graphen das Minnima angezeigt
    if 'min' in algorithm_checkmarks:
        fig0.add_trace(go.Scatter(x=[grp.loc['idxmin',data_names[0]]],y=[grp.loc['min',data_names[0]]],
            mode='markers',name='min',marker_color='orange '))
        fig1.add_trace(go.Scatter(x=[grp.loc['idxmin',data_names[1]]],y=[grp.loc['min',data_names[1]]],
            mode='markers',name='min',marker_color='orange '))
        fig2.add_trace(go.Scatter(x=[grp.loc['idxmin',data_names[2]]],y=[grp.loc['min',data_names[2]]],
            mode='markers',name='min',marker_color='orange '))

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
    bf = list_of_subjects[int(value)-1].subject_data
    fig3 = px.line(bf, x="Time (s)", y="Blood Flow (ml/s)")


    if bloodflow_checkmarks == ['SMA']:
        bf = list_of_subjects[int(value)-1].subject_data
        bf['Blood Flow (ml/s) - SMA']=ut.calculate_SMA(bf['Blood Flow (ml/s)'],5)
        fig3 = px.line(bf, x="Time (s)", y="Blood Flow (ml/s) - SMA")

    if bloodflow_checkmarks == ['CMA']:
        bf = list_of_subjects[int(value)-1].subject_data
        bf['Blood Flow (ml/s) - CMA']=ut.calculate_CMA(bf['Blood Flow (ml/s)'],2)
        fig3 = px.line(bf, x="Time (s)", y="Blood Flow (ml/s) - CMA")

    return fig3

if __name__ == '__main__':
    app.run_server(debug=True)