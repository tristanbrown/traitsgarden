from dash import dcc, html, callback, register_page
from dash.dependencies import Input, Output
from traitsgarden.db.connect import Session
from traitsgarden.db.models import Plant

register_page(__name__, path="/traitsgarden/plant")

def layout(id=None):
    return html.Div([
        html.Div(display_plant(id)),
    ])

def display_plant(id):
    with Session.begin() as session:
        plantdb = str(Plant.get(session, id))
    return f"Plant: {plantdb}"
