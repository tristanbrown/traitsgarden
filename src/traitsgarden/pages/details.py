from datetime import date
from dash import dcc, html, callback, register_page
from dash.dependencies import Input, Output, State, MATCH, ALL
import dash_bootstrap_components as dbc
from traitsgarden.db.connect import Session
from traitsgarden.db.models import Plant, Seeds, Cultivar

register_page(__name__, path='/traitsgarden/details')

def layout(cultivarid=None, seedsid=None, plantid=None):
    if cultivarid == seedsid == plantid == None:
        return
    ids = {
        'cultivar': cultivarid,
        'seeds': seedsid,
        'plant': plantid,
    }
    with Session.begin() as session:
        section1, section2 = resolve_display(
            session, cultivarid, seedsid, plantid
        )
    return html.Div([
        navbar,
        dcc.Store(id='ids', data=ids),
        section1,
        html.Br(),
        section2,
        html.Br(),
        html.Button('Save Changes', id='save-changes', n_clicks=0),
        html.Div(id='save-status', children='-'),
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
    layout = html.Div([
        html.H2(obj.name),
        html.H3(obj.category),
        f"Species: {obj.species}",
        html.Br(),
        f"Hybrid: {obj.hybrid}",
        html.Br(),
        f"Description:",
        html.Br(),
        obj.description,
    ])
    return layout

def display_seeds(obj):
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
        f"Parents: {obj.mother}, {obj.father}",
    ])
    return layout

def display_plant(obj):
    layout = html.Div([
        html.H3("Plant"),
        f"ID: {obj.plant_id}",
        html.Br(),
        f"Start Date: ",
        dcc.DatePickerSingle(
            id={'type': 'date-field', 'index': "start_date"},
            date=obj.start_date,
        ),
        html.Br(),
        f"Conditions:",
        dcc.Input(id={'type': 'input-field', 'index': "conditions"},
            type="text", value=obj.conditions),
        html.Br(),
        f"Variant Notes:",
        html.Br(),
        dcc.Textarea(id={'type': 'input-field', 'index': "variant_notes"},
            style={'width': '30%', 'height': 100},
            value=obj.variant_notes),
        html.Br(),
        "Height: ",
        dcc.Input(id={'type': 'input-field', 'index': "height"},
            type="number", value=obj.height),
        html.Br(),
        f"Fruit Description:",
        dcc.Input(id={'type': 'input-field', 'index': "fruit_desc"},
            type="text", value=obj.fruit_desc),
        html.Br(),
        f"Fruit Flavor:",
        dcc.Input(id={'type': 'input-field', 'index': "flavor"},
            type="text", value=obj.flavor),
        html.Br(),
    ])
    return layout

@callback(
    Output('save-status', 'children'),
    Input('save-changes', 'n_clicks'),
    State('ids', 'data'),
    State({'type': 'input-field', 'index': ALL}, 'id'),
    State({'type': 'input-field', 'index': ALL}, 'value'),
    State({'type': 'date-field', 'index': ALL}, 'id'),
    State({'type': 'date-field', 'index': ALL}, 'date'),
    prevent_initial_call=True,
)
def save_changes(n_clicks, ids, input_fields, inputs,
        date_fields, dates):
    fields = input_fields + date_fields
    values = inputs + dates
    form = {field['index']: val for field, val in zip(fields, values)}
    updates = {}
    with Session.begin() as session:
        obj = Plant.get(session, ids['plant'])
        for field, val in form.items():
            if getattr(obj, field) != val:
                setattr(obj, field, val)
                updates[field] = val
    return f"Changes Saved: {updates}"

PLOTLY_LOGO = "https://images.plot.ly/logo/new-branding/plotly-logomark.png"

search_bar = dbc.Row(
    [
        dbc.Col(dbc.Input(type="search", placeholder="Search")),
        dbc.Col(
            dbc.Button(
                "Search", color="primary", className="ms-2", n_clicks=0
            ),
            width="auto",
        ),
    ],
    className="g-0 ms-auto flex-nowrap mt-3 mt-md-0",
    align="center",
)

navbar = dbc.Navbar(
    # dbc.Container(
        [
            html.A(
                # Use row and col to control vertical alignment of logo / brand
                dbc.Row(
                    [
                        dbc.Col(html.Img(src=PLOTLY_LOGO, height="30px")),
                        dbc.Col(dbc.NavbarBrand("Navbar", className="ms-2")),
                    ],
                    align="center",
                    className="g-0",
                ),
                href="https://plotly.com",
                style={"textDecoration": "none"},
            ),
            dbc.NavbarToggler(id="navbar-toggler", n_clicks=0),
            dbc.Collapse(
                search_bar,
                id="navbar-collapse",
                is_open=False,
                navbar=True,
            ),
        ],
    # ),
    color="dark",
    dark=True,
)


# add callback for toggling the collapse on small screens
@callback(
    Output("navbar-collapse", "is_open"),
    [Input("navbar-toggler", "n_clicks")],
    [State("navbar-collapse", "is_open")],
)
def toggle_navbar_collapse(n, is_open):
    if n:
        return not is_open
    return is_open
