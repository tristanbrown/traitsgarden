from datetime import date
from dash import dcc, html, callback, register_page
from dash.dependencies import Input, Output, State, MATCH, ALL
import dash_bootstrap_components as dbc
from traitsgarden.db.connect import Session
from traitsgarden.db.entry import update_one_obj
from traitsgarden.db.models import Plant, Seeds, Cultivar
from traitsgarden.fragments.add_cultivar_display import cultivar_add_display
from traitsgarden.fragments.rename_cultivar_display import cultivar_rename_display
from traitsgarden.fragments.add_obj_display import add_display_modal
from traitsgarden.fragments.edit_parents_display import edit_parents_modal
from traitsgarden.fragments.delete_obj import del_display
from traitsgarden.fragments.dropdown_ids import display_dropdown_ids

register_page(__name__, path='/details')

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
            return self.get_obj_display(Plant, self.plantid, InputFormPlant)
        elif self.seedsid:
            return self.get_obj_display(Seeds, self.seedsid, InputFormSeeds)

    def get_section1(self):
        return self.get_obj_display(Cultivar, self.cultivarid, InputFormCultivar)

    def get_obj_display(self, model, obj_id, display_class):
        with Session.begin() as session:
            obj = model.get(session, obj_id)
            try:
                self.cultivarid = obj.cultivar.id
            except AttributeError:
                pass
            return display_class(obj).layout

class InputForm():
    """"""

    def __init__(self, obj, sectionname):
        self.obj = obj
        self.section = sectionname
        self.layout = self.get_layout(self.obj)

    def get_layout(self, obj):
        return html.Div()

    def text_input(self, fieldname, in_type='text'):
        """Returns a text input field indexed to the model attribute.
        in_type can be: text, number
        """
        return dcc.Input(
                id={'type': 'input-field', 'section': self.section, 'index': fieldname},
                type=in_type,
                value=getattr(self.obj, fieldname),
            )

    def date_input(self, fieldname):
        """Returns a date input field indexed to the model attribute."""
        return dcc.DatePickerSingle(
                id={'type': 'date-field', 'section': self.section, 'index': fieldname},
                date=getattr(self.obj, fieldname),
            )

    def text_box(self, fieldname):
        """Returns a large textbox input field indexed to the model attribute.
        """
        return dcc.Textarea(
                id={'type': 'input-field', 'section': self.section, 'index': fieldname},
                style={'width': '30%', 'height': 55},
                value=getattr(self.obj, fieldname),
            )

    def checkbox(self, fieldname, title):
        """"""
        return dbc.Col(
            dbc.Checkbox(
                id={'type': 'input-field', 'section': self.section, 'index': fieldname},
                label=f"{title}: ",
                label_style={'float': 'left'},
                input_style={'float': 'right'},
                value=getattr(self.obj, fieldname),
            ), width=1, align='left', className="g-0"
        )

class InputFormCultivar(InputForm):

    def __init__(self, obj):
        super().__init__(obj, 'cultivar')

    def get_layout(self, obj):
        layout = html.Div([
            dbc.Row([
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
            dbc.Row([
                dbc.Col(html.H2(obj.name), width='auto'),
                dbc.Col([
                    dbc.Button('Rename', id='rename-cultivar-open', n_clicks=0),
                    cultivar_rename_display(obj.id)
                ], width='auto'),
                ],
                align='center',
                justify="start"
            ),
            html.H3(obj.category),
            "Species: ",
            self.text_input('species'),
            html.Br(),
            dbc.Row(
                self.checkbox('hybrid', "Hybrid"),
            ),
            f"Description:",
            html.Br(),
            self.text_box('description'),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    dbc.Button('Add Seeds',
                        id={'type': 'open-dialogue', 'index': "add-seeds"},
                        n_clicks=0),
                    add_display_modal('seeds', obj.name, obj.category)
                    ], width='auto'),
                dbc.Col([
                    dbc.Button('Add Plant',
                        id={'type': 'open-dialogue', 'index': "add-plant"},
                        n_clicks=0),
                    add_display_modal('plant', obj.name, obj.category)
                    ], width='auto')
            ],
            align='center',
            justify="start"
            )

        ])
        return layout

