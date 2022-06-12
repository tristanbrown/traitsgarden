from dash import dcc, html, callback, register_page
from dash.dependencies import Input, Output
from traitsgarden.db.connect import Session

register_page(__name__, path="/test/app1")

layout = html.Div([
    html.H3('App 1'),
    dcc.Dropdown(
        id='app-1-dropdown',
        options=[
            {'label': 'App 1 - {}'.format(i), 'value': i} for i in [
                'NYC', 'MTL', 'LA'
            ]
        ]
    ),
    html.Div(id='app-1-display-value'),
    dcc.Link('Go to App 2', href='/test/app2'),
])

@callback(
    Output('app-1-display-value', 'children'),
    [Input('app-1-dropdown', 'value')])
def display_value(value):
    return f"DB URI: {str(Session().bind.url)}"
