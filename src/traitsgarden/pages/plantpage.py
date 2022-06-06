from dash import dcc, html, callback
from dash.dependencies import Input, Output
from traitsgarden.db.connect import Session
from traitsgarden.db.models import Plant

def get_layout(id):
    return html.Div([
        html.Div(display_plant(id)),
    ])

def display_plant(id):
    with Session.begin() as session:
        plantdb = str(Plant.get(session, id))
    return f"Plant: {plantdb}"