class InputFormSeeds(InputForm):

    def __init__(self, obj):
        super().__init__(obj, 'seeds')

    def get_layout(self, obj):
        parents = [
            f"{parent.name} {parent.plant_id}" for parent in obj.parents]
        layout = html.Div([
            html.H3("Seeds"),
            dbc.Row([
                dbc.Col("ID:", width='auto'),
                dbc.Col(display_dropdown_ids(obj.category, obj.name, Seeds, obj.pkt_id),
                    width=1),
            ]),
            html.Br(),
            f"Source: ",
            self.text_input('source'),
            html.Br(),
            f"Generation: ",
            self.text_input('generation'),
            html.Br(),
            f"Last Count: ",
            self.text_input('last_count', in_type='number'),
            html.Br(),
            dbc.Row([
                dbc.Col(f"Parents: {', '.join(parents)}", width='auto'),
                dbc.Col(dbc.Button('Edit',
                    id={'type': 'open-dialogue', 'index': "edit-parents"},
                    n_clicks=0), width='auto'),
                dbc.Col(edit_parents_modal(obj.name, obj.category, obj.pkt_id), width='auto')
            ]),
            html.Br(),
            f"Variant Notes: ",
            html.Br(),
            self.text_box('variant_notes'),
        ])
        return layout

class InputFormPlant(InputForm):

    def __init__(self, obj):
        super().__init__(obj, 'plant')

    def get_layout(self, obj):
        layout = html.Div([
            html.H3("Plant"),
            dbc.Row([
                dbc.Col("ID:", width='auto'),
                dbc.Col(display_dropdown_ids(obj.category, obj.name, Plant, obj.plant_id),
                    width=1),
            ]),
            html.Br(),
            dbc.Row([
                self.checkbox('active', "Active"),
                self.checkbox('seeds_collected', "Seeds coll")
            ]),
            dbc.Row([
                dbc.Col(["Start", html.Br(), self.date_input('start_date')], width=1),
                dbc.Col(["Germination", html.Br(), self.date_input('germ_date')], width=1),
                dbc.Col(["Pot up", html.Br(), self.date_input('pot_up_date')], width=1),
                dbc.Col(["Final pot", html.Br(), self.date_input('final_pot_date')], width=1),
                dbc.Col(["First flower", html.Br(), self.date_input('flower_date')], width=1),
                dbc.Col(["First fruit", html.Br(), self.date_input('fruit_date')], width=1),
                dbc.Col(["Died", html.Br(), self.date_input('died')], width=1),
            ], justify='start'),
            html.Br(),
            f"Conditions: ",
            self.text_input('conditions'),
            html.Br(),
            dbc.Row(self.checkbox('staked', "Staked")),
            f"Variant Notes: ",
            html.Br(),
            self.text_box('variant_notes'),
            html.Br(),
            f"Growth: ",
            self.text_input('growth'),
            html.Br(),
            dbc.Row([
                dbc.Col("Height, Width: ", width='auto'),
                dbc.Col(self.text_input('height', in_type='number'), width=1),
                dbc.Col(self.text_input('width', in_type='number'), width=1),
            ], justify='start'),
            f"Fruit Description: ",
            self.text_input('fruit_desc'),
            html.Br(),
            f"Fruit Flavor: ",
            self.text_input('flavor'),
            html.Br(),
            f"Brix (sg): ",
            self.text_input('brix_sg', in_type='number'),
            html.Br(),
            f"Health: ",
            self.text_input('health'),
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
            self.text_input('pros'),
            html.Br(),
            f"Cons: ",
            self.text_input('cons'),
            html.Br(),
            dbc.Row([
                dbc.Col("Ratings: ", width=1),
                dbc.Col(["Flavor", html.Br(), self.text_input('flavor_rating', in_type='number')], width=1),
                dbc.Col(["Growth", html.Br(), self.text_input('growth_rating', in_type='number')], width=1),
                dbc.Col(["Health", html.Br(), self.text_input('health_rating', in_type='number')], width=1),
            ], justify='start'),
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
