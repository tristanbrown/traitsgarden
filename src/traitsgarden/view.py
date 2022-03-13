"""Dash App Layout"""
from dash import dcc, html, callback, dash_table
from dash.dependencies import Input, Output, State

layout = html.Div([
    
], style={'paddingLeft': '40px', 'paddingRight': '40px'},)

@callback(
    Output('grouprun_output', 'children'),
    Input('submit-button-state', 'n_clicks'),
    State('grouprun_id', 'value'),
    prevent_initial_call=True,)
def update_output(n_clicks, input1):
    return f"Processing data {input1}..."
