"""URL routing for the Dash/Flask app"""
from dash import dcc, html, callback
from dash.dependencies import Input, Output

from traitsgarden.pages import app1, app2

## Dash Pages ##
layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

@callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/apps/app1':
        return app1.layout
    elif pathname == '/apps/app2':
        return app2.layout
