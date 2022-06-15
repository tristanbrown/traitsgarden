from dash import dcc, html, callback, register_page
from dash.dependencies import Input, Output
from traitsgarden.db.connect import Session
from traitsgarden.db.models import Plant, Seeds, Cultivar

register_page(__name__, path='/traitsgarden/details')

def layout(cultivarid=None, seedsid=None, plantid=None):
    if cultivarid == seedsid == plantid == None:
        return
    with Session.begin() as session:
        section1, section2 = resolve_display(
            session, cultivarid, seedsid, plantid
        )
    return html.Div([
        section1,
        html.Br(),
        section2,
    ])

def resolve_display(session, cultivarid, seedsid, plantid):
    if plantid:
        obj = Plant.get(session, plantid)
        cultivarid = obj.cultivar.id
        section2 = display_plant(obj)
    elif seedsid:
        obj = Seeds.get(session, seedsid)
        cultivarid = obj.cultivar.id
        section2 = display_seeds(obj)
    else:
        section2 = None
    cultivar = Cultivar.get(session, cultivarid)
    section1 = display_cultivar(cultivar)
    return section1, section2

def display_cultivar(obj):
    return f"{obj.__class__.__name__}: {str(obj)}"

def display_seeds(obj):
    return f"{obj.__class__.__name__}: {str(obj)}"

def display_plant(obj):
    return f"{obj.__class__.__name__}: {str(obj)}"
