from dash import dcc, html, callback, register_page
from dash.dependencies import Input, Output
from traitsgarden.db.connect import Session

register_page(__name__, path='/traitsgarden')

layout = html.Div([
    html.H3('Traitsgarden'),
    dcc.Link('Search', href='/traitsgarden/search'),
    html.Br(),
    dcc.Link('Cultivars', href='/traitsgarden/cultivar'),
    html.Br(),
    dcc.Link('Seeds', href='/traitsgarden/seeds'),
    html.Br(),
    dcc.Link('Plants', href='/traitsgarden/plants'),
])
