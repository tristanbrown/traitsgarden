from dash import dcc, html, callback, register_page
from dash.dependencies import Input, Output
from traitsgarden.db.connect import Session

register_page(__name__, path='/index')

layout = html.Div([
    html.H3('Traitsgarden'),
    dcc.Link('Cultivars', href=f'table?name=cultivar'),
    html.Br(),
    dcc.Link('Seeds', href=f'table?name=seeds'),
    html.Br(),
    dcc.Link('Plants', href=f'table?name=plant'),
])
