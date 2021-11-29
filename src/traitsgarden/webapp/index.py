"""URL routing for the Dash/Flask app"""
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
from flask import render_template

from traitsgarden.webapp import app, server
from traitsgarden.webapp.dashboards import app1, app2
# from traitsgarden.views import studies_blueprint

## Flask Pages ##
# server.register_blueprint(studies_blueprint, url_prefix="/studies")

@server.route("/home")
def index():
    return render_template('home.html')

## Dash Pages ##
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/apps/app1':
        return app1.layout
    elif pathname == '/apps/app2':
        return app2.layout
