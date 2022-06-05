"""URL routing for the Dash/Flask app"""
from dash import dcc, html, callback
from dash.dependencies import Input, Output

from traitsgarden.pages import home, app1, app2

## Dash Pages ##
layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content'),
    html.Br(),
    dcc.Link('Go Home', href='/traitsgarden'),
])

@callback(Output('page-content', 'children'),
            [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/traitsgarden':
        return home.layout
    elif pathname == '/test/app1':
        return app1.layout
    elif pathname == '/test/app2':
        return app2.layout
    else:
        return html.H1('404 - Page Not Found')
