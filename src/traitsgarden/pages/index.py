"""URL routing for the Dash/Flask app"""
from dash import dcc, html, callback
from dash.dependencies import Input, Output

from traitsgarden.pages import app1, app2

## Dash Pages ##
layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

def get_callbacks(sqlsession):

    @callback(Output('page-content', 'children'),
                [Input('url', 'pathname')])
    def display_page(pathname):
        if pathname == '/apps/app1':
            return init_app(app1, sqlsession)
        elif pathname == '/apps/app2':
            return init_app(app2, sqlsession)

def init_app(app, sqlsession):
    layout = app.layout
    app.get_callbacks(sqlsession)
    return layout
