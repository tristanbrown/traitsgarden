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
    display = DetailsDisplay(cultivarid, seedsid, plantid)
    return html.Div([
        dcc.Store(id='ids', data=display.ids),
        display.section1,
        html.Br(),
        display.section2,
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

class DetailsDisplay():
    """"""

    def __init__(self, cultivarid, seedsid, plantid):
        self.cultivarid = cultivarid
        self.seedsid = seedsid
        self.plantid = plantid
        self.section2 = self.get_section2()
        self.section1 = self.get_section1()

    @property
    def ids(self):
        return {
            'cultivar': self.cultivarid,
            'seeds': self.seedsid,
            'plant': self.plantid,
        }

    def get_section2(self):
        if self.plantid:
            return self.get_obj_display(Plant, self.plantid, display_plant)
        elif self.seedsid:
            return self.get_obj_display(Seeds, self.seedsid, display_seeds)

    def get_section1(self):
        return self.get_obj_display(Cultivar, self.cultivarid, display_cultivar)

    def get_obj_display(self, model, obj_id, display_func):
        with Session.begin() as session:
            obj = model.get(session, obj_id)
            try:
                self.cultivarid = obj.cultivar.id
            except AttributeError:
                pass
            return display_func(obj)

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
        generic_text_input(obj, 'cultivar', 'species'),
        html.Br(),
        dbc.Row(
            generic_checkbox(obj, 'cultivar', 'hybrid', "Hybrid"),
        ),
        f"Description:",
        html.Br(),
        generic_text_box(obj, 'cultivar', 'description'),
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
    def text_input(fieldname, in_type='text'):
        return generic_text_input(obj, 'seeds', fieldname, in_type)

    def text_box(fieldname):
        return generic_text_box(obj, 'seeds', fieldname)

    parents = [
        f"{parent.name} {parent.plant_id}" for parent in obj.parents]
    layout = html.Div([
        html.H3("Seeds"),
        f"ID: {obj.pkt_id}",
        html.Br(),
        f"Source: ",
        text_input('source'),
        html.Br(),
        f"Generation: ",
        text_input('generation'),
        html.Br(),
        f"Last Count: ",
        text_input('last_count', in_type='number'),
        html.Br(),
        f"Parents: {', '.join(parents)}",
        html.Br(),
        f"Variant Notes: ",
        html.Br(),
        text_box('variant_notes'),
    ])
    return layout

def display_plant(obj):
    def date_input(fieldname):
        return generic_date_input(obj, 'plant', fieldname)

    def text_input(fieldname, in_type='text'):
        return generic_text_input(obj, 'plant', fieldname, in_type)

    def text_box(fieldname):
        return generic_text_box(obj, 'plant', fieldname)

    def checkbox(fieldname, title):
        return generic_checkbox(obj, 'plant', fieldname, title)

    layout = html.Div([
        html.H3("Plant"),
        f"ID: {obj.plant_id}",
        html.Br(),
        dbc.Row([
            checkbox('active', "Active"),
            checkbox('seeds_collected', "Seeds coll")
        ]),
        dbc.Row([
            dbc.Col(["Start", html.Br(), date_input('start_date')], width=1),
            dbc.Col(["Germination", html.Br(), date_input('germ_date')], width=1),
            dbc.Col(["Pot up", html.Br(), date_input('pot_up_date')], width=1),
            dbc.Col(["Final pot", html.Br(), date_input('final_pot_date')], width=1),
            dbc.Col(["First flower", html.Br(), date_input('flower_date')], width=1),
            dbc.Col(["First fruit", html.Br(), date_input('fruit_date')], width=1),
            dbc.Col(["Died", html.Br(), date_input('died')], width=1),
        ], justify='start'),
        html.Br(),
        f"Conditions: ",
        text_input('conditions'),
        html.Br(),
        dbc.Row(checkbox('staked', "Staked")),
        f"Variant Notes: ",
        html.Br(),
        text_box('variant_notes'),
        html.Br(),
        f"Growth: ",
        text_input('growth'),
        html.Br(),
        dbc.Row([
            dbc.Col("Height, Width: ", width='auto'),
            dbc.Col(text_input('height', in_type='number'), width=1),
            dbc.Col(text_input('width', in_type='number'), width=1),
        ], justify='start'),
        f"Fruit Description: ",
        text_input('fruit_desc'),
        html.Br(),
        f"Fruit Flavor: ",
        text_input('flavor'),
        html.Br(),
        f"Brix (sg): ",
        text_input('brix_sg', in_type='number'),
        html.Br(),
        f"Health: ",
        text_input('health'),
        html.Br(),
        dbc.Row([
            dbc.Col(f"Powdery Mildew: ", width='auto'),
            dbc.Col(dcc.Dropdown(
                id={'type': 'input-field', 'section': 'plant', 'index': 'powdery_mildew'},
                value=obj.powdery_mildew,
                options=['low', 'med', 'high']
            ), width=1)
        ]),
        f"Pros: ",
        text_input('pros'),
        html.Br(),
        f"Cons: ",
        text_input('cons'),
        html.Br(),
        dbc.Row([
            dbc.Col("Ratings: ", width=1),
            dbc.Col(["Flavor", html.Br(), text_input('flavor_rating', in_type='number')], width=1),
            dbc.Col(["Growth", html.Br(), text_input('growth_rating', in_type='number')], width=1),
            dbc.Col(["Health", html.Br(), text_input('health_rating', in_type='number')], width=1),
        ], justify='start'),
    ])
    return layout

def generic_text_input(obj, section, fieldname, in_type='text'):
    """Returns a text input field indexed to the model attribute.
    in_type can be: text, number
    """
    return dcc.Input(
            id={'type': 'input-field', 'section': section, 'index': fieldname},
            type=in_type,
            value=getattr(obj, fieldname),
        )

def generic_date_input(obj, section, fieldname):
    """Returns a date input field indexed to the model attribute."""
    return dcc.DatePickerSingle(
            id={'type': 'date-field', 'section': section, 'index': fieldname},
            date=getattr(obj, fieldname),
        )

def generic_text_box(obj, section, fieldname):
    """Returns a large textbox input field indexed to the model attribute.
    """
    return dcc.Textarea(
            id={'type': 'input-field', 'section': section, 'index': fieldname},
            style={'width': '30%', 'height': 55},
            value=getattr(obj, fieldname),
        )

def generic_checkbox(obj, section, fieldname, title):
    """"""
    return dbc.Col(
        dbc.Checkbox(
            id={'type': 'input-field', 'section': section, 'index': fieldname},
            label=f"{title}: ",
            label_style={'float': 'left'},
            input_style={'float': 'right'},
            value=getattr(obj, fieldname),
        ), width=1, align='left', className="g-0"
    )

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
