import os
from dash import dcc, html, callback
from dash.dependencies import Input, Output
from traitsgarden.db.connect import Session
from traitsgarden.db.models import Plant

layout = html.Div([
    dcc.Location(id='url2', refresh=False),
    html.Div(id='plant-content'),
])

@callback(Output('plant-content', 'children'),
            [Input('url2', 'pathname')])
def display_plant(pathname):
    id = os.path.basename(pathname)
    with Session.begin() as session:
        plantdb = str(Plant.get(session, id))
    return f"Plant: {plantdb}"
