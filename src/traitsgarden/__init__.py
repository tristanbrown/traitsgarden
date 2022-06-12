"""Set up Flask app"""
import os
from dash import Dash, html, dcc, page_container

from traitsgarden.settings import Config
from traitsgarden.db.connect import Session, connect_db

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = Dash(__name__, external_stylesheets=external_stylesheets, use_pages=True)
server = app.server
server.config.from_object(Config())

## Initial layout
app.layout = html.Div([
    page_container,
    html.Br(),
    dcc.Link('Go Home', href='/traitsgarden'),
])
