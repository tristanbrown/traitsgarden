from dash import dcc, html, callback, register_page
from dash.dependencies import Input, Output, State, MATCH, ALL
import dash_bootstrap_components as dbc

from traitsgarden.fragments.search import search_bar, search_col

PLOTLY_LOGO = "https://images.plot.ly/logo/new-branding/plotly-logomark.png"

# search_bar = dbc.Row(
#     [
#         dbc.Col(dbc.Input(type="search", placeholder="Search")),
#         dbc.Col(
#             dbc.Button(
#                 "Search", color="primary", className="ms-2", n_clicks=0
#             ),
#             width="auto",
#         ),
#     ],
#     className="g-0 ms-auto flex-nowrap mt-3 mt-md-0",
#     align="center",
# )

navbar = dbc.Navbar(
    # dbc.Container(
        [
            dbc.Button("Open Offcanvas", id="open-offcanvas", n_clicks=0),
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
            title="Title",
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
