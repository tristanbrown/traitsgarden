from dash import dcc, html, callback
from dash.dependencies import Input, Output
from traitsgarden.db.connect import Session

layout = html.Div([
    html.H3('Traitsgarden'),
    dcc.Link('Search', href='/traitsgarden/search'),
    html.Br(),
    dcc.Link('Cultivars', href='/traitsgarden/cultivar'),
    html.Br(),
    dcc.Link('Seeds', href='/traitsgarden/seeds'),
    html.Br(),
    dcc.Link('Plants', href='/traitsgarden/plants'),
    html.Br(),
    dcc.Link('Go to App 1', href='/test/app1'),
    html.Br(),
    dcc.Link('Go to App 2', href='/test/app2'),
])
