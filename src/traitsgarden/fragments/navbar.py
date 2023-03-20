from dash import dcc, html, callback
from dash.dependencies import Input, Output, State, MATCH, ALL
import dash_bootstrap_components as dbc
from traitsgarden.fragments.search import search_bar, search_col

PLOTLY_LOGO = "https://images.plot.ly/logo/new-branding/plotly-logomark.png"

navbar = dbc.Navbar(
    # dbc.Container(
        [
            html.A(
                # Use row and col to control vertical alignment of logo / brand
                dbc.Row(
                    [
                        dbc.Col(html.Img(src=PLOTLY_LOGO, height="30px")),
                        dbc.Col(dbc.NavbarBrand("Traitsgarden", className="ms-2")),
                    ],
                    align="center",
                    className="g-0",
                ),
                href=f"index",
                style={"textDecoration": "none"},
            ),
            dbc.Button("Search", id="open-offcanvas", n_clicks=0),
            dbc.NavbarToggler(id="navbar-toggler", n_clicks=0),
            dbc.Collapse(
                # search_bar,
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

offcanvas = html.Div(
    [
        dbc.Offcanvas(
            search_col,
            id="offcanvas",
            title="Search",
            is_open=False,
        )
    ]
)

@callback(
    Output("offcanvas", "is_open"),
    Input("open-offcanvas", "n_clicks"),
    Input("search-button", "n_clicks"),
    [State("offcanvas", "is_open")],
)
def toggle_offcanvas(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open
