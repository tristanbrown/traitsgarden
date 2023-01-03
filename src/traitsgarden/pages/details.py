from datetime import date
from dash import dcc, html, callback, register_page
from dash.dependencies import Input, Output, State, MATCH, ALL
import dash_bootstrap_components as dbc
from traitsgarden.db.connect import Session
from traitsgarden.db.entry import update_one_obj
from traitsgarden.db.models import Plant, Seeds, Cultivar
from traitsgarden.fragments.add_cultivar_display import cultivar_add_display
from traitsgarden.fragments.add_obj_display import add_display_modal
from traitsgarden.fragments.delete_obj import del_display

register_page(__name__, path='/traitsgarden/details')

def layout(cultivarid=None, seedsid=None, plantid=None):
    if cultivarid == seedsid == plantid == None:
        return
    with Session.begin() as session:
        ids, section1, section2 = resolve_display(
            session, cultivarid, seedsid, plantid
        )
    return html.Div([
        dcc.Store(id='ids', data=ids),
        section1,
        html.Br(),
        section2,
        html.Br(),
        dbc.Row([
            dbc.Col(dbc.Button('Save Changes', id='save-changes', n_clicks=0), width='auto'),
            dbc.Col(dbc.Button('Delete', id='delete-entity-open', n_clicks=0), width='auto')
        ],
        align='center',
        justify="start"
        ),
        html.Div(id='save-status', children='-'),
        del_display,
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
    ids = {
        'cultivar': cultivarid,
        'seeds': seedsid,
        'plant': plantid,
    }
    return ids, section1, section2

def display_cultivar(obj):
    layout = html.Div([
        dbc.Row([
            dbc.Col(html.H2(obj.name), width='auto'),
            dbc.Col([
                dbc.Button('Add Cultivar', id='add-cultivar-open', n_clicks=0),
                cultivar_add_display
            ], width='auto'),
            dbc.Col([
                dbc.Button('Delete Cultivar', id='delete-cultivar-open', n_clicks=0),
            ])
        ],
        align='center',
        justify="start"
        ),
        html.H3(obj.category),
        "Species: ",
        dcc.Input(id={'type': 'input-field', 'section': 'cultivar', 'index': "species"},
            type="text", value=obj.species),
        html.Br(),
        f"Hybrid: {obj.hybrid}",
        html.Br(),
        f"Description:",
        html.Br(),
        obj.description,
        html.Br(),
        dbc.Row([
            dbc.Col([
                dbc.Button('Add Seeds',
                    id={'type': 'open-dialogue', 'index': "add-seeds"},
                    n_clicks=0),
                add_display_modal('seeds')
                ], width='auto'),
            dbc.Col([
                dbc.Button('Add Plant',
                    id={'type': 'open-dialogue', 'index': "add-plant"},
                    n_clicks=0),
                add_display_modal('plant')
                ], width='auto')
        ],
        align='center',
        justify="start"
        )

    ])
    return layout

def display_seeds(obj):
    parents = [
        f"{parent.name} {parent.plant_id}" for parent in obj.parents]
    layout = html.Div([
        html.H3("Seeds"),
        f"ID: {obj.pkt_id}",
        html.Br(),
        f"Source: {obj.source}",
        html.Br(),
        f"Generation: {obj.generation}",
        html.Br(),
        f"Last Count: {obj.last_count}",
        html.Br(),
        f"Parents: {','.join(parents)}",
    ])
    return layout

def display_plant(obj):
    layout = html.Div([
        html.H3("Plant"),
        f"ID: {obj.plant_id}",
        html.Br(),
        f"Start Date: ",
        dcc.DatePickerSingle(
            id={'type': 'date-field', 'section': 'plant', 'index': "start_date"},
            date=obj.start_date,
        ),
        html.Br(),
        f"Conditions:",
        dcc.Input(id={'type': 'input-field', 'section': 'plant', 'index': "conditions"},
            type="text", value=obj.conditions),
        html.Br(),
        f"Variant Notes:",
        html.Br(),
        dcc.Textarea(id={'type': 'input-field', 'section': 'plant', 'index': "variant_notes"},
            style={'width': '30%', 'height': 100},
            value=obj.variant_notes),
        html.Br(),
        "Height: ",
        dcc.Input(id={'type': 'input-field', 'section': 'plant', 'index': "height"},
            type="number", value=obj.height),
        html.Br(),
        f"Fruit Description:",
        dcc.Input(id={'type': 'input-field', 'section': 'plant', 'index': "fruit_desc"},
            type="text", value=obj.fruit_desc),
        html.Br(),
        f"Fruit Flavor:",
        dcc.Input(id={'type': 'input-field', 'section': 'plant', 'index': "flavor"},
            type="text", value=obj.flavor),
        html.Br(),
    ])
    return layout

@callback(
    Output('save-status', 'children'),
    Input('save-changes', 'n_clicks'),
    State('ids', 'data'),
    State({'type': 'input-field', 'section': ALL, 'index': ALL}, 'id'),
    State({'type': 'input-field', 'section': ALL, 'index': ALL}, 'value'),
    State({'type': 'date-field', 'section': ALL, 'index': ALL}, 'id'),
    State({'type': 'date-field', 'section': ALL, 'index': ALL}, 'date'),
    prevent_initial_call=True,
)
def save_changes(n_clicks, ids, input_fields, inputs,
        date_fields, dates):
    fields = input_fields + date_fields
    values = inputs + dates
    updates = {}
    for model in [Cultivar, Seeds, Plant]:
        modelname = model.__name__.lower()
        obj_id = ids[modelname]
        form = {field['index']: val for field, val in zip(fields, values)
            if field['section'] == modelname}
        updates[modelname] = update_one_obj(model, obj_id, form)
    return f"Changes Saved: {updates}"
